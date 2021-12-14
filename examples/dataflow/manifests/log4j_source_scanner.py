"""
This is a manifest shim next phase parser for log4j source scanner manifest
format 0.0.1

Dependency check does a port job of scanning source code for this in particular.
This is to supplement.
"""
import os
import re
import sys
import json
import copy
import pprint
import asyncio
import pathlib
import logging
import textwrap
import unittest
import itertools
import importlib
import contextlib
import subprocess
from typing import List, AsyncIterator, Tuple, Any, NamedTuple, Dict

import dffml.cli.dataflow
from dffml import *

import dffml_feature_git.feature.operations
import shouldi.java.dependency_check


WORKDIR = pathlib.Path(__file__).parent


@op(name=f"{pathlib.Path(__file__).stem}:pip_install")
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
            # Install newest versions of dffml-feature-git
            value=[
                "https://github.com/pdxjohnny/dffml/archive/refs/heads/manifest.zip#egg=dffml-feature-git&subdirectory=feature/git",
            ],
            definition=pip_install.op.inputs["packages"],
        ),
    ],
)


@contextlib.asynccontextmanager
async def get_log4j_versions(self):
    with sync_urlopen("https://archive.apache.org/dist/logging/log4j/") as response:
        # Source:
        # https://stackoverflow.com/questions/20841363/regex-finding-all-href-in-a-tags
        yield sorted([
            possible_version.replace("/", "")
            for possible_version in re.findall(r'<a[^>]* href="([^"]*)"', response.read().decode())
            if possible_version[:1].isdigit()
        ])


@op(
    name=f"{pathlib.Path(__file__).stem}:log4j_versions",
    imp_enter={"versions": get_log4j_versions}
)
def log4j_versions(self, contents: str) -> List[str]:
    # Return the match with the longest string so that we don't match a shorter
    # version string when there is a more specific match.
    found = []
    for line in contents.split("\n"):
        match = None
        for version in self.parent.versions:
            if version in line and (match is None or len(version) > len(match[0])):
                match = (version, line)
        if match is not None:
            found.append(match)
    return found

# Clone repo
# Checkout commit or branch given
# Look for matches with git grep because it's fast
# Run log4j version check
# Cleanup repo
DATAFLOW = DataFlow(
    dffml_feature_git.feature.operations.clone_git_repo,
    dffml_feature_git.feature.operations.git_grep,
    log4j_versions,
    GetSingle,
    dffml_feature_git.feature.operations.cleanup_git_repo,
    configs={
        dffml_feature_git.feature.operations.clone_git_repo.op.name: {
            "depth": 1,
        },
    },
    seed=[
        Input(
            value=[
                definition.name
                for definition in log4j_versions.op.outputs.values()
            ],
            definition=GetSingle.op.inputs["spec"],
        ),
        Input(
            value=True,
            definition=dffml_feature_git.feature.operations.valid_git_repository_URL,
        ),
        Input(
            value="log4j",
            definition=dffml_feature_git.feature.operations.git_grep_search,
        ),
    ],
)
# Grab directory from repo spec
DATAFLOW.flow[log4j_versions.op.name].inputs["contents"] = [
    "seed",
    {
        dffml_feature_git.feature.operations.git_grep.op.name: list(
            dffml_feature_git.feature.operations.git_grep.op.outputs.keys()
        )[0]
    },
]
# Update by_origin
DATAFLOW.update()


orchestrator = JobKubernetesOrchestrator(
    context=os.environ.get("KUBECTL_CONTEXT_CONTROLLER", "kind-kind"),
    prerun=prerun,
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
        pathlib.Path(pathlib.Path(f"{ctx!s}").stem).write_text(json.dumps(
            {f"{ctx!s}": export(results)}
        ))


async def main():
    # Read manifest from stdin from shim
    # contents = json.loads(sys.stdin.read())
    # TODO DEBUG Remove this when using with shim
    import yaml

    manifest = yaml.safe_load(
        textwrap.dedent(
            """\
            $schema: https://schema.dffml.org/dffml.security.scan.log4j.0.0.0.schema.json
            scan:
            - https://github.com/cabaletta/baritone
            """
        )
    )

    await execute_dataflow(manifest)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
