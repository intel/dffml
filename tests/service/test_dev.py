import io
import os
import sys
import json
import glob
import shutil
import inspect
import pathlib
import tarfile
import tempfile
import unittest
import contextlib
import dataclasses
import unittest.mock
from typing import Type, List, BinaryIO

from dffml.version import VERSION
from dffml.df.types import DataFlow
from dffml.service.dev import (
    Develop,
    RepoDirtyError,
    Export,
    Run,
    BumpPackages,
    MissingDependenciesError,
    Install,
    PinDeps,
    VersionNotFoundError,
    RCMissingHyphen,
)
from dffml.util.os import chdir
from dffml.util.skel import Skel
from dffml.util.net import cached_download_unpack_archive
from dffml.util.packaging import is_develop
from dffml.util.asynctestcase import AsyncTestCase, IntegrationCLITestCase

from ..util.test_skel import COMMON_FILES


class TestDevelopCreate(AsyncTestCase):
    def verify(self, root, name, package_specific_files):
        import_name = name.replace("-", "_")
        package_specific_files = list(
            map(
                lambda filename: tuple(
                    map(
                        lambda x: x.replace("{import_name}", import_name),
                        filename,
                    )
                ),
                package_specific_files,
            )
        )
        all_files = ", ".join(
            map(
                lambda path: path.replace(root, ""),
                glob.glob(os.path.join(root, "**")),
            )
        )
        for dirname in [(import_name,), ("tests",)]:
            check = os.path.join(root, *dirname)
            self.assertTrue(
                os.path.isdir(check), f"Not a directory: {check}: {all_files}"
            )
        for filename in [
            ("setup.py",),
            ("LICENSE",),
            ("README.md",),
            ("MANIFEST.in",),
            (import_name, "__init__.py"),
            (import_name, "version.py"),
            ("tests", "__init__.py"),
        ] + package_specific_files:
            check = os.path.join(root, *filename)
            self.assertTrue(
                os.path.isfile(check), f"Not a file: {check}: {all_files}"
            )

    async def generic_test(self, name, package_specific_files):
        package_name = "test-package"
        # Acquire the CreateCMD class of specified type
        cli_class = getattr(Develop.create, name)
        # Create tempdir to copy files to
        with tempfile.TemporaryDirectory() as tempdir:
            # Create directories in tempdir, one we cd into and one we use as
            # target parameter
            for target in [
                os.path.join(tempdir, "dot"),
                os.path.join(tempdir, "within"),
            ]:
                with self.subTest(target=target):
                    # Create the directory within the tempdir
                    os.mkdir(target)
                    # Instantiate an instance of the CreateCMD class
                    cli = cli_class(
                        package=package_name,
                        description=None,
                        target=target
                        if target[::-1].startswith(("dot")[::-1])
                        else None,
                    )
                    # Change directories
                    with chdir(target):
                        # Call create command
                        await cli.run()
                        # Verify that all went as planned
                        if target[::-1].startswith(("dot")[::-1]):
                            self.verify(
                                target, package_name, package_specific_files
                            )
                        elif target[::-1].startswith(("within")[::-1]):
                            self.verify(
                                os.path.join(target, package_name),
                                package_name,
                                package_specific_files,
                            )
                        else:  # pragma: no cov
                            pass

    async def test_model(self):
        await self.generic_test(
            "model",
            [("{import_name}", "myslr.py"), ("tests", "test_model.py")],
        )

    async def test_operations(self):
        await self.generic_test(
            "operations",
            [
                ("{import_name}", "definitions.py"),
                ("{import_name}", "operations.py"),
                ("tests", "test_operations.py"),
            ],
        )

    async def test_service(self):
        await self.generic_test(
            "service",
            [("{import_name}", "misc.py"), ("tests", "test_service.py")],
        )


class TestDevelopSkelLink(AsyncTestCase):

    skel = Skel()

    async def test_run(self):
        # Skip if not in development mode
        if not is_develop("dffml"):
            self.skipTest("dffml not installed in development mode")
        await Develop.cli("skel", "link")
        common_files = [
            path.relative_to(self.skel.common)
            for path in self.skel.common_files()
        ]
        # At time of writing there are 4 plugins in skel/ change this as needed
        plugins = self.skel.plugins()
        self.assertGreater(len(plugins), 3)
        for plugin in plugins:
            for check in COMMON_FILES:
                with chdir(plugin):
                    self.assertTrue(
                        check.is_symlink(),
                        f"{check.resolve()} is not a symlink",
                    )


@dataclasses.dataclass
class FakeProcess:
    cmd: List[str] = None
    returncode: int = 0
    stdout: BinaryIO = None

    def __post_init__(self):
        if self.cmd is None:
            self.cmd = []

    async def communicate(self):
        return b"", b""

    async def wait(self):
        if not "archive" in self.cmd:
            return
        with contextlib.ExitStack() as stack:
            # Create the bytes objects to build the tarfile in memory
            tar_fileobj = stack.enter_context(io.BytesIO())
            hello_txt_fileobj = stack.enter_context(io.BytesIO(b"world"))
            # Create the TarInfo objects
            hello_txt_tarinfo = tarfile.TarInfo(name="somedir/hello.txt")
            hello_txt_tarinfo.size = len(hello_txt_fileobj.getvalue())
            # Create the archive using the bytes objects
            with tarfile.open(mode="w|", fileobj=tar_fileobj) as archive:
                archive.addfile(hello_txt_tarinfo, fileobj=hello_txt_fileobj)
            # Write out the contents of the tar to the client
            self.stdout.write(tar_fileobj.getvalue())


def mkexec(proc_cls: Type[FakeProcess] = FakeProcess):
    async def fake_create_subprocess_exec(
        *args, stdin=None, stdout=None, stderr=None
    ):
        return proc_cls(cmd=args, stdout=stdout)

    return fake_create_subprocess_exec


class FakeResponse:
    def read(self, num=0):
        return json.dumps({"info": {"version": VERSION}}).encode()


@contextlib.contextmanager
def fake_urlopen(url):
    yield FakeResponse()


class TestRelease(AsyncTestCase):
    async def test_uncommited_changes(self):
        class FailedFakeProcess(FakeProcess):
            async def communicate(self):
                return b"There are changes", b""

        with unittest.mock.patch(
            "asyncio.create_subprocess_exec", new=mkexec(FailedFakeProcess)
        ):
            with self.assertRaises(RepoDirtyError):
                await Develop.cli("release", ".")

    async def test_already_on_pypi(self):
        stdout = io.StringIO()
        with unittest.mock.patch(
            "asyncio.create_subprocess_exec", new=mkexec()
        ), unittest.mock.patch(
            "urllib.request.urlopen", new=fake_urlopen
        ), contextlib.redirect_stdout(
            stdout
        ):
            await Develop.cli("release", ".")
        self.assertEqual(
            stdout.getvalue().strip(),
            f"Version {VERSION} of dffml already on PyPi",
        )

    async def test_okay(self):
        global VERSION
        VERSION = "0.0.0"
        for plugin in [".", "model/scikit"]:
            stdout = io.StringIO()
            with self.subTest(plugin=plugin):
                with unittest.mock.patch(
                    "asyncio.create_subprocess_exec", new=mkexec()
                ), unittest.mock.patch(
                    "urllib.request.urlopen", new=fake_urlopen
                ), contextlib.redirect_stdout(
                    stdout
                ):
                    await Develop.cli("release", plugin)
                self.assertEqual(
                    stdout.getvalue().strip(),
                    inspect.cleandoc(
                        f"""
                        $ git archive --format=tar HEAD
                        $ {sys.executable} setup.py sdist
                        $ {sys.executable} setup.py bdist_wheel
                        $ {sys.executable} -m twine upload dist/*
                        """
                    ),
                )


class TestSetupPyVersion(IntegrationCLITestCase):
    async def test_success(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            await Develop.cli(
                "setuppy",
                "version",
                self.mktempfile(text='VERSION = "0.0.42"'),
            )
        self.assertEqual("0.0.42", stdout.getvalue().strip())

    async def test_filenot_found(self):
        with self.assertRaises(VersionNotFoundError):
            await Develop.cli(
                "setuppy",
                "version",
                self.mktempfile(text='FEEDFACE = "0.0.42"'),
            ),


class TestBumpPackages(AsyncTestCase):
    async def test_bump_version(self):
        self.assertEqual(BumpPackages.bump_version("1.2.3", "5.6.7"), "6.8.10")

    async def test_bump_version_original_with_rc(self):
        self.assertEqual(
            BumpPackages.bump_version("1.2.3-rc0", "5.6.7"), "6.8.10"
        )

    async def test_bump_version_increment_with_rc(self):
        self.assertEqual(
            BumpPackages.bump_version("1.2.3", "5.6.7-rc0"), "6.8.10-rc0"
        )

    async def test_bump_version_both_with_rc(self):
        self.assertEqual(
            BumpPackages.bump_version("1.2.3-rc1", "5.6.7-rc2"), "6.8.10-rc3"
        )

    async def test_bump_version_zero(self):
        self.assertEqual(
            BumpPackages.bump_version("1.2.3-rc1", "5.6.Z"), "6.8.0"
        )

    async def test_bump_version_original_violates_semantic(self):
        with self.assertRaisesRegex(RCMissingHyphen, "original.*1\.2\.3rc1"):
            BumpPackages.bump_version("1.2.3rc1", "0.0.0")

    async def test_bump_version_increment_violates_semantic(self):
        with self.assertRaisesRegex(RCMissingHyphen, "increment.*5\.6\.7rc2"):
            BumpPackages.bump_version("1.2.3-rc1", "5.6.7rc2")


class TestExport(AsyncTestCase):
    async def test_run(self):
        stdout = io.BytesIO()
        with unittest.mock.patch("sys.stdout.buffer.write", new=stdout.write):
            await Export(
                export="tests.test_df:DATAFLOW", not_linked=False
            ).run()
        exported = json.loads(stdout.getvalue())
        DataFlow._fromdict(**exported)


class TestRun(AsyncTestCase):
    async def test_run(self):
        with tempfile.TemporaryDirectory() as tempdir:
            await Run.cli(
                "dffml.operation.db:db_query_create_table",
                "-table_name",
                "FEEDFACE",
                "-cols",
                json.dumps({"DEADBEEF": "text"}),
                "-config-database",
                "sqlite",
                "-config-database-filename",
                os.path.join(tempdir, "sqlite_database.db"),
                "-log",
                "debug",
            )


class TestInstall(AsyncTestCase):
    async def test_dep_check(self):
        with self.assertRaisesRegex(
            MissingDependenciesError,
            inspect.cleandoc(
                """
            The following plugins have unmet dependencies and could not be installed

                model/vowpalWabbit

                    feedface

            Install missing dependencies and re-run plugin install, or skip with

                -skip model/vowpalWabbit
            """
            ),
        ):
            Install.dep_check(
                {("model", "vowpalWabbit"): {"feedface": lambda: False}}, []
            )


class TestPinDeps(AsyncTestCase):
    @cached_download_unpack_archive(
        "https://github.com/intel/dffml/files/5978430/logs_2403.zip",
        pathlib.Path(__file__).parent / "logs.zip",
        pathlib.Path(__file__).parent / "logs",
        "4422bdcaf202d8b31ea131f9042def965fc7746125fd99038ca502cbdfeb2ca5bef12f88b053dcfd8a1305a41edd3371",
    )
    async def test_pin_deps(self, logs):
        await PinDeps._main(str(logs))
