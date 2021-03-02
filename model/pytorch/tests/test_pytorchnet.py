import torch.nn as nn
import os
import shutil
import tempfile

from dffml.cli.cli import CLI
from dffml.util.net import cached_download_unpack_archive
from dffml_model_pytorch.utils import create_network
from dffml.util.asynctestcase import IntegrationCLITestCase
from dffml.high_level import train, accuracy, predict
from dffml import Features, Feature, DirectorySource
from dffml_model_pytorch import PyTorchNeuralNetwork
from dffml_model_pytorch.utils import CrossEntropyLossFunction


class ConvNet(nn.Module):
    def __init__(self, in_channels=3, num_features=3):
        super(ConvNet, self).__init__()

        self.layers = []
        # BLOCK 1
        self.layers.extend(
            [
                nn.Conv2d(
                    in_channels=in_channels,
                    out_channels=32,
                    kernel_size=5,
                    padding=2,
                ),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2),
            ]
        )
        # BLOCK 2
        self.layers.extend(
            [
                nn.Conv2d(
                    in_channels=self.layers[0].out_channels,
                    out_channels=32,
                    kernel_size=3,
                    padding=1,
                ),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2),
            ]
        )
        # BLOCK 3
        self.layers.extend(
            [
                nn.Conv2d(
                    in_channels=self.layers[3].out_channels,
                    out_channels=32,
                    kernel_size=3,
                    padding=1,
                ),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2),
            ]
        )
        # BLOCK 4
        self.layers.extend(
            [
                nn.Conv2d(
                    in_channels=self.layers[6].out_channels,
                    out_channels=16,
                    kernel_size=3,
                    padding=1,
                ),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2),
            ]
        )

        self.conv_block = nn.Sequential(*self.layers)
        # output dimension of the conv layer is ((n+2p-k)/s+1)*((n+2p-k)/s+1)*Nc
        # output features after passing through a MaxPool2d is ((n-k)/s + 1)*((n-k)/s + 1)*Nc

        self.linear = nn.Linear(
            in_features=16 * 9 * 9, out_features=num_features
        )

    def forward(self, x):
        # fully connected layer
        x = self.conv_block(x)
        x = self.linear(x.view(-1, 16 * 9 * 9))
        return x


RockPaperScissorsModel = ConvNet()
Loss = CrossEntropyLossFunction()


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
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = PyTorchNeuralNetwork(
            classifications=["rock", "paper", "scissors"],
            features=Features(Feature("image", int, 300 * 300)),
            predict=Feature("label", int, 1),
            directory=cls.model_dir.name,
            network=RockPaperScissorsModel,
            epochs=1,
            batch_size=32,
            imageSize=150,
            validation_split=0.2,
            loss=Loss,
            optimizer="Adam",
            enableGPU=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

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
    async def test_02_predict(self, predictdir):
        target = self.model.config.predict.name
        predict_value = 0
        async for key, features, prediction in predict(
            self.model,
            DirectorySource(foldername=str(predictdir), feature="image",),
        ):
            pred = prediction
            break

        self.assertTrue(pred)
        self.assertTrue(pred[target])
        results = pred[target]
        self.assertIn("value", results)
        self.assertIn("confidence", results)
        self.assertIn(results["value"], self.model.config.classifications)
        self.assertTrue(results["confidence"])

    async def test_03_network_creation_from_dict(self):
        model1 = {
            "linear1": {
                "layer_type": "Linear",
                "in_features": 4096,
                "out_features": 256,
            },
            "relu": {"layer_type": "ReLU"},
            "linear_2": {
                "layer_type": "Linear",
                "in_features": "",
                "out_features": 17,
            },
        }
        model2 = {
            "conv1": {
                "layer_type": "Conv2d",
                "in_channels": 3,
                "out_channels": 32,
                "kernel_size": 3,
            },
            "relu1": {"layer_type": "ReLU"},
            "conv2": {
                "layer_type": "Conv2d",
                "in_channels": None,
                "out_channels": 64,
                "kernel_size": 3,
            },
            "relu2": {"layer_type": "ReLU"},
            "conv3": {
                "layer_type": "Conv2d",
                "in_channels": "",
                "out_channels": 96,
                "kernel_size": 3,
            },
            "relu3": {"layer_type": "ReLU"},
            "conv4": {
                "layer_type": "Conv2d",
                "in_channels": "96",
                "out_channels": 32,
                "kernel_size": 3,
            },
        }

        model1_net = create_network(model1)
        model2_net = create_network(model2)
        self.assertEqual(model2_net[2].in_channels, 32)
        self.assertEqual(model2_net[4].in_channels, 64)
        self.assertEqual(model2_net[6].in_channels, 96)
        self.assertEqual(model1_net[2].in_features, 256)

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
