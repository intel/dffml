import secrets
import abc
import asyncio
import json
from queue import Queue

from dataclasses import field
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from contextlib import asynccontextmanager, AsyncExitStack, ExitStack
from typing import Dict,List,Any

from ..df.types import DataFlow,Operation,Definition,Input
from ..base import config,BaseConfig
from ..df.memory import MemoryRedundancyChecker,MemoryLockNetwork
from ..df.base import (
    BaseOrchestratorContext,
    BaseOperationNetworkContext,
    BaseOperationNetwork,
    BaseDataFlowObject,
    BaseDataFlowObjectContext,
    )


# Subjects
RegisterSubNode = "RegisterSubNode"
ConnectToPrimaryNode = "ConnectToPrimaryNode"
##

class CircularQueue(Queue):
    def put(self,item):
        super().put(item)
    def get(self):
        v = super().get()
        self.put(v)
        return v


class NatsMainInputNetwork:
    pass

class NatsNodeInputNetwork:
    pass

class NatsOperationImplementationNetwork:
    pass



@config
class NatsNodeConfig:
    server: str
    cluster: str


class NatsNodeContext(BaseDataFlowObjectContext):
    async def __aenter__(self):
        self.uid = secrets.token_hex()
        self.nc = NATS()
        print(f"Connecting to nats server {self.parent.config.server}")
        await self.nc.connect(self.parent.config.server,
            name=self.uid,connect_timeout=10
            )
        print("Connected")

        self.sc = STAN()
        print(f"Connecting to stan cluster {self.parent.config.cluster}")
        await self.sc.connect(self.parent.config.cluster,self.uid,nats = self.nc,)
        print("Connected")


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
    dataflow:DataFlow = None

class NatsPrimaryNodeContext(NatsNodeContext):
    async def register_subnode(self,msg):
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
        if set(self.required_operations) == set(self.nodes_for_operation.keys()):
            self.got_all_operations.set()
        await self.nc.publish(reply,reply_data)

    async def init_node(self):
        # Primary node announces that it has started
        # All subnode contexts that are not already connected
        # sends list of operations supported by them.
        # Primary node responds with allocated token per operation
        self.got_all_operations = asyncio.Event()
        await self.sc.publish(ConnectToPrimaryNode,self.uid.encode())
        self.required_operations = [
            operation.name
            for operation in self.parent.config.dataflow.operations.values()
            ]
        self.nodes_for_operation = {} # maps operations to registered nodes
        await self.nc.subscribe(RegisterSubNode,
            queue="SubNodeRegistrationQueue",cb=self.register_subnode)
        await self.got_all_operations.wait()
        print("Ready to run dataflow")


class NatsPrimaryNode(BaseDataFlowObject):
    CONTEXT = NatsPrimaryNodeContext
    CONFIG = NatsPrimaryNodeConfig

    def __call__(self):
        return self.CONTEXT(BaseConfig(),self)

@config
class NatsSubNodeConfig(NatsNodeConfig):
    operations: List[Operation] =field(default_factory = lambda:[])
class NatsSubNodeContext(NatsNodeContext):

    async def connection_ack_handler(self,msg):
        print(f"Connected to primary node {msg}")
        # Subnode need to record the primary node context
        # which its connected to, so that it only accepts
        # input from that node; incase multiple primary nodes
        # are connected to the same server
        self.primary_node_id = msg.data.decode()
        self.connection_ack.set_result(None)


    async def init_node(self):
        # Subnode waits for a connection to a primary node
        self.connection_ack = asyncio.Future()
        await self.sc.subscribe(ConnectToPrimaryNode,
            cb=self.connection_ack_handler,start_at="first")
        await asyncio.wait_for(self.connection_ack,timeout=100)

        # Send list of operation supported by the node
        self.operation_token = {}
        msg_data = json.dumps(
            [operation.name for operation in self.parent.config.operations ]
            ).encode()
        response = await self.nc.request(RegisterSubNode,msg_data)
        # Response contains operation names mapped to token number
        response = json.loads(response.data.decode())
        self.operation_token.update(response)
        print(f"subnode initialised, operations : {self.operation_token}")

class NatsSubNode(BaseDataFlowObject):
    CONTEXT = NatsSubNodeContext
    CONFIG = NatsSubNodeConfig

    def __call__(self):
        return self.CONTEXT(BaseConfig(),self)


