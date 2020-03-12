import pathlib

from dffml.util.os import prepend_to_path
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.cargo_audit import run_cargo_audit


class TestRunCargo_AuditOp(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://github.com/rust-lang/rust.tar.gz",
        pathlib.Path(__file__).parent / "cargo_audit.tar.gz",
        pathlib.Path(__file__).parent / "cargo-audit-download",
        "",
    )
    @cached_download_unpack_archive(
        "https://github.com/xd009642/tarpaulin/archive/59f1c4f48765fba27319cf64e8aab7b08f8a0f66.tar.gz",
        pathlib.Path(__file__).parent / "tarpaulin.tar.gz",
        pathlib.Path(__file__).parent / "tarpaulin-download",
        "",
    )
    async def test_run(self, cargo_audit, tarpaulin):
        with prepend_to_path(cargo_audit / "bin",):
            results = await run_cargo_audit(
                str(
                    tarpaulin
                    / "tarpaulin-59f1c4f48765fba27319cf64e8aab7b08f8a0f66"
                )
            )
            self.assertEqual(type(results), int)
