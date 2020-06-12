import pathlib
from typing import Type, AsyncIterator

from dffml.base import config, BaseConfig
from dffml.configloader.configloader import BaseConfigLoader
from dffml.df.types import Definition, DataFlow, Input
from dffml.df.base import BaseOrchestrator
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
    orchestrator: BaseOrchestrator = MemoryOrchestrator.withconfig({})


class DataFlowSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        await self.sctx.update(record)

    async def records(self) -> AsyncIterator[Record]:
        async for record in self.sctx.records():
            async for ctx, result in self.octx.run(
                [
                    Input(
                        value=record.feature(feature.name),
                        definition=Definition(
                            name=feature.name, primitive=str(feature.dtype())
                        ),
                    )
                    for feature in self.parent.config.features
                ]
            ):
                if result:
                    record.evaluated(result)
                yield record

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
