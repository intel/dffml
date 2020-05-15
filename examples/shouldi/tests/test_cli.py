import io
import pathlib
from unittest.mock import patch

from dffml import (
    prepend_to_path,
    cached_download_unpack_archive,
    AsyncTestCase,
)

from shouldi.cli import ShouldI


class TestCLI(AsyncTestCase):
    async def test_install_py(self):
        # Issue is B322, use of input in Python 2 is unsafe (eval). DFFML is
        # Python 3.7+ only, so doesn't effect us (it's the 1 high that will be
        # found).
        dffml_source_root = list(pathlib.Path(__file__).parents)[3]
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            await ShouldI.install.cli(str(dffml_source_root))
            output = stdout.getvalue()
            self.assertIn("high=1", output)

    @cached_download_unpack_archive(
        "https://nodejs.org/dist/v14.2.0/node-v14.2.0-linux-x64.tar.xz",
        pathlib.Path(__file__).parent / "downloads" / "node.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "node-download",
        "fa2a9dfa4d0f99a0cc3ee6691518c026887677a0d565b12ebdcf9d78341db2066427c9970c41cbf72776a370bbb42729",
    )
    @cached_download_unpack_archive(
        "https://github.com/trekhleb/javascript-algorithms/archive/ba2d8dc4a8e27659c1420fe52390cb7981df4a94.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "javascript_algo.tar.gz",
        pathlib.Path(__file__).parent
        / "downloads"
        / "javascript_algo-download",
        "36b3ce51780ee6ea8dcec266c9d09e3a00198868ba1b041569950b82cf45884da0c47ec354dd8514022169849dfe8b7c",
    )
    async def test_install_js(self, node, javascript_algo):
        with prepend_to_path(node / "node-v14.2.0-linux-x64" / "bin",):
            with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                await ShouldI.install.cli(
                    str(
                        javascript_algo
                        / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                    )
                )
                output = stdout.getvalue()
                self.assertIn("high=2941", output)
