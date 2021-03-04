from dffml import AsyncTestCase, run_consoletest

from dffml_model_darts.myslr import MySLRModel


class TestIntegrationMySLRModel(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(MySLRModel)
