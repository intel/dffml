import io
import os
import sys
import abc
import glob
import json
import uuid
import shutil
import inspect
import asyncio
import hashlib
import tempfile
import unittest
import itertools
import collections
from itertools import product
from datetime import datetime
from contextlib import asynccontextmanager, AsyncExitStack
from typing import AsyncIterator, Dict, List, Tuple, Any, NamedTuple, Union, \
        get_type_hints, NewType, Optional, Set, Iterator

from dffml.df import *
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

definitions = [
    Definition(
        name='calc_string',
        primitive='str'
    ),
    Definition(
        name="is_add",
        primitive="bool"
    ),
    Definition(
        name="is_mult",
        primitive="bool"
    ),
    Definition(
        name="numbers",
        primitive="List[int]"
    ),
    Definition(
        name='result',
        primitive='int'
    )
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)

@op(inputs={
        'numbers': numbers
        },
    outputs={
        'sum': result
        },
    conditions=[is_add])
async def add(numbers: List[int]):
    return {'sum': sum(numbers)}

@op(inputs={
        'numbers': numbers
        },
    outputs={
        'product': result
        },
    conditions=[is_mult])
async def mult(numbers: List[int]):
    product = 1
    for number in numbers:
        product *= number
    return {'product': product}

@op(inputs={
        'line': calc_string
        },
    outputs={
        'add': is_add,
        'mult': is_mult,
        'numbers': numbers
        })
async def parse_line(line: str):
    return {
        'add': 'add' in line,
        'mult': 'mult' in line,
        'numbers': [int(item) for item in line.split() if item.isdigit()]
        }

class TestMemoryKeyValueStore(AsyncTestCase):

    def setUp(self):
        self.kvStore = MemoryKeyValueStore(BaseConfig())

    async def test_set(self):
        async with self.kvStore as ctx:
            await ctx.set('feed', b'face')
        self.assertEqual(self.kvStore.memory.get('feed'), b'face')

    async def test_get(self):
        self.kvStore.memory['feed'] = b'face'
        async with self.kvStore as ctx:
            self.assertEqual(await ctx.get('feed'), b'face')

class TestMemoryOperationImplementationNetwork(AsyncTestCase):

    def setUp(self):
        self.operationsNetwork = MemoryOperationImplementationNetwork(
            MemoryOperationImplementationNetworkConfig(
                operations={
                    'add': add.imp(BaseConfig())
                }
            )
        )

    async def test_contains(self):
        async with self.operationsNetwork() as ctx:
            self.assertTrue(await ctx.contains(add.op))

    async def test_run(self):
        async with self.operationsNetwork() as ctx:
            # No input set context and input network context required to test
            # the add operation
            self.assertEqual(42, (await ctx.run(None, None, add.op, {
                'numbers': [40, 2]
            }))['sum'])

class TestLinker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.linker = Linker()

    def test_resolve(self):
        self.linker.resolve(self.linker.export(add.op))

    def test_export(self):
        exported = self.linker.export(add.op)
        # Operations
        self.assertIn('operations', exported)
        self.assertIn('add', exported['operations'])
        self.assertIn('inputs', exported['operations']['add'])
        self.assertIn('outputs', exported['operations']['add'])
        self.assertIn('numbers', exported['operations']['add']['inputs'])
        self.assertEqual('numbers',
                         exported['operations']['add']['inputs']['numbers'])
        self.assertIn('sum', exported['operations']['add']['outputs'])
        self.assertEqual('result',
                         exported['operations']['add']['outputs']['sum'])
        # Definitions
        self.assertIn('definitions', exported)
        self.assertIn('numbers', exported['definitions'])
        self.assertIn('primitive', exported['definitions']['numbers'])
        self.assertEqual('List[int]',
                         exported['definitions']['numbers']['primitive'])
        self.assertIn('result', exported['definitions'])
        self.assertIn('primitive', exported['definitions']['result'])
        self.assertEqual('int',
                         exported['definitions']['result']['primitive'])

OPWRAPED = opwraped_in(sys.modules[__name__])
OPERATIONS = operation_in(sys.modules[__name__]) + \
             list(map(lambda item: item.op, OPWRAPED))
OPIMPS = opimp_in(sys.modules[__name__]) + \
         list(map(lambda item: item.imp, OPWRAPED))

class TestRunner(AsyncTestCase):

    async def test_run(self):
        linker = Linker()
        exported = linker.export(*OPERATIONS)
        definitions, operations, _outputs = linker.resolve(exported)

        calc_strings_check = {
                'add 40 and 2': 42,
                'multiply 42 and 10': 420
                }
        calc_strings = {to_calc: Input(
                                       value=to_calc,
                                       definition=definitions['calc_string'],
                                       parents=False) \
                        for to_calc in calc_strings_check.keys()}
        get_single_spec = Input(
            value=['result'],
            definition=definitions['get_single_spec'],
            parents=False)

        dff = DataFlowFacilitator()

        # Orchestrate the running of these operations
        async with dff(
            input_network = MemoryInputNetwork(BaseConfig()),
            operation_network = MemoryOperationNetwork(
                MemoryOperationNetworkConfig(
                    operations=list(operations.values())
                )
            ),
            lock_network = MemoryLockNetwork(BaseConfig()),
            rchecker = MemoryRedundancyChecker(
                BaseRedundancyCheckerConfig(
                    key_value_store=MemoryKeyValueStore(BaseConfig())
                )
            ),
            opimpn = MemoryOperationImplementationNetwork(
                MemoryOperationImplementationNetworkConfig(
                    operations={imp.op.name: imp \
                                for imp in \
                                [Imp(BaseConfig()) for Imp in OPIMPS]}
                )
            ),
            orchestrator = MemoryOrchestrator(BaseConfig())) as dffctx:
            # Add our inputs to the input network with the context being the URL
            for to_calc in calc_strings_check.keys():
                await dffctx.ictx.add(
                    MemoryInputSet(
                        MemoryInputSetConfig(
                            ctx=StringInputSetContext(to_calc),
                            inputs=[calc_strings[to_calc]] + \
                                   [get_single_spec]
                        )
                    )
                )
            async for ctx, results in dffctx.evaluate():
                ctx_str = (await ctx.handle()).as_string()
                print()
                print(ctx_str,
                      json.dumps(results, sort_keys=True,
                                 indent=4, separators=(',', ':')))
                print()
                self.assertEqual(calc_strings_check[ctx_str],
                                 results['get_single']['result'])
