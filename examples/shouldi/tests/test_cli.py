import io
from unittest.mock import patch

from dffml.util.asynctestcase import AsyncTestCase

from shouldi.cli import ShouldI


class TestCLI(AsyncTestCase):
    async def test_install(self):
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            await ShouldI.install.cli("insecure-package", "bandit")
            output = stdout.getvalue()
            self.assertIn("bandit is okay to install", output)
            self.assertIn("Do not install insecure-package!", output)
