import abc
import inspect
import pkg_resources
from contextlib import AsyncExitStack
from typing import (
    AsyncIterator,
    Dict,
    List,
    Tuple,
    Any,
    NamedTuple,
    Union,
    Optional,
    Set,
)

from .exceptions import NotOpImp
from .types import Operation, Input, Parameter, Stage, Definition

from .log import LOGGER

from ..base import (
    BaseConfig,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.asynchelper import context_stacker, aenter_stack
from ..util.entrypoint import base_entry_point


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
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
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
        Returns the operation implemention from a loaded entrypoint object, or
        None if its not an operation implemention or doesn't have the imp
        parameter which is an operation implemention.
        """
        for obj in [loaded, getattr(loaded, "imp", None)]:
            if inspect.isclass(obj) and issubclass(obj, cls):
                return obj
        return None

    @classmethod
    def load(cls, loading=None):
        loading_classes = []
        # Load operations
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            if loading is not None and i.name == loading:
                loaded = cls._imp(i.load())
                if loaded is not None:
                    return loaded
            elif loading is None:
                loaded = cls._imp(i.load())
                if loaded is not None:
                    loading_classes.append(loaded)
        if loading is not None:
            raise FailedToLoadOperationImplementation(
                "%s was not found in (%s)"
                % (
                    repr(loading),
                    ", ".join(list(map(lambda op: op.name, loading_classes))),
                )
            )
        return loading_classes


def op(imp_enter=None, ctx_enter=None, config_cls=None, **kwargs):
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
    """

    def wrap(func):
        if not "name" in kwargs:
            kwargs["name"] = func.__name__
        # TODO Make this grab from the defaults for Operation
        if not "conditions" in kwargs:
            kwargs["conditions"] = []

        func.op = Operation(**kwargs)
        cls_name = func.op.name.replace("_", " ").title().replace(" ", "")

        sig = inspect.signature(func)
        # Check if the function uses the operation implementation context
        uses_self = bool(
            imp_enter is not None
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
        uses_config = None
        if config_cls is not None:
            for name, param in sig.parameters.items():
                if param.annotation is config_cls:
                    uses_config = name

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
                    # Add config to inputs if it's used by the function
                    if uses_config is not None:
                        inputs[uses_config] = self.parent.config
                    # If imp_enter or ctx_enter exist then bind the function to
                    # the ImplementationContext so that it has access to the
                    # context and it's parent
                    if uses_self:
                        # We can't pass self to functions running in threads
                        # Its not thread safe!
                        return await (
                            func.__get__(self, self.__class__)(**inputs)
                        )
                    elif inspect.iscoroutinefunction(func):
                        return await func(**inputs)
                    else:
                        # TODO Add auto thread pooling of non-async functions
                        return func(**inputs)

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

    >>> # Get all operation implementations imported in a file
    >>> list(map(lambda item: item[1],
    >>>          inspect.getmembers(sys.modules[__name__],
    >>>                             predicate=isopimp)))
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

    >>> # Get all operations imported in a file
    >>> list(map(lambda item: item[1],
    >>>          inspect.getmembers(sys.modules[__name__],
    >>>                             predicate=isoperation)))
    """
    return bool(isinstance(item, Operation) and item is not Operation)


def isopwraped(item):
    """
    Similar to inspect.isclass and that family of functions. Returns true if a
    function has been wrapped with `op`.

    >>> # Get all functions imported in a file that have been wrapped with `op`
    >>> list(map(lambda item: item[1],
    >>>          inspect.getmembers(sys.modules[__name__],
    >>>                             predicate=isopwraped)))
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
                inspect.getmembers(to_check, predicate=predicate),
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


class BaseInputSetContext(abc.ABC):
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
    async def inputs(self) -> AsyncIterator[Input]:
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
    async def inputs(self, Definition: Definition) -> AsyncIterator[Input]:
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
    def definition(self, ctx: BaseInputSetContext) -> BaseDefinitionSetContext:
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

    @abc.abstractmethod
    async def operations_parameter_set_pairs(
        self,
        ictx: BaseInputNetworkContext,
        octx: BaseOperationNetworkContext,
        rctx: BaseRedundancyCheckerContext,
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


# TODO We should be able to specify multiple operation implementation  networks.
# This would enable operations to live in different place, accessed via the
# orchestrator transparently. This will probably invlove
# dffml.util.asynchelper.AsyncContextManagerList
@base_entry_point("dffml.operation.implementation.network", "opimp", "network")
class BaseOperationImplementationNetwork(BaseDataFlowObject):
    """
    Knows where operations are or if they can be made
    """


class BaseOrchestratorConfig(BaseConfig, NamedTuple):
    input_network: BaseInputNetwork
    operation_network: BaseOperationNetwork
    lock_network: BaseLockNetwork
    opimp_network: BaseOperationImplementationNetwork
    rchecker: BaseRedundancyChecker


class BaseOrchestratorContext(BaseDataFlowObjectContext):
    @abc.abstractmethod
    async def run_operations(
        self, strict: bool = True
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        """
        Run all the operations then run cleanup and output operations
        """


@base_entry_point("dffml.orchestrator", "orchestrator")
class BaseOrchestrator(BaseDataFlowObject):
    pass  # pragma: no cov
