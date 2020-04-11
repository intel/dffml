import asyncio
import concurrent.futures
from typing import Dict, Any

from dffml.df.types import Operation, Definition
from dffml.df.base import (
    op,
    OperationImplementationContext,
    OperationImplementation,
)


# Definitions
UserInput = Definition(name="UserInput", primitive="str")
DataToPrint = Definition(name="DataToPrint", primitive="str")

AcceptUserInput = Operation(
    name="AcceptUserInput",
    inputs={},
    outputs={"InputData": UserInput},
    conditions=[],
)


class AcceptUserInputContext(OperationImplementationContext):
    @staticmethod
    def receive_input():
        print("Enter the value: ", end="")
        return input()

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_input = await self.parent.loop.run_in_executor(
            self.parent.pool, self.receive_input
        )
        return {"InputData": user_input}


class AcceptUserInput(OperationImplementation):
    """
    Accept input from stdin using python input()

    Parameters
    ++++++++++
    inputs : dict
        A dictionary with a key and empty list as value.

    Returns
    +++++++
    dict
        A dictionary containing user input.

    Examples
    ++++++++

    The following example shows how to use AcceptUserInput.
    (Assumes that the input from stdio is "Data flow is awesome"!)

    >>> dataflow = DataFlow.auto(AcceptUserInput, GetSingle)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[AcceptUserInput.op.outputs["InputData"].name],
    ...         definition=GetSingle.op.inputs["spec"]
    ...     )
    ... )
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, {"input":[]}):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    Enter the value: {'UserInput': 'Data flow is awesome'}
    """

    op = AcceptUserInput
    CONTEXT = AcceptUserInputContext

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = None
        self.pool = None
        self.__pool = None

    async def __aenter__(self) -> "OperationImplementationContext":
        self.loop = asyncio.get_event_loop()
        self.pool = concurrent.futures.ThreadPoolExecutor()
        self.__pool = self.pool.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__pool.__exit__(exc_type, exc_value, traceback)
        self.__pool = None
        self.pool = None
        self.loop = None


@op(inputs={"data": DataToPrint}, outputs={}, conditions=[])
async def print_output(data: str):
    """
    Print the output on stdout using python print()

    Parameters
    ++++++++++
    inputs : list
        A list of Inputs whose value is to be printed.

    Examples
    ++++++++

    The following example shows how to use print_output.

    >>> dataflow = DataFlow.auto(print_output, GetSingle)
    >>> inputs = [
    ...     Input(
    ...         value="print_output example",
    ...         definition=dataflow.definitions["DataToPrint"],
    ...         parents=None,)]
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, inputs):
    ...         print("String to be printed is 'print_output example'")
    >>>
    >>> asyncio.run(main())
    print_output example
    String to be printed is 'print_output example'
    """
    print(data)
