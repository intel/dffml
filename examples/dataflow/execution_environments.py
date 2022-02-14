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

import httptest

import dffml

# --- Local and Remote same flow ---


# To start we're going to use the same dataflow when executing local and remote.
@dffml.op(
    inputs={
        "username": dffml.Definition(
            name="username_type", primitive="string",
        ),
    },
    outputs={
        "greeting": dffml.Definition(
            name="example_return_type", primitive="string",
        ),
    }
)
def say_hello(username: str) -> dict:
    return {"greeting": f"Hello {username}"}


SHARED_DATAFLOW = dffml.DataFlow(
    say_hello,
    dffml.GetSingle,
)
SHARED_DATAFLOW.seed += [
    dffml.Input(
        value=list(
            set(
                itertools.chain(
                    *[
                        [
                            definition.name
                            for definition in operation.outputs.values()
                        ]
                        for operation in SHARED_DATAFLOW.operations.values()
                        if operation.name != dffml.GetSingle.op.name
                    ]
                )
            )
        ),
        definition=dffml.GetSingle.op.inputs["spec"],
    ),
]
LOCAL_DATAFLOW = SHARED_DATAFLOW
REMOTE_DATAFLOW = SHARED_DATAFLOW


# Make the inputs for each dataflow all of the inputs from each dataflow's flow
# which come from that dataflow's seed values.
DATAFLOW = dffml.DataFlow(
    dffml.GetMulti,
    operations={
        "local": dffml.run_dataflow.op._replace(
            inputs=dict(
                itertools.chain(
                    *[
                        [
                            (input_name, LOCAL_DATAFLOW.operations[
                                instance_name
                            ].inputs[input_name],)
                            for input_name, origins in input_flow.inputs.items()
                            if "seed" in origins
                        ]
                        for instance_name, input_flow in LOCAL_DATAFLOW.flow.items()
                        if instance_name != "get_single"
                    ]
                )
            ),
        ),
        "remote": dffml.run_dataflow.op._replace(
            inputs=dict(
                itertools.chain(
                    *[
                        [
                            (input_name, REMOTE_DATAFLOW.operations[
                                instance_name
                            ].inputs[input_name],)
                            for input_name, origins in input_flow.inputs.items()
                            if "seed" in origins
                        ]
                        for instance_name, input_flow in REMOTE_DATAFLOW.flow.items()
                        if instance_name != "get_single"
                    ]
                )
            ),
        ),
    },
    configs={
        "local": {"dataflow": LOCAL_DATAFLOW,},
        "remote": {"dataflow": REMOTE_DATAFLOW,},
    },
)
DATAFLOW.seed += [
    dffml.Input(
        value="World",
        definition=say_hello.op.inputs["username"],
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

# TODO
# --- Next we change the remote example to execute a different operation with
# an extra input which we'll wire up ---
