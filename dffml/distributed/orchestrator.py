import abc
import json
import asyncio
import secrets
import traceback
from queue import Queue
from dataclasses import field
from typing import Dict, List, Any
from contextlib import asynccontextmanager, AsyncExitStack, ExitStack

from nats.aio.client import Client as NATS

from ..base import config, BaseConfig
from ..util.asynchelper import aenter_stack
from ..df.types import DataFlow, Operation, Definition, Input
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
    BaseOperationImplementationNetworkContext,
)


# Subjects
RegisterWorkerNode = "RegisterWorkerNode"
ConnectToOrchestratorNode = "ConnectToOrchestratorNode"
OrchestratorNodeReady = "OrchestratorNodeReady"

####

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


class NatsOperationImplementationNetworkContext(
    MemoryOperationImplementationNetworkContext
):
    def __init__(
        self, config: BaseConfig, parent: "NatsWorkerNodeContext",
    ):
        BaseOperationImplementationNetworkContext.__init__(
            self, config, parent
        )
        self.operations = {}

    async def instantiate_operation(self,operation,instance_name):
        opimp = self.parent.operation_configs.get(operation.name, None)
        opconfig = self.parent.operation_configs.get(instance_name, {})
        self.logger.debug(
            f"Instantiating instance {instance_name} of operation {operation} with config {opconfig}"
        )
        await self.instantiate(operation, config=opconfig, opimp=opimp)
        await self.parent.nc.publish(
            f"InstanceAck.{instance_name}.{self.parent.onid}", b""
        )

    async def __aenter__(self):
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        return self


class NatsNodeContext(BaseDataFlowObjectContext):
    async def __aenter__(self, enter=None, call=False):
        self.uid = secrets.token_hex(nbytes=NBYTES_UID)
        self.nc = self.parent.nc
        self._stack = AsyncExitStack()
        self._stack = await aenter_stack(self, enter, call)
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
    async def error_handler(self, msg):
        tb = traceback.format_exc()
        print()
        print(tb)
        print(f"ERROR in node {self.uid}")
        print()

    async def __aenter__(self, enter={}):
        self.uid = secrets.token_hex(nbytes=NBYTES_UID)
        self.logger.debug(f"New node: {self.uid}",)
        self.nc = NATS()
        self.logger.debug(f"Connecting to nats server {self.config.server}")
        await self.nc.connect(
            self.config.server,
            name=self.uid,
            connect_timeout=10,
            error_cb=self.error_handler,
        )
        self.logger.debug(f"Connected to nats server {self.config.server}")
        await self.init_node()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.nc.close()

    @abc.abstractmethod
    async def init_node(self):
        pass


@config
class NatsOrchestratorNodeConfig(NatsNodeConfig):
    dataflow: DataFlow = None


class NatsOrchestratorNodeContext(NatsNodeContext):
    async def register_worker_node(self, msg):
        self.logger.debug(f"Registering new worker node context")
        reply = msg.reply
        # Data of message contains list of names of
        # operation supported by the worker node
        data = msg.data.decode()
        data = json.loads(data)
        self.logger.debug(f"Received data {data}")

        reply_data = {}
        for operation_name in data:
            # Only register operations that are needed by the dataflow
            if operation_name in self.required_operations:
                # If some other node also supports running this
                # operation,assign this node a token number in the
                # queue for this operation.
                if operation_name in self.nodes_for_operation:
                    opq = self.nodes_for_operation[operation_name]
                    token = opq.qsize() + 1
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
            self.all_ops_available.set()

        await self.nc.publish(reply, reply_data)

    async def acknowledge_instance(self, msg):
        _, *instance_name, snctx_id = msg.subject.split(".")
        instance_name = ".".join(instance_name)

        self.logger.debug(f"Ack: Instance {instance_name} acknowleged")
        self.logger.debug(
            f"self.instances_to_be_acklowledged: {self.instances_to_be_acklowledged}"
        )

        self.instances_to_be_acklowledged.remove(instance_name)
        if len(self.instances_to_be_acklowledged) == 0:
            self.all_op_instantiated.set_result(None)

    async def init_context(self):
        self.logger.debug("Initializing new orchestrator node context")
        # Orchestrator node announces that it has started
        # All worker node contexts that are not already connected
        # sends list of operations supported by them.
        # Onode responds with allocated token per operation
        self.all_ops_available = asyncio.Event()
        await self.nc.publish(ConnectToOrchestratorNode, self.uid.encode())
        self.required_operations = [
            operation.name
            for operation in self.parent.config.dataflow.operations.values()
        ]

        # Maps operations to circular queue which contains
        # tokens of worker nodes allocated with different
        # instances of an operation
        self.nodes_for_operation = {}

        await self.nc.subscribe(
            f"{RegisterWorkerNode}.{self.uid}",
            queue="WorkerNodeRegistrationQueue",
            cb=self.register_worker_node,
        )
        self.logger.debug("Waiting for all operations to be found")
        await self.all_ops_available.wait()
        self.logger.debug("All required operations found")

        # Onode goes through operation instances
        # in dataflow and assign an instance to a worker node
        # making sure that each worker node gets at least
        # one instance
        self.dataflow = self.parent.config.dataflow
        self.node_token_managing_instance = {
            instance_name: (
                operation.name,
                self.nodes_for_operation[operation.name].get(),
            )
            for instance_name, operation in self.dataflow.operations.items()
        }
        self.logger.debug(
            f"Token allocated for instances {self.node_token_managing_instance}"
        )
        # Publish a message with subject as operation name,
        # with data containing node token number and operation
        # instance name. Sub node context will be subscribed
        # to operations they are running for the current dataflow.

        # Whenever pnctx publishes instance details to snctx
        # it keeps log of it and waits for acknwoledgment from
        # the same snctx after instantiating the operation.
        # Execution is blocked till all operations are instantiated.

        self.all_op_instantiated = asyncio.Future()
        self.instances_to_be_acklowledged = set()
        for (
            instance_name,
            (operation_name, token),
        ) in self.node_token_managing_instance.items():
            payload = {
                "instance_name": instance_name,
                "token": token,
                "config": (
                    self.dataflow.configs[instance_name]._asdict()
                    if instance_name in self.dataflow.configs
                    else {}
                ),
            }
            self.instances_to_be_acklowledged.add(instance_name)
            await self.nc.subscribe(
                f"InstanceAck.{instance_name}.{self.uid}",
                queue="InstanceAcknoledgments",
                cb=self.acknowledge_instance,
            )
            self.logger.debug(f"Publishing instance details: {payload}")
            await self.nc.publish(
                f"InstanceDetails{operation_name}.{self.uid}",
                json.dumps(payload).encode(),
            )

        await self.nc.publish(f"{OrchestratorNodeReady}.{self.uid}", b"")
        self.logger.debug("Waiting for all ops to be instantiated")
        await asyncio.wait_for(self.all_op_instantiated, timeout=None)
        self.logger.debug("All ops instantiated")


class NatsOrchestratorNode(NatsNode):
    CONTEXT = NatsOrchestratorNodeContext
    CONFIG = NatsOrchestratorNodeConfig

    def __call__(self):
        return self.CONTEXT(BaseConfig(), self)


@config
class NatsWorkerNodeContextConfig:
    orchestrator_node_id: str


class NatsWorkerNodeContext(NatsNodeContext):
    CONFIG = NatsWorkerNodeContextConfig

    async def __aenter__(self,):
        self.uid = secrets.token_hex(nbytes=NBYTES_UID)
        self.nc = self.parent.nc
        self.context_done = asyncio.Future()
        self._stack = AsyncExitStack()
        await self.init_context()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.logger.debug("Exiting context")
        await self._stack.aclose()

    async def set_instance_details(self, msg):
        subject = msg.subject
        # Operation name might contain '.'
        *subject, onid = subject.split(".")
        subject = ".".join(subject)
        operation_name = subject.replace("InstanceDetails", "")

        # data is expected to contain 'instance_name':('operation_name','token')
        data = msg.data.decode()

        data = json.loads(data)
        self.logger.debug(f"Received instance details: {data}")
        token = data["token"]
        instance_name = data["instance_name"]
        config = data["config"]

        op_for_instance = self.operation_names[
            operation_name
        ]._replace(instance_name=instance_name)
        self.operation_instances[instance_name] = op_for_instance
        if config:
            self.operation_configs[instance_name] = config

        # Instantiate operation
        await self.opimpctx.instantiate_operation(op_for_instance,instance_name)

    async def init_context(self):
        self.onid = self.config.orchestrator_node_id
        self.logger.debug(
            f"New worker node context {self.uid} connected to orchestrator node {self.onid}"
        )

        self.operation_implemtaions = {}
        self.operation_configs = {}
        self.operation_instances: Dict[str, Operation] = {}
        self.operation_token = {}  # op_name -> token

        self.operation_names = {
            operation.name: operation
            for operation in self.parent.config.operations
        }

        # Look for implementations provided in sub node
        # if any. If no implementations are provided,
        # the operation is assumed to be entrypoint loadable.
        # opimpNetworkctx raises an exception if implementation
        # is not found in both ways.
        for operation_name in self.operation_names:
            if operation_name in self.parent.config.implementations:
                self.operation_implemtaions[
                    operation_name
                ] = self.parent.config.implementations[operation_name]

        self.opimpctx = await self._stack.enter_async_context(
            NatsOperationImplementationNetworkContext(BaseConfig(), self)
        )
        self.logger.debug(f"Operation implementation network instantiated")

        # Subscribe to instance details.
        # We cannot request for instance details because,
        # all worker nodes need to complete registration before
        # orchestrator node can allocate instances uniformly
        for operation in self.parent.config.operations:
            self.logger.debug("Listening for instance details on"
                    + f"InstanceDetails{operation.name}.{self.onid}")

            await self.nc.subscribe(
                f"InstanceDetails{operation.name}.{self.onid}",
                queue="SetInstanceDetails",
                cb=self.set_instance_details,
            )


        # Send list of operation supported by the node
        msg_data = json.dumps(list(self.operation_names.keys())).encode()
        # Request node registration
        self.logger.debug(
            "Requesting context registration and token allocation"
        )
        response = await self.nc.request(
            f"{RegisterWorkerNode}.{self.onid}", msg_data
        )
        # Response contains operation names mapped to token number
        response = json.loads(response.data.decode())
        self.operation_token.update(response)
        self.logger.debug(f"Tokens received: {response}")


@config
class NatsWorkerNodeConfig(NatsNodeConfig):
    operations: List[Operation] = field(default_factory=lambda: [])
    implementations: Dict[str, "OperationImplementation"] = field(
        default_factory=lambda: {}
    )


class NatsWorkerNode(NatsNode):
    CONTEXT = NatsWorkerNodeContext
    CONFIG = NatsWorkerNodeConfig

    async def connection_ack_handler(self, msg):
        orchestrator_node_id = msg.data.decode()
        self.logger.debug(
            f"Got connection request from orchestrator node {orchestrator_node_id}"
        )
        self.running_contexts.append(
            await self.CONTEXT(
                NatsWorkerNodeContextConfig(orchestrator_node_id), self
            ).__aenter__()
        )

    async def init_node(self):
        self.logger.debug(
            f"New worker node with operations {self.config.operations}"
        )
        self.running_contexts = []
        # Worker node waits for a connection to a orchestrator node
        await self.nc.subscribe(
            ConnectToOrchestratorNode, cb=self.connection_ack_handler,
        )

    def __call__(self):
        return self
