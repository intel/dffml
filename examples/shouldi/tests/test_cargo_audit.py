import pathlib

from dffml import prepend_to_path, AsyncTestCase

from shouldi.rust.cargo_audit import run_cargo_audit, run_cargo_build

from .binaries import cached_rust, cached_cargo_audit, cached_target_crates


class TestRunCargoAuditOp(AsyncTestCase):
    @cached_rust
    @cached_cargo_audit
    @cached_target_crates
    async def test_run(self, rust, cargo_audit, crates):
        if not (
            cargo_audit
            / "cargo-audit-0.11.2"
            / "target"
            / "release"
            / "cargo-audit"
        ).is_file():
            await run_cargo_build(cargo_audit / "cargo-audit-0.11.2")

        with prepend_to_path(
            rust / "rust-1.42.0-x86_64-unknown-linux-gnu" / "cargo" / "bin",
            cargo_audit / "cargo-audit-0.11.2" / "target" / "release",
        ):
            results = await run_cargo_audit(
                str(
                    crates
                    / "crates.io-8c1a7e29073e175f0e69e0e537374269da244cee"
                )
            )
            self.assertGreater(
                len(results["report"]["vulnerabilities"]["list"]), 4
            )
