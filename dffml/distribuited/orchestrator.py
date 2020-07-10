import secrets
import abc
import asyncio
import json
from queue import Queue

from dataclasses import field
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from contextlib import asynccontextmanager, AsyncExitStack, ExitStack
from typing import Dict, List, Any

from ..df.types import DataFlow, Operation, Definition, Input
from ..base import config, BaseConfig
from ..df.memory import (
    MemoryRedundancyChecker,
    MemoryLockNetwork,
    MemoryOperationImplementationNetwork,
    MemoryOperationImplementationNetworkContext,
    MemoryOperationNetworkContext,
    MemoryOperationNetwork
)
from ..df.base import (
    BaseOrchestratorContext,
    BaseOperationNetworkContext,
    BaseOperationNetwork,
    BaseDataFlowObject,
    BaseDataFlowObjectContext,
)

from ..util.asynchelper import aenter_stack

# Subjects
RegisterSubNode = "RegisterSubNode"
ConnectToPrimaryNode = "ConnectToPrimaryNode"
##


class CircularQueue(Queue):
    def get(self):
        v = super().get()
        self.put(v)
        return v


class NatsMainInputNetwork:
    pass


class NatsNodeInputNetwork:
    pass


@config
class NatsOperationNetworkConfig:
    operations: Dict[str, "OperationImplementation"] = field(
        default_factory=lambda: {},
    )


class NatsOperationNetworkContext(MemoryOperationNetworkContext):
    pass


class NatsOperationNetwork(MemoryOperationNetwork):

    CONFIG = NatsOperationNetworkConfig
    CONTEXT = NatsOperationNetworkContext


@config
class NatsNodeConfig:
    server: str
    cluster: str


class NatsNodeContext(BaseDataFlowObjectContext):
    async def __aenter__(self, enter={}):
        self.uid = secrets.token_hex()
        self.nc = NATS()
        print(f"Connecting to nats server {self.parent.config.server}")
        await self.nc.connect(
            self.parent.config.server, name=self.uid, connect_timeout=10
        )
        print("Connected")

        self.sc = STAN()
        print(f"Connecting to stan cluster {self.parent.config.cluster}")
        await self.sc.connect(
            self.parent.config.cluster, self.uid, nats=self.nc,
        )
        print("Connected")

        self._stack = AsyncExitStack()
        self._stack = await aenter_stack(self, enter)
        await self.init_node()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.sc.close()
        await self.nc.close()

    @abc.abstractmethod
    async def init_node(self):
        pass


@config
class NatsPrimaryNodeConfig(NatsNodeConfig):
    dataflow: DataFlow = None


class NatsPrimaryNodeContext(NatsNodeContext):
    async def register_subnode(self, msg):
        reply = msg.reply
        # Data of message contains list of names of
        # operation supported by the subnode
        data = msg.data.decode()
        data = json.loads(data)
        reply_data = {}
        for operation_name in data:
            # Only register operations that are needed by the dataflow
            if operation_name in self.required_operations:
                # If some other node also supports running this
                # operation,assign this node a token number in the
                # queue for this operation.
                if operation_name in self.nodes_for_operation:
                    opq = self.nodes_for_operation[operation_name]
                    token = len(opq) + 1
                    opq.put(token)
                else:
                    opq = CircularQueue()
                    token = 1
                    opq.put(token)
                    self.nodes_for_operation[operation_name] = opq

                reply_data[operation_name] = token
        reply_data = json.dumps(reply_data).encode()
        if set(self.required_operations) == set(
            self.nodes_for_operation.keys()
        ):
            self.got_all_operations.set()
        await self.nc.publish(reply, reply_data)

    async def init_node(self):
        # Primary node announces that it has started
        # All subnode contexts that are not already connected
        # sends list of operations supported by them.
        # Primary node responds with allocated token per operation
        self.got_all_operations = asyncio.Event()
        await self.sc.publish(ConnectToPrimaryNode, self.uid.encode())
        self.required_operations = [
            operation.name
            for operation in self.parent.config.dataflow.operations.values()
        ]
        self.nodes_for_operation = (
            {}
        )  # maps operations to registered nodes token Q
        sid = await self.nc.subscribe(
            RegisterSubNode,
            queue="SubNodeRegistrationQueue",
            cb=self.register_subnode,
        )
        await self.got_all_operations.wait()
        await self.nc.unsubscribe(sid)  # Stop listening to new node
        print("Ready to run dataflow")

        # Primary node goes through operation instances
        # in dataflow and assign an instance to a subnode
        # making sure that each subnode gets at least
        # one instance
        self.node_token_managing_instance = {
            instance_name: (
                operation.name,
                self.nodes_for_operation[operation.name].get(),
            )
            for instance_name, operation in self.parent.config.dataflow.operations
        }

        # Publish a message with subject as operation name,
        # with data containing node token number and operation
        # instance name. Sub node context will be subscribed
        # to operations they are running for the current dataflow

        for (
            intance_name,
            (operation_name, token),
        ) in self.node_token_managing_instance.items():
            payload = {
                "instance_name": intance_name,
                "token": token,
                "primary_node_id": self.uid,
            }
            await self.nc.publish(
                f"InstanceDetails{operation_name}",
                json.dumps(payload).encode(),
            )


class NatsPrimaryNode(BaseDataFlowObject):
    CONTEXT = NatsPrimaryNodeContext
    CONFIG = NatsPrimaryNodeConfig

    def __call__(self):
        return self.CONTEXT(BaseConfig(), self)


@config
class NatsSubNodeConfig(NatsNodeConfig):
    operations: List[Operation] = field(default_factory=lambda: [])


class NatsSubNodeContext(NatsNodeContext):
    async def connection_ack_handler(self, msg):
        print(f"Connected to primary node {msg}")
        # Subnode need to record the primary node context
        # which its connected to, so that it only accepts
        # input from that node; incase multiple primary nodes
        # are connected to the same server
        self.primary_node_id = msg.data.decode()
        self.connection_ack.set_result(None)

    async def set_instance_details(self, msg):
        subject = msg.subject
        operation_name = subject.replace("InstanceDetails", "")
        # data is expected to contain 'instance_name':('operation_name','token')
        data = msg.data.decode()
        token = data["token"]
        instance_name = data["instance_name"]
        if (data["primary_node_id"] == self.primary_node_id) and (
            token == self.operation_token[operation_name]
        ):
            self.operation_instances[instance_name] = operation_name

    async def init_node(self):
        self.operation_names = {
            operation.name: operation
            for operation in self.parent.config.operations
        }
        self.operation_instances: Dict[str, Operation] = {}
        self.operation_token = {}  # op_name -> token

        # Subnode waits for a connection to a primary node
        self.connection_ack = asyncio.Future()
        await self.sc.subscribe(
            ConnectToPrimaryNode,
            cb=self.connection_ack_handler,
            start_at="first",
        )
        await asyncio.wait_for(self.connection_ack, timeout=100)

        # Subscribe to instance details
        # We cannot request for instance details because,
        # all subnodes need to complete registration before
        # primary node can allocate instances uniformly
        for operation in self.parent.config.operations:
            await self.nc.subscribe(
                f"InstanceDetails{operation.name}",
                queue="SetInstanceDetails",
                cb=self.set_instance_details,
            )

        # Send list of operation supported by the node
        msg_data = json.dumps(list(self.operation_names.keys())).encode()

        # Request node registration
        response = await self.nc.request(RegisterSubNode, msg_data)
        # Response contains operation names mapped to token number
        response = json.loads(response.data.decode())
        self.operation_token.update(response)
        print(f"subnode initialized, operations : {self.operation_token}")


class NatsSubNode(BaseDataFlowObject):
    CONTEXT = NatsSubNodeContext
    CONFIG = NatsSubNodeConfig

    def __call__(self):
        return self.CONTEXT(BaseConfig(), self)
