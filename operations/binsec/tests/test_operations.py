from dffml.operation.output import Associate
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase
from dffml.df.types import Input, DataFlow, Operation
from dffml_operations_binsec.operations import (
    URLToURLBytes,
    cleanup_rpm,
    files_in_rpm,
    is_binary_pie,
    urlbytes_to_rpmfile,
    urlbytes_to_tarfile,
)

OPERATIONS = [Associate.op, URLToURLBytes.op]


class TestRunner(AsyncTestCase):
    async def test_run(self):
        repos = [
            "http://pkg.freebsd.org/FreeBSD:13:amd64/latest/All/ImageMagick7-7.0.8.48.txz",
            "https://download.clearlinux.org/releases/10540/clear/x86_64/os/Packages/sudo-setuid-1.8.17p1-34.x86_64.rpm",
            "https://rpmfind.net/linux/fedora/linux/updates/29/Everything/x86_64/Packages/g/gzip-1.9-9.fc29.x86_64.rpm",
            "https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/20/Everything/x86_64/os/Packages/c/curl-7.32.0-3.fc20.x86_64.rpm",
        ]

        dataflow = DataFlow.auto(
            URLToURLBytes,
            files_in_rpm,
            urlbytes_to_rpmfile,
            urlbytes_to_tarfile,
            is_binary_pie,
            Associate,
            cleanup_rpm,
        )
        async with MemoryOrchestrator.withconfig({}) as orchestrator:

            definitions = Operation.definitions(*OPERATIONS)

            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(
                    {
                        URL: [
                            Input(value=URL, definition=definitions["URL"]),
                            Input(
                                value=["rpm_filename", "binary_is_PIE"],
                                definition=definitions["associate_spec"],
                            ),
                        ]
                        for URL in repos
                    },
                    strict=True,
                ):
                    self.assertTrue(results)
