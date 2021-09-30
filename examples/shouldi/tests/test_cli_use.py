import shutil
import pathlib

from dffml import (
    prepend_to_path,
    AsyncTestCase,
    cached_download_unpack_archive,
)

from shouldi.cli import ShouldI
from shouldi.rust.cargo_audit import run_cargo_build

from .binaries import (
    CACHED_NODE,
    CACHED_TARGET_JAVASCRIPT_ALGORITHMS,
    CACHED_RUST,
    CACHED_CARGO_AUDIT,
    CACHED_TARGET_RUST_CLIPPY,
)


class TestCLIUse(AsyncTestCase):
    async def test_use_python(self):
        dffml_source_root = list(pathlib.Path(__file__).parents)[3]
        results = await ShouldI._main("use", str(dffml_source_root))
        # The use of input() triggers B322, which is a false positive since we
        # don't support Python 2
        self.assertLess(
            list(results.values())[0]["static_analysis"][0].high, 2
        )
        if list(results.values())[0]["static_analysis"][0].high > 0:
            self.assertEqual(
                list(results.values())[0]["static_analysis"][0].report[
                    "run_bandit.outputs.result"
                ]["CONFIDENCE.HIGH_AND_SEVERITY.HIGH.issues"][0]["test_id"],
                "B322",
            )

    async def test_use_javascript(self):
        node = await cached_download_unpack_archive(*CACHED_NODE)
        javascript_algo = await cached_download_unpack_archive(
            *CACHED_TARGET_JAVASCRIPT_ALGORITHMS
        )
        with prepend_to_path(node / "node-v14.2.0-linux-x64" / "bin",):
            results = await ShouldI._main(
                "use",
                str(
                    javascript_algo
                    / "javascript-algorithms-ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                ),
            )
        self.assertGreater(
            list(results.values())[0]["static_analysis"][0].high, 2940
        )

    async def test_use_rust(self):
        rust = await cached_download_unpack_archive(*CACHED_RUST)
        cargo_audit = await cached_download_unpack_archive(*CACHED_CARGO_AUDIT)
        rust_clippy = await cached_download_unpack_archive(
            *CACHED_TARGET_RUST_CLIPPY
        )

        if not (
            cargo_audit
            / "rustsec-cargo-audit-v0.15.0"
            / "target"
            / "release"
            / "cargo-audit"
        ).is_file():
            await run_cargo_build(
                cargo_audit / "rustsec-cargo-audit-v0.15.0" / "cargo-audit"
            )

        # Fix for https://github.com/RustSec/rustsec/issues/331
        advisory_db_path = pathlib.Path("~", ".cargo", "advisory-db")
        if advisory_db_path.is_dir():
            shutil.rmtree(str(advisory_db_path))

        with prepend_to_path(
            rust / "rust-1.52.0-x86_64-unknown-linux-gnu" / "cargo" / "bin",
            cargo_audit / "rustsec-cargo-audit-v0.15.0" / "target" / "release",
        ):
            results = await ShouldI._main(
                "use",
                str(
                    rust_clippy
                    / "rust-clippy-52c25e9136f533c350fa1916b5bf5103f69c0f4d"
                ),
            )

            from pprint import pprint

            pprint(results)

            contexts = 0
            reports = 0
            for context in results.values():
                contexts += 1
                for report in context["static_analysis"]:
                    reports += 1
                    self.assertGreater(report.report["qualitative"]["low"], -1)
            self.assertEqual(contexts, 1, "One project context expected")
            self.assertEqual(reports, 1, "One reports expected")
