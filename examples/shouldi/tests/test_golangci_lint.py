import os
import copy
import pathlib

from dffml import (
    prepend_to_path,
    AsyncTestCase,
    cached_download_unpack_archive,
)

from shouldi.golang.golangci_lint import run_golangci_lint

from .binaries import (
    CACHED_GOLANG,
    CACHED_GOLANGCI_LINT,
    CACHED_TARGET_CRI_RESOURCE_MANAGER,
)


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

    async def test_run(self):
        golang = await cached_download_unpack_archive(*CACHED_GOLANG)
        golangci_lint = await cached_download_unpack_archive(
            *CACHED_GOLANGCI_LINT
        )
        cri_resource_manager = await cached_download_unpack_archive(
            *CACHED_TARGET_CRI_RESOURCE_MANAGER
        )
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
