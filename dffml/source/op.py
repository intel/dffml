from typing import List

from ..record import Record
from ..high_level import run
from .source import BaseSource
from ..base import config, field
from ..df.types import DataFlow, Input
from ..util.entrypoint import entrypoint
from ..operation.output import GetSingle
from ..df.base import OperationImplementation
from .memory import MemorySource, MemorySourceContext


class OnlyOneOutputAllowedError(Exception):
    """
    Raised when the opimp given has more than one output
    """


class EmptyError(Exception):
    """
    Raised when the source is still empty after running the opimp
    """


class NotEnoughArgs(Exception):
    """
    Raised when the source was not given an arg for each operation input
    """


@config
class OpSourceConfig:
    opimp: OperationImplementation
    args: List[str] = field(
        "Arguments to operation in input order", default_factory=lambda: [],
    )
    allowempty: bool = field(
        "Raise an error if the source is empty after running the loading operation",
        default=False,
    )


@entrypoint("op")
class OpSource(MemorySource):

    CONTEXT = MemorySourceContext
    CONFIG = OpSourceConfig

    async def __aenter__(self):
        await super().__aenter__()
        # Ensure the opimp only has one output
        if len(self.config.opimp.op.outputs) != 1:
            raise OnlyOneOutputAllowedError(self.config.opimp.op.outputs)
        # Make a DataFlow
        dataflow = DataFlow.auto(self.config.opimp.__class__, GetSingle)
        # Make get_single output operation grab the output we care about
        dataflow.seed.append(
            Input(
                value=[list(self.config.opimp.op.outputs.values())[0].name],
                definition=GetSingle.op.inputs["spec"],
            )
        )
        # Ensure we have enough inputs
        if len(self.config.args) != len(self.config.opimp.op.inputs):
            raise NotEnoughArgs(
                f"Args: {self.config.args}, Inputs: {self.config.opimp.op.inputs}"
            )
        # Add inputs for operation
        for value, definition in zip(
            self.config.args, self.config.opimp.op.inputs.values()
        ):
            dataflow.seed.append(Input(value=value, definition=definition))
        # Run the DataFlow
        async for _ctx, result in run(dataflow):
            # Grab output definition from result of get_single
            result = result[
                list(self.config.opimp.op.outputs.values())[0].name
            ]
            # Convert to record objects if dict's
            for key, value in result.items():
                if not isinstance(value, Record):
                    result[key] = Record(key, data=value)
            # Set mem to result of operation
            self.mem = result
        # Ensure the source isn't empty
        if not self.mem and not self.config.allowempty:
            raise EmptyError()
        return self
