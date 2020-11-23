from dffml import run_consoletest, AsyncTestCase

from dffml_model_autosklearn import AutoSklearnRegressorModel


class TestAutoSklearnRegressorModel(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(AutoSklearnRegressorModel)
