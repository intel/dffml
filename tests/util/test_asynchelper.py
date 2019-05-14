import asyncio

from dffml.util.asynchelper import concurrently
from dffml.util.asynctestcase import AsyncTestCase

class TestConcurrently(AsyncTestCase):

    async def _test_method(self, i):
        return (i * 2) + 7

    async def _test_bad_method(self, i):
        if (i % 2) == 0:
            raise ValueError
        return (i * 2) + 7

    async def test_no_errors(self):
        work = {asyncio.create_task(self._test_method(i)): i \
                for i in range(0, 10)}

        results = [(i, double_i_7,) \
                   async for i, double_i_7 in \
                   concurrently(work, errors='ignore')]

        self.assertEqual(len(results), 10)

        for i, double_i_7 in results:
            self.assertEqual(double_i_7, (i * 2) + 7)

    async def test_ignore_errors(self):
        work = {asyncio.create_task(self._test_bad_method(i)): i \
                for i in range(0, 10)}

        results = [(i, double_i_7,) \
                   async for i, double_i_7 in \
                   concurrently(work, errors='ignore')]

        self.assertEqual(len(results), 5)

        for i, double_i_7 in results:
            self.assertEqual(double_i_7, (i * 2) + 7)

    async def test_raise_errors(self):
        work = {asyncio.create_task(self._test_bad_method(i)): i \
                for i in range(0, 10)}

        with self.assertRaises(ValueError):
            results = [(i, double_i_7,) \
                       async for i, double_i_7 in \
                       concurrently(work, errors='strict')]
