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
from typing import AsyncIterator, Dict, List, Tuple, Any, NamedTuple, Union, \
        get_type_hints, NewType, Optional, Set, Iterator

from dffml.df import *
from dffml.operation.output import GroupBy
from dffml_feature_git.feature.operations import *

from dffml.util.asynctestcase import AsyncTestCase

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

        # Instantiate inputs
        repos = glob.glob(os.path.join(os.path.expanduser('~'), 'Documents',
                          'python', 'testrepos','*'))
        if not repos:
            repos = glob.glob(os.path.join(os.path.expanduser('~'), 'Documents',
                              'python', 'dffml'))
        if not repos:
            repos = ['https://github.com/intel/dffml',
                     'https://github.com/pdxjohnny/dffml']
        repos = repos[:1]
        urls = [Input(value=URL,
                      definition=definitions['URL'],
                      parents=False) for URL in repos]
        no_git_branch_given = Input(value=True,
                                    definition=definitions['no_git_branch_given'],
                                    parents=False)
        date_spec = Input(value=datetime.now()\
                                .strftime(TIME_FORMAT_MINTUE_RESOLUTION),
                          definition=definitions['quarter_start_date'],
                          parents=False)
        quarters = [Input(value=i,
                          definition=definitions['quarter'],
                          parents=False) for i in range(0, 10)]

        group_by_spec = Input(value={
                "cloc": {
                    "group": "quarter",
                    "by": "language_to_comment_ratio",
                    "fill": 0
                },
                "authors": {
                    "group": "quarter",
                    "by": "author_count",
                    "fill": 0
                },
                "work": {
                    "group": "quarter",
                    "by": "work_spread",
                    "fill": 0
                },
                "release": {
                    "group": "quarter",
                    "by": "release_within_period",
                    "fill": False
                },
                "commits": {
                    "group": "quarter",
                    "by": "commit_count",
                    "fill": 0
                }
            },
            definition=definitions['group_by_spec'],
            parents=False)

        opimps = {imp.op.name: imp \
                  for imp in \
                  [Imp(BaseConfig()) for Imp in OPIMPS]}

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
                        operations=opimps
                    )
                ),
                orchestrator = MemoryOrchestrator(BaseConfig())
            ) as dffctx:
            # Add our inputs to the input network with the context being the URL
            for url in urls:
                await dffctx.ictx.add(
                    MemoryInputSet(
                        MemoryInputSetConfig(
                            ctx=StringInputSetContext(url.value),
                            inputs=[url, no_git_branch_given, date_spec] + \
                                   quarters + \
                                   [group_by_spec]
                        )
                    )
                )
            async for ctx, results in dffctx.evaluate():
                print()
                print((await ctx.handle()).as_string(),
                      json.dumps(results, sort_keys=True,
                                 indent=4, separators=(',', ':')))
                print()
                self.assertTrue(results)
