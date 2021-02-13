import io
import json
import pathlib
import subprocess
from unittest.mock import patch

from dffml import prepend_to_path, AsyncTestCase

from shouldi.cli import ShouldI
from shouldi.rust.cargo_audit import run_cargo_build

from .binaries import (
    cached_node,
    cached_target_javascript_algorithms,
    cached_rust,
    cached_cargo_audit,
    cached_target_crates,
)


class TestCLIUse(AsyncTestCase):
    async def test_use_python(self):
        dffml_source_root = list(pathlib.Path(__file__).parents)[3]
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            await ShouldI._main("use", str(dffml_source_root))
            output = stdout.getvalue()
        results = json.loads(output)
        # The use of input() triggers B322, which is a false positive since we
        # don't support Python 2
        self.assertLess(
            list(results.values())[0]["static_analysis"][0]["high"], 2
        )
        if list(results.values())[0]["static_analysis"][0]["high"] > 0:
            self.assertEqual(
                list(results.values())[0]["static_analysis"][0]["report"][
                    "run_bandit.outputs.result"
                ]["CONFIDENCE.HIGH_AND_SEVERITY.HIGH.issues"][0]["test_id"],
                "B322",
            )

    @cached_node
    @cached_target_javascript_algorithms
    async def test_use_javascript(self, node, javascript_algo):
        with prepend_to_path(node / "node-v14.2.0-linux-x64" / "bin",):
            with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                await ShouldI._main(
                    "use",
                    str(
                        javascript_algo
                        / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                    ),
                )
                output = stdout.getvalue()
        results = json.loads(output)
        self.assertGreater(
            list(results.values())[0]["static_analysis"][0]["high"], 2940
        )

    @cached_node
    @cached_rust
    @cached_cargo_audit
    @cached_target_crates
    async def test_use_rust(self, node, rust, cargo_audit, crates):
        if not (rust / "rust-install" / "bin" / "cargo").is_file():
            subprocess.check_call(
                [
                    str(
                        rust
                        / "rust-1.42.0-x86_64-unknown-linux-gnu"
                        / "install.sh"
                    ),
                    f"--prefix={(rust / 'rust-install').resolve()}",
                ]
            )
        with prepend_to_path(
            node / "node-v14.2.0-linux-x64" / "bin",
            rust / "rust-install" / "bin",
            cargo_audit / "cargo-audit-0.11.2" / "target" / "release",
        ):
            if not (
                cargo_audit
                / "cargo-audit-0.11.2"
                / "target"
                / "release"
                / "cargo-audit"
            ).is_file():
                await run_cargo_build(cargo_audit / "cargo-audit-0.11.2")

            with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                await ShouldI._main(
                    "use",
                    str(
                        crates
                        / "crates.io-8c1a7e29073e175f0e69e0e537374269da244cee"
                    ),
                )
            output = stdout.getvalue()
            print(output)
            results = json.loads(output)

            from pprint import pprint

            pprint(results)

            contexts = 0
            reports = 0
            for context in results.values():
                contexts += 1
                for report in context["static_analysis"]:
                    reports += 1
                    if "npm_audit_output" in report["report"]:
                        self.assertGreater(
                            report["report"]["npm_audit_output"]["high"], 7
                        )
                    elif "qualitative" in report["report"]:
                        self.assertGreater(
                            report["report"]["qualitative"]["low"], 9
                        )
            self.assertEqual(contexts, 1, "One project context expected")
            self.assertEqual(reports, 2, "Two reports expected")
