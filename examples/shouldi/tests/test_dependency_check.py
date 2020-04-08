import pathlib

from dffml.util.os import prepend_to_path
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.dependency_check import run_dependency_check


class TestRunDependencyCheckOp(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://download.oracle.com/otn-pub/java/jdk/14+36/076bab302c7b4508975440c56f6cc26a/jdk-14_osx-x64_bin.tar.gz",
        pathlib.Path(__file__).parent / "downloads/java.tar.gz",
        pathlib.Path(__file__).parent / "downloads/java-download",
        "fcd50cde4ec05c9ace95da88b3700d02c7633bb504fcb0329f242804a0f7735495d19e5da19c7e03a2bf58f87e9403d3",
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
            java / "jdk-14.jdk" / "Contents" / "Home" / "bin",
            dependency_check / "DependencyCheck-5.3.2",
        ):
            results = await run_dependency_check(str(RxJava / "RxJava-2.2.16"))
            self.assertEqual(type(results["report"]["total_CVE"]), int)
