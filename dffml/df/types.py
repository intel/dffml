import uuid
import itertools
from enum import Enum
import pkg_resources
from typing import NamedTuple, Union, List, Dict, Optional, Any, Iterator

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
        del exported["name"]
        if not self.lock:
            del exported["lock"]
        return exported


class Stage(Enum):
    PROCESSING = "processing"
    CLEANUP = "cleanup"
    OUTPUT = "output"


@base_entry_point("dffml.operation", "operation")
class Operation(Entrypoint):
    def __init__(
        self,
        name: str,
        inputs: Dict[str, Definition],
        outputs: Dict[str, Definition],
        conditions: List[Definition],
        stage: Stage = Stage.PROCESSING,
        expand: Optional[List[str]] = None,
    ):
        super().__init__()
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.conditions = conditions
        self.stage = stage
        if expand is None:
            expand = []
        self.expand = expand

    def export(self):
        exported = {
            "inputs": self.inputs.copy(),
            "outputs": self.outputs.copy(),
            "conditions": self.conditions.copy(),
            "stage": self.stage,
            "expand": self.expand.copy(),
        }
        for to_string in ["conditions"]:
            exported[to_string] = list(
                map(lambda definition: definition.name, exported[to_string])
            )
        for to_string in ["inputs", "outputs"]:
            exported[to_string] = dict(
                map(
                    lambda key_def: (key_def[0], key_def[1].name),
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
        parents: List["Input"],
        *,
        uid: Optional[str] = "",
    ):
        self.value = value
        self.definition = definition
        self.parents = parents
        self.uid = uid
        if not self.uid:
            self.uid = str(uuid.uuid4())
        # Must explictly set parents to False to get an empty list of parents
        if parents == False:
            self.parents = []

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


class Parameter(NamedTuple):
    key: str
    value: Any
    origin: Input
    definition: Definition
