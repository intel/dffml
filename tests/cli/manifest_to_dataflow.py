"""
This is a manifest shim next phase parser for intel-sever-platform-validation
manifest format 0.0.1

This next phase parser currently kicks off execution of testplan in relevent
kubernetes clusters.
"""
import os
import sys
import json
import pprint
import asyncio
import pathlib
import logging
import textwrap
import unittest
import importlib
import contextlib
import subprocess
from typing import List

import dffml.cli.dataflow
from dffml import *

logging.basicConfig(level=logging.DEBUG)


TEST_TARGET = Definition(name="server.platform.target", primitive="string")

TEST_STDOUT = Definition(name="process.stdout", primitive="str")
TEST_STDERR = Definition(name="process.stderr", primitive="str")
PROCESS_RETURN_CODE = Definition(name="process.returncode", primitive="int")


WORKDIR = pathlib.Path(__file__).resolve().parent


@config
class ExecuteTestTargetConfig:
    cmd: List[str] = field(
        "Command to run to execute test target. $TARGET will be replaced with target file",
        default_factory=lambda: [sys.executable, "-u", "$TARGET"],
    )


async def execute_test_target(self, repo, target):
    output = {"stdout": "", "stderr": "", "returncode": 1}
    cmd = [arg.replace("$TARGET", target) for arg in self.parent.config.cmd]
    async for event, result in exec_subprocess(cmd, cwd=repo.directory):
        if event == Subprocess.STDOUT_READLINE:
            output["stdout"] += result.decode()
            result = result.decode().rstrip()
            self.logger.debug(f"{cmd}: {event}: {result}")
        elif event == Subprocess.STDERR_READLINE:
            output["stderr"] += result.decode()
            result = result.decode().rstrip()
            self.logger.error(f"{cmd}: {event}: {result}")
        elif event == Subprocess.COMPLETED:
            output["returncode"] = result
    return output


with contextlib.suppress((ImportError, ModuleNotFoundError)):
    from dffml_feature_git.feature.operations import *

    execute_test_target = op(
        inputs={"repo": git_repository_checked_out, "target": TEST_TARGET},
        outputs={
            "stdout": TEST_STDOUT,
            "stderr": TEST_STDERR,
            "returncode": PROCESS_RETURN_CODE,
        },
        config_cls=ExecuteTestTargetConfig,
    )(execute_test_target)


@op
def pip_install(self, packages: List[str]) -> List[str]:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-U", *packages]
    )
    return packages


@op
def add_ambassador(contents: str) -> str:
    return
    # TODO TCF Cookies
    doc = yaml.safe_load(contents)
    doc["spec"]["template"]["spec"]["containers"].append(
        {
            "name": "ambassador",
            "image": "intelotc/dffml:latest",
            "command": ["python", "-m", "http.server", "--cgi", "8080"],
            "env": [{"name": "DIRECTORY", "value": "/mount"},],
            "workingDir": "/usr/src/dffml-kubernetes-job-working-dir/",
            "volumeMounts": [
                {
                    "name": "dffml-kubernetes-job-working-dir",
                    "mountPath": "/usr/src/dffml-kubernetes-job-working-dir",
                },
            ],
            "ports": [{"containerPort": 8080},],
        }
    )
    return yaml.dump(doc)


def test_case_git_to_inputs(git):
    """
    For test cases with a git section they call this function passing the git
    section. Returns Input objects
    """
    return [
        Input(value=git["repo"], definition=URL),
        Input(value=git["branch"], definition=git_commit),
        Input(value=git["file"], definition=TEST_TARGET),
    ]


async def run_in_k8s(document):
    # Install latest versions of packages
    prerun = DataFlow(
        pip_install,
        GetSingle,
        seed=[
            Input(
                value=[pip_install.op.outputs["result"].name],
                definition=GetSingle.op.inputs["spec"],
            ),
            Input(
                value=[
                    "https://github.com/pdxjohnny/dffml/archive/refs/heads/manifest.zip#egg=dffml-feature-git&subdirectory=feature/git",
                ],
                definition=pip_install.op.inputs["packages"],
            ),
        ],
    )
    prerun.update()
    prerun.operations[pip_install.op.name] = prerun.operations[
        pip_install.op.name
    ]._replace(name=f"{pathlib.Path(__file__).stem}:{pip_install.op.name}")

    # Create orchestrators to talk to both clusters with varrying configs.
    # Inputs by context where context string is index in testplan.
    clusters = {
        "controller_default": (
            JobKubernetesOrchestrator(
                context=os.environ.get(
                    "KUBECTL_CONTEXT_CONTROLLER", "controller-context"
                ),
                workdir=WORKDIR,
                prerun=prerun,
                # DataFlow to add sidecar for SUT allocation
                # preapply=preapply,
            ),
            {},
        ),
        "sut_default": (
            JobKubernetesOrchestrator(
                context=os.environ.get("KUBECTL_CONTEXT_SUT", "sut-context"),
                workdir=WORKDIR,
                prerun=prerun,
            ),
            {},
        ),
    }

    # Go through each test case in the test plan
    for i, test_case in enumerate(document["testplan"]):
        # Create list of inputs for each test case context
        test_case_inputs = []
        if "git" in test_case:
            test_case_inputs += test_case_git_to_inputs(test_case["git"])
        # Find or create orchestrator config to run this testcase
        cluster_base_name = "controller"
        if "sut" in test_case:
            cluster_base_name = "sut"
        cluster_default_name = cluster_base_name + "_default"
        cluster_default, _ = clusters[cluster_default_name]
        if "image" in test_case:
            cluster_name = ".".join([cluster_base_name, test_case["image"]])
            # Handle custom container image
            if cluster_name not in clusters:
                clusters[cluster_name] = (
                    cluster_default.__class__(
                        cluster_default.config._replace(
                            image=test_case["image"]
                        )
                    ),
                    {},
                )
        else:
            cluster_name = cluster_default_name
        cluster = clusters[cluster_name]
        # Add to dict of inputs by context
        cluster[1][str(i)] = test_case_inputs

    # Clone repo
    # Checkout commit or branch given
    # Run test
    # Cleanup repo
    dataflow = DataFlow(
        check_if_valid_git_repository_URL,
        clone_git_repo,
        git_repo_checkout,
        execute_test_target,
        cleanup_git_repo,
        GetSingle,
        seed=[
            Input(
                value=[
                    definition.name
                    for definition in execute_test_target.op.outputs.values()
                ],
                definition=GetSingle.op.inputs["spec"],
            )
        ],
    )
    dataflow.operations[execute_test_target.op.name] = dataflow.operations[
        execute_test_target.op.name
    ]._replace(
        name=f"{pathlib.Path(__file__).stem}:{execute_test_target.op.name}"
    )

    # tcf run -vvt '(type:"Archer City" and not owner) or ipv4_addr' $file; done
    # tcf run -vvt '(type:"{platform}" and not owner) or ipv4_addr' $file; done

    # The preapply dataflow is responsible for adding the SUT allocation sidecar
    # to the cluster
    preapply = DataFlow(
        add_ambassador,
        GetSingle,
        configs={
            GetSingle.op.name: {
                "nostrict": [add_ambassador.op.outputs["result"]],
            },
        },
        seed=[
            Input(
                value=[add_ambassador.op.outputs["result"].name],
                definition=GetSingle.op.inputs["spec"],
            ),
        ],
    )
    preapply.flow[add_ambassador.op.name].inputs["seed"] = [
        {"seed": [JobKubernetesOrchestratorPreApplyDefinitions.JOB.value.name]}
    ]
    preapply.update()

    # Create dataflow for this testcase specific to it being a controller
    # testcase
    # dataflow.configs[github_get_repo.op.name] = GitHubGetRepoConfig(
    #     token=os.environ["GITHUB_TOKEN"],
    # )
    # Dump dataflow and diagram to stderr for debug purposes
    print(
        "To view the dataflow diagram paste into"
        " https://mermaid-js.github.io/mermaid-live-editor/"
    )
    async with dffml.cli.dataflow.Diagram(dataflow=dataflow) as diagram:
        print("========== BEGIN DIAGRAM ==========\n")
        await diagram.run()
        print("\n==========  END  DIAGRAM ==========")

    # TODO Run all test cases at the same time
    for orchestrator_name, (orchestrator, test_cases) in clusters.items():
        # NOTE Only attempt to run tests if there are any test cases or else the
        # dataflow will hang forever waiting on an initial input set
        if not test_cases:
            continue
        print()
        print(orchestrator_name, orchestrator, test_cases)
        print()
        async for ctx, results in run(
            dataflow, test_cases, orchestrator=orchestrator,
        ):
            print("testplan index {ctx!r} results: ", end="")
            pprint.pprint(results)


async def main():
    # Read manifest from stdin from shim
    # contents = json.loads(sys.stdin.read())
    # TODO DEBUG Remove this when using with shim
    import yaml

    manifest = yaml.safe_load(
        textwrap.dedent(
            """\
            $document_format: tps.manifest
            $document_version: 0.0.1
            testplan:
            - git:
                repo: https://gitlab.devtools.intel.com/johnsa1/phoenix-devops-poc
                branch: main
                file: mytest/test_pos_base.py
              image: amr-registry.caas.intel.com/raspv2/tcf.git__master
            """
        )
    )
    """
    - git:
        repo: https://example.com/their-repo.git
        branch: main
        file: their_test.py
    - sut: true
      git:
        repo: https://example.com/their-repo.git
        branch: main
        file: their_other_test.py
    """

    await run_in_k8s(manifest)


if __name__ == "__main__":
    asyncio.run(main())
