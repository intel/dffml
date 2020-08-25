import pathlib
from typing import Type, AsyncIterator, Dict, Any

from dffml.base import config, BaseConfig, field
from dffml.configloader.configloader import BaseConfigLoader
from dffml.df.types import Definition, DataFlow, Input, Operation
from dffml.df.base import BaseInputSetContext, BaseContextHandle
from dffml.df.base import (
    BaseOrchestrator,
    OperationImplementationContext,
    OperationImplementation,
)
from dffml.feature import Features
from dffml.record import Record
from dffml.source.source import BaseSource, BaseSourceContext
from dffml.util.entrypoint import entrypoint
from dffml.df.memory import MemoryOrchestrator


@config
class DataFlowSourceConfig:
    source: BaseSource
    dataflow: DataFlow
    features: Features
    length: str = field(
        "Definition name to add as source length", default=None
    )
    all_for_single: bool = False
    get_single_output: bool = True
    orchestrator: BaseOrchestrator = MemoryOrchestrator.withconfig({})


class RecordContextHandle(BaseContextHandle):
    def as_string(self) -> str:
        return self.ctx.record.key


class RecordInputSetContext(BaseInputSetContext):
    def __init__(self, record: Record):
        self.record = record

    async def handle(self) -> BaseContextHandle:
        return RecordContextHandle(self)

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return repr(self)


class DataFlowSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        await self.sctx.update(record)

    # TODO Implement this method. We forgot to implement it when we initially
    # added the DataFlowSourceContext
    async def record(self, key: str) -> AsyncIterator[Record]:
        if self.parent.config.all_for_single:
            async for ctx, result in self.records():
                if (await ctx.handle()).as_string() == key:
                    yield record
        else:
            async for ctx, result in self.octx.run(
                {
                    RecordInputSetContext(record): [
                        Input(
                            value=record.feature(feature.name),
                            definition=Definition(
                                name=feature.name,
                                primitive=str(feature.dtype()),
                            ),
                        )
                        for feature in self.parent.config.features
                    ]
                    + (
                        []
                        if not self.parent.config.length
                        else [
                            Input(
                                value=await self.sctx.length(),
                                definition=Definition(
                                    name=self.parent.config.length,
                                    primitive="int",
                                ),
                            )
                        ]
                    )
                    async for record in [self.sctx.record(key)]
                }
            ):
                if result:
                    ctx.record.evaluated(result)
                yield ctx.record

    async def records(self) -> AsyncIterator[Record]:
        async for ctx, result in self.octx.run(
            {
                RecordInputSetContext(record): [
                    Input(
                        value=record.feature(feature.name),
                        definition=Definition(
                            name=feature.name, primitive=str(feature.dtype())
                        ),
                    )
                    for feature in self.parent.config.features
                ]
                + (
                    []
                    if not self.parent.config.length
                    else [
                        Input(
                            value=await self.sctx.length(),
                            definition=Definition(
                                name=self.parent.config.length, primitive="int"
                            ),
                        )
                    ]
                )
                async for record in self.sctx.records()
            }
        ):
            if result:
                ctx.record.evaluated(result)
            yield ctx.record

    async def __aenter__(self) -> "DataFlowSourceContext":
        self.sctx = await self.parent.source().__aenter__()

        if isinstance(self.parent.config.dataflow, str):
            dataflow_path = pathlib.Path(self.parent.config.dataflow)
            config_type = dataflow_path.suffix.replace(".", "")
            config_cls = BaseConfigLoader.load(config_type)
            async with config_cls.withconfig({}) as configloader:
                async with configloader() as loader:
                    exported = await loader.loadb(dataflow_path.read_bytes())
                self.parent.config.dataflow = DataFlow._fromdict(**exported)

        self.octx = await self.parent.orchestrator(
            self.parent.config.dataflow
        ).__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.octx.__aexit__(exc_type, exc_value, traceback)
        await self.sctx.__aexit__(exc_type, exc_value, traceback)


@entrypoint("df")
class DataFlowSource(BaseSource):
    CONFIG = DataFlowSourceConfig
    CONTEXT = DataFlowSourceContext

    def __init__(self, cnfg: Type[BaseConfig]) -> None:
        super().__init__(cnfg)

    async def __aenter__(self) -> "DataFlowSource":
        self.source = await self.config.source.__aenter__()
        self.orchestrator = await self.config.orchestrator.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.orchestrator.__aexit__(exc_type, exc_value, traceback)
        await self.source.__aexit__(exc_type, exc_value, traceback)
