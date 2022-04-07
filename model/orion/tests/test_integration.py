from dffml import AsyncTestCase, run_consoletest

from dffml_model_orion.orion_model import OrionModel


class TestIntegrationOrionModel(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(OrionModel)
