import pathlib

from dffml.util.os import prepend_to_path
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.npm_audit import run_npm_audit


class TestRunNPM_AuditOp(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://nodejs.org/dist/v12.16.1/node-v12.16.1-linux-x64.tar.gz",
        pathlib.Path(__file__).parent / "npm.tar.gz",
        pathlib.Path(__file__).parent / "npm-audit-download",
        "7df0e7b9f0d7e387c866c3b75596d924a63d11233e7a1a850acdeb333729ebbc9dcf01b1724ddf48a48bedf0cf2fddd8",
    )
    @cached_download_unpack_archive(
        "https://github.com/trekhleb/javascript-algorithms/archive/ba2d8dc4a8e27659c1420fe52390cb7981df4a94.tar.gz",
        pathlib.Path(__file__).parent / "javascript_algo.tar.gz",
        pathlib.Path(__file__).parent / "javascript_algo-download",
        "36b3ce51780ee6ea8dcec266c9d09e3a00198868ba1b041569950b82cf45884da0c47ec354dd8514022169849dfe8b7c",
    )
    async def test_run(self, npm_audit, javascript_algo):
        with prepend_to_path(npm_audit / "bin",):
            results = await run_npm_audit(
                str(
                    javascript_algo
                    / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                )
            )
            self.assertEqual(type(results), dict)
