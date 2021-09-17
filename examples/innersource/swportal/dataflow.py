import sys
import json
import asyncio
import pathlib

import dffml

# Import the sources we implemented
from sources.orgs_repos_yml import OrgsReposYAMLSource
from sources.sap_portal_repos_json import SAPPortalReposJSONSource

# Import all the operations we implemented into this file's global namespace
from operations.gh import *

# Read in the repos.json backup to learn it's format. It's in the same directory
# as this file (dataflow.py) so we can reference it by looking in the parent
# directory of this file and then down (via .joinpath()) into repos.json.bak
repos_json_bak_path = pathlib.Path(__file__).parent.joinpath("repos.json.bak")
# Read in the contents
repos_json_bak_text = repos_json_bak_path.read_text()
# Parse the contents
repos_json_bak = json.loads(repos_json_bak_text)
# We'll inspect the first element in the list to find out what keys must be
# present in the object
required_data_top_level = list(repos_json_bak[0].keys())
# It should look like this:
#   required_data_top_level = [
#       'id', 'name', 'full_name', 'html_url', 'description', 'created_at',
#       'updated_at', 'pushed_at', 'stargazers_count', 'watchers_count',
#       'language', 'forks_count', 'open_issues_count', 'license',
#       'default_branch', 'owner', '_InnerSourceMetadata'
#   ]
# We're first going to create output operations to grab each of the keys
# We know that _InnerSourceMetadata is not a single value, so we'll handle that
# separately and remove it from our list
required_data_top_level.remove("_InnerSourceMetadata")

# Make a list of any imported OpeartionImplementations (functions decorated with
# @op()) from any that are in the global namespace of this file
operation_implementations = dffml.opimp_in(sys.modules[__name__])

# Create a DataFlow using every operation in all the modules we imported. Also
# use the remap operation
dataflow = dffml.DataFlow(
    dffml.remap,
    *operation_implementations,
    # The remap operation allows us to specify which keys should appear in the
    # outputs of each dataflow run. We do that by configuring it to use a
    # subflow, which is a dataflow run within a dataflow.
    # TODO(pdxjohnny) Remove .export() after unifying config code.
    configs={
        dffml.remap.op.name: {
            # Our subflow will run the get_single operation, which grabs one
            # Input object matching the given definition name. The one Input we
            # grab at first is the raw ouput of the PyGithub Repository object.
            "dataflow": dffml.DataFlow(
                dffml.GetSingle,
                seed=[
                    dffml.Input(
                        value=[github_repo_raw.op.outputs["raw_repo"].name],
                        definition=dffml.GetSingle.op.inputs["spec"],
                    )
                ],
            ).export()
        }
    },
    seed=[
        dffml.Input(
            # The output of the top level dataflow will be a dict where the keys
            # are what we give here, and the values are the output of a call to
            # traverse_get(), where the keys to traverse are the values we give
            # here, and the dict being traversed the results from the subflow.
            # {key: traverse_get(subflow_results, *value)}
            value={
                key: [github_repo_raw.op.outputs["raw_repo"].name, key]
                for key in required_data_top_level
            },
            definition=dffml.remap.op.inputs["spec"],
        )
    ],
)


# Path to the output repos.json file
repos_json_path = pathlib.Path(__file__).parent.joinpath(
    "html-client", "repos.json"
)


async def main():
    # Clear the file so we overwrite with new data
    repos_json_path.write_text("[]")
    # Create and enter our sources (__aenter__()) following the Double Context
    # Entry pattern (see tutorial page for more details)
    async with OrgsReposYAMLSource(
        directory=pathlib.Path(__file__).parent.joinpath("orgs")
    ) as input_source, SAPPortalReposJSONSource(
        filename=repos_json_path, readwrite=True,
    ) as output_source:
        # Second context entry
        async with input_source() as input_source_ctx, output_source() as output_source_ctx:
            # Run the dataflow
            async for ctx, results in dffml.run(
                dataflow,
                {
                    # We will run the dataflow on all input repos at the same
                    # time. The dataflow will run on each repo / record
                    # concurrently. We do this by creating a dictionary where
                    # each key is an InputSetContext, a RecordInputSetContext to
                    # be excat, since the context for each run is tied to the
                    # record / repo.
                    dffml.RecordInputSetContext(record): [
                        # Create a list of Inputs for each record's context. The
                        # only input we add at this time is the url of the repo.
                        dffml.Input(
                            value=record.key,
                            definition=dataflow.definitions["github.repo.url"],
                        )
                    ]
                    async for record in input_source_ctx.records()
                },
                strict=False,
            ):
                # Update the feature data of the record. The feature data is
                # what we are writing out to repos.json in the source we
                # implemented.
                ctx.record.evaluated(results)
                # Print results for debugging purposes
                print(ctx.record.export())
                # Save to output repos.json
                await output_source_ctx.update(ctx.record)


if __name__ == "__main__":
    asyncio.run(main())
