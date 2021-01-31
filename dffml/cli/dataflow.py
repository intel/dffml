import pathlib
import hashlib
import contextlib
from typing import List, Dict, Any

from ..base import BaseConfig
from ..df.base import BaseOrchestrator, OperationImplementation
from ..df.types import DataFlow, Stage, Operation, Input, InputFlow
from ..df.exceptions import DefinitionNotFoundInDataFlow
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
from ..util.data import merge, split_dot_seperated, traverse_set
from ..util.entrypoint import load
from ..util.cli.cmd import CMD, CMDOutputOverride
from ..util.cli.cmds import (
    SourcesCMD,
    KeysCMD,
    KeysCMDConfig,
)
from ..util.cli.parser import ParseInputsAction
from ..base import config, field
from ..high_level import run as run_dataflow


@config
class MergeConfig:
    dataflows: List[pathlib.Path] = field("DataFlows to merge")
    configloader: BaseConfigLoader = field(
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
        async with self.configloader(BaseConfig()) as configloader:
            async with configloader() as loader:
                exported = dataflow.export(linked=not self.not_linked)
                print((await loader.dumpb(exported)).decode())


@config
class CreateConfig:
    operations: List[str] = field("Operations to create a dataflow for",)
    configloader: BaseConfigLoader = field(
        "ConfigLoader to use", default=JSONConfigLoader,
    )
    not_linked: bool = field(
        "Do not export dataflows as linked", default=False,
    )
    inputs: List[str] = field(
        "Inputs to be added to every context",
        action=ParseInputsAction,
        default_factory=lambda: [],
    )
    flow: List[str] = field(
        "Flow of inputs", action=ParseInputsAction, default_factory=lambda: [],
    )
    config: List[str] = field(
        "configs", action=ParseInputsAction, default_factory=lambda: [],
    )


class Create(CMD):

    CONFIG = CreateConfig

    async def run(self):
        operations = []
        operation_names = []
        for load_operation in self.operations:
            if "=" in load_operation:
                opname, operation = load_operation.split("=")
            else:
                opname = operation = load_operation
            operation_names.append(opname)
            if ":" in operation:
                operations.extend(
                    map(
                        OperationImplementation._imp,
                        load(operation, relative=True),
                    )
                )
            else:
                operations += [Operation.load(operation)]
        async with self.configloader(BaseConfig()) as configloader:
            async with configloader() as loader:
                dataflow = DataFlow(
                    operations=dict(zip(operation_names, operations))
                )
                # flow argument key is of the form opname.inputs/conditions.keyname
                for v, k in self.flow:
                    *opname, val_type, key = split_dot_seperated(k)
                    opname = ".".join(opname)
                    if val_type == "inputs":
                        dataflow.flow[opname].inputs[key] = v
                    else:
                        dataflow.flow[opname].conditions = v
                for v, k in self.config:
                    traverse_set(dataflow.configs, k, value=v)
                exported = dataflow.export(linked=not self.not_linked)
                if self.inputs:
                    if not "seed" in exported:
                        exported["seed"] = []
                    for val, input_info in self.inputs:
                        if "=" in input_info:
                            def_name, origin = input_info.split(
                                "=", maxsplit=1
                            )
                            # self.inputs is of the form val=def_name=origin
                            exported["seed"].append(
                                {
                                    "value": val,
                                    "definition": def_name,
                                    "origin": origin,
                                }
                            )
                        else:
                            # self.inputs is of the form val=def_name
                            exported["seed"].append(
                                {"value": val, "definition": input_info}
                            )
                print((await loader.dumpb(exported)).decode())


@config
class RunCMDConfig:
    dataflow: str = field(
        "File containing exported DataFlow", required=True,
    )
    configloader: BaseConfigLoader = field(
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
        config_cls = self.configloader
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


@config
class RunSingleConfig:
    dataflow: str = field(
        "File containing exported DataFlow", required=True,
    )
    no_echo: bool = field(
        "Do not echo back records", default=False,
    )
    configloader: BaseConfigLoader = field(
        "ConfigLoader to use for importing DataFlow", default=None,
    )
    orchestrator: BaseOrchestrator = field(
        "Orchestrator", default=MemoryOrchestrator,
    )
    inputs: List[str] = field(
        "Other inputs to add under each ctx",
        action=ParseInputsAction,
        default_factory=lambda: [],
    )
    no_strict: bool = field(
        "Do not exit on operation exceptions, just log errors", default=False,
    )


class RunSingle(CMD):
    CONFIG = RunSingleConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = self.orchestrator.withconfig(self.extra_config)

    async def get_dataflow(self, dataflow_path):
        dataflow_path = pathlib.Path(dataflow_path)
        config_cls = self.configloader
        if config_cls is None:
            config_type = dataflow_path.suffix.replace(".", "")
            config_cls = BaseConfigLoader.load(config_type)
        async with config_cls.withconfig(self.extra_config) as configloader:
            async with configloader() as loader:
                exported = await loader.loadb(dataflow_path.read_bytes())
                dataflow = DataFlow._fromdict(**exported)
        return dataflow

    def input_objects(self, dataflow):
        for value, def_name in self.inputs:
            if not def_name in dataflow.definitions:
                raise DefinitionNotFoundInDataFlow(
                    f"{def_name!r} not found in {list(dataflow.definitions.keys())}"
                )
            yield Input(value=value, definition=dataflow.definitions[def_name])

    async def run(self):
        dataflow = await self.get_dataflow(self.dataflow)
        async for ctx, results in run_dataflow(
            dataflow,
            list(self.input_objects(dataflow)),
            orchestrator=self.orchestrator,
            strict=not self.no_strict,
        ):
            if not self.no_echo:
                yield results
        if self.no_echo:
            yield CMDOutputOverride


@config
class RunContextsConfig(RunSingleConfig):
    context_def: str = field(
        "Definition to be used for contexts key. "
        + "If set, the key will be added to the set of inputs "
        + "under each context (which is also the contexts name)",
        default=False,
    )
    contexts: List[str] = field(
        "Contexts to run", default_factory=lambda: ["context1"], required=False
    )


class RunContexts(RunSingle):
    CONFIG = RunContextsConfig

    async def run(self):
        dataflow = await self.get_dataflow(self.dataflow)

        common_inputs = list(self.input_objects(dataflow))

        if not self.context_def in dataflow.definitions:
            raise DefinitionNotFoundInDataFlow(
                f"{self.context_def!r} not found in {list(dataflow.definitions.keys())}"
            )

        dataflow_inputs = {
            ctx_string: [
                Input(
                    value=ctx_string,
                    definition=dataflow.definitions[self.context_def],
                )
            ]
            + common_inputs
            for ctx_string in self.contexts
        }

        async for ctx, result in run_dataflow(
            dataflow,
            dataflow_inputs,
            orchestrator=self.orchestrator,
            strict=not self.no_strict,
        ):
            if not self.no_echo:
                yield {(await ctx.handle()).as_string(): result}
        if self.no_echo:
            yield CMDOutputOverride


class Run(CMD):
    """Run dataflow"""

    single = RunSingle
    contexts = RunContexts
    records = RunRecords


@config
class DiagramConfig:
    dataflow: str = field("File containing exported DataFlow")
    configloader: BaseConfigLoader = field(
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
        config_cls = self.configloader
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
                        print(
                            f"{seed_input_node}({source}<br>{input_definition.name})"
                        )
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
                    elif isinstance(source, dict) and isinstance(
                        list(source.values())[0], list
                    ):
                        # Handle the case where the key is the origin (so
                        # something like "seed") and the value is a list of
                        # acceptable definitions from that origin.
                        origin, definition_names = list(source.items())[0]
                        for definition_name in definition_names:
                            origin_definition_name = (
                                origin + "." + definition_name
                            )
                            seed_input_node = hashlib.md5(
                                origin_definition_name.encode()
                            ).hexdigest()
                            print(
                                f"{seed_input_node}({source}<br>{origin_definition_name})"
                            )
                            if len(self.stages) == 1:
                                print(
                                    f"style {seed_input_node} fill:#f6dbf9,stroke:#a178ca"
                                )
                            if not self.simple:
                                input_node = hashlib.md5(
                                    (
                                        "input."
                                        + instance_name
                                        + "."
                                        + input_name
                                    ).encode()
                                ).hexdigest()
                                print(f"{seed_input_node} --> {input_node}")
                            else:
                                print(f"{seed_input_node} --> {node}")
                    else:
                        # In order to support selection an input based using an
                        # alternate definition along with restriction to inputs
                        # who's origins match the alternate definitions in the
                        # list. We select the first output source since that
                        # will be the immediate alternate definition
                        if (
                            isinstance(source, list)
                            and source
                            and isinstance(source[0], dict)
                        ):
                            source = source[0]
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
            for i, condition in enumerate(input_flow.conditions):
                if isinstance(condition, str):
                    if not self.simple:
                        condition_name = operation.conditions[i].name
                        seed_condition_node = hashlib.md5(
                            (condition + "." + condition_name).encode()
                        ).hexdigest()
                        print(f"{seed_condition_node}({condition_name})")
                        seed_dependent_node = hashlib.md5(
                            (
                                "condition."
                                + instance_name
                                + "."
                                + condition_name
                            ).encode()
                        ).hexdigest()
                        print(
                            f"{seed_condition_node} --> {seed_dependent_node}"
                        )
                else:
                    if not self.simple:
                        dependee_node = hashlib.md5(
                            (
                                "output."
                                + ".".join(list(condition.items())[0])
                            ).encode()
                        ).hexdigest()
                        dependent_node = hashlib.md5(
                            (
                                "condition."
                                + instance_name
                                + "."
                                + dataflow.operations[
                                    list(condition.keys())[0]
                                ]
                                .outputs[list(condition.values())[0]]
                                .name
                            ).encode()
                        ).hexdigest()
                        print(f"{dependee_node} --> {dependent_node}")
                    else:
                        dependee_operation_node = hashlib.md5(
                            list(condition.keys())[0].encode()
                        ).hexdigest()
                        print(f"{dependee_operation_node} --> {node}")
        if len(self.stages) != 1:
            print(f"end")


# Name collision
class Dataflow(CMD):

    merge = Merge
    create = Create
    run = Run
    diagram = Diagram
