import os
import copy
import pathlib

from dffml.util.os import prepend_to_path
from dffml.util.net import cached_download_unpack_archive
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.golangci_lint import run_golangci_lint


class TestRunGolangci_lintOp(AsyncTestCase):
    async def setUp(self):
        # We'll be adding golang specific environment variables, so let's be
        # sure to save and restore
        self.old_environ = copy.deepcopy(os.environ)

    async def tearDown(self):
        # Remove keys that we're there before
        for k in os.environ:
            if not k in self.old_environ:
                del os.environ[k]
        # Reset the rest
        os.environ.update(self.old_environ)

    @cached_download_unpack_archive(
        "https://dl.google.com/go/go1.14.linux-amd64.tar.gz",
        pathlib.Path(__file__).parent / "golang.tar.gz",
        pathlib.Path(__file__).parent / "golang-download",
        "5dcc7b2e9049d80ceee9d3a7a4b76b578f42de64eaadabd039f080a9f329f2ad448da710626ed8fb4b070b4555b50e6f",
    )
    @cached_download_unpack_archive(
        "https://github.com/golangci/golangci-lint/releases/download/v1.23.7/golangci-lint-1.23.7-linux-amd64.tar.gz",
        pathlib.Path(__file__).parent / "golangci-lint.tar.gz",
        pathlib.Path(__file__).parent / "golangci-lint-download",
        "088a65ae7aa45c8a5695f40cc90672d00dece7f08ce307567fddc8b2d03858cb5baf9d162193922d36c57c504cc52999",
    )
    @cached_download_unpack_archive(
        "https://github.com/intel/cri-resource-manager/archive/c5e6091c79830cf7d076bbdec59c4a253b369d6a.tar.gz",
        pathlib.Path(__file__).parent / "cri-resource-manager.tar.gz",
        pathlib.Path(__file__).parent / "cri-resource-manager-download",
        "bdcbc8dadf9c6ee2f7571d10cb54459fe54773036982ad7485f007606efae96d7aaec7da18e2fea806fb6f68eb1722a8",
    )
    async def test_run(self, golang, golangci_lint, cri_resource_manager):
        os.environ["GOROOT"] = str(golang / "go")
        os.environ["GOPATH"] = str(cri_resource_manager / ".gopath")
        os.environ["GOBIN"] = str(cri_resource_manager / ".gopath" / "bin")
        with prepend_to_path(
            golang / "go" / "bin",
            golangci_lint / "golangci-lint-1.23.7-linux-amd64",
        ):
            results = await run_golangci_lint(
                str(
                    cri_resource_manager
                    / "cri-resource-manager-c5e6091c79830cf7d076bbdec59c4a253b369d6a"
                )
            )
            self.assertEqual(results["issues"], 99)
