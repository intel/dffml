import abc
import sys
import types
import inspect
import logging
import collections
import collections.abc
import pkg_resources
from typing import (
    AsyncIterator,
    AsyncContextManager,
    Dict,
    List,
    Tuple,
    Any,
    NamedTuple,
    Union,
    Optional,
    Set,
)
from dataclasses import dataclass, is_dataclass, replace
from contextlib import asynccontextmanager

from .exceptions import NotOpImp
from .types import (
    Operation,
    Input,
    Parameter,
    Stage,
    Definition,
    NO_DEFAULT,
    primitive_types,
    primitive_convert,
    resolve_if_forward_ref,
    new_type_to_defininition,
    create_definition,
    DataFlow,
    APPLY_INSTALLED_OVERLAYS,
)

from .log import LOGGER

from ..base import (
    BaseConfig,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..util.entrypoint import Entrypoint
from ..util.cli.arg import Arg
from ..util.data import get_origin, get_args
from ..util.asynchelper import context_stacker
from ..util.entrypoint import base_entry_point
from ..util.entrypoint import load as load_entrypoint


class BaseDataFlowObjectContext(BaseDataFlowFacilitatorObjectContext):
    """
    Data Flow Object Contexts are instantiated by being passed their
    config, and their parent, a BaseDataFlowObject.
    """

    def __init__(
        self, config: BaseConfig, parent: "BaseDataFlowObject"
    ) -> None:
        self.config = config
        self.parent = parent


class BaseDataFlowObject(BaseDataFlowFacilitatorObject):
    """
    Data Flow Objects create their child contexts' by passing only itself as an
    argument to the child's __init__ (of type BaseDataFlowObjectContext).
    """

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        if hasattr(cls, "CONFIG"):
            return super(BaseDataFlowObject, cls).args(args, *above)
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        if hasattr(cls, "CONFIG"):
            return super(BaseDataFlowObject, cls).config(config, *above)
        return BaseConfig()


class OperationImplementationContext(BaseDataFlowObjectContext):
    def __init__(
        self,
        parent: "OperationImplementation",
        ctx: "BaseInputSetContext",
        octx: "BaseOrchestratorContext",
    ) -> None:
        self.parent = parent
        self.ctx = ctx
        self.octx = octx

    @property
    def config(self):
        """
        Alias for self.parent.config
        """
        return self.parent.config

    @abc.abstractmethod
    async def run(self, inputs: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        """
        Implementation of the operation goes here. Should take and return a dict
        with keys matching the input and output parameters of the Operation
        object associated with this operation implementation context.
        """

    @asynccontextmanager
    async def subflow(
        self,
        dataflow,
        *,
        reuse: Dict[str, BaseDataFlowObjectContext] = None,
        overlay: Optional[DataFlow] = None,
        overlay_application_orchestrator: Optional["BaseOrchestrator"] = None,
    ):
        r"""
        Registers subflow `dataflow` with parent flow and yields an instance of `BaseOrchestratorContext`

        >>> import dffml
        >>> import dffml.noasync
        >>>
        >>> @dffml.op
        ... async def my_operation(self):
        ...     async with self.subflow(
        ...         dffml.DataFlow(),
        ...         overlay=dffml.DataFlow(),
        ...         overlay_application_orchestrator=dffml.MemoryOrchestrator(),
        ...     ) as octx:
        ...         print(octx.run({"ctx_str": []}))
        >>>
        >>> print(list(dffml.noasync.run(dffml.DataFlow(my_operation))))
        """
        # TODO(alice) Also accept SystemContext for overlay, run deployment
        # ``dffml.overlay`` to produce dataflow to apply as overlay.
        # TODO(alice) Rework once we have system context. Run overlay system context
        # using orchestrator from that. System context is basic clay a dataclass
        # with the properties as this functions arguments.
        if overlay is APPLY_INSTALLED_OVERLAYS:
            # Load defaults via entrypoints, aka installed dataflows registered as
            # plugins.
            # TODO Maybe pass orchestrator to default
            overlay = DFFMLOverlaysInstalled
        # Apply overlay if given or installed
        if overlay is not None:
            orchestrator = self.octx.parent
            if overlay_application_orchestrator is not None:
                orchestrator = overlay_application_orchestrator
            # This effectivly creates a new system context, a direct ancestor of the
            # of the one that got passed in and the overlay. Therefore they are both
            # listed in the input parents when we finally split this out so that run
            # is called as an operation, where the overlay is applied prior to
            # calling run.
            overlay_cls = overlay
            async with overlay_cls(orchestrator=self.octx.parent) as overlay:
                async with overlay() as overlay_context:
                    dataflow = await overlay_context.apply(dataflow)
        async with self.octx.parent(dataflow, reuse=reuse) as octx:
            self.octx.subflows[self.parent.op.instance_name] = octx
            yield octx


class FailedToLoadOperationImplementation(Exception):
    """
    Raised when an OperationImplementation wasn't found to be registered with
    the dffml.operation entrypoint.
    """


@base_entry_point("dffml.operation", "opimp")
class OperationImplementation(BaseDataFlowObject):
    def __init__(self, config: "BaseConfig") -> None:
        super().__init__(config)
        if not getattr(self, "op", False):
            raise ValueError(
                "OperationImplementation's may not be "
                + "created without an `op`"
            )

    def __call__(
        self, ctx: "BaseInputSetContext", octx: "BaseOrchestratorContext"
    ) -> OperationImplementationContext:
        return self.CONTEXT(self, ctx, octx)

    @classmethod
    def add_orig_label(cls, *above):
        return list(above) + cls.op.name.split("_")

    @classmethod
    def add_label(cls, *above):
        return list(above) + cls.op.name.split("_")

    @classmethod
    def _imp(cls, loaded):
        """
        Returns the operation implementation from a loaded entrypoint object, or
        None if its not an operation implementation or doesn't have the imp
        parameter which is an operation implementation.
        """
        for obj in [getattr(loaded, "imp", None), loaded]:
            if inspect.isclass(obj) and issubclass(obj, cls):
                return obj
        if (
            inspect.isfunction(loaded)
            or inspect.isgeneratorfunction(loaded)
            or inspect.iscoroutinefunction(loaded)
            or inspect.isasyncgenfunction(loaded)
        ):
            return op(loaded).imp
        return None

    @classmethod
    def load(cls, loading: str = None):
        loading_classes = []
        # Load operations
        for i in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
            if loading is not None and i.name == loading:
                loaded = cls._imp(i.load())
                if loaded is not None:
                    return loaded
            elif loading is None:
                loaded = cls._imp(i.load())
                if loaded is not None:
                    loading_classes.append(loaded)
        # Loading from entrypoint if ":" is in name
        if loading is not None and ":" in loading:
            loaded = next(load_entrypoint(loading, relative=True))
            loaded = cls._imp(loaded)
            return loaded
        if loading is not None:
            raise FailedToLoadOperationImplementation(
                "%s was not found in (%s)"
                % (
                    repr(loading),
                    ", ".join(list(map(lambda op: op.name, loading_classes))),
                )
            )
        return loading_classes


def op(
    *args,
    imp_enter=None,
    ctx_enter=None,
    config_cls=None,
    valid_return_none=True,
    multi_output=True,
    **kwargs,
):
    """
    The ``op`` decorator creates a subclass of
    :py:class:`dffml.df.OperationImplementation` and assigns that
    ``OperationImplementation`` to the ``.imp`` parameter of the
    function it decorates.

    If the decorated object is not already a class which is a subclass of
    ``OperationImplementationContext``, it creates an
    :py:class:`dffml.df.OperationImplementationContext`
    and assigns it to the ``CONTEXT`` class parameter of the
    ``OperationImplementation`` which was created.

    Upon context entry into the ``OperationImplementation``, imp_enter is
    iterated over and the values in that ``dict`` are entered. The value yielded
    upon entry is assigned to a parameter in the ``OperationImplementation``
    instance named after the respective key.

    Examples
    --------

    >>> from dffml import Definition, Input, op
    >>> from typing import NamedTuple, List, Dict
    >>>
    >>> class Person(NamedTuple):
    ...     name: str
    ...     age: int
    ...
    >>> @op
    ... def cannotVote(p: List[Person]):
    ...     return list(filter(lambda person: person.age < 18, p))
    ...
    >>>
    >>> Input(
    ...     value=[
    ...         {"name": "Bob", "age": 20},
    ...         {"name": "Mark", "age": 21},
    ...         {"name": "Alice", "age": 90},
    ...     ],
    ...     definition=cannotVote.op.inputs["p"],
    ... )
    Input(value=[Person(name='Bob', age=20), Person(name='Mark', age=21), Person(name='Alice', age=90)], definition=cannotVote.inputs.p)
    >>>
    >>> @op
    ... def canVote(p: Dict[str, Person]) -> Dict[str, Person]:
    ...     return {
    ...         person.name: person
    ...         for person in filter(lambda person: person.age >= 18, p.values())
    ...     }
    ...
    >>>
    >>> Input(
    ...     value={
    ...         "Bob": {"name": "Bob", "age": 19},
    ...         "Alice": {"name": "Alice", "age": 21},
    ...         "Mark": {"name": "Mark", "age": 90},
    ...     },
    ...     definition=canVote.op.inputs["p"],
    ... )
    Input(value={'Bob': Person(name='Bob', age=19), 'Alice': Person(name='Alice', age=21), 'Mark': Person(name='Mark', age=90)}, definition=canVote.inputs.p)
    >>>
    >>> Input(
    ...     value={
    ...         "Bob": {"name": "Bob", "age": 19},
    ...         "Alice": {"name": "Alice", "age": 21},
    ...         "Mark": {"name": "Mark", "age": 90},
    ...     },
    ...     definition=canVote.op.outputs["result"],
    ... )
    Input(value={'Bob': Person(name='Bob', age=19), 'Alice': Person(name='Alice', age=21), 'Mark': Person(name='Mark', age=90)}, definition=canVote.outputs.result)
    """

    def wrap(func):
        if not "name" in kwargs:
            name = func.__name__
            if name == "<lambda>":
                raise ValueError("op.name must given when lambda is wrapped")
            module_name = inspect.getmodule(func).__name__
            if module_name != "__main__":
                name = f"{module_name}:{name}"
            # Check if it's already been registered as another name
            for i in pkg_resources.iter_entry_points(Operation.ENTRYPOINT):
                entrypoint_load_path = i.module_name + ":" + ".".join(i.attrs)
                # If it has, then let that name take precedence
                if entrypoint_load_path == name:
                    name = i.name
                    break
            kwargs["name"] = name
        # TODO Make this grab from the defaults for Operation
        if not "conditions" in kwargs:
            kwargs["conditions"] = []

        forward_refs_from_cls = None
        if hasattr(func, "__qualname__") and "." in func.__qualname__:
            # Attempt to lookup type definitions defined within class
            forward_refs_from_cls = getattr(
                sys.modules[func.__module__],
                func.__qualname__.split(".")[0],
                None,
            )

        sig = inspect.signature(func)
        # Check if the function uses the env (skip passing self)
        uses_env = "env" if bool(
            sig.parameters and "env" in list(sig.parameters.keys())
        ) else None
        # Check if the function uses the logger (skip passing self)
        uses_logger = "logger" if bool(
            (sig.parameters and list(sig.parameters.keys())[0] == "logger")
            or (
                [
                    name
                    for name, param in sig.parameters.items()
                    if param.annotation is logging.Logger
                ]
            )
        ) else None
        # Check if the function uses the operation implementation context
        uses_self = bool(
            (sig.parameters and list(sig.parameters.keys())[0] == "self")
            or imp_enter is not None
            or ctx_enter is not None
            or (
                [
                    name
                    for name, param in sig.parameters.items()
                    if param.annotation is OperationImplementationContext
                ]
            )
        )
        # Check if the function uses the operation implementation config
        # This exists because eventually we will make non async functions
        # wrapped with op run with loop.run_in_executor when that happens it's
        # likely that self won't be serializeable into the thread / process.
        # Config's are guaranteed to be serializable, therefore this lets us
        # define operations that have configs and needs to access them when
        # running within another thread.
        uses_config = None
        if config_cls is not None:
            for name, param in sig.parameters.items():
                if param.annotation is config_cls:
                    uses_config = name

        # Definition for inputs of the function
        if not "inputs" in kwargs:
            sig = inspect.signature(func)
            kwargs["inputs"] = {}
            for name, param in sig.parameters.items():
                if name in ("self", "env", "logger"):
                    continue
                name_list = [kwargs["name"], "inputs", name]

                param_annotation = param.annotation
                if forward_refs_from_cls:
                    param_annotation = resolve_if_forward_ref(
                        param_annotation, forward_refs_from_cls
                    )

                if get_origin(param_annotation) in [
                    Union,
                    collections.abc.AsyncIterator,
                ]:
                    param_annotation = list(get_args(param_annotation))[0]
                    param_annotation = resolve_if_forward_ref(
                        param_annotation, forward_refs_from_cls
                    )

                definition_name = ".".join(name_list)
                if hasattr(param_annotation, "__supertype__") and hasattr(
                    param_annotation, "__name__"
                ):
                    definition_name = param_annotation.__name__
                if inspect.isclass(param_annotation) and hasattr(
                    param_annotation, "__qualname__"
                ):
                    definition_name = param_annotation.__qualname__

                if isinstance(param_annotation, Definition):
                    kwargs["inputs"][name] = param_annotation
                else:
                    kwargs["inputs"][name] = create_definition(
                        definition_name,
                        param_annotation,
                        forward_refs_from_cls=forward_refs_from_cls,
                    )

                if param.default is not inspect.Parameter.empty:
                    kwargs["inputs"][name] = kwargs["inputs"][name]._replace(
                        default=param.default
                    )

        auto_def_outputs = False
        # Definition for return type of a function
        if not "outputs" in kwargs:
            return_type = inspect.signature(func).return_annotation
            if return_type not in (None, inspect._empty):
                name_list = [kwargs["name"], "outputs", "result"]

                param_annotation = return_type
                if forward_refs_from_cls:
                    param_annotation = resolve_if_forward_ref(
                        param_annotation, forward_refs_from_cls
                    )

                if get_origin(param_annotation) in [
                    Union,
                    collections.abc.AsyncIterator,
                ]:
                    param_annotation = list(get_args(param_annotation))[0]
                    param_annotation = resolve_if_forward_ref(
                        param_annotation, forward_refs_from_cls
                    )

                definition_name = ".".join(name_list)
                if hasattr(param_annotation, "__supertype__") and hasattr(
                    param_annotation, "__name__"
                ):
                    definition_name = param_annotation.__name__
                if inspect.isclass(param_annotation) and hasattr(
                    param_annotation, "__qualname__"
                ):
                    definition_name = param_annotation.__qualname__

                if isinstance(param_annotation, Definition):
                    definition = param_annotation
                else:
                    definition = create_definition(
                        definition_name,
                        param_annotation,
                        forward_refs_from_cls=forward_refs_from_cls,
                    )

                kwargs["outputs"] = {
                    "result": definition,
                }
                auto_def_outputs = True

        # Support operation defined with one output via auto def or keyword
        # argument.
        if auto_def_outputs:
            nonlocal multi_output
            multi_output = False

        func.op = Operation(**kwargs)
        func.ENTRY_POINT_NAME = ["operation"]
        cls_name = (
            func.op.name.replace(".", " ")
            .replace("_", " ")
            .title()
            .replace(" ", "")
        )

        # Create the test method which creates the contexts and runs
        async def test(**kwargs):
            async with func.imp(BaseConfig()) as obj:
                async with obj(None, None) as ctx:
                    return await ctx.run(kwargs)

        func.test = test

        class Implementation(
            context_stacker(OperationImplementation, imp_enter)
        ):
            def __init__(self, config):
                if config_cls is not None and isinstance(config, dict):
                    if getattr(config_cls, "_fromdict", None) is not None:
                        # Use _fromdict method if it exists
                        config = config_cls._fromdict(**config)
                    else:
                        # Otherwise expand if existing config is a dict
                        config = config_cls(**config)
                super().__init__(config)

        if config_cls is not None:
            Implementation.CONFIG = config_cls

        if inspect.isclass(func) and issubclass(
            func, OperationImplementationContext
        ):
            func.imp = type(
                f"{cls_name}Implementation",
                (Implementation,),
                {"op": func.op, "CONTEXT": func},
            )
            return func
        else:

            class ImplementationContext(
                context_stacker(OperationImplementationContext, ctx_enter)
            ):
                async def run(
                    self, inputs: Dict[str, Any]
                ) -> Union[bool, Dict[str, Any]]:
                    # Comes from top level op scope
                    nonlocal multi_output
                    # Add logger to inputs if it's used by the function
                    if uses_logger:
                        inputs["logger"] = self.logger
                    # Add env to inputs if it's used by the function
                    if uses_env:
                        inputs["env"] = self.env
                    # Add config to inputs if it's used by the function
                    if uses_config is not None:
                        inputs[uses_config] = self.parent.config
                    # If imp_enter or ctx_enter exist then bind the function to
                    # the ImplementationContext so that it has access to the
                    # context and it's parent
                    if uses_self:
                        # We can't pass self to functions running in threads
                        # Its not thread safe!
                        bound = func.__get__(self, self.__class__)
                        result = bound(**inputs)
                        if inspect.isawaitable(result):
                            result = await result
                    elif inspect.iscoroutinefunction(func):
                        result = await func(**inputs)
                    else:
                        # TODO Add auto thread pooling of non-async functions
                        result = func(**inputs)
                    if not multi_output and len(self.parent.op.outputs) == 1:
                        if inspect.isasyncgen(result):

                            async def convert_asyncgen(outputs):
                                async for yielded_output in outputs:
                                    yield {
                                        list(self.parent.op.outputs.keys())[
                                            0
                                        ]: yielded_output
                                    }

                            result = convert_asyncgen(result)
                        elif result is not None and valid_return_none:
                            result = {
                                list(self.parent.op.outputs.keys())[0]: result
                            }
                    return result

            func.imp = type(
                f"{cls_name}Implementation",
                (Implementation,),
                {
                    "op": func.op,
                    "CONTEXT": type(
                        f"{cls_name}ImplementationContext",
                        (ImplementationContext,),
                        {},
                    ),
                },
            )
            return func

    # This case handles if op was called with no arguments, args will be a tuple
    # with one element, that element being func, the function to wrap.
    if args:
        return wrap(args[0])

    return wrap


def opimp_name(item):
    if (
        inspect.isclass(item)
        and issubclass(item, OperationImplementation)
        and item is not OperationImplementation
    ):
        return item.op.name
    if (
        inspect.ismethod(item)
        and issubclass(item.__self__, OperationImplementationContext)
        and item.__name__ == "imp"
    ):
        return item.__self__.op.name
    raise NotOpImp(item)


def isopimp(item):
    """
    Similar to inspect.isclass and that family of functions. Returns true if
    item is a subclass of OperationImpelmentation.
    """
    return bool(
        (
            inspect.isclass(item)
            and issubclass(item, OperationImplementation)
            and item is not OperationImplementation
        )
        or (
            inspect.ismethod(item)
            and issubclass(item.__self__, OperationImplementationContext)
            and item.__name__ == "imp"
        )
    )


def isoperation(item):
    """
    Similar to inspect.isclass and that family of functions. Returns true if
    item is an instance of Operation.
    """
    return bool(isinstance(item, Operation) and item is not Operation)


def isopwraped(item):
    """
    Similar to inspect.isclass and that family of functions. Returns true if a
    function has been wrapped with `op`.
    """
    return bool(
        getattr(item, "op", False)
        and getattr(item, "imp", False)
        and isoperation(item.op)
        and isopimp(item.imp)
    )


def mk_base_in(predicate):
    """
    Creates the functions which use inspect getmembers to extract operations or
    implementations from some list which.
    """

    def base_in(to_check):
        return list(
            map(
                lambda item: item[1],
                inspect.getmembers(
                    to_check
                    if not isinstance(to_check, dict)
                    else types.SimpleNamespace(**to_check),
                    predicate=predicate,
                ),
            )
        )

    return base_in


opwraped_in = mk_base_in(isopwraped)

__operation_in = mk_base_in(isoperation)


def operation_in(iterable):
    return __operation_in(iterable) + list(
        map(lambda item: item.op, opwraped_in(iterable))
    )


__opimp_in = mk_base_in(isopimp)


def opimp_in(iterable):
    return __opimp_in(iterable) + list(
        map(lambda item: item.imp, opwraped_in(iterable))
    )


class BaseKeyValueStoreContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for key value storage context
    """

    @abc.abstractmethod
    async def get(self, key: str) -> Union[bytes, None]:
        """
        Get a value from the key value store
        """

    @abc.abstractmethod
    async def set(self, name: str, value: bytes):
        """
        Get a value in the key value store
        """


@base_entry_point("dffml.kvstore", "kvstore")
class BaseKeyValueStore(BaseDataFlowObject):
    """
    Abstract Base Class for key value storage
    """


class BaseContextHandle(abc.ABC):
    def __init__(self, ctx: "BaseInputSetContext") -> None:
        self.ctx = ctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    def as_string(self) -> str:
        pass


@base_entry_point("dffml.df.input_set_context", "isctx")
class BaseInputSetContext(Entrypoint):
    @abc.abstractmethod
    async def handle(self) -> BaseContextHandle:
        pass


class StringContextHandle(BaseContextHandle):
    def as_string(self) -> str:
        return self.ctx.as_string


class StringInputSetContext(BaseInputSetContext):
    def __init__(self, as_string):
        self.as_string = as_string

    async def handle(self) -> BaseContextHandle:
        return StringContextHandle(self)

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return repr(self)


class BaseInputSetConfig(NamedTuple):
    ctx: BaseInputSetContext


class BaseInputSet(abc.ABC):
    def __init__(self, config: BaseInputSetConfig) -> None:
        self.config = config
        self.ctx = config.ctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def add(self, item: Input) -> None:
        """
        Add an input to the input set.
        """

    @abc.abstractmethod
    async def definitions(self) -> Set[Definition]:
        pass

    @abc.abstractmethod
    async def inputs(self) -> AsyncIterator[Input]:
        pass

    async def _asdict(self) -> Dict[str, Any]:
        """
        Returns an input definition name to input value dict
        """
        return {
            item.definition.name: item.value async for item in self.inputs()
        }

    @abc.abstractmethod
    async def remove_input(self, item: Input) -> None:
        """
        Removes item from input set
        """

    @abc.abstractmethod
    async def remove_unvalidated_inputs(self) -> "BaseInputSet":
        """
        Removes `unvalidated` inputs from internal list and returns the same.
        """


class BaseParameterSetConfig(NamedTuple):
    ctx: BaseInputSetContext


class BaseParameterSet(abc.ABC):
    def __init__(self, config: BaseParameterSetConfig) -> None:
        self.config = config
        self.ctx = config.ctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def parameters(self) -> AsyncIterator[Parameter]:
        pass

    @abc.abstractmethod
    async def inputs_and_parents_recursive(self) -> AsyncIterator[Input]:
        pass

    async def _asdict(self) -> Dict[str, Any]:
        """
        Returns an parameter definition name to parameter value dict
        """
        return {
            parameter.key: parameter.value
            async for parameter in self.parameters()
        }


class BaseDefinitionSetContext(BaseDataFlowObjectContext):
    def __init__(
        self,
        config: BaseConfig,
        parent: "BaseInputNetworkContext",
        ctx: "BaseInputSetContext",
    ) -> None:
        super().__init__(config, parent)
        self.ctx = ctx

    @abc.abstractmethod
    async def inputs(
        self, Definition: Optional[Definition] = None
    ) -> AsyncIterator[Input]:
        """
        Asynchronous iterator of all inputs within a context, which are of a
        definition.
        """


class BaseInputNetworkContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for context managing input_set
    """

    @abc.abstractmethod
    async def add(self, input_set: BaseInputSet):
        """
        Adds new input set to the network
        """

    @abc.abstractmethod
    async def ctx(self) -> BaseInputSetContext:
        """
        Returns when a new input set context has entered the network
        """

    @abc.abstractmethod
    async def added(self, ctx: BaseInputSetContext) -> BaseInputSet:
        """
        Returns when a new input set has entered the network within a context
        """

    @abc.abstractmethod
    async def definition(
        self, ctx: BaseInputSetContext, definition: str
    ) -> Definition:
        """
        Search for the definition within a context given its name as a string.
        Return the definition. Otherwise raise a DefinitionNotInContext
        error. If the context is not present, raise a ContextNotPresent error.
        """

    @abc.abstractmethod
    def definitions(
        self, ctx: BaseInputSetContext
    ) -> BaseDefinitionSetContext:
        """
        Return a DefinitionSet context that can be used to access the inputs
        within the given context, by definition.
        """

    @abc.abstractmethod
    async def gather_inputs(
        self,
        rctx: "BaseRedundancyCheckerContext",
        operation: Operation,
        ctx: Optional[BaseInputSetContext] = None,
    ) -> AsyncIterator[BaseParameterSet]:
        """
        Generate all possible permutations of applicable inputs for an operation
        that, according to the redundancy checker, haven't been run yet.
        """


@base_entry_point("dffml.input.network", "input", "network")
class BaseInputNetwork(BaseDataFlowObject):
    """
    Input networks store all of the input data and output data of operations,
    which in turn becomes input data to other operations.
    """


class OperationImplementationNotInstantiable(Exception):
    """
    OperationImplementation cannot be instantiated and is required to continue.
    """


class OperationImplementationNotInstantiated(Exception):
    """
    OperationImplementation is instantiable, but is not has not been
    instantiated within the network and was required to continue.

    Attempted to run operation which could be instantiated, but has not yet
    been.
    """


class BaseOperationNetworkContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for context managing operations
    """

    @abc.abstractmethod
    async def add(self, operations: List[Operation]):
        """
        Add operations to the network
        """

    @abc.abstractmethod
    async def operations(
        self, input_set: BaseInputSet = None, stage: Stage = Stage.PROCESSING
    ) -> AsyncIterator[Operation]:
        """
        Retrieve all operations in the network of a given stage filtering by
        operations who have inputs with definitions in the input set.
        """


# TODO Make this operate like a BaseInputNetwork were operations can
# be added dynamically
@base_entry_point("dffml.operation.network", "operation", "network")
class BaseOperationNetwork(BaseDataFlowObject):
    """
    Operation networks hold Operation objects to allow for looking up of their
    inputs, outputs, and conditions.
    """


class BaseRedundancyCheckerConfig(NamedTuple):
    key_value_store: BaseKeyValueStore


# TODO store redundancy checks by BaseInputSetContext.handle() and add method
# to remove all associated with a particular handle. Aka allow us to clean up
# the input, redundancy, etc. networks after execution of a context completes
# via the orchestrator.
class BaseRedundancyCheckerContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for redundancy checking context
    """

    @abc.abstractmethod
    async def exists(
        self, operation: Operation, parameter_set: BaseParameterSet
    ) -> bool:
        pass

    @abc.abstractmethod
    async def add(self, operation: Operation, parameter_set: BaseParameterSet):
        pass


@base_entry_point("dffml.redundancy.checker", "rchecker")
class BaseRedundancyChecker(BaseDataFlowObject):
    """
    Redundancy Checkers ensure that each operation within a context only gets
    run with a give permutation of inputs once.
    """


# TODO Provide a way to clear out all locks for inputs within a context
class BaseLockNetworkContext(BaseDataFlowObjectContext):
    @abc.abstractmethod
    async def acquire(self, parameter_set: BaseParameterSet) -> bool:
        """
        An async context manager which will acquire locks of all inputs within
        the parameter set.
        """


@base_entry_point("dffml.lock.network", "lock", "network")
class BaseLockNetwork(BaseDataFlowObject):
    """
    Acquires locks on inputs which may not be used simultaneously
    """


class BaseOperationImplementationNetworkContext(BaseDataFlowObjectContext):
    @abc.abstractmethod
    async def contains(self, operation: Operation) -> bool:
        """
        Checks if the network contains / has the ability to run a given
        operation.
        """

    @abc.abstractmethod
    async def instantiable(self, operation: Operation) -> bool:
        """
        Prior to figuring out which operation implementation networks contain
        an operation, if none do, they will need to instantiate it on the fly.
        """

    @abc.abstractmethod
    async def instantiate(
        self, operation: Operation, config: BaseConfig
    ) -> bool:
        """
        Instantiate a given operation so that it can be run within this network.
        """

    @abc.abstractmethod
    async def run(
        self, operation: Operation, inputs: Dict[str, Any]
    ) -> Union[bool, Dict[str, Any]]:
        """
        Find the operation implementation for the given operation and create an
        operation implementation context, call the run method of the context and
        return the results.
        """

    @abc.abstractmethod
    async def operation_completed(self):
        """
        Returns when an operation finishes
        """

    @abc.abstractmethod
    async def dispatch(
        self,
        ictx: BaseInputNetworkContext,
        lctx: BaseLockNetworkContext,
        operation: Operation,
        parameter_set: BaseParameterSet,
    ):
        """
        Schedule the running of an operation
        """


# TODO We should be able to specify multiple operation implementation  networks.
# This would enable operations to live in different place, accessed via the
# orchestrator transparently. This will probably involve
# dffml.util.asynchelper.AsyncContextManagerList
@base_entry_point("dffml.operation.implementation.network", "opimp", "network")
class BaseOperationImplementationNetwork(BaseDataFlowObject):
    """
    Knows where operations are or if they can be made
    """


class OperationException(Exception):
    """
    Raised by the orchestrator when an operation throws an exception.
    """


@dataclass(frozen=True)
class BaseOrchestratorConfig:
    input_network: BaseInputNetwork
    operation_network: BaseOperationNetwork
    lock_network: BaseLockNetwork
    opimp_network: BaseOperationImplementationNetwork
    rchecker: BaseRedundancyChecker

    def _replace(self, **kwargs):
        return replace(self, **kwargs)


class BaseOrchestratorContext(BaseDataFlowObjectContext):
    @abc.abstractmethod
    async def run_operations(
        self, strict: bool = True
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        """
        Run all the operations then run cleanup and output operations
        """

    @abc.abstractmethod
    async def operations_parameter_set_pairs(
        self,
        ctx: BaseInputSetContext,
        *,
        new_input_set: BaseInputSet = None,
        stage: Stage = Stage.PROCESSING,
    ) -> AsyncIterator[Tuple[Operation, BaseParameterSet]]:
        """
        Use new_input_set to determine which operations in the network might be
        up for running. Cross check using existing inputs to generate per
        input set context novel input pairings. Yield novel input pairings
        along with their operations as they are generated.
        """

    @abc.abstractmethod
    async def modify_dataflow(
        self,
    ) -> AsyncContextManager:
        """
        Take nessicary actions to support modification of config.dataflow
        """


@base_entry_point("dffml.orchestrator", "orchestrator")
class BaseOrchestrator(BaseDataFlowObject):
    @classmethod
    async def run(cls, dataflow, inputs, *, config=None, **kwargs):
        if config is None:
            self = cls.withconfig({})
        else:
            self = cls(config=config, **kwargs)
        async with self as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(inputs):
                    yield ctx, results
