import os
import json
import shlex
import pathlib
import tempfile
import contextlib
import subprocess

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.util.asynctestcase import IntegrationCLITestCase

ROOT = pathlib.Path(__file__).resolve().parents[3]


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(ROOT, "examples", "nlp", "train_data.sh",),
                ]
            )

            subprocess.check_output(
                [
                    "bash",
                    os.path.join(ROOT, "examples", "nlp", "test_data.sh",),
                ]
            )
            yield tempdir


class TestNLPOps(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-operations-nlp", "dffml-model-tensorflow")

        # Test .sh files
        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-directory") + 1] = directory
            cmnd[cmnd.index("-source-text-dataflow") + 1] = os.path.join(
                directory, "nlp_ops_dataflow.json",
            )
            if "-pretty" in cmnd:
                del cmnd[cmnd.index("-pretty")]
            return cmnd

        with directory_with_csv_files() as tempdir:
            with open(
                os.path.join(ROOT, "examples", "nlp", "create_dataflow.sh",),
                "r",
            ) as f:
                cmnd = f.readlines()
                cmnd = shlex.split(
                    " ".join(cmnd)
                    .replace("\n", "")
                    .replace("\\", "")
                    .split("|")[0]
                )
                with contextlib.redirect_stdout(self.stdout):
                    await CLI._main(*cmnd[1:])
                    std_output = self.stdout.getvalue()
                    self.stdout.truncate(0)
                    self.stdout.seek(0)
                with open(
                    os.path.join(tempdir, "nlp_ops_dataflow.json"), "w"
                ) as fd:
                    fd.write(std_output)

            with open(
                os.path.join(ROOT, "examples", "nlp", "train.sh"), "r"
            ) as f:
                train_cmnd = clean_args(f, tempdir)
            await CLI.cli(*train_cmnd[1:])

            with open(
                os.path.join(ROOT, "examples", "nlp", "accuracy.sh",), "r",
            ) as f:
                accuracy_cmnd = clean_args(f, tempdir)
            await CLI.cli(*accuracy_cmnd[1:])

            with open(
                os.path.join(ROOT, "examples", "nlp", "predict.sh",), "r",
            ) as f:
                predict_cmnd = clean_args(f, tempdir)
            results = await CLI.cli(*predict_cmnd[1:])
            self.assertTrue(isinstance(results, list))
            self.assertTrue(results)
            results = results[0].data.dict()
            self.assertIn("prediction", results)
            results = results["prediction"]
            self.assertIn("sentiment", results)
            results = results["sentiment"]
            self.assertIn("value", results)
            results = results["value"]
            self.assertIn(results, [0, 1])
