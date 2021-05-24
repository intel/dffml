import pathlib

from dffml import (
    prepend_to_path,
    AsyncTestCase,
    cached_download_unpack_archive,
)

from shouldi.javascript.npm_audit import run_npm_audit

from .binaries import CACHED_NODE, CACHED_TARGET_JAVASCRIPT_ALGORITHMS


class TestRunNPMAuditOp(AsyncTestCase):
    async def test_run(self):
        node = await cached_download_unpack_archive(*CACHED_NODE)
        javascript_algo = await cached_download_unpack_archive(
            *CACHED_TARGET_JAVASCRIPT_ALGORITHMS
        )
        with prepend_to_path(node / "node-v14.2.0-linux-x64" / "bin"):
            results = await run_npm_audit(
                str(
                    javascript_algo
                    / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                )
            )
            self.assertGreater(results["report"]["high"], 2941)
