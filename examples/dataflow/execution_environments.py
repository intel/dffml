"""
Local vs. Production DataFlow Orchestration
###########################################

This example demonstrates the us of DFFML to execute against different
configurations for dataflows meant for different environments.

We will have two deployments, local, and remote.

The local and remote environments get inputs from the command line and
environment variables respectively.

TODO
****

- Load and execute RunDataFlow operation from file containing dataflow and
  orchestrator configurations.
"""
import asyncio
import itertools

import dffml


# To start we're going to use the same dataflow when executing local and remote.
# TODO Later in the example, we'll change the remote example to execute a
# different operation with an extra input which we'll wire up.
example_return_type = dffml.Definition(
    name="example_return_type", primitive="string",
)
SHARED_DATAFLOW = dffml.DataFlow(
    dffml.GetSingle,
    seed=[
        dffml.Input(
            value=[example_return_type.name],
            definition=dffml.GetSingle.op.inputs["spec"],
        ),
    ],
)
SHARED_DATAFLOW.definitions[example_return_type.name] = example_return_type
LOCAL_DATAFLOW = SHARED_DATAFLOW
REMOTE_DATAFLOW = SHARED_DATAFLOW


DATAFLOW = dffml.DataFlow(
    dffml.GetMulti,
    operations={"local": dffml.run_dataflow, "remote": dffml.run_dataflow,},
    configs={
        "local": {"dataflow": LOCAL_DATAFLOW,},
        "remote": {"dataflow": REMOTE_DATAFLOW,},
    },
)
DATAFLOW.seed += [
    dffml.Input(
        value={
            "context": [
                {
                    "value": "the_return_value",
                    "definition": example_return_type.name,
                },
            ]
        },
        definition=dffml.run_dataflow.op.inputs["inputs"],
    ),
    dffml.Input(
        value=list(
            set(
                itertools.chain(
                    *[
                        [
                            definition.name
                            for definition in operation.outputs.values()
                        ]
                        for operation in DATAFLOW.operations.values()
                        if operation.name != dffml.GetMulti.op.name
                    ]
                )
            )
        ),
        definition=dffml.GetMulti.op.inputs["spec"],
    ),
]


async def main():
    async for ctx, result in dffml.run(DATAFLOW):
        print(ctx, result)


if __name__ == "__main__":
    asyncio.run(main())
