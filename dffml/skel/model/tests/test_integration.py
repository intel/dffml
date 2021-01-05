from dffml import AsyncTestCase, run_consoletest

from REPLACE_IMPORT_PACKAGE_NAME.myslr import MySLRModel


class TestIntegrationMySLRModel(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(MySLRModel)
