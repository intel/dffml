import pathlib
from typing import AsyncIterator, List

from ..base import config, field
from ..configloader.configloader import BaseConfigLoader
from ..df.types import DataFlow, Definition, Input
from ..df.base import BaseInputSetContext, BaseContextHandle
from ..df.base import BaseOrchestrator
from ..feature import Features
from ..record import Record
from ..source.source import BaseSource, BaseSourceContext
from ..util.entrypoint import entrypoint
from ..util.cli.parser import ParseInputsAction
from ..df.memory import MemoryOrchestrator


@config
class DataFlowPreprocessSourceConfig:
    source: BaseSource = field("Source to wrap")
    dataflow: DataFlow = field("DataFlow to use for preprocessing")
    features: Features = field(
        "Features to pass as definitions to each context from each "
        "record to be preprocessed",
        default_factory=lambda: Features(),
    )
    inputs: List[str] = field(
        "Other inputs to add under each ctx (record's key will "
        + "be used as the context)",
        action=ParseInputsAction,
        default_factory=lambda: [],
    )
    record_def: str = field(
        "Definition to be used for record.key."
        "If set, record.key will be added to the set of inputs "
        "under each context (which is also the record's key)",
        default=None,
    )
    length: str = field(
        "Definition name to add as source length", default=None
    )
    all_for_single: bool = field(
        "Run all records through dataflow before grabing "
        "results of desired record on a call to record()",
        default=False,
    )
    no_strict: bool = field(
        "Do not exit on operation exceptions, just log errors", default=False,
    )
    orchestrator: BaseOrchestrator = field(
        "Orchestrator",
        default_factory=lambda: MemoryOrchestrator.withconfig({}),
    )


class RecordContextHandle(BaseContextHandle):
    def as_string(self) -> str:
        return self.ctx.record.key


class RecordInputSetContext(BaseInputSetContext):
    def __init__(self, record: Record):
        self.record = record

    async def handle(self) -> BaseContextHandle:
        return RecordContextHandle(self)

    def __repr__(self):
        return self.record.key

    def __str__(self):
        return repr(self)


class DataFlowPreprocessSourceContext(BaseSourceContext):
    async def input_set(self, record: Record) -> List[Input]:
        return (
            [
                Input(
                    value=record.feature(feature.name),
                    definition=Definition(
                        name=feature.name, primitive=str(feature.dtype()),
                    ),
                )
                for feature in self.parent.config.features
            ]
            + [
                Input(
                    value=value,
                    definition=self.parent.config.dataflow.definitions[name],
                )
                for value, name in self.parent.config.inputs
            ]
            + (
                []
                if not self.parent.config.length
                else [
                    Input(
                        value=await self.sctx.length(),
                        definition=Definition(
                            name=self.parent.config.length, primitive="int",
                        ),
                    )
                ]
            )
            + (
                []
                if not self.parent.config.record_def
                else [
                    Input(
                        value=record.key,
                        definition=Definition(
                            name=self.parent.config.record_def,
                            primitive="string",
                        ),
                    )
                ]
            )
        )

    async def update(self, record: Record):
        await self.sctx.update(record)

    # TODO Implement this method. We forgot to implement it when we initially
    # added the DataFlowPreprocessSourceContext
    async def record(self, key: str) -> AsyncIterator[Record]:
        if self.parent.config.all_for_single:
            async for ctx, result in self.records():
                if (await ctx.handle()).as_string() == key:
                    return record
        else:
            async for ctx, result in self.octx.run(
                {
                    RecordInputSetContext(record): await self.input_set(record)
                    for record in [await self.sctx.record(key)]
                },
                strict=not self.parent.config.no_strict,
            ):
                if result:
                    ctx.record.evaluated(result)
                return ctx.record

    async def records(self) -> AsyncIterator[Record]:
        async for ctx, result in self.octx.run(
            {
                RecordInputSetContext(record): await self.input_set(record)
                async for record in self.sctx.records()
            },
            strict=not self.parent.config.no_strict,
        ):
            if result:
                ctx.record.evaluated(result)
            yield ctx.record

    async def __aenter__(self) -> "DataFlowPreprocessSourceContext":
        self.sctx = await self.parent.source().__aenter__()

        if isinstance(self.parent.config.dataflow, str):
            dataflow_path = pathlib.Path(self.parent.config.dataflow)
            config_type = dataflow_path.suffix.replace(".", "")
            config_cls = BaseConfigLoader.load(config_type)
            async with config_cls.withconfig({}) as configloader:
                async with configloader() as loader:
                    exported = await loader.loadb(dataflow_path.read_bytes())
                with self.parent.config.no_enforce_immutable():
                    self.parent.config.dataflow = DataFlow._fromdict(
                        **exported
                    )

        self.octx = await self.parent.orchestrator(
            self.parent.config.dataflow
        ).__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.octx.__aexit__(exc_type, exc_value, traceback)
        await self.sctx.__aexit__(exc_type, exc_value, traceback)


@entrypoint("dfpreprocess")
class DataFlowPreprocessSource(BaseSource):
    """
    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> records = [
    ...     Record(
    ...         "0",
    ...         data={
    ...             "features": {
    ...                 "Years": 1,
    ...                 "Expertise": 3,
    ...                 "Trust": 0.2,
    ...                 "Salary": 20,
    ...             }
    ...         },
    ...     ),
    ... ]
    >>>
    >>> features = Features(
    ...     Feature("Years", int, 1),
    ...     Feature("Expertise", int, 1),
    ...     Feature("Trust", float, 1),
    ...     Feature("Salary", int, 1),
    ... )
    >>>
    >>> dataflow = DataFlow(multiply, AssociateDefinition)
    >>> dataflow.flow["multiply"].inputs["multiplicand"] = [
    ...     {"seed": ["Years", "Expertise", "Trust", "Salary"]}
    ... ]
    >>> dataflow.seed = [
    ...     Input(
    ...         value={
    ...             feature.name: multiply.op.outputs["product"].name
    ...             for feature in features
    ...         },
    ...         definition=AssociateDefinition.op.inputs["spec"],
    ...     ),
    ...     Input(value=10, definition=multiply.op.inputs["multiplier"],),
    ... ]
    >>>
    >>>
    >>> memory_source = Sources(MemorySource(MemorySourceConfig(records=records)))
    >>>
    >>> source = DataFlowPreprocessSource(
    ...     DataFlowPreprocessSourceConfig(
    ...         source=memory_source, dataflow=dataflow, features=features,
    ...     )
    ... )
    >>>
    >>>
    >>> async def main():
    ...     async with source as src:
    ...         async with src() as sctx:
    ...             async for record in sctx.records():
    ...                 print(record.features())
    ...
    >>>
    >>> asyncio.run(main())
    {'Years': 10, 'Expertise': 30, 'Trust': 2.0, 'Salary': 200}
    """

    CONFIG = DataFlowPreprocessSourceConfig
    CONTEXT = DataFlowPreprocessSourceContext

    async def __aenter__(self) -> "DataFlowPreprocessSource":
        self.source = await self.config.source.__aenter__()
        self.orchestrator = await self.config.orchestrator.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.orchestrator.__aexit__(exc_type, exc_value, traceback)
        await self.source.__aexit__(exc_type, exc_value, traceback)
