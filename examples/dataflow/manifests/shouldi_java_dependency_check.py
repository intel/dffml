"""
This is a manifest shim next phase parser for shouldi manifest format 0.0.1

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
from typing import List, AsyncIterator, Tuple, Any, NamedTuple, Dict

import dffml.cli.dataflow
from dffml import *

import dffml_feature_git.feature.operations
import shouldi.java.dependency_check


WORKDIR = pathlib.Path(__file__).parent


@op(name=f"{pathlib.Path(__file__).stem}:pip_install",)
def pip_install(self, packages: List[str]) -> List[str]:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-U", *packages]
    )
    return packages


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
            # Install newest versions of dffml-feature-git and shouldi
            value=[
                "https://github.com/pdxjohnny/dffml/archive/refs/heads/manifest.zip#egg=dffml-feature-git&subdirectory=feature/git",
                "https://github.com/pdxjohnny/dffml/archive/refs/heads/manifest.zip#egg=shouldi&subdirectory=examples/shouldi",
            ],
            definition=pip_install.op.inputs["packages"],
        ),
    ],
)

# Clone repo
# Checkout commit or branch given
# Run dependency check
# Cleanup repo
DATAFLOW = DataFlow(
    dffml_feature_git.feature.operations.clone_git_repo,
    mapping_extract_value,
    shouldi.java.dependency_check.run_dependency_check,
    GetSingle,
    dffml_feature_git.feature.operations.cleanup_git_repo,
    seed=[
        Input(
            value=[
                definition.name
                for definition in shouldi.java.dependency_check.run_dependency_check.op.outputs.values()
            ],
            definition=GetSingle.op.inputs["spec"],
        ),
        Input(
            value=True,
            definition=dffml_feature_git.feature.operations.valid_git_repository_URL,
        ),
        Input(
            value=["directory"],
            definition=mapping_extract_value.op.inputs["traverse"],
        ),
    ],
)
# Grab directory from repo spec
DATAFLOW.flow[mapping_extract_value.op.name].inputs["mapping"] = [
    {
        dffml_feature_git.feature.operations.clone_git_repo.op.name: list(
            dffml_feature_git.feature.operations.clone_git_repo.op.outputs.keys()
        )[0]
    },
]
# Use repo directory as dependency check pkg to scan
DATAFLOW.flow[
    shouldi.java.dependency_check.run_dependency_check.op.name
].inputs["pkg"] = [
    {
        mapping_extract_value.op.name: list(
            mapping_extract_value.op.outputs.keys()
        )[0]
    },
]
# Update by_origin
DATAFLOW.update()


orchestrator = JobKubernetesOrchestrator(
    context=os.environ.get("KUBECTL_CONTEXT_CONTROLLER", "kind-kind"),
    prerun=prerun,
)
orchestrator = MemoryOrchestrator(
    max_ctxs=1,
)


async def synthesize_dataflow(manifest):
    print(json.dumps(export(DATAFLOW), indent=4, sort_keys=True))


async def execute_dataflow(manifest):
    async for ctx, results in run(
        DATAFLOW,
        {
            target: [
                Input(
                    value=target,
                    definition=dffml_feature_git.feature.operations.clone_git_repo.op.inputs[
                        "URL"
                    ],
                )
            ]
            for target in manifest["scan"]
        },
        strict=False,
        orchestrator=orchestrator,
    ):
        print(f"{ctx!s} results: ", end="")
        pprint.pprint(results)
        pathlib.Path(pathlib.Path(f"{ctx!s}-dependency-check.json").stem).write_text(json.dumps(
            {f"{ctx!s}": export(results)}
        ))


async def main():
    # Read manifest from stdin from shim
    # contents = json.loads(sys.stdin.read())
    # TODO DEBUG Remove this when using with shim
    import yaml

    contents = textwrap.dedent(
        """\
        $schema: https://schema.dffml.org/dffml.shouldi.java.dependency_check.0.0.0.schema.json
        scan:
        """
    ) + "- "+ "\n- ".join(
        pathlib.Path("/tmp/repos-to-scan").read_text().strip().split("\n")
    )

    print(contents)

    # TODO Git clone credentials
    manifest = yaml.safe_load(contents)

    await execute_dataflow(manifest)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
