import shutil
import pathlib

from dffml import (
    prepend_to_path,
    AsyncTestCase,
    cached_download_unpack_archive,
)

from shouldi.rust.cargo_audit import run_cargo_audit, run_cargo_build

from .binaries import (
    CACHED_RUST,
    CACHED_CARGO_AUDIT,
    CACHED_TARGET_RUST_CLIPPY,
)


class TestRunCargoAuditOp(AsyncTestCase):
    async def test_run(self):
        rust = await cached_download_unpack_archive(*CACHED_RUST)
        cargo_audit = await cached_download_unpack_archive(*CACHED_CARGO_AUDIT)
        rust_clippy = await cached_download_unpack_archive(
            *CACHED_TARGET_RUST_CLIPPY
        )
        if not (
            cargo_audit / "rustsec-0.14.1" / "target" / "release" / "rustsec"
        ).is_file():
            await run_cargo_build(cargo_audit / "rustsec-0.14.1")

        # Fix for https://github.com/RustSec/rustsec/issues/331
        advisory_db_path = pathlib.Path("~", ".cargo", "advisory-db")
        if advisory_db_path.is_dir():
            shutil.rmtree(str(advisory_db_path))

        with prepend_to_path(
            rust / "rust-1.52.0-x86_64-unknown-linux-gnu" / "cargo" / "bin",
            cargo_audit / "rustsec-0.14.1" / "target" / "release",
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
