import pathlib

from dffml import (
    prepend_to_path,
    cached_download_unpack_archive,
    AsyncTestCase,
)

from shouldi.javascript.npm_audit import run_npm_audit


class TestRunNPMAuditOp(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://nodejs.org/dist/v14.2.0/node-v14.2.0-linux-x64.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "node.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "node-download",
        "1c7fc8285840a41be27cf23b0e181477f6f001ca76d685d8ebde336e4433092388ff37e3ef165ecd97e869001e4b8b83",
    )
    @cached_download_unpack_archive(
        "https://github.com/trekhleb/javascript-algorithms/archive/ba2d8dc4a8e27659c1420fe52390cb7981df4a94.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "javascript_algo.tar.gz",
        pathlib.Path(__file__).parent
        / "downloads"
        / "javascript_algo-download",
        "36b3ce51780ee6ea8dcec266c9d09e3a00198868ba1b041569950b82cf45884da0c47ec354dd8514022169849dfe8b7c",
    )
    async def test_run(self, node, javascript_algo):
        with prepend_to_path(node / "node-v14.2.0-linux-x64" / "bin"):
            results = await run_npm_audit(
                str(
                    javascript_algo
                    / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                )
            )
            self.assertEqual(results["report"]["high"], 2941)
