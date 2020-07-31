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
    >>> dataflow = DataFlow.auto(multiply, AssociateDefinition)
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
    >>> source = DataFlowSource(
    ...     DataFlowSourceConfig(
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
