import os
import shutil

from dffml.cli.cli import CLI
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import IntegrationCLITestCase
from dffml.high_level import train, accuracy, predict
from dffml import Features, Feature, DirectorySource
from dffml_model_pytorch import PyTorchNeuralNetwork
from ..examples.pytorchnet.python_example import RockPaperScissorsModel, Loss


def sh_filepath(filename):
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "examples",
        "rockpaperscissors",
        filename,
    )


class TestPyTorchNeuralNetwork(IntegrationCLITestCase):
    REQUIRED_PLUGINS = ["dffml-model-pytorch", "dffml-config-image"]

    @classmethod
    def setUpClass(cls):
        cls.model = PyTorchNeuralNetwork(
            classifications=["rock", "paper", "scissors"],
            features=Features(Feature("image", int, 300 * 300)),
            predict=Feature("label", int, 1),
            directory="rps_model",
            network=RockPaperScissorsModel,
            epochs=1,
            batch_size=32,
            imageSize=150,
            validation_split=0.2,
            loss=Loss,
            optimizer="Adam",
            enableGPU=True,
        )

    @cached_download_unpack_archive(
        "https://storage.googleapis.com/laurencemoroney-blog.appspot.com/rps.zip",
        "rps.zip",
        "traindir",
        "c6a9119b0c6a0907b782bd99e04ce09a0924c0895df6a26bc6fb06baca4526f55e51f7156cceb4791cc65632d66085e8",
    )
    async def test_00_train(self, traindir):
        await train(
            self.model,
            DirectorySource(
                foldername=str(traindir) + "/rps",
                feature="image",
                labels=["rock", "paper", "scissors"],
            ),
        )

    @cached_download_unpack_archive(
        "https://storage.googleapis.com/laurencemoroney-blog.appspot.com/rps-test-set.zip",
        "rps-test-set.zip",
        "testdir",
        "fc45a0ebe58b9aafc3cd5a60020fa042d3a19c26b0f820aee630b9602c8f53dd52fd40f35d44432dd031dea8f30a5f66",
    )
    async def test_01_accuracy(self, testdir):
        acc = await accuracy(
            self.model,
            DirectorySource(
                foldername=str(testdir) + "/rps-test-set",
                feature="image",
                labels=["rock", "paper", "scissors"],
            ),
        )
        self.assertGreater(acc, 0)

    @cached_download_unpack_archive(
        "https://storage.googleapis.com/laurencemoroney-blog.appspot.com/rps-validation.zip",
        "rps-validation.zip",
        "predictdir",
        "375457bb95771ffeace2beedab877292d232f31e76502618d25e0d92a3e029d386429f52c771b05ae1c7229d2f5ecc29",
    )
    async def test_00_predict(self, predictdir):
        target = self.model.config.predict.name
        predict_value = 0
        async for key, features, prediction in predict(
            self.model,
            DirectorySource(foldername=str(predictdir), feature="image",),
        ):
            predict_value = prediction[target]["value"]
            break
        self.assertIn(predict_value, self.model.config.classifications)

    @cached_download_unpack_archive(
        "https://storage.googleapis.com/laurencemoroney-blog.appspot.com/rps.zip",
        "rps.zip",
        "traindir",
        "c6a9119b0c6a0907b782bd99e04ce09a0924c0895df6a26bc6fb06baca4526f55e51f7156cceb4791cc65632d66085e8",
    )
    @cached_download_unpack_archive(
        "https://storage.googleapis.com/laurencemoroney-blog.appspot.com/rps-test-set.zip",
        "rps-test-set.zip",
        "testdir",
        "fc45a0ebe58b9aafc3cd5a60020fa042d3a19c26b0f820aee630b9602c8f53dd52fd40f35d44432dd031dea8f30a5f66",
    )
    @cached_download_unpack_archive(
        "https://storage.googleapis.com/laurencemoroney-blog.appspot.com/rps-validation.zip",
        "rps-validation.zip",
        "predictdir",
        "375457bb95771ffeace2beedab877292d232f31e76502618d25e0d92a3e029d386429f52c771b05ae1c7229d2f5ecc29",
    )
    async def test_shell(self, traindir, testdir, predictdir):
        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-source-foldername") + 1] = directory
            if "-model-epochs" in cmnd:
                cmnd[cmnd.index("-model-epochs") + 1] = "1"
            return cmnd

        shutil.copy(
            sh_filepath("model.yaml"), os.path.join(os.getcwd(), "model.yaml"),
        )

        with open(sh_filepath("train.sh"), "r") as f:
            train_command = clean_args(f, str(traindir) + "/rps")
        await CLI.cli(*train_command[1:])

        with open(sh_filepath("accuracy.sh"), "r") as f:
            accuracy_command = clean_args(f, str(testdir) + "/rps-test-set")
        await CLI.cli(*accuracy_command[1:])

        with open(sh_filepath("predict.sh"), "r") as f:
            predict_command = clean_args(f, str(predictdir))
        results = await CLI.cli(*predict_command[1:-1])

        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0]
        self.assertTrue(results.prediction("label"))
        results = results.prediction("label")
        self.assertIn("value", results)
        self.assertIn("confidence", results)
        self.assertIn(isinstance(results["value"], str), [True])
        self.assertTrue(results["confidence"])
