import pathlib

from dffml.util.os import prepend_to_path
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.cargo_audit import run_cargo_audit


class TestRunCargo_AuditOp(AsyncTestCase):
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
        "https://github.com/xd009642/tarpaulin/archive/59f1c4f48765fba27319cf64e8aab7b08f8a0f66.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "tarpaulin.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "tarpaulin-download",
        "03c10779bdf09baa9b6a8caab367de8e780e9b72778b40c017adb85c1b1ec38b96355ba67482067fcd06917632a81f69",
    )
    async def test_run(self, rust, cargo_audit, tarpaulin):
        with prepend_to_path(
            rust / "rust-1.42.0-x86_64-unknown-linux-gnu" / "cargo" / "bin",
            cargo_audit / "cargo-audit-0.11.2",
        ):
            results = await run_cargo_audit(
                str(
                    tarpaulin
                    / "tarpaulin-59f1c4f48765fba27319cf64e8aab7b08f8a0f66"
                )
            )
            self.assertEqual(results["report"], int)
