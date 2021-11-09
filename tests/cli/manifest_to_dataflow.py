"""
This is a manifest shim next phase parser for intel-sever-platform-validation
manifest format 0.0.1

This next phase parser currently kicks off execution of testplan in relevent
kubernetes clusters.
"""
import os
import sys
import json
import pathlib
import logging
import textwrap
import unittest
import importlib
import contextlib

from dffml import *
from dffml_feature_git.feature.operations import *

logging.basicConfig(level=logging.DEBUG)


TEST_TARGET = Definition(name="server.platform.target", primitive="string")

TEST_STDOUT = Definition(name="process.stdout", primitive="List[str]")
TEST_STDERR = Definition(name="process.stderr", primitive="List[str]")
PROCESS_RETURN_CODE = Definition(name="process.returncode", primitive="int")


@op(
    inputs={"repo": git_repository_checked_out, "target": TEST_TARGET},
    outputs={
        "stdout": TEST_STDOUT,
        "stderr": TEST_STDERR,
        "returncode": PROCESS_RETURN_CODE,
    },
)
async def execute_test_target(target: str):
    output = {"stdout": [], "stderr": [], "returncode": 1}
    async for event, result in exec_subprocess([target], cwd=repo.directory):
        if event == Subprocess.STDOUT_READLINE:
            result = result.decode().rstrip()
            self.logger.debug(f"{cmd}: {event}: {result}")
            output["stdout"].append(result)
        elif event == Subprocess.STDERR_READLINE:
            result = result.decode().rstrip()
            self.logger.debug(f"{cmd}: {event}: {result}")
            output["stderr"].append(result)
        elif event == Subprocess.COMPLETED:
            output["returncode"] = result
    return output


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
        Input(value=git["branch"], definition=git_branch),
        Input(value=git["file"], definition=TEST_TARGET),
    ]


async def run_in_k8s(document):
    # Inputs by context where context string is index in testplan
    on_sut_test_cases = {}
    controller_test_cases = {}
    # Go through each test case in the test plan
    for i, test_case in enumerate(document["testplan"]):
        # Create list of inputs for each test case context
        test_case_inputs = []
        if "git" in test_case:
            test_case_inputs += test_case_git_to_inputs(test_case["git"])
        # Add to dict of inputs by context
        i = str(i)
        if "sut" in test_case:
            on_sut_test_cases[i] = test_case_inputs
        else:
            controller_test_cases[i] = test_case_inputs

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

    # Create orchestrators to talk to both clusters
    controller_cluster = JobKubernetesOrchestrator(
        context=os.environ.get(
            "KUBECTL_CONTEXT_CONTROLLER", "controller-context"
        ),
        workdir=os.getcwd(),
        requirements=["dffml-feature-git"],
        # DataFlow to add sidecar for SUT allocation
        preapply=preapply,
    )
    sut_cluster = JobKubernetesOrchestrator(
        context=os.environ.get("KUBECTL_CONTEXT_SUT", "sut-context"),
        workdir=os.getcwd(),
        requirements=["dffml-feature-git"],
    )

    # Create dataflow for this testcase specific to it being a controller
    # testcase
    # dataflow.configs[github_get_repo.op.name] = GitHubGetRepoConfig(
    #     token=os.environ["GITHUB_TOKEN"],
    # )

    # TODO Run all test cases at the same time
    for test_cases, orchestrator in [
        (on_sut_test_cases, sut_cluster),
        (controller_test_cases, controller_cluster),
    ]:
        # NOTE Only attempt to run tests if there are any test cases or else the
        # dataflow will hang forever waiting on an initial input set
        if not test_cases:
            continue
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
                repo: https://example.com/my-repo.git
                branch: main
                file: my_test.py
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
        )
    )

    await run_in_k8s(manifest)


if __name__ == "__main__":
    asyncio.run(main())
