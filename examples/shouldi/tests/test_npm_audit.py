import pathlib

from dffml import prepend_to_path, AsyncTestCase

from shouldi.javascript.npm_audit import run_npm_audit

from .binaries import cached_node, cached_target_javascript_algorithms


class TestRunNPMAuditOp(AsyncTestCase):
    @cached_node
    @cached_target_javascript_algorithms
    async def test_run(self, node, javascript_algo):
        with prepend_to_path(node / "node-v14.2.0-linux-x64" / "bin"):
            results = await run_npm_audit(
                str(
                    javascript_algo
                    / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                )
            )
            self.assertEqual(results["report"]["high"], 2941)
