import pathlib

from dffml.util.os import prepend_to_path
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.dependency_check import run_dependency_check


class TestRunDependencyCheckOp(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://download.java.net/openjdk/jdk14/ri/openjdk-14+36_linux-x64_bin.tar.gz",
        pathlib.Path(__file__).parent / "downloads/java.tar.gz",
        pathlib.Path(__file__).parent / "downloads/java-download",
        "d87ab7b623e17c85d763fd9bf810fc6de7d7c001facf238266bb316586081732cfd4b08d9fbaa83655cbdf9a4f497ac9",
    )
    @cached_download_unpack_archive(
        "https://github.com/jeremylong/DependencyCheck/archive/v5.3.2.tar.gz",
        pathlib.Path(__file__).parent / "downloads/dependency_check.tar.gz",
        pathlib.Path(__file__).parent / "downloads/dependency_check-download",
        "9f08a8e106e065cdd5d54f5b968c684250d9a188edb26a36ce49815a2494969a365508bbea704da1676aefa3b6409a20",
    )
    @cached_download_unpack_archive(
        "https://github.com/ReactiveX/RxJava/archive/v2.2.16.tar.gz",
        pathlib.Path(__file__).parent / "downloads/RxJava.tar.gz",
        pathlib.Path(__file__).parent / "downloads/RxJava-download",
        "2a15b4eb165e36a3de35e0d53f90b99bb328e3c18b7ef4f0a6c253d3898e794dec231fc726e154f339151eb8cf5ee5bb",
    )
    async def test_run(self, java, dependency_check, RxJava):
        with prepend_to_path(
            java / "jdk-14" / "bin",
            dependency_check / "DependencyCheck-5.3.2",
        ):
            results = await run_dependency_check(str(RxJava / "RxJava-2.2.16"))
            self.assertEqual(type(results["report"]["total_CVE"]), int)
