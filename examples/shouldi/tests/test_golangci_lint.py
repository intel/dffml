import os
import copy
import pathlib

from dffml import prepend_to_path, AsyncTestCase

from shouldi.golang.golangci_lint import run_golangci_lint

from .binaries import (
    cached_golang,
    cached_golangci_lint,
    cached_target_cri_resource_manager,
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

    @cached_golang
    @cached_golangci_lint
    @cached_target_cri_resource_manager
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
