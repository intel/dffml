import io
from unittest.mock import patch

from shouldi.cli import ShouldI

from dffml.util.asynctestcase import AsyncTestCase


class TestCLI(AsyncTestCase):
    async def test_install(self):
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            await ShouldI.install.cli("insecure-package", "shouldi")
            output = stdout.getvalue()
        self.assertIn("shouldi is okay to install", output)
        self.assertIn("Do not install insecure-package!", output)
