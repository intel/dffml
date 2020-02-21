import os
import sys
import glob
from datetime import datetime

from dffml.df.types import Input, DataFlow
from dffml.operation.output import GroupBy  # skipcq: PYL-W0611
from dffml.df.memory import MemoryOrchestrator
from dffml.df.base import operation_in, opimp_in
from dffml.operation.output import GroupBy  # skipcq: PYL-W0611
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_git.feature.operations import *

OPERATIONS = operation_in(sys.modules[__name__])
OPIMPS = opimp_in(sys.modules[__name__])


class TestRunner(AsyncTestCase):
    async def test_run(self):
        dataflow = DataFlow.auto(*OPIMPS)

        # Instantiate inputs
        repos = glob.glob(
            os.path.join(
                os.path.expanduser("~"),
                "Documents",
                "python",
                "testrepos",
                "*",
            )
        )
        if not repos:
            repos = glob.glob(
                os.path.join(
                    os.path.expanduser("~"), "Documents", "python", "dffml"
                )
            )
        if not repos:
            repos = [
                "https://github.com/intel/dffml",
                "https://github.com/pdxjohnny/dffml",
            ]
        repos = repos[:2]
        urls = [
            Input(
                value=URL, definition=dataflow.definitions["URL"], parents=None
            )
            for URL in repos
        ]
        no_git_branch_given = Input(
            value=True,
            definition=dataflow.definitions["no_git_branch_given"],
            parents=None,
        )
        date_spec = Input(
            value=datetime.now().strftime(TIME_FORMAT_MINTUE_RESOLUTION),
            definition=dataflow.definitions["quarter_start_date"],
            parents=None,
        )
        quarters = [
            Input(
                value=i,
                definition=dataflow.definitions["quarter"],
                parents=None,
            )
            for i in range(0, 10)
        ]

        group_by_spec = Input(
            value={
                "cloc": {
                    "group": "quarter",
                    "by": "language_to_comment_ratio",
                    "fill": 0,
                },
                "authors": {
                    "group": "quarter",
                    "by": "author_count",
                    "fill": 0,
                },
                "work": {"group": "quarter", "by": "work_spread", "fill": 0},
                "release": {
                    "group": "quarter",
                    "by": "release_within_period",
                    "fill": False,
                },
                "commits": {
                    "group": "quarter",
                    "by": "commit_count",
                    "fill": 0,
                },
            },
            definition=dataflow.definitions["group_by_spec"],
            parents=None,
        )

        # Orchestrate the running of these operations
        async with MemoryOrchestrator.basic_config() as orchestrator:
            async with orchestrator(dataflow) as octx:
                # Add our inputs to the input network with the context being the URL
                async for ctx, results in octx.run(
                    {
                        url.value: [
                            url,
                            no_git_branch_given,
                            date_spec,
                            group_by_spec,
                            *quarters,
                        ]
                        for url in urls
                    }
                ):
                    self.assertTrue(results)
