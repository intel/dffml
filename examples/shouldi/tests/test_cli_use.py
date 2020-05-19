import io
import pathlib
from unittest.mock import patch

from dffml import prepend_to_path, AsyncTestCase

from shouldi.cli import ShouldI

from .binaries import cached_node, cached_target_javascript_algorithms


class TestCLIUse(AsyncTestCase):
    async def test_use_python(self):
        # Issue is B322, use of input in Python 2 is unsafe (eval). DFFML is
        # Python 3.7+ only, so doesn't effect us (it's the 1 high that will be
        # found).
        dffml_source_root = list(pathlib.Path(__file__).parents)[3]
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            await ShouldI.cli("use", str(dffml_source_root))
            output = stdout.getvalue()
        self.assertIn("high=1", output)

    @cached_node
    @cached_target_javascript_algorithms
    async def test_use_javascript(self, node, javascript_algo):
        with prepend_to_path(node / "node-v14.2.0-linux-x64" / "bin",):
            with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                await ShouldI.cli(
                    "use",
                    str(
                        javascript_algo
                        / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                    ),
                )
                output = stdout.getvalue()
        self.assertIn("high=2941", output)
