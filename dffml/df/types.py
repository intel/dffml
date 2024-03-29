import uuid
import copy
import types
import inspect
import itertools
import collections
import pkg_resources
import collections.abc
from enum import Enum
from dataclasses import dataclass, field, asdict, replace, is_dataclass
from typing import (
    NamedTuple,
    Union,
    List,
    Dict,
    Optional,
    Any,
    AsyncIterator,
    Callable,
    Tuple,
    Type,
    NewType,
    ForwardRef,
)

from ..base import BaseConfig
from ..util.data import get_origin, get_args
from ..util.data import export_dict, type_lookup
from ..util.entrypoint import Entrypoint, base_entry_point


class _NO_DEFAULT:
    pass


NO_DEFAULT = _NO_DEFAULT()


class _APPLY_INSTALLED_OVERLAYS:
    pass


APPLY_INSTALLED_OVERLAYS = _APPLY_INSTALLED_OVERLAYS()


Expand = Union


primitive_types = (int, float, str, bool, dict, list, bytes)
# Used to convert python types in to their programming language agnostic
# names
# TODO Combine with logic in dffml.util.data
primitive_convert = {dict: "map", list: "array"}


def find_primitive(new_type: Type) -> Type:
    if new_type in primitive_types:
        return new_type
    if hasattr(new_type, "__supertype__"):
        return find_primitive(new_type.__supertype__)
    if isinstance(new_type, type):
        return object
    raise TypeError(
        f"{new_type} has no member __supertype__. Are you sure it is a typing.NewType? It says it is of type {type(new_type)!r}"
    )


def new_type_to_defininition(new_type: Type) -> Type:
    """
    >>> from typing import NewType
    >>> from dffml import new_type_to_defininition
    >>>
    >>> new_type_to_defininition(NewType("FeedFace", str))
    Definition(name='FeedFace', primitive='str')
    """
    # TODO Split on capital letters into lowercase dot separated.
    return Definition(
        name=new_type.__name__,
        primitive=find_primitive(new_type).__qualname__,
        links=(
            create_definition(
                find_primitive(new_type).__qualname__, new_type.__supertype__
            ),
        ),
    )


class FailedToAutoCreateDefinitionInvalidNameError(ValueError):
    pass


class CouldNotDeterminePrimitive(Exception):
    """
    Could not determine the primitive of the parameter
    """


def resolve_if_forward_ref(param_annotation, forward_refs_from_cls):
    if isinstance(param_annotation, ForwardRef):
        param_annotation = param_annotation.__forward_arg__
    if (
        isinstance(param_annotation, str)
        and forward_refs_from_cls
        and hasattr(forward_refs_from_cls, param_annotation)
    ):
        param_annotation = getattr(forward_refs_from_cls, param_annotation)
        if hasattr(param_annotation, "__name__") and hasattr(
            param_annotation, "__supertype__"
        ):
            # typing.NewType support
            return new_type_to_defininition(param_annotation)
    return param_annotation


def _create_definition(
    name,
    param_annotation,
    default=NO_DEFAULT,
    *,
    forward_refs_from_cls: Optional[object] = None,
):
    param_annotation = resolve_if_forward_ref(
        param_annotation, forward_refs_from_cls
    )
    if isinstance(param_annotation, Definition):
        return param_annotation
    if (
        inspect.isclass(param_annotation)
        and param_annotation in primitive_types
    ):
        return Definition(
            name=name,
            primitive=primitive_convert.get(
                param_annotation, param_annotation.__name__
            ),
            default=default,
        )
    elif get_origin(param_annotation) in [
        Union,
        collections.abc.AsyncIterator,
    ]:
        # If the annotation is of the form Optional
        return create_definition(
            name,
            list(get_args(param_annotation))[0],
            forward_refs_from_cls=forward_refs_from_cls,
        )
    elif (
        get_origin(param_annotation) is list
        or get_origin(param_annotation) is dict
    ):
        # If the annotation are of the form List[MyDataClass] or Dict[str, MyDataClass]
        if get_origin(param_annotation) is list:
            primitive = "array"
            innerclass = list(get_args(param_annotation))[0]
        else:
            primitive = "map"
            innerclass = list(get_args(param_annotation))[1]
        # Create definition for internal type
        definition = create_definition(
            name,
            innerclass,
            default=default,
            forward_refs_from_cls=forward_refs_from_cls,
        )._replace(primitive=primitive,)
        # NOTE(security) NamedTuple is safe to use a spec, because it offers no
        # mechanisms around running code during init. Dataclasses and everything
        # else cannot be trusted! They might run __post_init__() code! We MUST
        # traverse the graph of links to sandbox instatiation of the correct
        # type.
        if is_dataclass(innerclass) or bool(
            inspect.isclass(innerclass)
            and issubclass(innerclass, tuple)
            and hasattr(innerclass, "_asdict")
        ):
            return definition._replace(spec=innerclass, subspec=True,)

        return definition
    elif is_dataclass(param_annotation) or bool(
        inspect.isclass(param_annotation)
        and issubclass(param_annotation, tuple)
        and hasattr(param_annotation, "_asdict")
    ):
        # If the annotation is either a dataclass or namedtuple
        return Definition(
            name=name, primitive="map", default=default, spec=param_annotation,
        )
    elif inspect.isclass(param_annotation):
        # In the event the annotation is Python class. We create definitions for
        # both it's usage within the context (aka name). As well as a definition
        # for the parent (param_annotation) as well as for the parent's module.
        # This will allow us to dynamicly apply serialization/deserialization
        # sandboxing aka allowlist of modules and types which can be
        # instantiated based off inputs, and what operations they must go
        # through before instantiatation (aka overlays should apply vetting to
        # input data to avoid yaml.load CVE-2017-18342 style situations).
        return Definition(
            name=".".join(
                filter(
                    bool,
                    [
                        param_annotation.__module__,
                        param_annotation.__qualname__,
                        name,
                    ],
                )
            ),
            primitive="object",
            default=default,
            links=(
                Definition(
                    name=param_annotation.__qualname__,
                    primitive="object",
                    links=(
                        Definition(
                            name=param_annotation.__module__,
                            primitive="object",
                            links=(
                                Definition(name="module", primitive="object"),
                            ),
                        ),
                    ),
                ),
            ),
        )

    raise CouldNotDeterminePrimitive(
        f"The primitive of {name} could not be determined: {param_annotation}"
    )


def create_definition(
    name,
    param_annotation,
    default=NO_DEFAULT,
    *,
    forward_refs_from_cls: Optional[object] = None,
):
    if hasattr(param_annotation, "__name__") and hasattr(
        param_annotation, "__supertype__"
    ):
        # typing.NewType support
        return new_type_to_defininition(param_annotation)
    definition = _create_definition(
        name,
        param_annotation,
        default=default,
        forward_refs_from_cls=forward_refs_from_cls,
    )
    # We can guess name if converting from NewType. However, we can't otherwise.
    if not definition.name:
        raise FailedToAutoCreateDefinitionInvalidNameError(repr(name))
    return definition


class DefinitionMissing(Exception):
    """
    Definition missing from linked DataFlow
    """


class PrimitiveDoesNotMatchValue(Exception):
    """
    Primitive does not match the value type
    """


class Definition(NamedTuple):
    """
    Examples
    --------

    >>> from dffml import Definition, Input
    >>> from typing import NamedTuple
    >>>
    >>> class Person(NamedTuple):
    ...   name: str
    ...   age: int
    >>>
    >>> Friend = Definition(name="Friend", primitive="map", spec=Person)
    >>> Input(value={"name": "Bob", "age": 42}, definition=Friend)
    Input(value=Person(name='Bob', age=42), definition=Friend)
    >>>
    >>> SignUpQueue = Definition(name="SignUpQueue", primitive="array", spec=Person, subspec=True)
    >>> Input(value=[{"name": "Bob", "age": 42}], definition=SignUpQueue)
    Input(value=[Person(name='Bob', age=42)], definition=SignUpQueue)
    >>>
    >>> AddressBook = Definition(name="AddressBook", primitive="map", spec=Person, subspec=True)
    >>> Input(value={"bob": {"name": "Bob", "age": 42}}, definition=AddressBook)
    Input(value={'bob': Person(name='Bob', age=42)}, definition=AddressBook)
    """

    name: str
    primitive: str
    default: Any = NO_DEFAULT
    lock: bool = False
    # spec is a NamedTuple which could be populated via a dict
    spec: NamedTuple = None
    # subspec is when your input is a list or dict of values which conform to
    # the spec
    subspec: bool = False
    # TODO Remove validate callable code, should be using operations instead via
    # overlays
    # validate property will be a callable (function or lambda) which returns
    # the sanitized version of the value
    validate: Callable[[Any], Any] = None
    # Links to other inputs/definitions
    links: Tuple["Definition"] = None

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return bool(self.export() == other.export())

    def export(self):
        exported = dict(self._asdict())
        if "dffml.df.types._NO_DEFAULT" in repr(self.default):
            del exported["default"]
        if not self.lock:
            del exported["lock"]
        if not self.validate:
            del exported["validate"]
        if not self.links:
            del exported["links"]
        else:
            exported["links"] = tuple(
                [tuple(link.export().items()) for link in exported["links"]]
            )
        if not self.spec:
            del exported["spec"]
            del exported["subspec"]
        elif all(
            [
                hasattr(self.spec, key)
                for key in [
                    "__qualname__",
                    "__annotations__",
                    "_field_defaults",
                ]
            ]
        ):
            exported["spec"] = export_dict(
                name=self.spec.__qualname__,
                types=self.spec.__annotations__,
                defaults=self.spec._field_defaults,
            )
        else:
            raise NotImplementedError(f"Unknown how to export {self.spec}")
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
            # source code
            # https://github.com/python/cpython/blob/3.7/Lib/typing.py#L1360
            # and seeing that we can hijack the __annotations__ property to
            # allow us to set default values
            def_tuple = kwargs["spec"]["defaults"]
            # All dict are ordered in 3.7+
            annotations = {}
            annotations_with_defaults = {}
            for key, typename in kwargs["spec"]["types"].items():
                # Properties without defaults must come before those with
                # defaults
                if key not in def_tuple:
                    annotations[key] = cls.type_lookup(typename)
                else:
                    annotations_with_defaults[key] = cls.type_lookup(typename)
            # Ensure annotations with defaults are after those without defaults
            # in dict
            for key, dtype in annotations_with_defaults.items():
                annotations[key] = dtype
            def_tuple["__annotations__"] = annotations

            def populate_ns(ns):
                ns.update(def_tuple)
                ns["__module__"] = "dffml.types"
                return None

            kwargs["spec"] = types.new_class(
                kwargs["spec"]["name"],
                bases=(NamedTuple,),
                exec_body=populate_ns,
            )
        if "links" in kwargs:
            kwargs["links"] = tuple(
                cls._fromdict(
                    **(dict(link) if isinstance(link, (tuple, list)) else link)
                )
                for link in kwargs["links"]
            )
        return cls(**kwargs)

    @classmethod
    def type_lookup(cls, typename):
        # Allowlist of non-python builtin types
        if typename in ["Definition"]:
            # TODO More types
            return cls
        return type_lookup(typename)


# Some common types
GENERIC = Definition(name="generic", primitive="generic")


class Stage(Enum):
    PROCESSING = "processing"
    CLEANUP = "cleanup"
    OUTPUT = "output"


class FailedToLoadOperation(Exception):
    """
    Raised when an Operation wasn't found to be registered with the
    dffml.operation entrypoint.
    """


@dataclass(frozen=True)
@base_entry_point("dffml.operation", "operation")
class Operation(Entrypoint):
    name: str
    inputs: Dict[str, Definition] = field(default_factory=lambda: {})
    outputs: Dict[str, Definition] = field(default_factory=lambda: {})
    stage: Stage = Stage.PROCESSING
    conditions: Optional[List[Definition]] = field(default_factory=lambda: [])
    expand: Optional[List[str]] = field(default_factory=lambda: [])
    instance_name: Optional[str] = None
    validator: bool = False
    retry: int = 0

    def __post_init__(self):
        # Covert all typing.NewType's to definitions
        for definition_container_name in (
            "inputs",
            "outputs",
            "conditions",
        ):
            definition_container = getattr(self, definition_container_name)
            if isinstance(definition_container, list):
                definition_iterable = enumerate(definition_container)
            else:
                definition_iterable = definition_container.items()
            for i, definition in definition_iterable:
                if definition.__class__.__qualname__ != "Definition":
                    # typing.NewType support
                    definition_container[i] = create_definition(
                        ".".join(
                            [self.name, definition_container_name]
                            + (
                                [str(i)]
                                if not isinstance(
                                    definition_container_name, int
                                )
                                else []
                            )
                        ),
                        definition,
                    )

    def _replace(self, **kwargs):
        return replace(self, **kwargs)

    def export(self):
        exported = {
            "name": self.name,
            "inputs": self.inputs.copy(),
            "outputs": self.outputs.copy(),
            "conditions": self.conditions.copy(),
            "stage": self.stage.value,
            "expand": self.expand.copy(),
            "retry": self.retry,
        }
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
        for i in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
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
        for i in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
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
        for i in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
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
        # TODO(alice) Rename Input.parents to Input.links
        origin: Optional[Union[str, Tuple[Operation, str]]] = "seed",
        validated: bool = True,
        *,
        uid: Optional[str] = "",
        links: Optional[Tuple["Input"]] = None,
    ):
        # TODO(alice)

        # NOTE For some reason doctests end up with id(type(definition)) not
        # equal to id(Definition). Therefore just compare the class name.
        # typing.NewType support. Auto convert NewTypes into definitions.
        if definition.__class__.__qualname__ != "Definition":
            # typing.NewType support
            old_definition = definition
            definition = create_definition("", definition)
        # TODO Add optional parameter Input.target which specifies the operation
        # instance name this Input is intended for.
        self.validated = validated
        if parents is None:
            parents = []
        if definition.spec is not None:
            if definition.subspec:
                if isinstance(value, list) and definition.primitive == "array":
                    for i, subvalue in enumerate(value):
                        value[i] = definition.spec(**subvalue)
                elif isinstance(value, dict) and definition.primitive == "map":
                    for key, subvalue in value.items():
                        value[key] = definition.spec(**subvalue)
                else:
                    raise PrimitiveDoesNotMatchValue(
                        f"{type(value)} is not the right type for primitive {definition.primitive}"
                    )
            elif isinstance(value, dict):
                value = definition.spec(**value)
        if definition.validate is not None:
            if callable(definition.validate):
                value = definition.validate(value)
            # if validate is a string (operation.instance_name) set `not validated`
            elif isinstance(definition.validate, str):
                self.validated = False
        self.value = value
        self.definition = definition
        self.parents = parents
        self.origin = origin
        self.uid = uid
        if not self.uid:
            self.uid = str(uuid.uuid4())

    async def get_parents(self) -> AsyncIterator["Input"]:
        parents = []
        for item in self.parents:
            parents.append(
                [item] + [item async for item in item.get_parents()]
            )
        for parent in list(set(itertools.chain(*parents))):
            yield parent

    def __repr__(self):
        return f"Input(value={self.value}, definition={self.definition})"

    def __str__(self):
        return repr(self)

    def export(self):
        return dict(
            value=self.value,
            definition=self.definition.export(),
            origin=self.origin,
        )

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["definition"] = Definition._fromdict(**kwargs["definition"])
        return cls(**kwargs)


class Parameter(Input):
    def __init__(
        self, key: str, value: Any, origin: Input, definition: Definition,
    ):
        super().__init__(
            value=value, definition=definition,
        )
        self.key = key
        self.origin = origin


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

    @staticmethod
    def get_alternate_definitions(
        origin: Tuple[Union[List[str], Tuple[str]], str]
    ) -> Tuple[Union[List[str], Tuple[str]], str]:
        """
        Returns the alternate definitions and origin for an entry within an input
        flow. If there are no alternate defintions then the first element of the
        returned tuple is an empty list.

        Examples
        --------

        >>> from dffml import InputFlow
        >>>
        >>> input_flow = InputFlow(
        ...     inputs={
        ...         "features": [
        ...             {"seed": ["Years", "Expertise", "Trust", "Salary"]}
        ...         ],
        ...         "token": [
        ...             "client",
        ...         ]
        ...     }
        ... )
        >>>
        >>> input_flow.get_alternate_definitions(list(input_flow.inputs["features"][0].items())[0])
        (['Years', 'Expertise', 'Trust', 'Salary'], 'seed')
        >>>
        input_flow.get_alternate_definitions(list(input_flow.inputs["other"][0].items())[0])
        ([], 'client')
        """
        if isinstance(origin, tuple) and isinstance(origin[1], (list, tuple)):
            return origin[1], origin[0]
        return [], origin


@dataclass
class Forward:
    """
    Keeps a map of operation instance_names to list of definitions
    of inputs which should be forwarded to the subflow running in that operation.
    """

    book: "Dict[str, List[Definitions]]" = None

    def __post_init__(self):
        if self.book is None:
            self.book = {}
        self._internal_book = []

    def add(self, instance_name: str, definition_list: List[Definition]):
        self.book[instance_name] = definition_list
        self._internal_book.extend(definition_list)

    def get_instances_to_forward(self, definition: Definition) -> List[str]:
        """
        Returns a list of all instances of operation to which `definition` should
        be forwarded to.
        """
        if not definition in self._internal_book:
            return []
        return [
            instance_name
            for instance_name, definitions in self.book.items()
            if definition in definitions
        ]

    def export(self):
        return export_dict(**asdict(self))

    @classmethod
    def _fromdict(cls, **kwargs):
        return cls(**kwargs)


class DataFlow:

    CONFIGLOADABLE = True
    DEFINITION = Definition(name="dataflow", primitive="object")

    def __init__(
        self,
        *args,
        operations: Dict[str, Union[Operation, Callable]] = None,
        seed: List[Input] = None,
        configs: Dict[str, BaseConfig] = None,
        definitions: Dict[str, Definition] = False,
        flow: Dict[str, InputFlow] = None,
        by_origin: Dict[Stage, Dict[str, Operation]] = None,
        # Implementations can be provided in case they haven't been registered
        # via the entrypoint system.
        implementations: Dict[str, "OperationImplementation"] = None,
        forward: Forward = None,
    ) -> None:
        # Prevent usage of a global dict (if we set default to {} then all the
        # instances will share the same instance of that dict, or list)
        if operations is None:
            operations = {}
        if forward is None:
            forward = Forward()
        if seed is None:
            seed = []
        if configs is None:
            configs = {}
        if by_origin is None:
            by_origin = {}
        if implementations is None:
            implementations = {}
        if definitions == False:
            definitions = {}
        validators = {}  # Maps `validator` ops instance_name to op

        for operation in args:
            name = getattr(getattr(operation, "op", operation), "name")
            if name in operations:
                raise ValueError(f"Operation {name} given as positional and in dict")
            operations[name] = operation

        self.operations = operations
        self.seed = seed
        self.configs = configs
        self.definitions = definitions
        self.flow = flow
        self.by_origin = by_origin
        self.implementations = implementations
        self.forward = forward
        self.validators = validators

        self.update(auto_flow=bool(self.flow is None))

    def update(self, auto_flow: bool = False):
        self.update_operations()
        self.update_definitions()
        if auto_flow:
            self.flow = self.auto_flow()
        self.update_by_origin()

    def update_operations(self):
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
            value = value._replace(instance_name=instance_name)
            self.operations[instance_name] = value
            if value.validator:
                self.validators[instance_name] = value

    def update_definitions(self):
        # Grab all definitions from operations
        operations = list(self.operations.values())
        definitions = list(
            set(
                itertools.chain(
                    self.definitions.values(),
                    [item.definition for item in self.seed],
                    *[
                        itertools.chain(
                            operation.inputs.values(),
                            operation.outputs.values(),
                            operation.conditions,
                        )
                        for operation in operations
                    ],
                )
            )
        )
        definitions = {
            definition.name: definition for definition in definitions
        }
        self.definitions = definitions

    def update_by_origin(self):
        # Create by_origin which maps operation instance names to the sources
        self.by_origin = {}
        for instance_name, input_flow in self.flow.items():
            operation = self.operations[instance_name]
            self.by_origin.setdefault(operation.stage, {})
            # TODO(p5) Make stanardize this so that seed is also a dict?
            for output_source in input_flow.conditions:
                if isinstance(output_source, str):
                    self.by_origin[operation.stage].setdefault(
                        output_source, {}
                    )
                    self.by_origin[operation.stage][output_source][
                        operation.instance_name
                    ] = operation
                else:
                    for origin in output_source.items():
                        _, origin = input_flow.get_alternate_definitions(
                            origin
                        )
                        self.by_origin[operation.stage].setdefault(origin, {})
                        self.by_origin[operation.stage][origin][
                            operation.instance_name
                        ] = operation
            for output_name, output_sources in input_flow.inputs.items():
                for output_source in output_sources:
                    if isinstance(output_source, str):
                        self.by_origin[operation.stage].setdefault(
                            output_source, {}
                        )
                        self.by_origin[operation.stage][output_source][
                            operation.instance_name
                        ] = operation
                    else:
                        # In order to support selection an input based using an
                        # alternate definition along with restriction to inputs
                        # who's origins match the alternate definitions in the
                        # list. We select the first output source since that
                        # will be the immediate alternate definition
                        if (
                            isinstance(output_source, list)
                            and output_source
                            and isinstance(output_source[0], dict)
                        ):
                            output_source = output_source[0]
                        for origin in output_source.items():
                            # If we have an output_source item with an origin
                            # that has a list as it's value we know that the key
                            # (aka origin[0] since output_source is a dict) is
                            # the Input.origin (like "seed"). And the value
                            # (origin[1]) is the list of definitions which are
                            # acceptable from that origin for this input.
                            _, origin = input_flow.get_alternate_definitions(
                                origin
                            )
                            self.by_origin[operation.stage].setdefault(
                                origin, {}
                            )
                            self.by_origin[operation.stage][origin][
                                operation.instance_name
                            ] = operation
        # NOTE We converted to and from dict here so that operations in
        # lists would be unique based on instance name.
        for stage, origins in self.by_origin.items():
            for origin in origins:
                origins[origin] = list(origins[origin].values())

    def export(self, *, linked: bool = False):
        exported = {
            "operations": {
                instance_name: operation.export()
                for instance_name, operation in self.operations.items()
            }
        }
        if self.seed:
            exported["seed"] = self.seed.copy()
        if self.flow:
            exported["flow"] = self.flow.copy()
        if self.configs:
            exported["configs"] = self.configs.copy()
        if self.forward.book:
            exported["forward"] = self.forward.export()
        exported = export_dict(**exported)
        if linked:
            self._linked(exported)
        return exported

    @classmethod
    def _fromdict(cls, *, linked: bool = False, **kwargs):
        # Import all operations
        if linked:
            kwargs.update(cls._resolve(kwargs))
            kwargs["definitions"] = {
                name: Definition._fromdict(**definition)
                for name, definition in kwargs["definitions"].items()
            }
        kwargs["operations"] = {
            instance_name: Operation._fromdict(
                instance_name=instance_name, **operation
            )
            for instance_name, operation in kwargs["operations"].items()
        }
        # Import seed inputs
        if "seed" in kwargs:
            kwargs["seed"] = [
                Input._fromdict(**input_data) for input_data in kwargs["seed"]
            ]
        # Import input flows
        if "flow" in kwargs:
            kwargs["flow"] = {
                instance_name: InputFlow._fromdict(**input_flow)
                for instance_name, input_flow in kwargs["flow"].items()
            }
        # Import forward
        if "forward" in kwargs:
            kwargs["forward"] = Forward._fromdict(**kwargs["forward"])
        return cls(**kwargs)

    @classmethod
    def auto(cls, *operations):
        return cls(*operations)

    def auto_flow(self):
        # Determine the dataflow if not given
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
                            f"While resolving {instance_name}.{arg}, missing {definition_name} not found in {definitions.keys()}"
                        )
                    operation[arg][i] = definitions[definition_name]
            for arg in ["inputs", "outputs"]:
                if not arg in operation:
                    continue
                for input_name, definition_name in operation[arg].items():
                    if not definition_name in definitions:
                        raise DefinitionMissing(
                            f"While resolving {instance_name}.{arg}, missing {definition_name} not found in {definitions.keys()}"
                        )
                    operation[arg][input_name] = definitions[definition_name]
            operation.setdefault("name", name)
        for item in source.get("seed", []):
            # Replaces strings referencing definitions with definitions
            if not item["definition"] in definitions:
                raise DefinitionMissing(
                    f"While resolving seed {item}, definition {item['definition']} not found in {definitions.keys()}"
                )
            item["definition"] = definitions[item["definition"]]
        return source

    def _linked(self, exported):
        # Set linked
        exported["linked"] = True
        # Include definitions
        exported["definitions"] = export_dict(**self.definitions.copy())
        # Remove definitions from operations, just use definition name
        for operation in exported["operations"].values():
            for arg in ["conditions"]:
                if not arg in operation:
                    continue
                for i, definition in enumerate(operation[arg]):
                    operation[arg][i] = definition["name"]
            for arg in ["inputs", "outputs"]:
                if not arg in operation:
                    continue
                for io_name, definition in operation[arg].items():
                    operation[arg][io_name] = definition["name"]
        # Remove definitions from seed inputs, just use definition name
        if "seed" in exported:
            for item in exported["seed"]:
                item["definition"] = item["definition"]["name"]
        return exported
