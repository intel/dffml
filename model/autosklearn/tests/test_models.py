import pathlib

from dffml import run_consoletest, AsyncTestCase

from dffml_model_autosklearn import AutoSklearnRegressorModel


class TestAutoSklearnRegressorModel(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(
            AutoSklearnRegressorModel,
            docs_root_dir=pathlib.Path(__file__).parents[3] / "docs",
        )
