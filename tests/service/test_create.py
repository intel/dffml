import os
import glob
import tempfile
from contextlib import contextmanager

from dffml.service.create import Create
from dffml.util.asynctestcase import AsyncTestCase


@contextmanager
def chdir(path):
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)


class TestCreate(AsyncTestCase):
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
        cli_class = getattr(Create, name)
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

    async def test_model(self):
        await self.generic_test(
            "model", [("{import_name}", "misc.py"), ("tests", "test_model.py")]
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
