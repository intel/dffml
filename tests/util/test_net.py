import io
import os
import shutil
import tarfile
import pathlib
import tempfile
import contextlib
import unittest.mock

import httptest

from dffml.util.os import chdir
from dffml.util.net import cached_download
from dffml.util.asynctestcase import AsyncTestCase


class TestCachedDownloadServer(httptest.Handler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/x-gzip")
        self.end_headers()

        with contextlib.ExitStack() as stack:
            # gzip will add a last modified time by calling time.time, to ensure
            # that the hash is always the same, we set the time to 0
            stack.enter_context(
                unittest.mock.patch("time.time", return_value=1)
            )
            # Create the bytes objects to build the tarfile in memory
            tar_fileobj = stack.enter_context(io.BytesIO())
            hello_txt_fileobj = stack.enter_context(io.BytesIO(b"world"))
            dead_bin_fileobj = stack.enter_context(io.BytesIO(b"\xBE\xEF"))
            # Create the TarInfo objects
            hello_txt_tarinfo = tarfile.TarInfo(name="somedir/hello.txt")
            hello_txt_tarinfo.size = len(hello_txt_fileobj.getvalue())
            dead_bin_tarinfo = tarfile.TarInfo(name="somedir/dead.bin")
            dead_bin_tarinfo.size = len(dead_bin_fileobj.getvalue())
            # Create the archive using the bytes objects
            with tarfile.open(mode="w|gz", fileobj=tar_fileobj) as archive:
                archive.addfile(hello_txt_tarinfo, fileobj=hello_txt_fileobj)
                archive.addfile(dead_bin_tarinfo, fileobj=dead_bin_fileobj)
            # Write out the contents of the tar to the client
            self.wfile.write(tar_fileobj.getvalue())


class TestNet(AsyncTestCase):
    @httptest.Server(TestCachedDownloadServer)
    async def test_call_response(self, ts=httptest.NoServer()):
        with tempfile.TemporaryDirectory() as tempdir:

            @cached_download(
                ts.url() + "/archive.tar.gz",
                pathlib.Path(tempdir) / "archive.tar.gz",
                "cd538a17ce51458e3315639eba0650e96740d3d6abadbf174209ee7c5cae000ac739e99d9f32c9c2ba417b0cf67e69b8",
                protocol_allowlist=["http://"],
            )
            async def func(filename):
                return filename

            # Directory to extract to
            extracted = pathlib.Path(tempdir, "extracted")

            # Unpack the archive
            shutil.unpack_archive(await func(), extracted)

            # Verify contents are correct
            self.assertTrue((extracted / "somedir").is_dir())
            self.assertEqual(
                (extracted / "somedir" / "hello.txt").read_text(), "world"
            )
            self.assertEqual(
                (extracted / "somedir" / "dead.bin").read_bytes(), b"\xBE\xEF"
            )
