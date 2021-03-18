import shutil
import pathlib

from dffml import prepend_to_path, AsyncTestCase

from shouldi.rust.cargo_audit import run_cargo_audit, run_cargo_build

from .binaries import (
    cached_rust,
    cached_cargo_audit,
    cached_target_rust_clippy,
)


class TestRunCargoAuditOp(AsyncTestCase):
    @cached_rust
    @cached_cargo_audit
    @cached_target_rust_clippy
    async def test_run(self, rust, cargo_audit, rust_clippy):
        if not (
            cargo_audit
            / "cargo-audit-0.14.0"
            / "target"
            / "release"
            / "cargo-audit"
        ).is_file():
            await run_cargo_build(cargo_audit / "cargo-audit-0.14.0")

        # Fix for https://github.com/RustSec/cargo-audit/issues/331
        advisory_db_path = pathlib.Path("~", ".cargo", "advisory-db")
        if advisory_db_path.is_dir():
            shutil.rmtree(str(advisory_db_path))

        with prepend_to_path(
            rust / "rust-1.50.0-x86_64-unknown-linux-gnu" / "cargo" / "bin",
            cargo_audit / "cargo-audit-0.14.0" / "target" / "release",
        ):
            results = await run_cargo_audit(
                str(
                    rust_clippy
                    / "rust-clippy-52c25e9136f533c350fa1916b5bf5103f69c0f4d"
                )
            )
            self.assertGreater(
                len(results["report"]["vulnerabilities"]["list"]), -1
            )
