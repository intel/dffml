import uuid
import itertools
import pkg_resources
from enum import Enum
from types import SimpleNamespace
from typing import NamedTuple, Union, List, Dict, Optional, Any, Iterator

from ..base import BaseConfig
from ..util.entrypoint import Entrypoint, base_entry_point


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
        return exported

    @classmethod
    def _fromdict(cls, **kwargs):
        return cls(**kwargs)


class Stage(Enum):
    PROCESSING = "processing"
    CLEANUP = "cleanup"
    OUTPUT = "output"


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
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            loaded = i.load()
            loaded.ENTRY_POINT_LABEL = i.name
            if isinstance(loaded, cls):
                loading_classes.append(loaded)
                if loading is not None and loaded.name == loading:
                    return loaded
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
    def _fromdict(cls, **kwargs):
        for prop in ["inputs", "outputs"]:
            kwargs[prop] = {
                argument_name: Definition._fromdict(**definition)
                for argument_name, definition in kwargs[prop].items()
            }
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
        *,
        uid: Optional[str] = "",
    ):
        if parents is None:
            parents = []
        self.value = value
        self.definition = definition
        self.parents = parents
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
        return "%s: %s" % (self.definition.name, self.value)

    def __str__(self):
        return repr(self)

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["definition"] = Definition._fromdict(**kwargs["definition"])
        return cls(**kwargs)


class Parameter(NamedTuple):
    key: str
    value: Any
    origin: Input
    definition: Definition


class DataFlow(NamedTuple):
    seed: List[Input]
    definitions: Dict[str, Definition]
    operations: Dict[str, Operation]
    configs: Dict[str, BaseConfig]

    @classmethod
    def _fromdict(cls, **kwargs):
        # Import all operations
        kwargs["operations"] = {
            instance_name: Operation._fromdict(instance_name=instance_name, **operation)
            for instance_name, operation in kwargs["operations"].items()
        }
        # Grab all definitions from operations
        operations = list(kwargs["operations"].values())
        definitions = list(set(itertools.chain(*[
            itertools.chain(operation.inputs.values(), operation.outputs.values())
            for operation in operations
        ])))
        definitions = {definition.name: definition
                       for definition in definitions}
        kwargs["definitions"] = definitions
        # Import seed inputs
        kwargs["seed"] = [
            Input._fromdict(**input_data)
            for input_data in kwargs["seed"]
        ]
        return cls(**kwargs)
