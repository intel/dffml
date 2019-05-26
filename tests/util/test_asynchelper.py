import asyncio
from contextlib import asynccontextmanager

from dffml.util.asynchelper import AsyncContextManagerList, concurrently
from dffml.util.asynctestcase import AsyncTestCase


@asynccontextmanager
async def set_key_on_aenter(obj, key, value):
    obj[key] = value
    yield
    del obj[key]


class TestAsyncContextManagerList(AsyncTestCase):
    async def test_aenter_all(self):
        one = {}
        two = {}
        set_one = set_key_on_aenter(one, 1, True)
        set_two = set_key_on_aenter(two, 2, False)
        async with AsyncContextManagerList(set_one, set_two) as l:
            self.assertIn(1, one)
            self.assertTrue(one[1])
            self.assertIn(2, two)
            self.assertFalse(two[2])
        self.assertNotIn(1, one)
        self.assertNotIn(2, two)


class TestConcurrently(AsyncTestCase):
    async def _test_method(self, i):
        return (i * 2) + 7

    async def _test_bad_method(self, i):
        if (i % 2) == 0:
            raise ValueError
        return (i * 2) + 7

    async def test_no_errors(self):
        work = {
            asyncio.create_task(self._test_method(i)): i for i in range(0, 10)
        }

        results = [
            (i, double_i_7)
            async for i, double_i_7 in concurrently(work, errors="ignore")
        ]

        self.assertEqual(len(results), 10)

        for i, double_i_7 in results:
            self.assertEqual(double_i_7, (i * 2) + 7)

    async def test_ignore_errors(self):
        work = {
            asyncio.create_task(self._test_bad_method(i)): i
            for i in range(0, 10)
        }

        results = [
            (i, double_i_7)
            async for i, double_i_7 in concurrently(work, errors="ignore")
        ]

        self.assertEqual(len(results), 5)

        for i, double_i_7 in results:
            self.assertEqual(double_i_7, (i * 2) + 7)

    async def test_raise_errors(self):
        work = {
            asyncio.create_task(self._test_bad_method(i)): i
            for i in range(0, 10)
        }

        with self.assertRaises(ValueError):
            results = [
                (i, double_i_7)
                async for i, double_i_7 in concurrently(work, errors="strict")
            ]
