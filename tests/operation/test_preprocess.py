from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.preprocess import literal_eval


class TestPreprocess(AsyncTestCase):
    async def test_literal_eval(self):
        value = await literal_eval("[1,2]")
        self.assertEqual(value, {"str_after_eval": [1, 2]})
