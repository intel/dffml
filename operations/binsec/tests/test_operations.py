from dffml.df.types import Input, DataFlow
from dffml.operation.output import Associate
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_binsec.operations import (
    URLToURLBytes,
    cleanup_rpm,
    files_in_rpm,
    is_binary_pie,
    urlbytes_to_rpmfile,
    urlbytes_to_tarfile,
)

dataflow = DataFlow.auto(
    URLToURLBytes,
    files_in_rpm,
    urlbytes_to_rpmfile,
    urlbytes_to_tarfile,
    is_binary_pie,
    Associate,
    cleanup_rpm,
)


class TestRunner(AsyncTestCase):
    async def test_run(self):
        packages = {
            "http://pkg.freebsd.org/FreeBSD:13:amd64/latest/All/ImageMagick7-7.0.8.48.txz": {},
            "https://download.clearlinux.org/releases/10540/clear/x86_64/os/Packages/sudo-setuid-1.8.17p1-34.x86_64.rpm": {
                "./usr/bin/sudo": True
            },
            "https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/20/Everything/x86_64/os/Packages/c/curl-7.32.0-3.fc20.x86_64.rpm": {
                "./usr/bin/curl": False
            },
        }
        found = dict(zip(packages.keys(), [False] * len(packages)))
        async for ctx, results in MemoryOrchestrator.run(
            dataflow,
            {
                URL: [
                    Input(
                        value=URL, definition=URLToURLBytes.op.inputs["URL"]
                    ),
                    Input(
                        value=["rpm_filename", "binary_is_PIE"],
                        definition=Associate.op.inputs["spec"],
                    ),
                ]
                for URL in packages
            },
            strict=True,
        ):
            package_url = (await ctx.handle()).as_string()
            with self.subTest(package_url=package_url):
                self.assertIn("binary_is_PIE", results)
                self.assertDictEqual(
                    results["binary_is_PIE"], packages[package_url]
                )
            found[package_url] = True
        self.assertTrue(
            all(found.values()), "Not all packages we analyized: f{found}"
        )
