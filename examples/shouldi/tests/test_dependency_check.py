import pathlib

from dffml import (
    prepend_to_path,
    cached_download_unpack_archive,
    AsyncTestCase,
)

from shouldi.dependency_check import run_dependency_check


class TestRunDependencyCheckOp(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://download.java.net/openjdk/jdk14/ri/openjdk-14+36_linux-x64_bin.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "java.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "java-download",
        "d87ab7b623e17c85d763fd9bf810fc6de7d7c001facf238266bb316586081732cfd4b08d9fbaa83655cbdf9a4f497ac9",
    )
    @cached_download_unpack_archive(
        "https://dl.bintray.com/jeremy-long/owasp/dependency-check-5.3.2-release.zip",
        pathlib.Path(__file__).parent / "downloads" / "dependency_check.zip",
        pathlib.Path(__file__).parent
        / "downloads"
        / "dependency_check-download",
        "02652657e658193369ccd38c000dfbdcbafdcbe991467a8d4f4ef6845ec7af1eae6e2739df6ec851b2d5684fede77c5b",
    )
    @cached_download_unpack_archive(
        "https://github.com/ReactiveX/RxJava/archive/v2.2.16.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "RxJava.tar.gz",
        pathlib.Path(__file__).parent / "downloads" / "RxJava-download",
        "2a15b4eb165e36a3de35e0d53f90b99bb328e3c18b7ef4f0a6c253d3898e794dec231fc726e154f339151eb8cf5ee5bb",
    )
    async def test_run(self, java, dependency_check, RxJava):
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
            results = await run_dependency_check(str(RxJava / "RxJava-2.2.16"))
            self.assertEqual(results["report"]["total_CVE"], 3)
