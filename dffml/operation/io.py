import asyncio
import concurrent.futures
from typing import Dict, Any

from dffml.df.base import op
from dffml.df.types import Operation
from dffml.df.types import Definition
from dffml.df.base import (
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
        return input()

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_input = await self.parent.loop.run_in_executor(
            self.parent.pool, self.receive_input
        )
        return {"InputData": {"data": user_input}}


class AcceptUserInput(OperationImplementation):

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


@op(
    inputs={"data": DataToPrint}, outputs={}, conditions=[],
)
async def print_output(data: str):
    print("\n" + data)
