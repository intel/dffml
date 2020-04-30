import io
from unittest.mock import patch

from dffml import AsyncTestCase

from shouldi.cli import ShouldI


class TestCLI(AsyncTestCase):
    async def test_install(self):
        import pathlib

        await ShouldI.install.cli(str(list(pathlib.Path(__file__).parents)[3]))
        # await ShouldI.install.cli("https://github.com/intel/dffml")

        return

        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            await ShouldI.install.cli("insecure-package", "shouldi")
            output = stdout.getvalue()
        self.assertIn("shouldi is okay to install", output)
        self.assertIn("Do not install insecure-package!", output)
