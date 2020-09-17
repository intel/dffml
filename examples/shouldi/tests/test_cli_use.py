import io
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
                await ShouldI.cli(
                    "use",
                    str(
                        crates
                        / "crates.io-8c1a7e29073e175f0e69e0e537374269da244cee"
                    ),
                )
            output = stdout.getvalue()
            # cargo audit
            self.assertIn("low=3,", output)
            # npm audit
            self.assertIn("high=8,", output)
