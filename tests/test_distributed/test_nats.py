import os
import time
import asyncio
import sqlite3
import tempfile
import subprocess
import contextlib
import concurrent
from collections import defaultdict
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

from tests.test_df import parse_line, add, mult, is_add, is_mult

# Source for _ProcQueue
#https://stackoverflow.com/questions/24687061/can-i-somehow-share-an-asynchronous-queue-with-a-subprocess

class NatsTestCase(AsyncTestCase):
    async def echoAll(self,msg):
        print(msg)

    async def setUp(self):
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

@op(
    inputs={"q":Definition(name="shared_q",primitive="AsyncProceeQueue")},
    outputs = {}
)
async def q_op(q):
    q.put(1)
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
        m = Manager()
        q = m.Queue()
        loop = asyncio.get_event_loop()

        for worker_config in worker_configs:
            # await loop.run_in_executor(ProcessPoolExecutor(),spawnWorker,q,worker_config)
            Process(target = spawnWorker,args = (q,worker_config)).start()

        time.sleep(1)

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

        all_workers_ran = asyncio.Event()
        async def check_all_workers_ran():
            while True:
                print(q.qsize())
                if q.qsize() == n_workers:
                    all_workers_ran.set()
                asyncio.sleep(.5)

        await check_all_workers_ran()
        async with orchestrator_node as onode:
                async with onode() as onctx:
                    await all_workers_ran.wait()

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
