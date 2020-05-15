from typing import Type, AsyncIterator

from dffml.base import config, BaseConfig
from dffml.df.types import Definition, DataFlow, Input
from dffml.feature import Features
from dffml.record import Record
from dffml.source.source import BaseSource, BaseSourceContext
from dffml.util.entrypoint import entrypoint
from dffml.df.memory import MemoryOrchestrator


@config
class DataFlowSourceConfig(BaseConfig):
    source: BaseSource
    dataflow: DataFlow
    features: Features


class DataFlowSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        self.sctx.update(record)

    async def records(self) -> AsyncIterator[Record]:
        async for record in self.sctx.records():
            async for ctx, result in MemoryOrchestrator.run(
                self.parent.config.dataflow,
                [
                    Input(
                        value=record.feature(feature.NAME),
                        definition=Definition(
                            name=feature.NAME, primitive=str(feature.dtype())
                        ),
                    )
                    for feature in self.parent.config.features
                ],
            ):
                if result:
                    record.evaluated(result)
                yield record

    async def __aenter__(self) -> "DataFlowSourceContext":
        self.sctx = await self.parent.source().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.sctx.__aexit__(exc_type, exc_value, traceback)


@entrypoint("df")
class DataFlowSource(BaseSource):
    CONFIG = DataFlowSourceConfig
    CONTEXT = DataFlowSourceContext

    def __init__(self, cnfg: Type[BaseConfig]) -> None:
        super().__init__(cnfg)

    async def __aenter__(self) -> "DataFlowSource":
        self.source = await self.config.source.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.source.__aexit__(exc_type, exc_value, traceback)
