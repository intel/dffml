import os
import sys
import uuid
import tempfile
from unittest import mock

from dffml.df.base import opimp_in
from dffml.df.types import Input, DataFlow
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase
from dffml.base import BaseDataFlowFacilitatorObjectContext

from dffml.operation.output import GetSingle
from dffml_operations_deploy.operations import *
from dffml_feature_git.feature.operations import (
    clone_git_repo,
    cleanup_git_repo,
)
from dffml_feature_git.util.proc import check_output
from dffml_operations_deploy.operations import check_secret_match

OPIMPS = opimp_in(sys.modules[__name__])
OPIMPS.remove(check_secret_match.imp)

REPO = str(uuid.uuid4()).split("-")[-1]
USER = str(uuid.uuid4()).split("-")[-1]

DOCKERFILE_CONTENT = (
    "# Usage\n"
    + f"# docker run -d -t {USER}/{REPO}\n"
    + "# \n"
    + "FROM alpine\n"
)


class FakeCloneRepoImp(BaseDataFlowFacilitatorObjectContext):
    def __init__(self, *args, **kwargs):
        super().__init__()

    async def run(*args, **kwargs):
        URL = args[1]["URL"]
        directory = tempfile.mkdtemp(prefix="test_deploy")
        with open(os.path.join(directory, "Dockerfile"), "w+") as dockerfile:
            dockerfile.write(DOCKERFILE_CONTENT)
        return {"repo": {"URL": URL, "directory": directory}}


class TestOperations(AsyncTestCase):
    async def setUp(self):
        self.dataflow = DataFlow.auto(*OPIMPS)
        self.dataflow.seed += [
            Input(
                value=[
                    restart_running_containers.op.outputs["containers"].name
                ],
                definition=GetSingle.op.inputs["spec"],
            ),
            Input(value=True, definition=clone_git_repo.op.conditions[0]),
        ]

        test_data = {
            "ref": "refs/master",
            "repository": {
                "clone_url": f"https://github.com/{USER}/{REPO}.git",
                "default_branch": "master",
                "html_url": f"https://github.com/{USER}/{REPO}",
            },
        }

        self.test_inputs = {
            "TestRun": [
                Input(
                    value=test_data,
                    definition=check_secret_match.op.outputs["git_payload"],
                )
            ]
        }
        self.containers_to_remove = []

    async def tearDown(self):
        for container in self.containers_to_remove:
            await check_output("docker", "rm", "-f", container)
        await check_output("docker", "rmi", f"{USER}/{REPO}")

    # test are numbered so that the first test (test_0_..) builds an image and starts a container,
    # testing that a container will be started if one is not running already.
    # (test_1_..) restarts the container started by test_0.
    async def test_0_start_container(self):
        with mock.patch.object(
            clone_git_repo.imp, "CONTEXT", new=FakeCloneRepoImp
        ):
            tag = f"{USER}/{REPO}"
            before = await check_output(
                "docker",
                "ps",
                "--filter",
                f"ancestor={tag}",
                "--format",
                "{{.ID}} {{.RunningFor}}",
            )
            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(self.dataflow) as octx:
                    async for ctx, results in octx.run(self.test_inputs):
                        after = await check_output(
                            "docker",
                            "ps",
                            "--filter",
                            f"ancestor={tag}",
                            "--format",
                            "{{.ID}} {{.RunningFor}}",
                        )
                        self.assertNotEqual(before, after)
                        self.assertIn("docker_restarted_containers", results)
                        self.containers_to_remove = results[
                            "docker_restarted_containers"
                        ]

    async def test_1_restart_container(self):
        tag = f"{USER}/{REPO}"
        before = await check_output(
            "docker",
            "ps",
            "--filter",
            f"ancestor={tag}",
            "--format",
            "{{.ID}} {{.RunningFor}}",
        )
        with mock.patch.object(
            clone_git_repo.imp, "CONTEXT", new=FakeCloneRepoImp
        ):
            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(self.dataflow) as octx:
                    async for ctx, results in octx.run(self.test_inputs):
                        after = await check_output(
                            "docker",
                            "ps",
                            "--filter",
                            f"ancestor={tag}",
                            "--format",
                            "{{.ID}} {{.RunningFor}}",
                        )
                        self.assertNotEqual(before, after)
                        self.assertIn("second", after)
                        self.assertIn("docker_restarted_containers", results)
                        self.containers_to_remove = results[
                            "docker_restarted_containers"
                        ]
