import pathlib

from dffml.util.os import prepend_to_path
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.cargo_audit import run_cargo_audit, run_cargo_build


class TestRunCargoAuditOp(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://static.rust-lang.org/dist/rust-1.42.0-x86_64-unknown-linux-gnu.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "rust.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "rust-download",
        "ad2ab72dc407b0f5d34621640555e2da751da8803cbad734396faa54111e03093093f6fa66f14a1948bece8f9e33730d",
    )
    @cached_download_unpack_archive(
        "https://github.com/RustSec/cargo-audit/archive/v0.11.2.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "cargo_audit.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "cargo-audit-download",
        "dea36731efaac4d0fd37a295c65520a7e9b23b5faa0a92dce7ab20764f8323fc34856079524c676e4cad1cb065ee6472",
    )
    @cached_download_unpack_archive(
        "https://github.com/rust-lang/crates.io/archive/8c1a7e29073e175f0e69e0e537374269da244cee.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "crates.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "crates-download",
        "1bf0c3459373882f51132942872d0dbf8da01eee8d42c3c2090d234e4db99b39d4858c1fd2492c85917d670cae2519ca",
    )
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
            self.assertEqual(type(results["report"]), int)
