import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase, IntegrationCLITestCase

from dffml_model_scratch.ridge import RidgeRegression, RidgeConfig

Features_data = [
    {"Years": 0, "Salary": 21,  "Expertise": 1, "Trust": 0.1}, 
    {"Years": 1, "Salary": 31, "Expertise": 1, "Trust": 0.1}, 
    {"Years": 2, "Salary": 40, "Expertise": 1, "Trust": 0.1}, 
    {"Years": 3, "Salary": 79, "Expertise": 3, "Trust": 0.2}, 
    {"Years": 4, "Salary": 89, "Expertise": 3, "Trust": 0.2}, 
    {"Years": 5, "Salary": 102, "Expertise": 3, "Trust": 0.2}, 
    {"Years": 6, "Salary": 145, "Expertise": 5, "Trust": 0.3}, 
    {"Years": 7, "Salary": 150, "Expertise": 5, "Trust": 0.3}, 
    {"Years": 8, "Salary": 160, "Expertise": 5, "Trust": 0.3}, 
    {"Years": 9, "Salary": 209, "Expertise": 7, "Trust": 0.4}, 
    {"Years": 10, "Salary": 210, "Expertise": 7, "Trust": 0.4}, 
    {"Years": 11, "Salary": 215, "Expertise": 7, "Trust": 0.4}, 
]

class TestRidge(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.feature1 = DefFeature("Years", float, 1)
        cls.feature2 = DefFeature("Expertise", float, 1)
        cls.feature3 = DefFeature("Trust", float, 1)
        cls.features = ['Expertise', 'Trust', 'Years']
        cls.repos = [
            Repo(str(i), data={"features": Features_data[i]})
            for i in range(0, len(Features_data))
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )
        cls.model = RidgeRegression(
            RidgeConfig(
                directory=cls.model_dir.name,
                predict=DefFeature("Salary", float, 1),
                features=cls.features,
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_context(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                # Test train
                await mctx.train(sctx)
                # Test accuracy
                res = await mctx.accuracy(sctx)
                self.assertTrue(0.0 <= res < 1.0)
                # Test predict
                target_name = model.config.predict.NAME
                async for repo in mctx.predict(sctx.repos()):
                    correct = Features_data[int(repo.key)]["Salary"]
                    # Comparison of correct to prediction to make sure prediction is within a reasonable range
                    prediction = repo.prediction(target_name).value
                    self.assertGreater(prediction, correct - (correct * 0.20))
                    self.assertLess(prediction, correct + (correct * 0.20))

    async def test_00_train(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                res = await mctx.accuracy(sctx)
                self.assertTrue(0.0 <= res < 1.0)

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                target_name = model.config.predict.NAME
                async for repo in mctx.predict(sctx.repos()):
                    target_name = model.config.predict.NAME
                    correct = Features_data[int(repo.key)]["Salary"]
                    prediction = repo.prediction(target_name).value
                    self.assertGreater(prediction, correct - (correct * 0.20))
                    self.assertLess(prediction, correct + (correct * 0.20))




class TestScratchRidgeRegression(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-scratch")
        # Create the training data
        train_filename = self.mktempfile() + ".csv"
        pathlib.Path(train_filename).write_text(
            inspect.cleandoc(
                """
                crim,zn,indus,chas,nox,rm,age,dis,rad,tax,ptratio,b,lstat,medv
                0.00632,18,2.31,0,0.538,6.575,65.2,4.09,1,296,15.3,396.9,4.98,24
                0.02731,0,7.07,0,0.469,6.421,78.9,4.9671,2,242,17.8,396.9,9.14,21.6
                0.02729,0,7.07,0,0.469,7.185,61.1,4.9671,2,242,17.8,392.83,4.03,34.7
                0.03237,0,2.18,0,0.458,6.998,45.8,6.0622,3,222,18.7,394.63,2.94,33.4
                0.06905,0,2.18,0,0.458,7.147,54.2,6.0622,3,222,18.7,396.9,5.33,36.2
                """
            )
            + "\n"
        )
        # Create the test data
        test_filename = self.mktempfile() + ".csv"
        pathlib.Path(test_filename).write_text(
            inspect.cleandoc(
                """
                crim,zn,indus,chas,nox,rm,age,dis,rad,tax,ptratio,b,lstat,medv
                0.02985,0,2.18,0,0.458,6.43,58.7,6.0622,3,222,18.7,394.12,5.21,28.7
                0.08829,12.5,7.87,0,0.524,6.012,66.6,5.5605,5,311,15.2,395.6,12.43,22.9
                """
            )
            + "\n"
        )
        # Create the prediction data
        predict_filename = self.mktempfile() + ".csv"
        pathlib.Path(predict_filename).write_text(
            inspect.cleandoc(
                """
                crim,zn,indus,chas,nox,rm,age,dis,rad,tax,ptratio,b,lstat,medv
                0.14455,12.5,7.87,0,0.524,6.172,96.1,5.9505,5,311,15.2,396.9,19.15,27.1
                """
            )
            + "\n"
        )
        # Features
        features = "-model-features crim:float:1 zn:float:1 indus:float:1 chas:int:1 nox:float:1 rm:float:1 age:int:1 dis:float:1 rad:int:1 tax:float:1 ptratio:float:1 b:float:1 lstat:float:1".split()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "ridge",
            *features,
            "-model-predict",
            "medv:float:1",
            "-sources",
            "training_data=csv",
            "-source-filename",
            train_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "ridge",
            *features,
            "-model-predict",
            "medv:float:1",
            "-sources",
            "test_data=csv",
            "-source-filename",
            test_filename,
        )
        # Ensure JSON output works as expected (#261)
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "ridge",
                *features,
                "-model-predict",
                "medv:float:1",
                "-sources",
                "predict_data=csv",
                "-source-filename",
                predict_filename,
            )
        results = json.loads(self.stdout.getvalue())
        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0]
        self.assertIn("prediction", results)
        results = results["prediction"]
        self.assertIn("medv", results)
        results = results["medv"]
        self.assertIn("value", results)
        results = results["value"]
        self.assertTrue(results is not None)
