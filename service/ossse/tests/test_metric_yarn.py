import asyncio
import unittest

from dffml.metric import Data, Metrics
from dffml.util.asynctestcase import AsyncTestCase

from dffml_metric_git.metric.git import GitMetric

from ossse.cli import YarnTestMetric

class TestYarnTest(AsyncTestCase):

    def setUp(self):
        self.url = 'https://github.com/pillarjs/csrf'
        self.yarn_test = YarnTestMetric()
        self.metrics = Metrics(self.yarn_test)

    async def test_applicable(self):
        async with self.metrics:
            applicable = await self.metrics.applicable(Data(self.url))
            self.assertIn(self.yarn_test, applicable)
