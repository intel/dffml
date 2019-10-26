import uuid
import copy
import pydoc
import inspect
import itertools
import pkg_resources
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import (
    NamedTuple,
    Union,
    List,
    Dict,
    Optional,
    Any,
    Iterator,
    Callable,
    Tuple,
)

from ..base import BaseConfig
from ..util.data import export_dict, type_lookup
from ..util.entrypoint import Entrypoint, base_entry_point


class DefinitionMissing(Exception):
    """
    Definition missing from linked DataFlow
    """


class Definition(NamedTuple):
    """
    List[type] is how to specify a list
    """

    name: str
    primitive: str
    lock: bool = False
    # spec is a NamedTuple which could be populated via a dict
    spec: NamedTuple = None

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)

    def export(self):
        exported = dict(self._asdict())
        if not self.lock:
            del exported["lock"]
        if not self.spec:
            del exported["spec"]
        else:
            exported["spec"] = export_dict(
                name=self.spec.__qualname__,
                types=self.spec._field_types,
                defaults=self.spec._field_defaults,
            )
        return exported

    @classmethod
    def _fromdict(cls, **kwargs):
        # TODO(p5) We should avoid coping here, i think
        kwargs = copy.deepcopy(kwargs)
        if "spec" in kwargs:
            # Alright this is horrible. But bear with me here. The
            # typing.NamedTuple API as of 3.7 does not provide a clean way to
            # create a new NamedTuple class where you specify the type hinting
            # and the default values. The following is based on looking at the
            # soruce code
            # https://github.com/python/cpython/blob/3.7/Lib/typing.py#L1360
            # and seeing that we can hijack the __annotations__ property to
            # allow us to set default values
            def_tuple = kwargs["spec"]["defaults"]
            annotations = {}
            for key, typename in kwargs["spec"]["types"].items():
                annotations[key] = cls.type_lookup(typename)
            def_tuple["__annotations__"] = annotations
            kwargs["spec"] = type(
                kwargs["spec"]["name"], (NamedTuple,), def_tuple
            )
        return cls(**kwargs)

    @classmethod
    def type_lookup(cls, typename):
        # Allowlist of non-python builtin types
        if typename in ["Definition"]:
            # TODO More types
            return cls
        return type_lookup(typename)


class Stage(Enum):
    PROCESSING = "processing"
    CLEANUP = "cleanup"
    OUTPUT = "output"


class FailedToLoadOperation(Exception):
    """
    Raised when an Operation wasn't found to be registered with the
    dffml.operation entrypoint.
    """


@base_entry_point("dffml.operation", "operation")
class Operation(NamedTuple, Entrypoint):
    name: str
    inputs: Dict[str, Definition]
    outputs: Dict[str, Definition]
    stage: Stage = Stage.PROCESSING
    conditions: Optional[List[Definition]] = []
    expand: Optional[List[str]] = []
    instance_name: Optional[str] = None

    def export(self):
        exported = {
            "name": self.name,
            "inputs": self.inputs.copy(),
            "outputs": self.outputs.copy(),
            "conditions": self.conditions.copy(),
            "stage": self.stage.value,
            "expand": self.expand.copy(),
        }
        for to_string in ["conditions"]:
            exported[to_string] = list(
                map(lambda definition: definition.name, exported[to_string])
            )
        for to_string in ["inputs", "outputs"]:
            exported[to_string] = dict(
                map(
                    lambda key_def: (key_def[0], key_def[1].export()),
                    exported[to_string].items(),
                )
            )
        if not exported["conditions"]:
            del exported["conditions"]
        if not exported["expand"]:
            del exported["expand"]
        return exported

    @classmethod
    def definitions(cls, *args: "Operation"):
        """
        Create key value mapping of definition names to definitions for all
        given operations.
        """
        definitions = {}
        for op in args:
            for has_definition in ["inputs", "outputs"]:
                for definition in getattr(op, has_definition, {}).values():
                    definitions[definition.name] = definition
            for has_definition in ["conditions"]:
                for definition in getattr(op, has_definition, []):
                    definitions[definition.name] = definition
        return definitions

    @classmethod
    def load(cls, loading=None):
        loading_classes = []
        # Load operations
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            if loading is not None and i.name == loading:
                loaded = i.load()
                if isinstance(loaded, cls):
                    return loaded
                elif isinstance(getattr(loaded, "op", None), cls):
                    # Handle operations decorated with op
                    return loaded.op
            else:
                loaded = i.load()
                loading_classes.append(loaded)
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            if loading is not None and i.name == loading:
                return i.load()
            else:
                loading_classes.append(loaded)
        if loading is not None:
            raise KeyError(
                "%s was not found in (%s)"
                % (
                    repr(loading),
                    ", ".join(list(map(lambda op: op.name, loading_classes))),
                )
            )
        return loading_classes

    @classmethod
    def _op(cls, loaded):
        """
        Returns the operation from a loaded entrypoint object, or None if its
        not an operation or doesn't have the op parameter which is an operation.
        """
        for obj in [loaded, getattr(loaded, "op", None)]:
            if isinstance(obj, cls):
                return obj
        return None

    @classmethod
    def load(cls, loading=None):
        loading_classes = []
        # Load operations
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            if loading is not None and i.name == loading:
                loaded = cls._op(i.load())
                if loaded is not None:
                    return loaded
            elif loading is None:
                loaded = cls._op(i.load())
                if loaded is not None:
                    loading_classes.append(loaded)
        if loading is not None:
            raise FailedToLoadOperation(
                "%s was not found in (%s)"
                % (
                    repr(loading),
                    ", ".join(list(map(lambda op: op.name, loading_classes))),
                )
            )
        return loading_classes

    @classmethod
    def _fromdict(cls, **kwargs):
        for prop in ["inputs", "outputs"]:
            if not prop in kwargs:
                continue
            kwargs[prop] = {
                argument_name: Definition._fromdict(**definition)
                for argument_name, definition in kwargs[prop].items()
            }
        for prop in ["conditions"]:
            if not prop in kwargs:
                continue
            kwargs[prop] = [
                Definition._fromdict(**definition)
                for definition in kwargs[prop]
            ]
        if "stage" in kwargs:
            kwargs["stage"] = Stage[kwargs["stage"].upper()]
        return cls(**kwargs)


class Output(NamedTuple):
    name: str
    select: List[Definition]
    fill: Any
    single: bool = False
    ismap: bool = False


class Input(object):
    """
    All inputs have a unique id. Without it they can't be tracked for locking
    purposes.
    """

    def __init__(
        self,
        value: Any,
        definition: Definition,
        parents: Optional[List["Input"]] = None,
        origin: Optional[Union[str, Tuple[Operation, str]]] = "seed",
        *,
        uid: Optional[str] = "",
    ):
        # TODO Add optional parameter Input.target which specifies the operation
        # instance name this Input is intended for.
        if parents is None:
            parents = []
        self.value = value
        self.definition = definition
        self.parents = parents
        self.origin = origin
        self.uid = uid
        if not self.uid:
            self.uid = str(uuid.uuid4())

    def get_parents(self) -> Iterator["Input"]:
        return list(
            set(
                itertools.chain(
                    *[
                        [item] + list(set(item.get_parents()))
                        for item in self.parents
                    ]
                )
            )
        )

    def __repr__(self):
        return f"Input(value={self.value}, definition={self.definition})"

    def __str__(self):
        return repr(self)

    def export(self):
        return dict(value=self.value, definition=self.definition.export())

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["definition"] = Definition._fromdict(**kwargs["definition"])
        return cls(**kwargs)


class Parameter(NamedTuple):
    key: str
    value: Any
    origin: Input
    definition: Definition


@dataclass
class InputFlow:
    """
    Inputs of an operation by their name as used by the operation implementation
    mapped to a list of locations they can come from. The list contains strings
    in the format of operation_instance_name.key_in_output_mapping or the
    literal "seed" which specifies that the value could be seeded to the
    network.
    """

    inputs: Dict[str, List[Dict[str, Operation]]] = field(default=None)
    conditions: List[Dict[str, Operation]] = field(default=None)

    def __post_init__(self):
        if self.inputs is None:
            self.inputs = {}
        if self.conditions is None:
            self.conditions = []

    def export(self):
        exported = export_dict(**asdict(self))
        if not exported["conditions"]:
            del exported["conditions"]
        return exported

    @classmethod
    def _fromdict(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class DataFlow:
    operations: Dict[str, Union[Operation, Callable]]
    seed: List[Input] = field(default=None)
    configs: Dict[str, BaseConfig] = field(default=None)
    definitions: Dict[str, Definition] = field(init=False)
    flow: Dict[str, InputFlow] = field(default=None)
    by_origin: Dict[Stage, Dict[str, Operation]] = field(default=None)
    # Implementations can be provided in case they haven't been registered via
    # the entrypoint system.
    implementations: Dict[str, "OperationImplementation"] = field(default=None)

    def __post_init__(self):
        # Prevent usage of a global dict (if we set default to {} then all the
        # instances will share the same instance of that dict, or list)
        if self.seed is None:
            self.seed = []
        if self.configs is None:
            self.configs = {}
        if self.by_origin is None:
            self.by_origin = {}
        if self.implementations is None:
            self.implementations = {}
        # Allow callers to pass in functions decorated with op. Iterate over the
        # given operations and replace any which have been decorated with their
        # operation. Add the implementation to our dict of implementations.
        for instance_name, value in self.operations.items():
            # TODO(p4) We can't do isinstance because its defined in base, maybe
            # we should move it in here. This is a hack.
            is_opimp_non_decorated = bool(
                getattr(value, "ENTRY_POINT_NAME", ["not-opimp"]) == ["opimp"]
            )
            if (
                getattr(value, "imp", None) is not None
                or is_opimp_non_decorated
            ) and getattr(value, "op", None) is not None:
                # Get the operation and implementation from the wrapped object
                operation = getattr(value, "op", None)
                opimp = (
                    value
                    if is_opimp_non_decorated
                    else getattr(value, "imp", None)
                )
                # Set the implementation if not explicitly set
                self.implementations.setdefault(operation.name, opimp)
                # Change this entry to the instance of Operation associated with
                # the wrapped object
                self.operations[instance_name] = operation
                value = operation
            # Make sure every operation has the correct instance name
            self.operations[instance_name] = value._replace(
                instance_name=instance_name
            )
        # Grab all definitions from operations
        operations = list(self.operations.values())
        definitions = list(
            set(
                itertools.chain(
                    *[
                        itertools.chain(
                            operation.inputs.values(),
                            operation.outputs.values(),
                            operation.conditions,
                        )
                        for operation in operations
                    ]
                )
            )
        )
        definitions = {
            definition.name: definition for definition in definitions
        }
        self.definitions = definitions
        # Determine the dataflow if not given
        if self.flow is None:
            self.flow = self.auto_flow()
        # Create by_origin which maps operation instance names to the sources
        self.by_origin = {}
        for instance_name, input_flow in self.flow.items():
            operation = self.operations[instance_name]
            self.by_origin.setdefault(operation.stage, {})
            # TODO(p5) Make stanardize this so that seed is also a dict?
            for output_source in input_flow.conditions:
                if isinstance(output_source, str):
                    self.by_origin[operation.stage].setdefault(
                        output_source, []
                    )
                    self.by_origin[operation.stage][output_source].append(
                        operation
                    )
                else:
                    for origin in output_source.items():
                        self.by_origin[operation.stage].setdefault(origin, [])
                        self.by_origin[operation.stage][origin].append(
                            operation
                        )
            for output_name, output_sources in input_flow.inputs.items():
                for output_source in output_sources:
                    if isinstance(output_source, str):
                        self.by_origin[operation.stage].setdefault(
                            output_source, []
                        )
                        self.by_origin[operation.stage][output_source].append(
                            operation
                        )
                    else:
                        for origin in output_source.items():
                            self.by_origin[operation.stage].setdefault(
                                origin, []
                            )
                            self.by_origin[operation.stage][origin].append(
                                operation
                            )

    def export(self, *, linked: bool = False):
        exported = {
            "operations": {
                instance_name: operation.export()
                for instance_name, operation in self.operations.items()
            },
            "seed": self.seed.copy(),
            "configs": self.configs.copy(),
            "flow": self.flow.copy(),
        }
        if linked:
            exported["linked"] = True
            exported["definitions"] = self.definitions.copy()
            exported.update(self._linked()),
        return export_dict(**exported)

    @classmethod
    def _fromdict(cls, *, linked: bool = False, **kwargs):
        # Import all operations
        if linked:
            kwargs.update(cls._resolve(kwargs))
            del kwargs["definitions"]
        kwargs["operations"] = {
            instance_name: Operation._fromdict(
                instance_name=instance_name, **operation
            )
            for instance_name, operation in kwargs["operations"].items()
        }
        # Import seed inputs
        kwargs["seed"] = [
            Input._fromdict(**input_data) for input_data in kwargs["seed"]
        ]
        # Import input flows
        kwargs["flow"] = {
            instance_name: InputFlow._fromdict(**input_flow)
            for instance_name, input_flow in kwargs["flow"].items()
        }
        return cls(**kwargs)

    @classmethod
    def auto(cls, *operations):
        return cls(
            operations={
                getattr(getattr(operation, "op", operation), "name"): operation
                for operation in operations
            }
        )

    def auto_flow(self):
        flow_dict = {}
        # Create output_dict, which maps all of the definitions to the
        # operations that create them.
        output_dict = {}
        for operation in self.operations.values():
            for definition in operation.outputs.values():
                output_dict.setdefault(definition.name, {})
                output_dict[definition.name].update(
                    {operation.instance_name: operation}
                )
        # Got through all the operations and look at their inputs
        for operation in self.operations.values():
            # TODO Auto flow on operation conditions too
            flow_dict.setdefault(operation.instance_name, InputFlow())
            # Example operation:
            # Operation(
            #     name="pypi_package_json",
            #     # internal_name: package
            #     # definition: package = Definition(name="package", primitive="str")
            #     inputs={"package": package},
            #     # internal_name: response_json
            #     # definition: package_json = Definition(name="package_json", primitive="Dict")
            #     outputs={"response_json": package_json},
            # )
            # For each input
            for internal_name, definition in operation.inputs.items():
                # With pypi_package_json example
                # internal_name = "package"
                # definition = package
                #            = Definition(name="package", primitive="str")
                if definition.name in output_dict:
                    # Grab the dict of operations that produce this definition
                    # as an output
                    producing_operations = output_dict[definition.name]
                    # If the input could be produced by an operation in the
                    # network, then it's definition name will be in output_dict.
                    flow_dict[operation.instance_name].inputs[
                        internal_name
                    ] = []
                    # We look through the outputs and add any one that matches
                    # the definition and add it to the list in format of
                    # operation_name . internal_name (of output)
                    for producting_operation in producing_operations.values():
                        for (
                            internal_name_of_output,
                            output_definition,
                        ) in producting_operation.outputs.items():
                            if output_definition == definition:
                                flow_dict[operation.instance_name].inputs[
                                    internal_name
                                ].append(
                                    {
                                        producting_operation.instance_name: internal_name_of_output
                                    }
                                )
                else:
                    flow_dict[operation.instance_name].inputs[
                        internal_name
                    ] = ["seed"]
            # Now do conditions
            for definition in operation.conditions:
                if definition.name in output_dict:
                    # Grab the dict of operations that produce this definition
                    # as an output
                    producing_operations = output_dict[definition.name]
                    # We look through the outputs and add any one that matches
                    # the definition and add it to the list in format of
                    # operation_name . internal_name (of output)
                    for producting_operation in producing_operations.values():
                        for (
                            internal_name_of_output,
                            output_definition,
                        ) in producting_operation.outputs.items():
                            if output_definition == definition:
                                flow_dict[
                                    operation.instance_name
                                ].conditions.append(
                                    {
                                        producting_operation.instance_name: internal_name_of_output
                                    }
                                )
                else:
                    flow_dict[operation.instance_name].conditions = ["seed"]
        return flow_dict

    @classmethod
    def _resolve(cls, source: Dict):
        definitions = {}
        operations = {}
        for name, definition in source.get("definitions", {}).items():
            definition.setdefault("name", name)
            definitions[name] = definition
        for instance_name, operation in source.get("operations", {}).items():
            # Replaces strings referencing definitions with definitions
            for arg in ["conditions"]:
                if not arg in operation:
                    continue
                for i, definition_name in enumerate(operation[arg]):
                    if not definition_name in definitions:
                        raise DefinitionMissing(
                            f"While resolving {instance_name}.{arg}, missing {definition_name}"
                        )
                    operation[arg][i] = definitions[definition_name]
            for arg in ["inputs", "outputs"]:
                if not arg in operation:
                    continue
                for input_name, definition_name in operation[arg].items():
                    if not definition_name in definitions:
                        raise DefinitionMissing(
                            f"While resolving {instance_name}.{arg}, missing {definition_name}"
                        )
                    operation[arg][input_name] = definitions[definition_name]
            operation.setdefault("name", name)
        for item in source.get("seed", []):
            # Replaces strings referencing definitions with definitions
            if not item["definition"] in definitions:
                raise DefinitionMissing(
                    f"While resolving {instance_name}.{arg}, missing {definition_name}"
                )
            item["definition"] = definitions[item["definition"]]
        return source

    def _linked(self):
        exported = {}
        # Remove definitions from operations, just use definition name
        operations = {}
        for operation in self.operations.values():
            exported_operation = operation.export()
            for name, definition in operation.inputs.items():
                exported_operation["inputs"][name] = definition.name
            for name, definition in operation.outputs.items():
                exported_operation["outputs"][name] = definition.name
            operations[operation.instance_name] = exported_operation
        # Remove definitions from seed inputs, just use definition name
        seed = []
        for item in self.seed:
            exported_item = item.export()
            exported_item["definition"] = exported_item["definition"]["name"]
            seed.append(exported_item)
        # Set linked exported
        exported["seed"] = seed
        exported["operations"] = operations
        return exported
