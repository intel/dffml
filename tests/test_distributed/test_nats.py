import os
import time
import base64
import pathlib
import asyncio
import sqlite3
import tempfile
import subprocess
import contextlib
import concurrent
from collections import defaultdict
from multiprocessing.managers import BaseManager
from multiprocessing import Manager, cpu_count,Queue, Process
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from nats.aio.client import Client as NATS

from dffml.distributed.orchestrator import (
    NatsOrchestratorNode,
    NatsOrchestratorNodeConfig,
    NatsWorkerNode,
    NatsWorkerNodeConfig,
)

from dffml import DataFlow,op,Definition,Input
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.output import GetSingle
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_create_table,
    db_query_insert_or_update,
)
from dffml.util.net import cached_download_unpack_archive
from dffml.util.os import prepend_to_path

from tests.test_df import parse_line, add, mult, is_add, is_mult

# Source for _ProcQueue
#https://stackoverflow.com/questions/24687061/can-i-somehow-share-an-asynchronous-queue-with-a-subprocess

class NatsTestCase(AsyncTestCase):
    async def echoAll(self,msg):
        print(msg)

    @cached_download_unpack_archive(
        "https://github.com/nats-io/nats-server/releases/download/v2.0.0/nats-server-v2.0.0-linux-amd64.zip",
        pathlib.Path(__file__).parent / "downloads" / "nats-server.zip",
        pathlib.Path(__file__).parent / "downloads" / "nats-server",
        "47c56fd6ae24b339fbb77bfa9b0e578e56b8f191e31abc09c15f5db87eda928291119023947d80dfd902708dcc2bdf25",
    )
    async def setUp(self, nats_server):
        with prepend_to_path(nats_server / "nats-server-v2.0.0-linux-amd64"):
            os.chmod(
                nats_server / "nats-server-v2.0.0-linux-amd64" / "nats-server",
                0o755
            )
            self.nats_proc = subprocess.Popen(
                ["nats-server", "-p", "-1",],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        ready = False
        listen_text = "Listening for client connections on "
        while not ready:
            line = self.nats_proc.stdout.readline().decode()
            if listen_text in line:
                line = line.strip().split(listen_text)
                self.server_addr = line[-1]
            if "Server is ready" in line:
                ready = True

        self.nc = NATS()
        await self.nc.connect(self.server_addr)
        # await self.nc.subscribe(
        #     ">",
        #     cb=self.echoAll,
        # )

    async def tearDown(self):
        self.nats_proc.terminate()


# See
# https://docs.python.org/3.7/library/multiprocessing.html#using-a-remote-manager
# for more details.
class QueueManager(BaseManager):
    pass


QueueManager.register('get_queue')


@op
async def q_op(port: int, authkey: bytes, number: int) -> None:
    m = QueueManager(
        address=("127.0.0.1", port),
        authkey=base64.b64decode(authkey),
    )
    m.connect()
    q = m.get_queue()
    q.put(number)
    return
    print(f"length of queue {len(q)}")
    while len(q) < 1:
        continue
    print(f"{os.getpid()}: Operation Complete")

async def _spawnWorker(q:"AsyncProcessQueue",
    worker_config:"NatsWorkerNodeConfig",
    ):
    print(f"Spawning worker")
    wnode = NatsWorkerNode(worker_config)
    await wnode.__aenter__()
    # Notify orchestrator that we are ready for processing
    q.put(1)
    await asyncio.Event().wait()

def spawnWorker(q,worker_config):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_spawnWorker(q,worker_config))


class TestNatsOrchestratorSimple(NatsTestCase):
    async def test_run(self):
        server = self.server_addr
        test_operations = [
            [parse_line.op,],
            [add.op,mult.op]
        ]

        worker_nodes = [
            NatsWorkerNode(NatsWorkerNodeConfig(server, operations=ops))
            for ops in test_operations
        ]


        dataflow = DataFlow.auto(parse_line,add,mult,GetSingle)

        dataflow.seed = [
                Input(
                    value=[dataflow.definitions["result"].name],
                    definition=GetSingle.op.inputs["spec"],
             )
            ]

        orchestrator_node = NatsOrchestratorNode(
            NatsOrchestratorNodeConfig(
                server=server,
                dataflow=dataflow
            )
        )

        test_input = {
            "testInput": [
                Input(
                    value = "add 40 and 42",
                    definition=parse_line.op.inputs["line"]
                )
            ]
        }

        async with contextlib.AsyncExitStack() as stack:
            worker_nodes = [
                await stack.enter_async_context(wnode)
                for wnode in worker_nodes
            ]
            async with orchestrator_node as onode:
                async with onode() as onctx:
                    async for ctx,results in onctx.run(test_input):
                        print(results)

class TestNatsOrchestratorParallel(NatsTestCase):
    async def test_run(self):
        n_workers = 4

        worker_configs = [
            NatsWorkerNodeConfig(self.server_addr,operations=[q_op.op])
            for _ in range(n_workers)
        ]


        class QueueManager(BaseManager):
            pass


        q = Queue()
        QueueManager.register('get_queue', callable=lambda: q)


        # Port of the multiprocessing.BaseManager to connect to. Will be set to the
        # bound to port by the process running the manager.
        manager_port = 0
        # The authkey for the multiprocessing.BaseManager (384 random bits)
        # TODO(pdxjohnny -> aghinsa) Here I've base 64 encoded the bytes to be
        # used as the authkey. This is because there was a JSON encode error
        # when it was raw bytes being sent to nats. You should b64 encode and
        # decode any values for definitions with "bytes" or "binary" primitives.
        manager_authkey = os.urandom(int(384 / 8))
        # We use a remote multiprocessing.BaseManager to provide worker nodes
        # with access to the queue
        m = QueueManager(
            address=("127.0.0.1", manager_port),
            authkey=manager_authkey,
        )

        loop = asyncio.get_event_loop()

        for worker_config in worker_configs:
            # await loop.run_in_executor(ProcessPoolExecutor(),spawnWorker,q,worker_config)
            Process(target = spawnWorker,args = (q,worker_config)).start()

        # Never rely on timing. Always ensure you know state of a distributed
        # system through some form of communication
        for i, _ in enumerate(worker_configs):
            q.get()

        orchestrator_node = NatsOrchestratorNode(
            NatsOrchestratorNodeConfig(
                server=self.server_addr,
                dataflow=DataFlow(
                    operations={
                        "q_op.op": q_op.op,
                    },
                ),
            )
        )

        with m:
            # The port the listening manager server is bound to
            manager_port = m._address[1]
            async with orchestrator_node as onode:
                async with onode() as onctx:
                    async for ctx,results in onctx.run([
                        Input(
                            value=manager_port,
                            definition=q_op.op.inputs["port"],
                        ),
                        Input(
                            value=base64.b64encode(manager_authkey).decode('ascii'),
                            definition=q_op.op.inputs["authkey"],
                        ),
                    ] + [
                        Input(
                            value=i,
                            definition=q_op.op.inputs["number"]
                        )
                        for i in range(0, n_workers)
                    ]):
                        print(results)


class TestNatsOrchestrator(NatsTestCase):
    async def setUp(self):
        await super().setUp()
        # - A worker node reads from a file containing input strings
        # - Input string are processed by another worker nodes(s)
        #   perfroming calc_string
        # - The result is stored in a database by another worker node
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS calculations (asString text PRIMARY KEY,value integer);"
        )
        self.cursor.execute("INSERT INTO calculations VALUES ('1+2' , 2)")
        self.cursor.execute("SELECT * FROM calculations")
        rows = self.cursor.fetchall()


    async def tearDown(self):
        self.conn.close()
        self.nats_proc.terminate()

    async def test_run(self):
        server = self.server_addr
        test_operations = [
            [parse_line.op,],
            [add.op, mult.op],
            [db_query_create_table.op, db_query_insert_or_update.op],
            [GetSingle.op],
        ]

        worker_nodes = [
            NatsWorkerNode(NatsWorkerNodeConfig(server, operations=ops))
            for ops in test_operations
        ]

        # Creating database
        fileno, database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        sdb = SqliteDatabase(SqliteDatabaseConfig(filename=":memory:"))

        primarynode = NatsOrchestratorNode(
            NatsOrchestratorNodeConfig(
                server=server,
                dataflow=DataFlow(
                    operations={
                        "parse_line": parse_line.op,
                        "add": add.op,
                        "mult": mult.op,
                        "db_create": db_query_create_table.op,
                        "db_insert": db_query_insert_or_update.op,
                        "get_single": GetSingle.imp.op,
                    },
                    configs={
                        "db_create": DatabaseQueryConfig(database=sdb),
                        "db_insert": DatabaseQueryConfig(database=sdb),
                    },
                ),
            )
        )

        async with contextlib.AsyncExitStack() as stack:
            worker_nodes = [
                await stack.enter_async_context(wnode)
                for wnode in worker_nodes
            ]
            async with primarynode as pn:
                async with pn() as pnctx:
                    tokens_assigned = defaultdict(lambda: [])
                    opimps_instantiated = []
                    # Itertate through all worker nodes and
                    # make sure contexts are instantiated, all
                    # the expected operation tokens/implementations
                    # have been set.
                    for wnode in worker_nodes:
                        self.assertTrue(wnode.running_contexts)
                        for snctx in wnode.running_contexts:
                            for (
                                op_name,
                                token,
                            ) in snctx.operation_token.items():
                                tokens_assigned[op_name].append(token)
                            opimps_instantiated.extend(
                                snctx.opimpctx.operations.keys()
                            )

                    print(tokens_assigned)
                    print(opimps_instantiated)
