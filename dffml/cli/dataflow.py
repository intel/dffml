import pathlib
import hashlib
import contextlib
from typing import List

from ..base import BaseConfig
from ..df.base import BaseOrchestrator, OperationImplementation
from ..df.types import DataFlow, Stage, Operation, Input
from ..df.memory import (
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
    StringInputSetContext,
)
from ..configloader.configloader import BaseConfigLoader
from ..configloader.json import JSONConfigLoader
from ..source.source import SubsetSources, Sources
from ..source.json import JSONSource
from ..source.file import FileSourceConfig
from ..util.data import merge
from ..util.entrypoint import load
from ..util.cli.cmd import CMD, CMDOutputOverride
from ..util.cli.cmds import (
    SourcesCMD,
    KeysCMD,
    KeysCMDConfig,
)
from ..util.cli.parser import ParseInputsAction
from ..base import config, field


@config
class MergeConfig:
    dataflows: List[pathlib.Path] = field("DataFlows to merge")
    config: BaseConfigLoader = field(
        "ConfigLoader to use for exporting", default=JSONConfigLoader,
    )
    not_linked: bool = field(
        "Do not export dataflows as linked", default=False,
    )


class Merge(CMD):

    CONFIG = MergeConfig

    async def run(self):
        # The merged dataflow
        merged: Dict[str, Any] = {}
        # For entering ConfigLoader contexts
        async with contextlib.AsyncExitStack() as exit_stack:
            # Load config loaders we'll need as we see their file types
            parsers: Dict[str, BaseConfigLoader] = {}
            for path in self.dataflows:
                _, exported = await BaseConfigLoader.load_file(
                    parsers, exit_stack, path
                )
                merge(merged, exported, list_append=True)
        # Export the dataflow
        dataflow = DataFlow._fromdict(**merged)
        async with self.config(BaseConfig()) as configloader:
            async with configloader() as loader:
                exported = dataflow.export(linked=not self.not_linked)
                print((await loader.dumpb(exported)).decode())


@config
class CreateConfig:
    operations: List[str] = field("Operations to create a dataflow for",)
    config: BaseConfigLoader = field(
        "ConfigLoader to use", default=JSONConfigLoader,
    )
    not_linked: bool = field(
        "Do not export dataflows as linked", default=False,
    )
    seed: List[str] = field(
        "Inputs to be added to every context",
        action=ParseInputsAction,
        default_factory=lambda: [],
    )


class Create(CMD):

    CONFIG = CreateConfig

    async def run(self):
        operations = []
        for load_operation in self.operations:
            if ":" in load_operation:
                operations.extend(
                    map(
                        OperationImplementation._imp,
                        load(load_operation, relative=True),
                    )
                )
            else:
                operations += [Operation.load(load_operation)]
        async with self.config(BaseConfig()) as configloader:
            async with configloader() as loader:
                dataflow = DataFlow.auto(*operations)
                self.seed = [
                    Input(value=val, definition=dataflow.definitions[def_name])
                    for val, def_name in self.seed
                ]
                dataflow.seed.extend(self.seed)
                exported = dataflow.export(linked=not self.not_linked)
                print((await loader.dumpb(exported)).decode())


@config
class RunCMDConfig:
    dataflow: str = field(
        "File containing exported DataFlow", required=True,
    )
    config: BaseConfigLoader = field(
        "ConfigLoader to use for importing DataFlow", default=None,
    )
    sources: Sources = field(
        "Sources for loading and saving",
        default_factory=lambda: Sources(
            JSONSource(
                FileSourceConfig(
                    filename=pathlib.Path("~", ".cache", "dffml.json")
                )
            )
        ),
        labeled=True,
    )
    caching: List[str] = field(
        "Skip running DataFlow if a record already contains these features",
        default_factory=lambda: [],
    )
    no_update: bool = field(
        "Update record with sources", default=False,
    )
    no_echo: bool = field(
        "Do not echo back records", default=False,
    )
    no_strict: bool = field(
        "Do not exit on operation exceptions, just log errors", default=False,
    )
    orchestrator: BaseOrchestrator = field(
        "Orchestrator", default=MemoryOrchestrator,
    )
    inputs: List[str] = field(
        "Other inputs to add under each ctx (record's key will "
        + "be used as the context)",
        action=ParseInputsAction,
        default_factory=lambda: [],
    )
    record_def: str = field(
        "Definition to be used for record.key."
        + "If set, record.key will be added to the set of inputs "
        + "under each context (which is also the record's key)",
        default=False,
    )


class RunCMD(SourcesCMD):

    CONFIG = RunCMDConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = self.orchestrator.withconfig(self.extra_config)


@config
class RunAllRecordsConfig(RunCMDConfig):
    pass


class RunAllRecords(RunCMD):
    """Run dataflow for all records in sources"""

    CONFIG = RunAllRecordsConfig

    async def records(self, sctx):
        """
        This method exists so that it can be overriden by RunRecordSet
        """
        async for record in sctx.records():
            yield record

    async def run_dataflow(self, orchestrator, sources, dataflow):
        # Orchestrate the running of these operations
        async with orchestrator(dataflow) as octx, sources() as sctx:
            # Add our inputs to the input network with the context being the
            # record key
            inputs = []
            async for record in self.records(sctx):
                # Skip running DataFlow if record already has features
                existing_features = record.features()
                if self.caching and all(
                    map(
                        lambda cached: cached in existing_features,
                        self.caching,
                    )
                ):
                    continue

                record_inputs = []
                for value, def_name in self.inputs:
                    record_inputs.append(
                        Input(
                            value=value,
                            definition=dataflow.definitions[def_name],
                        )
                    )
                if self.record_def:
                    record_inputs.append(
                        Input(
                            value=record.key,
                            definition=dataflow.definitions[self.record_def],
                        )
                    )

                # TODO(p1) When OrchestratorContext is fixed to accept an
                # asyncgenerator we won't have to build a list
                inputs.append(
                    MemoryInputSet(
                        MemoryInputSetConfig(
                            ctx=StringInputSetContext(record.key),
                            inputs=record_inputs,
                        )
                    )
                )

            if not inputs:
                return

            async for ctx, results in octx.run(
                *inputs, strict=not self.no_strict
            ):
                ctx_str = (await ctx.handle()).as_string()
                # TODO(p4) Make a RecordInputSetContext which would let us
                # store the record instead of recalling it by the URL
                record = await sctx.record(ctx_str)
                # Store the results
                record.evaluated(results)
                yield record
                if not self.no_update:
                    await sctx.update(record)

    async def run(self):
        dataflow_path = pathlib.Path(self.dataflow)
        config_cls = self.config
        if config_cls is None:
            config_type = dataflow_path.suffix.replace(".", "")
            config_cls = BaseConfigLoader.load(config_type)
        async with config_cls.withconfig(self.extra_config) as configloader:
            async with configloader() as loader:
                exported = await loader.loadb(dataflow_path.read_bytes())
                dataflow = DataFlow._fromdict(**exported)
        async with self.orchestrator as orchestrator, self.sources as sources:
            async for record in self.run_dataflow(
                orchestrator, sources, dataflow
            ):
                if not self.no_echo:
                    yield record
        if self.no_echo:
            yield CMDOutputOverride


@config
class RunRecordSetConfig(RunAllRecordsConfig, KeysCMDConfig):
    pass


class RunRecordSet(RunAllRecords, KeysCMD):
    """Run dataflow for single record or set of records"""

    CONFIG = RunRecordSetConfig

    async def records(self, sctx):
        for key in self.keys:
            yield await sctx.record(key)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class RunRecords(CMD):
    """Run DataFlow and assign output to a record"""

    _set = RunRecordSet
    _all = RunAllRecords


class Run(CMD):
    """Run dataflow"""

    records = RunRecords


@config
class DiagramConfig:
    dataflow: str = field("File containing exported DataFlow")
    config: BaseConfigLoader = field(
        "ConfigLoader to use for importing DataFlow", default=None,
    )
    stages: List[str] = field(
        "Which stages to display: (processing, cleanup, output)",
        default_factory=lambda: [],
    )
    simple: bool = field("Don't display input and output names", default=False)
    display: str = field(
        "How to display (TD: top down, LR, RL, BT)", default="TD",
    )


class Diagram(CMD):

    CONFIG = DiagramConfig

    async def run(self):
        dataflow_path = pathlib.Path(self.dataflow)
        config_cls = self.config
        if config_cls is None:
            config_type = dataflow_path.suffix.replace(".", "")
            config_cls = BaseConfigLoader.load(config_type)
        async with config_cls.withconfig(self.extra_config) as configloader:
            async with configloader() as loader:
                exported = await loader.loadb(dataflow_path.read_bytes())
                dataflow = DataFlow._fromdict(**exported)
        print(f"graph {self.display}")
        for stage in Stage:
            # Skip stage if not wanted
            if self.stages and stage.value not in self.stages:
                continue
            stage_node = hashlib.md5(
                ("stage." + stage.value).encode()
            ).hexdigest()
            if len(self.stages) != 1:
                print(f"subgraph {stage_node}[{stage.value.title()} Stage]")
                print(f"style {stage_node} fill:#afd388b5,stroke:#a4ca7a")
            for instance_name, operation in dataflow.operations.items():
                if operation.stage != stage:
                    continue
                subgraph_node = hashlib.md5(
                    ("subgraph." + instance_name).encode()
                ).hexdigest()
                node = hashlib.md5(instance_name.encode()).hexdigest()
                if not self.simple:
                    print(f"subgraph {subgraph_node}[{instance_name}]")
                    print(f"style {subgraph_node} fill:#fff4de,stroke:#cece71")
                print(f"{node}[{operation.instance_name}]")
                for input_name in operation.inputs.keys():
                    input_node = hashlib.md5(
                        ("input." + instance_name + "." + input_name).encode()
                    ).hexdigest()
                    if not self.simple:
                        print(f"{input_node}({input_name})")
                        print(f"{input_node} --> {node}")
                for output_name in operation.outputs.keys():
                    output_node = hashlib.md5(
                        (
                            "output." + instance_name + "." + output_name
                        ).encode()
                    ).hexdigest()
                    if not self.simple:
                        print(f"{output_node}({output_name})")
                        print(f"{node} --> {output_node}")
                for condition in operation.conditions:
                    condition_node = hashlib.md5(
                        (
                            "condition." + instance_name + "." + condition.name
                        ).encode()
                    ).hexdigest()
                    if not self.simple:
                        print(f"{condition_node}{'{' + condition.name + '}'}")
                        print(f"{condition_node} --> {node}")
                if not self.simple:
                    print(f"end")
            if len(self.stages) != 1:
                print(f"end")
        if len(self.stages) != 1:
            print(f"subgraph inputs[Inputs]")
            print(f"style inputs fill:#f6dbf9,stroke:#a178ca")
        for instance_name, input_flow in dataflow.flow.items():
            operation = dataflow.operations[instance_name]
            if self.stages and not operation.stage.value in self.stages:
                continue
            node = hashlib.md5(instance_name.encode()).hexdigest()
            for input_name, sources in input_flow.inputs.items():
                for source in sources:
                    # TODO Put various sources in their own "Inputs" subgraphs
                    if isinstance(source, str):
                        input_definition = operation.inputs[input_name]
                        seed_input_node = hashlib.md5(
                            (source + "." + input_definition.name).encode()
                        ).hexdigest()
                        print(f"{seed_input_node}({input_definition.name})")
                        if len(self.stages) == 1:
                            print(
                                f"style {seed_input_node} fill:#f6dbf9,stroke:#a178ca"
                            )
                        if not self.simple:
                            input_node = hashlib.md5(
                                (
                                    "input." + instance_name + "." + input_name
                                ).encode()
                            ).hexdigest()
                            print(f"{seed_input_node} --> {input_node}")
                        else:
                            print(f"{seed_input_node} --> {node}")
                    else:
                        if not self.simple:
                            source_output_node = hashlib.md5(
                                (
                                    "output."
                                    + ".".join(list(source.items())[0])
                                ).encode()
                            ).hexdigest()
                            input_node = hashlib.md5(
                                (
                                    "input." + instance_name + "." + input_name
                                ).encode()
                            ).hexdigest()
                            print(f"{source_output_node} --> {input_node}")
                        else:
                            source_operation_node = hashlib.md5(
                                list(source.keys())[0].encode()
                            ).hexdigest()
                            print(f"{source_operation_node} --> {node}")
        if len(self.stages) != 1:
            print(f"end")


# Name collision
class Dataflow(CMD):

    merge = Merge
    create = Create
    run = Run
    diagram = Diagram
