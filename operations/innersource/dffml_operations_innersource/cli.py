import sys
import json
import pathlib
import tempfile
import platform
import itertools
from typing import Dict, NewType

import dffml

import dffml_feature_git.feature.definitions
import dffml_feature_git.feature.operations

from . import operations


@dffml.config
class EnsureTokeiConfig:
    cache_dir: pathlib.Path = dffml.field("Cache directory to store downloads in",)
    platform_urls: Dict[str, Dict[str, str]] = dffml.field(
        "Mapping of platform.system() return values to tokei download URLs with hashes",
        default_factory=lambda: {
            "Linux": {
                "url": "https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-unknown-linux-gnu.tar.gz",
                "expected_hash": "b54fa0959e7a3a8935bd5cd86795b92e14d0a7b2cb6fb8f362b7b48198ce83e6dedc35a87e7c8fa405328f19d0ea6c47",
            },
            "Darwin": {
                "url": "https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz",
                "expected_hash": "8c8a1d8d8dd4d8bef93dabf5d2f6e27023777f8553393e269765d7ece85e68837cba4374a2615d83f071dfae22ba40e2",
            },
        },
    )


import contextlib


@dffml.op(
    config_cls=EnsureTokeiConfig, imp_enter={"stack": contextlib.AsyncExitStack,},
)
async def ensure_tokei(self) -> str:
    tokei = await dffml.cached_download_unpack_archive(
        **{
            "file_path": self.parent.config.cache_dir.joinpath("tokei.tar.gz"),
            "directory_path": self.parent.config.cache_dir.joinpath("tokei-download"),
            # Use whatever values are appropriate for the system we are on
            **self.parent.config.platform_urls[platform.system()],
        }
    )
    self.parent.stack.enter_context(dffml.prepend_to_path(tokei))
    return tokei.joinpath("tokei")


GitHubRepoID = NewType("GitHubRepoID", str)


@dffml.op
async def github_repo_id_to_clone_url(
    self, repo_id: GitHubRepoID,
) -> dffml_feature_git.feature.definitions.URLType:
    """
    Convert GitHub Integer Repository ID to Clonable URL.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        # Write out the API query response to a file
        api_response_contents_path = pathlib.Path(tempdir, "contents")
        with open(api_response_contents_path , "wb") as stdout:
            await dffml.run_command(
                ["gh", "api", f"https://api.github.com/repositories/{repo_id}"],
                stdout=stdout,
            )
            stdout.seek(0)
        # Parse in the response body as JSON
        repository = json.loads(api_response_contents_path.read_text())
    return repository["clone_url"]


COLLECTOR_DATAFLOW = dffml.DataFlow(
    dffml.GroupBy,
    *dffml.opimp_in(dffml_feature_git.feature.operations),
    *dffml.opimp_in(operations),
    *dffml.opimp_in(sys.modules[__name__]),
    # TODO(alice) Update to use the real overlay infra within run()
    *itertools.chain(
        *[
            dffml.object_to_operations(cls)
            for cls in dffml.Overlay.load(
                entrypoint="dffml.overlays.alice.shouldi.contribute",
            )
        ],
    ),
    configs={
        ensure_tokei.op.name: EnsureTokeiConfig(
            cache_dir=pathlib.Path(
                ".tools", "open-architecture", "innersource", ".cache", "tokei",
            )
        ),
    },
)
COLLECTOR_DATAFLOW.seed = [
    dffml.Input(value=1, definition=COLLECTOR_DATAFLOW.definitions["quarters"]),
    dffml.Input(
        value=True, definition=COLLECTOR_DATAFLOW.definitions["no_git_branch_given"],
    ),
    dffml.Input(
        value=dict(
            itertools.chain(
                *[
                    [
                        (output.name, {
                            "group": output.name,
                            "by": "quarter",
                            "nostrict": True,
                        })
                        for output in operation.outputs.values()
                    ]
                    for operation in COLLECTOR_DATAFLOW.operations.values()
                ]
            )
        ),
        definition=COLLECTOR_DATAFLOW.definitions["group_by_spec"],
    ),
]
COLLECTOR_DATAFLOW.operations[
    COLLECTOR_DATAFLOW.operations["lines_of_code_by_language"].name
] = COLLECTOR_DATAFLOW.operations[
    COLLECTOR_DATAFLOW.operations["lines_of_code_by_language"].name
]._replace(
    conditions=[ensure_tokei.op.outputs["result"]]
)
COLLECTOR_DATAFLOW.update(auto_flow=True)
# Operations which should take inputs from other operations in flow and seed
# MUST have their input flow modified to add the seed origin to the allowlist.
for operation_name, (input_name, origins) in [
    (dffml_feature_git.feature.operations.clone_git_repo.op.name, ("URL", ["seed",])),
    (dffml_feature_git.feature.operations.check_if_valid_git_repository_URL.op.name, ("URL", ["seed",])),
]:
    COLLECTOR_DATAFLOW.flow[operation_name].inputs[input_name].extend(origins)
COLLECTOR_DATAFLOW.update_by_origin()


import copy
import dataclasses
import dffml.cli.dataflow


DEFAULT_SOURCE = dffml.JSONSource(
    filename=pathlib.Path(".tools", "open-architecture", "innersource", "repos.json",),
    readwrite=True,
    allowempty=True,
    mkdirs=True,
)


# NOTE When CLI and operations are merged: All this is the same stuff that will
# happen to Operation config_cls structures. We need a more ergonomic API to
# obsucre the complexity dataclasses introduces when modifying fields/defaults
# within subclasses.
for dffml_cli_class_name, field_modifications in {
    "RunAllRecords": {
        # metadata setting could be less awkward
        "dataflow": {"default": COLLECTOR_DATAFLOW},
        "record_def": {"default": COLLECTOR_DATAFLOW.definitions["URL"].name},
        "sources": {"default_factory": lambda: dffml.Sources(DEFAULT_SOURCE)},
    },
    "RunRecordSet": {
        "dataflow": {"default": COLLECTOR_DATAFLOW},
        "record_def": {"default": COLLECTOR_DATAFLOW.definitions["URL"].name},
        "sources": {"default_factory": lambda: dffml.Sources(DEFAULT_SOURCE)},
    },
    "Diagram": {"dataflow": {"default": COLLECTOR_DATAFLOW,},},
}.items():
    # Create the class and config names by prepending InnerSource
    new_class_name = "InnerSource" + dffml_cli_class_name
    # Create a derived class
    new_class = getattr(dffml.cli.dataflow, dffml_cli_class_name).subclass(
        new_class_name, field_modifications,
    )
    # Add our new class to the global namespace
    setattr(
        sys.modules[__name__], new_class.CONFIG.__qualname__, new_class.CONFIG,
    )
    setattr(
        sys.modules[__name__], new_class.__qualname__, new_class,
    )


class InnerSourceRunRecords(dffml.CMD):
    """Run DataFlow and assign output to a record"""

    _set = InnerSourceRunRecordSet
    _all = InnerSourceRunAllRecords


class InnerSourceRun(dffml.CMD):
    """Run dataflow"""

    records = InnerSourceRunRecords


class InnerSourceCLI(dffml.CMD):

    run = InnerSourceRun
    diagram = InnerSourceDiagram
