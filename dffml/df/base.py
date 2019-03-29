import abc
import inspect
import pkg_resources
from typing import AsyncIterator, Dict, List, Tuple, Any, NamedTuple, Union, \
                   Optional

from .exceptions import NotOpImp
from .types import Operation, Input, Parameter, Stage, Definition

from .log import LOGGER

from ..util.cli.base import Arg, CMD
from ..util.entrypoint import Entrypoint

class DFEntrypoint(abc.ABC, Entrypoint):

    @classmethod
    @abc.abstractmethod
    def args(cls) -> Dict[str, Arg]:
        pass

    @classmethod
    @abc.abstractmethod
    def config(cls, cmd: CMD):
        pass

class OperationImplementationContext(abc.ABC):

    def __init__(self,
                 parent: 'OperationImplementation',
                 ctx: 'BaseInputSetContext',
                 ictx: 'BaseInputNetworkContext') -> None:
        self.parent = parent
        self.ctx = ctx
        self.ictx = ictx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def run(self, inputs: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        pass

    async def __aenter__(self) -> 'OperationImplementationContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @classmethod
    def implementation(cls, operation: Operation):
        class Implementation(OperationImplementation):

            op = operation

            def __init__(self, config: 'BaseConfig') -> None:
                self.config = config

            def __call__(self,
                         ctx: 'BaseInputSetContext',
                         ictx: 'BaseInputNetworkContext') -> cls:
                return cls(self, ctx, ictx)

        return Implementation

    @classmethod
    def imp(cls, config: 'BaseConfig'):
        return cls.implementation(cls.op)(config)

class OperationImplementation(object):

    ENTRY_POINT = 'dffml.operation.implementation'

    def __init__(self, config: 'BaseConfig') -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)
        if not getattr(self, 'op', False):
            raise ValueError('OperationImplementation\'s may not be ' + \
                             'created without an `op`')

    @abc.abstractmethod
    async def __call__(self,
                       ctx: 'BaseInputSetContext',
                       ictx: 'BaseInputNetworkContext') \
            -> OperationImplementationContext:
        return OperationImplementationContext(self, ictx)

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @classmethod
    def load(cls, loading=None):
        '''
        Loads all installed loading and returns them as a list. Sources to be
        loaded should be registered to ENTRY_POINT via setuptools.
        '''
        raise NotImplementedError()

    @classmethod
    def load_multiple(cls, to_load: List[str]):
        '''
        Loads each class requested without instantiating it.
        '''
        loading_classes = {}
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            loaded = i.load()
            if isopimp(loaded):
                loading_classes[opimp_name(loaded)] = loaded
        for loading in to_load:
            if not loading in loading_classes:
                raise KeyError('%s was not found in (%s)' % \
                        (repr(loading),
                         ', '.join(list(map(str, loading_classes)))))
        return loading_classes

def op(**kwargs):
    def wrap(func):

        if not 'name' in kwargs:
            kwargs['name'] = func.__name__
        # TODO Make this grab from the defaults for Operation
        if not 'conditions' in kwargs:
            kwargs['conditions'] = []

        func.op = Operation(**kwargs)

        class ImplementationContext(OperationImplementationContext):

            async def run(self, inputs: Dict[str, Any]) \
                    -> Union[bool, Dict[str, Any]]:
                return await func(**inputs)

        func.imp = ImplementationContext.implementation(func.op)

        return func

    return wrap

def opimp_name(item):
    if inspect.isclass(item) \
            and issubclass(item, OperationImplementation) \
            and item is not OperationImplementation:
        return item.op.name
    if inspect.ismethod(item) \
            and issubclass(item.__self__, OperationImplementationContext) \
            and item.__name__ == 'imp':
        return item.__self__.op.name
    raise NotOpImp(item)

def isopimp(item):
    '''
    Similar to inspect.isclass and that family of functions. Returns true if
    item is a subclass of OperationImpelmentation.

    >>> # Get all operation implementations imported in a file
    >>> list(map(lambda item: item[1],
    >>>          inspect.getmembers(sys.modules[__name__],
    >>>                             predicate=isopimp)))
    '''
    return bool((inspect.isclass(item) \
                 and issubclass(item, OperationImplementation) \
                 and item is not OperationImplementation) \
                or \
                (inspect.ismethod(item) \
                 and issubclass(item.__self__, OperationImplementationContext) \
                 and item.__name__ == 'imp'))

def isoperation(item):
    '''
    Similar to inspect.isclass and that family of functions. Returns true if
    item is an instance of Operation.

    >>> # Get all operations imported in a file
    >>> list(map(lambda item: item[1],
    >>>          inspect.getmembers(sys.modules[__name__],
    >>>                             predicate=isoperation)))
    '''
    return bool(isinstance(item, Operation) \
                and item is not Operation)

def isopwraped(item):
    '''
    Similar to inspect.isclass and that family of functions. Returns true if a
    function has been wrapped with `op`.

    >>> # Get all functions imported in a file that have been wrapped with `op`
    >>> list(map(lambda item: item[1],
    >>>          inspect.getmembers(sys.modules[__name__],
    >>>                             predicate=isopwraped)))
    '''
    return bool(getattr(item, 'op', False) \
                and getattr(item, 'imp', False) \
                and isoperation(item.op) \
                and isopimp(item.imp))

def mk_base_in(predicate):
    '''
    Creates the functions which use inspect getmembers to extract operations or
    implementations from some list which.
    '''
    def base_in(to_check):
        return list(map(lambda item: item[1],
                        inspect.getmembers(to_check, predicate=predicate)))
    return base_in

opwraped_in = mk_base_in(isopwraped)
operation_in = mk_base_in(isoperation)
opimp_in = mk_base_in(isopimp)

class BaseConfig(NamedTuple):
    pass

class BaseKeyValueStoreContext(abc.ABC):
    '''
    Abstract Base Class for key value storage context
    '''

    def __init__(self, parent: 'BaseKeyValueStore') -> None:
        self.parent = parent
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def get(self, key: str) -> Union[bytes, None]:
        pass

    @abc.abstractmethod
    async def set(self, name: str, value: bytes):
        pass

class BaseKeyValueStore(DFEntrypoint):
    '''
    Abstract Base Class for key value storage
    '''

    ENTRY_POINT = 'dffml.kvstore'

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def __aenter__(self) -> BaseKeyValueStoreContext:
        pass

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseContextHandle(abc.ABC):

    def __init__(self, ctx: 'BaseInputSetContext') -> None:
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
    async def inputs(self) -> AsyncIterator[Input]:
        pass

    async def _asdict(self) -> Dict[str, Any]:
        '''
        Returns an input definition name to input value dict
        '''
        return {item.definition.name: item.value \
                  async for item in self.inputs()}

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
        '''
        Returns an parameter definition name to parameter value dict
        '''
        return {parameter.key: parameter.value \
                async for parameter in self.parameters()}

class BaseDefinitionSetContext(abc.ABC):

    def __init__(self,
                 parent: 'BaseInputNetworkContext',
                 ctx: 'BaseInputSetContext') -> None:
        self.parent = parent
        self.ctx = ctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def inputs(self, Definition: Definition) -> AsyncIterator[Input]:
        '''
        Asynchronous iterator of all inputs within a context, which are of a
        definition.
        '''
        pass

    async def __aenter__(self) -> 'BaseDefinitionSetContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseInputNetworkContext(abc.ABC):
    '''
    Abstract Base Class for context managing input_set
    '''

    def __init__(self, parent: 'BaseInputNetwork') -> None:
        self.parent = parent
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def add(self, input_set: BaseInputSet):
        '''
        Adds new input set to the network
        '''
        pass

    @abc.abstractmethod
    async def ctx(self) -> BaseInputSetContext:
        '''
        Returns when a new input set context has entered the network
        '''
        pass

    @abc.abstractmethod
    async def added(self, ctx: BaseInputSetContext) -> BaseInputSet:
        '''
        Returns when a new input set has entered the network within a context
        '''
        pass

    @abc.abstractmethod
    async def definition(self, ctx: BaseInputSetContext, definition: str) \
            -> Definition:
        '''
        Search for the definition within a context given its name as a string.
        Return the definition. Otherwise raise a DefinitionNotInContext
        error. If the context is not present, raise a ContextNotPresent error.
        '''
        pass

    @abc.abstractmethod
    def definition(self, ctx: BaseInputSetContext) -> BaseDefinitionSetContext:
        '''
        Return a DefinitionSet context that can be used to access the inputs
        within the given context, by definition.
        '''
        pass

    @abc.abstractmethod
    async def gather_inputs(self,
                            rctx: 'BaseRedundancyCheckerContext',
                            operation: Operation,
                            ctx: Optional[BaseInputSetContext] = None) \
                                    -> AsyncIterator[BaseParameterSet]:
        '''
        Generate all possible permutations of applicable inputs for an operation
        that, according to the redundancy checker, haven't been run yet.
        '''
        pass

    async def __aenter__(self) -> 'BaseInputNetworkContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseInputNetwork(DFEntrypoint):
    '''
    Abstract Base Class for managing input_set
    '''

    ENTRY_POINT = 'dffml.input.network'

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    def __call__(self) -> 'BaseInputNetworkContext':
        pass

class BaseOperationNetworkContext(abc.ABC):
    '''
    Abstract Base Class for context managing operations
    '''

    def __init__(self, parent: 'BaseOperationNetwork') -> None:
        self.parent = parent
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def add(self, operations: List[Operation]):
        pass

    @abc.abstractmethod
    async def operations(self,
            input_set: BaseInputSet = None,
            stage: Stage = Stage.PROCESSING) -> AsyncIterator[Operation]:
        pass

    async def __aenter__(self) -> 'BaseOperationNetworkContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

# TODO Make this operate like a BaseInputNetwork were operations can
# be added dynamically
class BaseOperationNetwork(DFEntrypoint):
    '''
    Abstract Base Class for managing operations
    '''

    ENTRY_POINT = 'dffml.operation.network'

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    def __call__(self) -> 'BaseOperationNetworkContext':
        pass

class BaseRedundancyCheckerConfig(NamedTuple):
    key_value_store: BaseKeyValueStore

# TODO store redundancy checks by BaseInputSetContext.handle() and add method
# to remove all associated with a particular handle. Aka allow us to clean up
# the input, redundancy, etc. networks after execution of a context completes
# via the orchestrator.
class BaseRedundancyCheckerContext(abc.ABC):
    '''
    Abstract Base Class for redundancy checking context
    '''

    def __init__(self, parent: 'BaseRedundancyChecker') -> None:
        self.parent = parent
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def exists(self,
            operation: Operation,
            parameter_set: BaseParameterSet) -> bool:
        pass

    @abc.abstractmethod
    async def add(self,
            operation: Operation,
            parameter_set: BaseParameterSet):
        pass

    async def __aenter__(self) -> 'BaseRedundancyCheckerContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseRedundancyChecker(DFEntrypoint):
    '''
    Abstract Base Class for redundancy checking
    '''

    ENTRY_POINT = 'dffml.redundancy.checker'

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    async def __call__(self) -> BaseRedundancyCheckerContext:
        return BaseRedundancyCheckerContext(self)

# TODO Provide a way to clear out all locks for inputs within a context
class BaseLockNetworkContext(abc.ABC):

    def __init__(self, parent: 'BaseLockNetwork') -> None:
        self.parent = parent
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def acquire(self, parameter_set: BaseParameterSet) -> bool:
        pass

    async def __aenter__(self) -> 'BaseLockNetworkContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseLockNetwork(DFEntrypoint):
    '''
    Acquires locks on inputs which may not be used simultaneously
    '''

    ENTRY_POINT = 'dffml.lock.network'

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    def __call__(self) -> BaseLockNetworkContext:
        pass

class BaseOperationImplementationNetworkContext(abc.ABC):

    def __init__(self, parent: 'BaseOperationImplementationNetwork') -> None:
        self.parent = parent
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def contains(self, operation: Operation) -> bool:
        pass

    @abc.abstractmethod
    async def instantiable(self, operation: Operation) -> bool:
        pass

    @abc.abstractmethod
    async def instantiate(self, operation: Operation,
            config: BaseConfig) -> bool:
        pass

    @abc.abstractmethod
    async def run(self, operation: Operation,
            inputs: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        pass

    @abc.abstractmethod
    async def operation_completed(self):
        '''
        Returns when an operation finishes
        '''
        pass

    @abc.abstractmethod
    async def dispatch(self,
            ictx: BaseInputNetworkContext,
            lctx: BaseLockNetworkContext,
            operation: Operation,
            parameter_set: BaseParameterSet):
        '''
        Schedule the running of an operation
        '''
        pass

    @abc.abstractmethod
    async def operations_parameter_set_pairs(self,
            ictx: BaseInputNetworkContext,
            octx: BaseOperationNetworkContext,
            rctx: BaseRedundancyCheckerContext,
            ctx: BaseInputSetContext,
            *,
            new_input_set: BaseInputSet = None,
            stage: Stage = Stage.PROCESSING) -> \
                    AsyncIterator[Tuple[Operation, BaseParameterSet]]:
        '''
        Use new_input_set to determine which operations in the network might be
        up for running. Cross check using existing inputs to generate per
        input set context novel input pairings. Yield novel input pairings
        along with their operations as they are generated.
        '''
        pass

    async def __aenter__(self) -> 'BaseOperationImplementationNetworkContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseOperationImplementationNetwork(DFEntrypoint):
    '''
    Knows where operations are or if they can be made
    '''

    ENTRY_POINT = 'dffml.operation.implementation.network'

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    def __call__(self) -> BaseOperationImplementationNetworkContext:
        pass

class BaseOrchestratorContext(object):

    def __init__(self,
            ictx: BaseInputNetworkContext,
            octx: BaseOperationNetworkContext,
            lctx: BaseLockNetworkContext,
            nctx: BaseOperationImplementationNetworkContext,
            rctx: BaseRedundancyCheckerContext) -> None:
        self.ictx = ictx
        self.octx = octx
        self.lctx = lctx
        self.nctx = nctx
        self.rctx = rctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def run_operations(self) \
            -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        '''
        Run all Stage.PROCESSING operations
        '''
        pass

    async def run_until_complete(self) \
            -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        '''
        Run all the operations then run cleanup and output operations
        '''
        # Run all operations until no more are run
        async for ctx, results in self.run_operations():
            yield ctx, results

    async def __aenter__(self) -> 'BaseOrchestratorContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseOrchestrator(DFEntrypoint):

    CONTEXT = BaseOrchestratorContext

    ENTRY_POINT = 'dffml.orchestrator'

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    def __call__(self,
            ictx: BaseInputNetworkContext,
            octx: BaseOperationNetworkContext,
            lctx: BaseLockNetworkContext,
            nctx: BaseOperationImplementationNetworkContext,
            rctx: BaseRedundancyCheckerContext) -> 'BaseOrchestratorContext':
        return self.CONTEXT(ictx=ictx, octx=octx, lctx=lctx, nctx=nctx,
                            rctx=rctx)
