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
    MemoryOperationNetwork,
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

NBYTES_UID = 6


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


class NatsNodeContext(BaseDataFlowObjectContext):
    async def __aenter__(self, enter={}):
        self.uid = secrets.token_hex(nbytes=NBYTES_UID)
        self.nc = self.parent.nc

        self._stack = AsyncExitStack()
        self._stack = await aenter_stack(self, enter)
        await self.init_context()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._stack.aclose()

    @abc.abstractmethod
    async def init_context(self):
        pass


@config
class NatsNodeConfig:
    server: str


class NatsNode(BaseDataFlowObject):
    async def __aenter__(self, enter={}):
        self.uid = secrets.token_hex(nbytes=NBYTES_UID)
        self.nc = NATS()
        print(f"Connecting to nats server {self.config.server}")
        await self.nc.connect(
            self.config.server, name=self.uid, connect_timeout=10
        )
        print("Connected")

        await self.init_node()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # await self.sc.close()
        await self.nc.close()

    @abc.abstractmethod
    async def init_node(self):
        pass


@config
class NatsPrimaryNodeConfig(NatsNodeConfig):
    dataflow: DataFlow = None


class NatsPrimaryNodeContext(NatsNodeContext):
    async def register_subnode(self, msg):
        print(f"Registering subnode {msg}")
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

    async def init_context(self):
        # Primary node announces that it has started
        # All subnode contexts that are not already connected
        # sends list of operations supported by them.
        # Primary node responds with allocated token per operation
        self.got_all_operations = asyncio.Event()
        await self.nc.publish(ConnectToPrimaryNode, self.uid.encode())
        self.required_operations = [
            operation.name
            for operation in self.parent.config.dataflow.operations.values()
        ]
        self.nodes_for_operation = (
            {}
        )  # maps operations to registered nodes token Q

        sid = await self.nc.subscribe(
            f"{RegisterSubNode}.{self.uid}",
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
            for instance_name, operation in self.parent.config.dataflow.operations.items()
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
            }
            await self.nc.publish(
                f"InstanceDetails{operation_name}.{self.uid}",
                json.dumps(payload).encode(),
            )


class NatsPrimaryNode(NatsNode):
    CONTEXT = NatsPrimaryNodeContext
    CONFIG = NatsPrimaryNodeConfig

    def __call__(self):
        return self.CONTEXT(BaseConfig(), self)


@config
class NatsSubNodeContextConfig:
    primary_node_id: str


class NatsSubNodeContext(NatsNodeContext):
    CONFIG = NatsSubNodeContextConfig

    async def set_instance_details(self, msg):
        subject = msg.subject
        subject, primary_id = subject.split(".")
        operation_name = subject.replace("InstanceDetails", "")
        # data is expected to contain 'instance_name':('operation_name','token')
        data = msg.data.decode()
        token = data["token"]
        instance_name = data["instance_name"]
        if (data["primary_node_id"] == self.pnid) and (
            token == self.operation_token[operation_name]
        ):
            self.operation_instances[instance_name] = operation_name

    async def init_context(self):
        self.pnid = self.config.primary_node_id
        print(f"New sub node context intialized id: {self.uid}")
        print(f"<{self.uid}>: connected to primary node {self.pnid}")

        self.operation_names = {
            operation.name: operation
            for operation in self.parent.config.operations
        }
        self.operation_instances: Dict[str, Operation] = {}
        self.operation_token = {}  # op_name -> token

        # Subscribe to instance details
        # We cannot request for instance details because,
        # all subnodes need to complete registration before
        # primary node can allocate instances uniformly
        for operation in self.parent.config.operations:
            await self.nc.subscribe(
                f"InstanceDetails{operation.name}.{self.pnid}",
                queue="SetInstanceDetails",
                cb=self.set_instance_details,
            )

        # Send list of operation supported by the node
        msg_data = json.dumps(list(self.operation_names.keys())).encode()

        # Request node registration
        response = await self.nc.request(
            f"{RegisterSubNode}.{self.pnid}", msg_data
        )
        # Response contains operation names mapped to token number
        response = json.loads(response.data.decode())
        self.operation_token.update(response)
        print(
            f"subnode context initialized, operations : {self.operation_token}"
        )


@config
class NatsSubNodeConfig(NatsNodeConfig):
    operations: List[Operation] = field(default_factory=lambda: [])


class NatsSubNode(NatsNode):
    CONTEXT = NatsSubNodeContext
    CONFIG = NatsSubNodeConfig

    async def connection_ack_handler(self, msg):
        primary_node_id = msg.data.decode()
        self.running_contexts.append(
            await self.CONTEXT(
                NatsSubNodeContextConfig(primary_node_id), self
            ).__aenter__()
        )

    async def init_node(self):
        self.running_contexts = []
        # Subnode waits for a connection to a primary node
        await self.nc.subscribe(
            ConnectToPrimaryNode, cb=self.connection_ack_handler,
        )
        self.keep_running = asyncio.Future()
        await asyncio.wait_for(self.keep_running, timeout=None)

    def __call__(self):
        return self
