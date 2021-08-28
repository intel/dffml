import pathlib
from typing import AsyncIterator, List

from ..base import config, field
from ..configloader.configloader import BaseConfigLoader
from ..df.types import DataFlow, Input
from ..df.base import BaseOrchestrator
from ..feature import Features
from ..record import Record
from ..source.source import BaseSource, BaseSourceContext
from ..util.entrypoint import entrypoint
from ..util.cli.parser import ParseInputsAction
from ..df.memory import MemoryOrchestrator


@config
class DataFlowSourceConfig:
    source: BaseSource = field("Source to wrap")
    dataflow: DataFlow = field("DataFlow to use for preprocessing")
    features: Features = field(
        "Features to pass as definitions to each context from each "
        "record to be preprocessed",
        default=Features(),
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
        "Orchestrator", default=MemoryOrchestrator.withconfig({}),
    )


class DataFlowSourceContext(BaseSourceContext):
    async def update(self):
        raise NotImplementedError

    async def record(self, key: str) -> AsyncIterator[Record]:
        raise NotImplementedError

    async def records(self) -> AsyncIterator[Record]:
        async for ctx, result in self.octx.run(
            [
                Input(
                    value=value,
                    definition=self.parent.config.dataflow.definitions[name],
                )
                for value, name in self.parent.config.inputs
            ],
            strict=not self.parent.config.no_strict,
        ):
            if result:
                # result is a dict having single key, value as the row data
                for key, data in result["records"].items():
                    yield Record(
                        key=key, data=data,
                    )

    async def __aenter__(self) -> "DataFlowPreprocessSourceContext":
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

    async def __aenter__(self) -> "DataFlowSource":
        self.source = await self.config.source.__aenter__()
        self.orchestrator = await self.config.orchestrator.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.orchestrator.__aexit__(exc_type, exc_value, traceback)
        await self.source.__aexit__(exc_type, exc_value, traceback)
