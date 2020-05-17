import pathlib

from dffml import prepend_to_path, AsyncTestCase

from shouldi.java.dependency_check import run_dependency_check

from .binaries import (
    cached_openjdk,
    cached_dependency_check,
    cached_target_rxjava,
)


class TestRunDependencyCheckOp(AsyncTestCase):
    @cached_openjdk
    @cached_dependency_check
    @cached_target_rxjava
    async def test_run(self, java, dependency_check, rxjava):
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
            results = await run_dependency_check(str(rxjava / "RxJava-2.2.16"))
            self.assertEqual(results["report"]["total_CVE"], 3)
