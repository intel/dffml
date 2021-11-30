"""
This is a manifest shim next phase parser for intel-sever-platform-validation
manifest format 0.0.1

This next phase parser currently kicks off execution of testplan in relevent
kubernetes clusters.
"""
import os
import sys
import json
import copy
import pprint
import asyncio
import pathlib
import logging
import textwrap
import unittest
import importlib
import contextlib
import subprocess
from typing import List, AsyncIterator, Tuple, Any

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

# Clone repo
# Checkout commit or branch given
# Run test
# Cleanup repo
test_case_dataflow = DataFlow()

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

    test_case_dataflow = DataFlow(
        check_if_valid_git_repository_URL,
        clone_git_repo,
        git_repo_checkout,
        execute_test_target,
        GetSingle,
        cleanup_git_repo,
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

    test_case_dataflow.operations[
        execute_test_target.op.name
    ] = test_case_dataflow.operations[execute_test_target.op.name]._replace(
        name=f"{pathlib.Path(__file__).stem}:{execute_test_target.op.name}"
    )


# We must create a dataflow to run the dataflows because the execute_test_target
# config.cmd will be dependent on the BKC. We need to create a dataflow with a
# modified flow (merge command) which intercepts and modifes each dataflow in a
# RunDataFlowCustomSpec (which should eventually just be our new CLI +
# OperationImplementation verison of RunDataFlowConfig)
class RunDataFlowCustomSpec(NamedTuple):
    dataflow: DataFlow
    inputs: List[Input]
    orchestrator_name: str
    orchestrator: BaseOrchestrator


@op(
    inputs={
        "spec": Definition(
            name="run_dataflow_custom_spec",
            primitive="object",
            spec=RunDataFlowCustomSpec,
        )
    },
    outputs={
        "result": Definition(
            name="run_dataflow_custom_ctx_results_pair", primitive="object",
        )
    },
)
async def run_dataflow_custom(
    self, spec: RunDataFlowCustomSpec,
) -> AsyncIterator[Tuple[BaseInputSetContext, Any]]:
    print()
    print(spec.orchestrator_name, spec.orchestrator, spec.inputs)
    print()
    # NOTE Only attempt to run tests if there are any test cases or else the
    # dataflow will hang forever waiting on an initial input set
    if not spec.inputs:
        return
    async for ctx, results in run(
        spec.dataflow, spec.inputs, orchestrator=spec.orchestrator,
    ):
        print("{ctx!r} results: ", end="")
        pprint.pprint(results)
        yield ctx, results


# Create orchestrators to talk to both clusters with varrying configs.
# Inputs by context where context string is index in testplan.
clusters = {
    "controller_default": RunDataFlowCustomSpec(
        copy.deepcopy(test_case_dataflow),
        {},
        "controller_default",
        JobKubernetesOrchestrator(
            context=os.environ.get(
                "KUBECTL_CONTEXT_CONTROLLER", "controller-context"
            ),
            workdir=WORKDIR,
            prerun=prerun,
        ),
    ),
    "sut_default": RunDataFlowCustomSpec(
        copy.deepcopy(test_case_dataflow),
        {},
        "sut_default",
        JobKubernetesOrchestrator(
            context=os.environ.get("KUBECTL_CONTEXT_SUT", "sut-context"),
            workdir=WORKDIR,
            prerun=prerun,
        ),
    ),
}

DATAFLOW = DataFlow(
    run_dataflow_custom,
    GetMulti,
    seed=[
        Input(
            value=[
                definition.name
                for definition in execute_test_target.op.outputs.values()
            ],
            definition=GetMulti.op.inputs["spec"],
        )
    ],
)

DATAFLOW.operations[run_dataflow_custom.op.name] = DATAFLOW.operations[
    run_dataflow_custom.op.name
]._replace(name=f"{pathlib.Path(__file__).stem}:{run_dataflow_custom.op.name}")


async def run_in_k8s(document):
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
        cluster_default = clusters[cluster_default_name]
        if "image" in test_case:
            cluster_name = ".".join([cluster_base_name, test_case["image"]])
            # Handle custom container image
            if cluster_name not in clusters:
                clusters[cluster_name] = RunDataFlowCustomSpec(
                    copy.deepcopy(cluster_default.dataflow),
                    {},
                    cluster_name,
                    cluster_default.orchestrator.__class__(
                        cluster_default.orchestrator.config._replace(
                            image=test_case["image"]
                        )
                    ),
                )
        else:
            cluster_name = cluster_default_name
        # Add to dict of inputs by context
        cluster = clusters[cluster_name]
        cluster.inputs[str(i)] = test_case_inputs

    # tcf run -vvt '(type:"Archer City" and not owner) or ipv4_addr' $file; done
    # tcf run -vvt '(type:"{platform}" and not owner) or ipv4_addr' $file; done

    # dataflow.configs[github_get_repo.op.name] = GitHubGetRepoConfig(
    #     token=os.environ["GITHUB_TOKEN"],
    # )
    # DataFlow to execute test cases within clusters
    dataflow = copy.deepcopy(DATAFLOW)
    for cluster in clusters.values():
        dataflow.seed.append(
            Input(
                value=cluster,
                definition=run_dataflow_custom.op.inputs["spec"],
            )
        )

    # NOTE Using yaml
    import yaml

    print(yaml.dump(export(dataflow)))


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
