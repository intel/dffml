import pathlib

from dffml import (
    prepend_to_path,
    AsyncTestCase,
    cached_download_unpack_archive,
)

from shouldi.java.dependency_check import run_dependency_check

from .binaries import (
    CACHED_OPENJDK,
    CACHED_DEPENDENCY_CHECK,
    CACHED_TARGET_RXJAVA,
)


class TestRunDependencyCheckOp(AsyncTestCase):
    async def test_run(self):
        java = await cached_download_unpack_archive(*CACHED_OPENJDK)
        dependency_check = await cached_download_unpack_archive(
            *CACHED_DEPENDENCY_CHECK
        )
        rxjava = await cached_download_unpack_archive(*CACHED_TARGET_RXJAVA)
        with prepend_to_path(
            java / "jdk-14" / "bin",
            dependency_check / "dependency-check" / "bin",
        ):
            (
                dependency_check
                / "dependency-check"
                / "bin"
                / "dependency-check.sh"
            ).chmod(0o755)
            results = await run_dependency_check.test(
                pkg=str(rxjava / "RxJava-2.2.16")
            )
            self.assertGreater(results["report"]["total_CVE"], 3)
