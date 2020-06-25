import os
import ast
import sys
import json
import shlex
import shutil
import asyncio
import pathlib
import tempfile
import contextlib
import subprocess
import unittest.mock

from dffml import chdir, IntegrationCLITestCase

from dffml_service_http.cli import HTTPService
from dffml_service_http.util.testing import ServerRunner


def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), "quickstart", filename)


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(["sh", sh_filepath("train_data.sh")])
            subprocess.check_output(["sh", sh_filepath("test_data.sh")])
            subprocess.check_output(["sh", sh_filepath("predict_data.sh")])
            yield tempdir


class TestQuickstart(IntegrationCLITestCase):
    def python_test(self, filename):
        # Path to target file
        filepath = os.path.join(os.path.dirname(__file__), filename)
        # Capture output
        stdout = subprocess.check_output([sys.executable, filepath])
        lines = stdout.decode().split("\n")
        # Check the Accuracy
        self.assertIn("Accuracy: 1.0", lines[0])
        # Check the salary
        self.assertEqual(round(ast.literal_eval(lines[1])["Salary"]), 70)
        self.assertEqual(round(ast.literal_eval(lines[2])["Salary"]), 80)

    def test_python(self):
        self.python_test("quickstart.py")

    def test_python_async(self):
        self.python_test("quickstart_async.py")

    def test_python_filenames(self):
        with directory_with_csv_files() as tempdir:
            self.python_test("quickstart_filenames.py")

    def test_shell(self):
        with directory_with_csv_files() as tempdir:
            # Run training
            subprocess.check_output(["sh", sh_filepath("train.sh")])
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["sh", sh_filepath("accuracy.sh")]
            )
            self.assertEqual(stdout.decode().strip(), "1.0")
            # Make the prediction
            stdout = subprocess.check_output(["sh", sh_filepath("predict.sh")])
            records = json.loads(stdout.decode())
            # Check the salary
            self.assertEqual(
                round(records[0]["prediction"]["Salary"]["value"]), 70
            )
            self.assertEqual(
                round(records[1]["prediction"]["Salary"]["value"]), 80
            )

    async def test_http(self):
        # Read in command to start HTTP server
        server_cmd = pathlib.Path(sh_filepath("model_start_http.sh"))
        server_cmd = server_cmd.read_text()
        server_cmd = server_cmd.replace("\n", "")
        server_cmd = server_cmd.replace("\\", "")
        # Remove `dffml service http server`
        server_cmd = server_cmd.replace("dffml service http server", "")
        # Replace port
        server_cmd = server_cmd.replace("8080", "0")
        server_cmd = shlex.split(server_cmd)
        # Read in the curl command
        curl_cmd = pathlib.Path(sh_filepath("model_curl_http.sh"))
        curl_cmd = curl_cmd.read_text()
        # Modify the curl command to use the correct version of python
        curl_cmd = curl_cmd.replace("python", sys.executable)
        # Create a temporary directory for new curl command
        with directory_with_csv_files() as tempdir:
            # Run training
            subprocess.check_output(["sh", sh_filepath("train.sh")])
            async with ServerRunner.patch(HTTPService.server) as tserver:
                # Start the HTTP server
                cli = await tserver.start(HTTPService.server.cli(*server_cmd))
                # Modify the curl command to use the correct port
                curl_cmd = curl_cmd.replace("8080", str(cli.port))
                # Write out the modified curl command
                pathlib.Path("curl.sh").write_text(curl_cmd)
                # Make the prediction
                proc = await asyncio.create_subprocess_exec(
                    "sh",
                    "curl.sh",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if proc.returncode != 0:
                    raise Exception(stderr.decode())
                response = json.loads(stdout)
                # Check the result
                records = response["records"]
                self.assertEqual(len(records), 1)
                for record in records.values():
                    # Correct value should be 90
                    should_be = 90
                    prediction = record["prediction"]["Salary"]["value"]
                    # Check prediction within 20% of correct value
                    percent_error = abs(should_be - prediction) / should_be
                    self.assertLess(percent_error, 0.2)
