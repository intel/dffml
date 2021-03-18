import os
import subprocess
import shutil

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import IntegrationCLITestCase


def sh_filepath(sub_dir, filename):
    return os.path.join(
        os.path.dirname(__file__), "..", "examples", sub_dir, filename
    )


class TestResNet18Model(IntegrationCLITestCase):
    @cached_download_unpack_archive(
        "https://download.pytorch.org/tutorial/hymenoptera_data.zip",
        "hymenoptera_data.zip",
        "tempdir",
        "491db45cfcab02d99843fbdcf0574ecf99aa4f056d52c660a39248b5524f9e6e8f896d9faabd27ffcfc2eaca0cec6f39",
    )
    async def test_shell(self, tempdir):
        self.required_plugins("dffml-model-pytorch", "dffml-config-image")

        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-directory") + 1] = directory
            if "-model-epochs" in cmnd:
                cmnd[cmnd.index("-model-epochs") + 1] = "1"
            return cmnd

        with chdir(tempdir):
            os.unlink(
                os.path.join(
                    "hymenoptera_data", "train", "ants", "imageNotFound.gif"
                )
            )
            subprocess.check_output(
                ["bash", sh_filepath("resnet18", "unknown_data.sh")]
            )
            shutil.copy(
                sh_filepath("resnet18", "layers.yaml"),
                os.path.join(os.getcwd(), "layers.yaml"),
            )

            with open(sh_filepath("resnet18", "train.sh"), "r") as f:
                train_command = clean_args(f, str(tempdir))
            await CLI.cli(*train_command[1:])

            with open(sh_filepath("resnet18", "accuracy.sh"), "r") as f:
                accuracy_command = clean_args(f, str(tempdir))
            await CLI.cli(*accuracy_command[1:])

            with open(sh_filepath("resnet18", "predict.sh"), "r") as f:
                predict_command = clean_args(f, str(tempdir))
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
