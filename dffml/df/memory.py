import io
import asyncio
import secrets
import hashlib
import inspect
import itertools
import traceback
from datetime import datetime
from itertools import product, chain
from contextlib import asynccontextmanager, AsyncExitStack
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

from .exceptions import ContextNotPresent, DefinitionNotInContext
from .types import Input, Parameter, Definition, Operation, Stage, DataFlow
from .base import (
    OperationImplementation,
    FailedToLoadOperationImplementation,
    BaseDataFlowObject,
    BaseDataFlowObjectContext,
    BaseConfig,
    BaseContextHandle,
    BaseKeyValueStoreContext,
    BaseKeyValueStore,
    BaseInputSetContext,
    StringInputSetContext,
    BaseInputSet,
    BaseParameterSet,
    BaseDefinitionSetContext,
    BaseInputNetworkContext,
    BaseInputNetwork,
    BaseOperationNetworkContext,
    BaseOperationNetwork,
    BaseRedundancyCheckerConfig,
    BaseRedundancyCheckerContext,
    BaseRedundancyChecker,
    BaseLockNetworkContext,
    BaseLockNetwork,
    OperationImplementationNotInstantiated,
    OperationImplementationNotInstantiable,
    BaseOperationImplementationNetworkContext,
    BaseOperationImplementationNetwork,
    BaseOrchestratorConfig,
    BaseOrchestratorContext,
    BaseOrchestrator,
)

from ..util.entrypoint import entry_point, EntrypointNotFound
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.data import ignore_args, traverse_get
from ..util.asynchelper import context_stacker, aenter_stack

from .log import LOGGER


class MemoryDataFlowObjectContextConfig(NamedTuple):
    # Unique ID of the context, in other implementations this might be a JWT or
    # something
    uid: str


class BaseMemoryDataFlowObject(BaseDataFlowObject):
    def __call__(self) -> BaseDataFlowObjectContext:
        return self.CONTEXT(
            MemoryDataFlowObjectContextConfig(uid=secrets.token_hex()), self
        )


class MemoryKeyValueStoreContext(BaseKeyValueStoreContext):
    def __init__(
        self, config: BaseConfig, parent: "MemoryKeyValueStore"
    ) -> None:
        super().__init__(config, parent)
        self.memory: Dict[str, bytes] = {}
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Union[bytes, None]:
        async with self.lock:
            return self.memory.get(key)

    async def set(self, key: str, value: bytes):
        async with self.lock:
            self.memory[key] = value


@entry_point("memory")
class MemoryKeyValueStore(BaseKeyValueStore, BaseMemoryDataFlowObject):
    """
    Key Value store backed by dict
    """

    CONTEXT = MemoryKeyValueStoreContext


class MemoryInputSetConfig(NamedTuple):
    ctx: BaseInputSetContext
    inputs: List[Input]


class MemoryInputSet(BaseInputSet):
    def __init__(self, config: MemoryInputSetConfig) -> None:
        super().__init__(config)
        self.__inputs = config.inputs

    async def add(self, item: Input) -> None:
        self.__inputs.append(item)

    async def definitions(self) -> Set[Definition]:
        return set(map(lambda item: item.definition, self.__inputs))

    async def inputs(self) -> AsyncIterator[Input]:
        for item in self.__inputs:
            yield item


class MemoryParameterSetConfig(NamedTuple):
    ctx: BaseInputSetContext
    parameters: List[Parameter]


class MemoryParameterSet(BaseParameterSet):
    def __init__(self, config: MemoryParameterSetConfig) -> None:
        super().__init__(config)
        self.__parameters = config.parameters

    async def parameters(self) -> AsyncIterator[Parameter]:
        for parameter in self.__parameters:
            yield parameter

    async def inputs(self) -> AsyncIterator[Input]:
        for item in itertools.chain(
            *[
                [parameter.origin] + list(parameter.origin.get_parents())
                for parameter in self.__parameters
            ]
        ):
            yield item


class NotificationSetContext(object):
    def __init__(self, parent: "NotificationSet") -> None:
        self.parent = parent
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    async def add(self, notification_item: Any, set_items: List[Any]):
        """
        Add set_items to set and notification_item to the notification queue
        """
        async with self.parent.lock:
            self.parent.notification_items.append(notification_item)
            self.parent.event_added.set()

    async def added(self) -> Tuple[bool, List[Any]]:
        """
        Gets item from FIFO notification queue. Returns a bool for if there are
        more items to get and one of the items.
        """
        more = True
        # Make sure waiting on event_added is done by one coroutine at a time.
        # Multiple might be waiting and if there is only one event in the queue
        # they would all otherwise be triggered
        async with self.parent.event_added_lock:
            await self.parent.event_added.wait()
            async with self.parent.lock:
                notification_item = self.parent.notification_items.pop(0)
                # If there are still more items that the added event hasn't
                # processed then make sure we will return immediately if called
                # again
                if not self.parent.notification_items:
                    more = False
                    self.parent.event_added.clear()
                return more, notification_item

    async def __aenter__(self) -> "NotificationSetContext":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass


class NotificationSet(object):
    """
    Set which can notifies user when it was added to (FIFO)
    """

    def __init__(self) -> None:
        # TODO audit use of memory (should be used sparingly)
        self.lock = asyncio.Lock()
        self.event_added = asyncio.Event()
        self.event_added_lock = asyncio.Lock()
        self.notification_items = []

    def __call__(self) -> NotificationSetContext:
        return NotificationSetContext(self)


class MemoryInputNetworkContextEntry(NamedTuple):
    ctx: BaseInputSetContext
    definitions: Dict[Definition, List[Input]]
    by_origin: Dict[Union[str, Tuple[str, str]], List[Input]]


class MemoryDefinitionSetContext(BaseDefinitionSetContext):
    async def inputs(self, definition: Definition) -> AsyncIterator[Input]:
        # Grab the input set context handle
        handle = await self.ctx.handle()
        handle_string = handle.as_string()
        # Associate inputs with their context handle grouped by definition
        async with self.parent.ctxhd_lock:
            # Yield all items under the context for the given definition
            entry = self.parent.ctxhd[handle_string]
            for item in entry.definitions[definition]:
                yield item


class MemoryInputNetworkContext(BaseInputNetworkContext):
    def __init__(
        self, config: BaseConfig, parent: "MemoryInputNetwork"
    ) -> None:
        super().__init__(config, parent)
        self.ctx_notification_set = NotificationSet()
        self.input_notification_set = {}
        # Organize by context handle string then by definition within that
        self.ctxhd: Dict[str, Dict[Definition, Any]] = {}
        # TODO Create ctxhd_locks dict to manage a per context lock
        self.ctxhd_lock = asyncio.Lock()

    async def add(self, input_set: BaseInputSet):
        # Grab the input set context handle
        handle = await input_set.ctx.handle()
        handle_string = handle.as_string()
        # TODO These ctx.add calls should probably happen after inputs are in
        # self.ctxhd
        # If the context for this input set does not exist create a
        # NotificationSet for it to notify the orchestrator
        if not handle_string in self.input_notification_set:
            self.input_notification_set[handle_string] = NotificationSet()
            async with self.ctx_notification_set() as ctx:
                await ctx.add(input_set.ctx, [])
        # Add the input set to the incoming inputs
        async with self.input_notification_set[handle_string]() as ctx:
            await ctx.add(
                input_set, [item async for item in input_set.inputs()]
            )
        # Associate inputs with their context handle grouped by definition
        async with self.ctxhd_lock:
            # Create dict for handle_string if not present
            if not handle_string in self.ctxhd:
                self.ctxhd[handle_string] = MemoryInputNetworkContextEntry(
                    ctx=input_set.ctx, definitions={}, by_origin={}
                )
            # Go through each item in the input set
            async for item in input_set.inputs():
                # Create set for item definition if not present
                if (
                    not item.definition
                    in self.ctxhd[handle_string].definitions
                ):
                    self.ctxhd[handle_string].definitions[item.definition] = []
                # Add input to by defintion set
                self.ctxhd[handle_string].definitions[item.definition].append(
                    item
                )
                # Create set for item origin if not present
                if not item.origin in self.ctxhd[handle_string].by_origin:
                    self.ctxhd[handle_string].by_origin[item.origin] = []
                # Add input to by origin set
                self.ctxhd[handle_string].by_origin[item.origin].append(item)

    async def uadd(self, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with a StringInputSetContext
        containing a random value for the string.
        """
        # TODO(security) Allow for tuning nbytes
        return await self.sadd(secrets.token_hex(), *args)

    async def sadd(self, context_handle_string, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with a StringInputSetContext.

        >>> await octx.ictx.add(
        ...     MemoryInputSet(
        ...         MemoryInputSetConfig(
        ...             ctx=StringInputSetContext(context_handle_string),
        ...             inputs=list(args),
        ...         )
        ...     )
        ... )
        """
        ctx = StringInputSetContext(context_handle_string)
        await self.add(
            MemoryInputSet(MemoryInputSetConfig(ctx=ctx, inputs=list(args)))
        )
        return ctx

    async def cadd(self, ctx, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with an existing context.

        >>> await octx.ictx.add(
        ...     MemoryInputSet(
        ...         MemoryInputSetConfig(
        ...             ctx=ctx,
        ...             inputs=list(args),
        ...         )
        ...     )
        ... )
        """
        await self.add(
            MemoryInputSet(MemoryInputSetConfig(ctx=ctx, inputs=list(args)))
        )
        return ctx

    async def ctx(self) -> Tuple[bool, BaseInputSetContext]:
        async with self.ctx_notification_set() as ctx:
            return await ctx.added()

    async def added(
        self, watch_ctx: BaseInputSetContext
    ) -> Tuple[bool, BaseInputSet]:
        # Grab the input set context handle
        handle_string = (await watch_ctx.handle()).as_string()
        # Notify whatever is listening for new inputs in this context
        async with self.input_notification_set[handle_string]() as ctx:
            """
            return await ctx.added()
            """
            async with ctx.parent.event_added_lock:
                await ctx.parent.event_added.wait()
                ctx.parent.event_added.clear()
                async with ctx.parent.lock:
                    notification_items = ctx.parent.notification_items
                    ctx.parent.notification_items = []
                    return False, notification_items

    async def definition(
        self, ctx: BaseInputSetContext, definition: str
    ) -> Definition:
        async with self.ctxhd_lock:
            # Grab the input set context handle
            handle_string = (await ctx.handle()).as_string()
            # Ensure that the handle_string is present in ctxhd
            if not handle_string in self.ctxhd:
                raise ContextNotPresent(handle_string)
            # Search through the definitions to find one with a matching name
            found = list(
                filter(
                    lambda check: check.name == definition,
                    self.ctxhd[handle_string].definitions,
                )
            )
            # Raise an error if the definition was not found in given context
            if not found:
                raise DefinitionNotInContext(
                    "%s: %s" % (handle_string, definition)
                )
            # If found then return the definition
            return found[0]

    def definitions(
        self, ctx: BaseInputSetContext
    ) -> BaseDefinitionSetContext:
        return MemoryDefinitionSetContext(self.config, self, ctx)

    async def gather_inputs(
        self,
        rctx: "BaseRedundancyCheckerContext",
        operation: Operation,
        dataflow: DataFlow,
        ctx: Optional[BaseInputSetContext] = None,
    ) -> AsyncIterator[BaseParameterSet]:
        # Create a mapping of definitions to inputs for that definition
        gather: Dict[str, List[Parameter]] = {}
        async with self.ctxhd_lock:
            # If no context is given we will generate input pairs for all
            # contexts
            contexts = self.ctxhd.values()
            # If a context is given only search definitions within that context
            if not ctx is None:
                # Grab the input set context handle
                handle_string = (await ctx.handle()).as_string()
                # Ensure that the handle_string is present in ctxhd
                if not handle_string in self.ctxhd:
                    return
                # Limit search to given context via context handle
                contexts = [self.ctxhd[handle_string]]
            for ctx, _, by_origin in contexts:
                # Grab the input flow to check for definition overrides
                input_flow = dataflow.flow[operation.instance_name]
                # TODO(p1) This only checks that Inputs that are present are
                # true. If there are none present, the operation will run
                # Check that all conditions are present and logicly True
                for i, condition_source in enumerate(input_flow.conditions):
                    # Create a list of places this input originates from
                    origins = []
                    if isinstance(condition_source, dict):
                        for origin in condition_source.items():
                            origins.append(origin)
                    else:
                        origins.append(condition_source)
                    # Ensure all conditions from all origins are True
                    for origin in origins:
                        # Bail if the condition doesn't exist
                        if not origin in by_origin:
                            return
                        # Bail if the condition is not True
                        for item in by_origin[origin]:
                            # TODO(p2) Alright, this shits fucked, way not clean
                            # / clear. We're just trying to skip any conditions
                            # (and inputs for input_flow.inputs.items()) where
                            # the definition doesn't match, but it's within the
                            # correct origin.
                            if isinstance(condition_source, str):
                                if (
                                    item.definition.name
                                    != operation.conditions[i].name
                                ):
                                    continue
                            elif (
                                item.definition.name
                                != dataflow.operations[origin[0]]
                                .outputs[origin[1]]
                                .name
                            ):
                                continue
                            if not bool(item.value):
                                return
                # Gather all inputs with matching definitions and contexts
                for input_name, input_sources in input_flow.inputs.items():
                    for input_source in input_sources:
                        # Create a list of places this input originates from
                        origins = []
                        if isinstance(input_source, dict):
                            for origin in input_source.items():
                                origins.append(origin)
                        else:
                            origins.append(input_source)
                        # Create parameters for all the inputs
                        gather[input_name] = []
                        for origin in origins:
                            # Don't try to grab inputs from an origin that
                            # doesn't have any to give us
                            if not origin in by_origin:
                                continue
                            # Generate parameters from inputs
                            for item in by_origin[origin]:
                                # TODO(p2) We favored comparing names to
                                # defintions because sometimes we create
                                # defintions which have specs which create new
                                # types which will not equal each other. We
                                # maybe want to consider switching to comparing
                                # exported Defintions
                                if isinstance(input_source, str):
                                    if (
                                        item.definition.name
                                        != operation.inputs[input_name].name
                                    ):
                                        continue
                                elif (
                                    item.definition.name
                                    != dataflow.operations[origin[0]]
                                    .outputs[origin[1]]
                                    .name
                                ):
                                    continue
                                gather[input_name].append(
                                    Parameter(
                                        key=input_name,
                                        value=item.value,
                                        origin=item,
                                        definition=operation.inputs[
                                            input_name
                                        ],
                                    )
                                )
                        # Return if there is no data for an input
                        if not gather[input_name]:
                            return
        # Generate all possible permutations of applicable inputs
        for permutation in product(*list(gather.values())):
            # Create the parameter set
            parameter_set = MemoryParameterSet(
                MemoryParameterSetConfig(ctx=ctx, parameters=permutation)
            )
            # Check if this permutation has been executed before
            if not await rctx.exists(operation, parameter_set):
                # If not then return the permutation
                yield parameter_set


@entry_point("memory")
class MemoryInputNetwork(BaseInputNetwork, BaseMemoryDataFlowObject):
    """
    Inputs backed by a set
    """

    CONTEXT = MemoryInputNetworkContext


class MemoryOperationNetworkConfig(NamedTuple):
    # Starting set of operations
    operations: List[Operation]


class MemoryOperationNetworkContext(BaseOperationNetworkContext):
    def __init__(
        self, config: BaseConfig, parent: "MemoryOperationNetwork"
    ) -> None:
        super().__init__(config, parent)
        self.memory = {}
        self.lock = asyncio.Lock()

    async def add(self, operations: List[Operation]):
        async with self.lock:
            for operation in operations:
                self.memory[operation.instance_name] = operation

    async def operations(
        self,
        dataflow: DataFlow,
        *,
        input_set: Optional[BaseInputSet] = None,
        stage: Stage = Stage.PROCESSING,
    ) -> AsyncIterator[Operation]:
        operations: Dict[str, Operation] = {}
        if stage not in dataflow.by_origin:
            return
        if input_set is None:
            for operation in chain(*dataflow.by_origin[stage].values()):
                operations[operation.instance_name] = operation
        else:
            async for item in input_set.inputs():
                origin = item.origin
                if isinstance(origin, Operation):
                    origin = origin.instance_name
                if origin not in dataflow.by_origin[stage]:
                    continue
                for operation in dataflow.by_origin[stage][origin]:
                    operations[operation.instance_name] = operation
        for operation in operations.values():
            yield operation


@entry_point("memory")
class MemoryOperationNetwork(BaseOperationNetwork, BaseMemoryDataFlowObject):
    """
    Operations backed by a set
    """

    CONTEXT = MemoryOperationNetworkContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args, above, "ops", Arg(type=Operation.load, nargs="+", default=[])
        )
        return args

    @classmethod
    def config(cls, config, *above) -> MemoryOperationNetworkConfig:
        return MemoryOperationNetworkConfig(
            operations=cls.config_get(config, above, "ops")
        )


class MemoryRedundancyCheckerContext(BaseRedundancyCheckerContext):
    def __init__(
        self, config: BaseConfig, parent: "MemoryRedundancyChecker"
    ) -> None:
        super().__init__(config, parent)
        self.kvctx = None

    async def __aenter__(self) -> "MemoryRedundancyCheckerContext":
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.kvctx = await self.__stack.enter_async_context(
            self.parent.key_value_store()
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__stack.aclose()

    async def unique(
        self, operation: Operation, parameter_set: BaseParameterSet
    ) -> str:
        """
        SHA384 hash of the parameter set context handle as a string, the
        operation.instance_name, and the sorted list of input uuids.
        """
        uid_list = sorted(
            map(
                lambda x: x.uid,
                [item async for item in parameter_set.inputs()],
            )
        )
        uid_list.insert(0, (await parameter_set.ctx.handle()).as_string())
        uid_list.insert(0, operation.instance_name)
        return hashlib.sha384(", ".join(uid_list).encode("utf-8")).hexdigest()

    async def exists(
        self, operation: Operation, parameter_set: BaseParameterSet
    ) -> bool:
        # self.logger.debug('checking parameter_set: %s', list(map(
        #     lambda p: p.value,
        #     [p async for p in parameter_set.parameters()])))
        if (
            await self.kvctx.get(await self.unique(operation, parameter_set))
            != "\x01"
        ):
            return False
        return True

    async def add(self, operation: Operation, parameter_set: BaseParameterSet):
        # self.logger.debug('adding parameter_set: %s', list(map(
        #     lambda p: p.value,
        #     [p async for p in parameter_set.parameters()])))
        await self.kvctx.set(
            await self.unique(operation, parameter_set), "\x01"
        )


@entry_point("memory")
class MemoryRedundancyChecker(BaseRedundancyChecker, BaseMemoryDataFlowObject):
    """
    Redundancy Checker backed by Memory Key Value Store
    """

    CONTEXT = MemoryRedundancyCheckerContext

    async def __aenter__(self) -> "MemoryRedundancyCheckerContext":
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.key_value_store = await self.__stack.enter_async_context(
            self.config.key_value_store
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__stack.__aexit__(exc_type, exc_value, traceback)

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        # Enable the user to specify a key value store
        cls.config_set(
            args,
            above,
            "kvstore",
            Arg(type=BaseKeyValueStore.load, default=MemoryKeyValueStore),
        )
        # Load all the key value stores and add the arguments they might require
        for loaded in BaseKeyValueStore.load():
            loaded.args(args, *cls.add_orig_label(*above))
        return args

    @classmethod
    def config(cls, config, *above):
        kvstore = cls.config_get(config, above, "kvstore")
        return BaseRedundancyCheckerConfig(
            key_value_store=kvstore.withconfig(config, *cls.add_label(*above))
        )


class MemoryLockNetworkContext(BaseLockNetworkContext):
    def __init__(
        self, config: BaseConfig, parent: "MemoryLockNetwork"
    ) -> None:
        super().__init__(config, parent)
        self.lock = asyncio.Lock()
        self.locks: Dict[str, asyncio.Lock] = {}

    @asynccontextmanager
    async def acquire(self, parameter_set: BaseParameterSet):
        """
        Acquire the lock for each input in the input set which must be locked
        prior to running an operation using the input.
        """
        need_lock = {}
        # Acquire the master lock to find and or create needed locks
        async with self.lock:
            # Get all the inputs up the ancestry tree
            inputs = [item async for item in parameter_set.inputs()]
            # Only lock the ones which require it
            for item in filter(lambda item: item.definition.lock, inputs):
                # Create the lock for the input if not present
                if not item.uid in self.locks:
                    self.locks[item.uid] = asyncio.Lock()
                # Retrieve the lock
                need_lock[item.uid] = (item, self.locks[item.uid])
        # Use AsyncExitStack to lock the variable amount of inputs required
        async with AsyncExitStack() as stack:
            # Take all the locks we found we needed for this parameter set
            for _uid, (item, lock) in need_lock.items():
                # Take the lock
                self.logger.debug("Acquiring: %s(%r)", item.uid, item.value)
                await stack.enter_async_context(lock)
                self.logger.debug("Acquired: %s(%r)", item.uid, item.value)
            # All locks for these parameters have been acquired
            yield


@entry_point("memory")
class MemoryLockNetwork(BaseLockNetwork, BaseMemoryDataFlowObject):

    CONTEXT = MemoryLockNetworkContext


class MemoryOperationImplementationNetworkConfig(NamedTuple):
    operations: Dict[str, OperationImplementation]


class MemoryOperationImplementationNetworkContext(
    BaseOperationImplementationNetworkContext
):
    def __init__(
        self,
        config: BaseConfig,
        parent: "MemoryOperationImplementationNetwork",
    ) -> None:
        super().__init__(config, parent)
        self.opimps = self.parent.config.operations
        self.operations = {}
        self.completed_event = asyncio.Event()

    async def __aenter__(
        self
    ) -> "MemoryOperationImplementationNetworkContext":
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        self.operations = {
            opimp.op.name: await self._stack.enter_async_context(opimp)
            for opimp in self.opimps.values()
        }
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._stack is not None:
            await self._stack.__aexit__(exc_type, exc_value, traceback)
            self._stack = None

    async def contains(self, operation: Operation) -> bool:
        """
        Checks if operation in is operations we have loaded in memory
        """
        return operation.instance_name in self.operations

    async def instantiable(
        self, operation: Operation, *, opimp: OperationImplementation = None
    ) -> bool:
        """
        Looks for class registered with ____ entrypoint using pkg_resources.
        """
        # This is pure Python, so if we're given an operation implementation we
        # will be able to instantiate it
        if opimp is not None:
            return True
        try:
            opimp = OperationImplementation.load(operation.name)
        except FailedToLoadOperationImplementation as error:
            self.logger.debug(
                "OperationImplementation %r is not instantiable: %s",
                operation.name,
                error,
            )
            return False
        return True

    async def instantiate(
        self,
        operation: Operation,
        config: BaseConfig,
        *,
        opimp: OperationImplementation = None,
    ) -> bool:
        """
        Instantiate class registered with ____ entrypoint using pkg_resources.
        Return true if instantiation was successful.
        """
        if opimp is None:
            if await self.instantiable(operation):
                opimp = OperationImplementation.load(operation.name)
            else:
                raise OperationImplementationNotInstantiable(operation.name)
        self.operations[
            operation.instance_name
        ] = await self._stack.enter_async_context(opimp(config))

    async def ensure_contains(self, operation: Operation):
        """
        Raise errors if we don't have and can't instantiate an operation.
        """
        # Check that our network contains the operation
        if not await self.contains(operation):
            if not await self.instantiable(operation):
                raise OperationImplementationNotInstantiable(operation.name)
            else:
                raise OperationImplementationNotInstantiated(
                    operation.instance_name
                )

    async def run(
        self,
        ctx: BaseInputSetContext,
        octx: BaseOrchestratorContext,
        operation: Operation,
        inputs: Dict[str, Any],
    ) -> Union[bool, Dict[str, Any]]:
        """
        Run an operation in our network.
        """
        # Check that our network contains the operation
        await self.ensure_contains(operation)
        # Create an opimp context and run the opertion
        async with self.operations[operation.instance_name](
            ctx, octx
        ) as opctx:
            self.logger.debug("---")
            self.logger.debug(
                "Stage: %s: %s",
                operation.stage.value.upper(),
                operation.instance_name,
            )
            self.logger.debug("Inputs: %s", inputs)
            self.logger.debug(
                "Conditions: %s",
                dict(
                    zip(
                        map(
                            lambda condition: condition.name,
                            operation.conditions,
                        ),
                        ([True] * len(operation.conditions)),
                    )
                ),
            )
            outputs = await opctx.run(inputs)
            self.logger.debug("Output: %s", outputs)
            self.logger.debug("---")
            return outputs

    async def operation_completed(self):
        await self.completed_event.wait()
        self.completed_event.clear()

    async def run_dispatch(
        self,
        octx: BaseOrchestratorContext,
        operation: Operation,
        parameter_set: BaseParameterSet,
    ):
        """
        Run an operation in the background and add its outputs to the input
        network when complete
        """
        # Ensure that we can run the operation
        # Lock all inputs which cannot be used simultaneously
        async with octx.lctx.acquire(parameter_set):
            # Run the operation
            outputs = await self.run(
                parameter_set.ctx,
                octx,
                operation,
                await parameter_set._asdict(),
            )
            if outputs is None:
                return []
        # Create a list of inputs from the outputs using the definition mapping
        try:
            inputs = []
            if operation.expand:
                expand = operation.expand
            else:
                expand = []
            parents = [item async for item in parameter_set.inputs()]
            for key, output in outputs.items():
                if not key in expand:
                    output = [output]
                for value in output:
                    inputs.append(
                        Input(
                            value=value,
                            definition=operation.outputs[key],
                            parents=parents,
                            origin=(operation.instance_name, key),
                        )
                    )
        except KeyError as error:
            raise KeyError(
                "Value %s missing from output:definition mapping %s(%s)"
                % (
                    str(error),
                    operation.instance_name,
                    ", ".join(operation.outputs.keys()),
                )
            ) from error
        # Add the input set made from the outputs to the input set network
        await octx.ictx.add(
            MemoryInputSet(
                MemoryInputSetConfig(ctx=parameter_set.ctx, inputs=inputs)
            )
        )
        return inputs

    async def dispatch(
        self,
        octx: BaseOrchestratorContext,
        operation: Operation,
        parameter_set: BaseParameterSet,
    ):
        """
        Schedule the running of an operation
        """
        self.logger.debug("[DISPATCH] %s", operation.instance_name)
        task = asyncio.create_task(
            self.run_dispatch(octx, operation, parameter_set)
        )
        task.add_done_callback(ignore_args(self.completed_event.set))
        return task

    async def operations_parameter_set_pairs(
        self,
        ictx: BaseInputNetworkContext,
        octx: BaseOperationNetworkContext,
        rctx: BaseRedundancyCheckerContext,
        ctx: BaseInputSetContext,
        dataflow: DataFlow,
        *,
        new_input_set: Optional[BaseInputSet] = None,
        stage: Stage = Stage.PROCESSING,
    ) -> AsyncIterator[Tuple[Operation, BaseInputSet]]:
        """
        Use new_input_set to determine which operations in the network might be
        up for running. Cross check using existing inputs to generate per
        input set context novel input pairings. Yield novel input pairings
        along with their operations as they are generated.
        """
        # Get operations which may possibly run as a result of these new inputs
        async for operation in octx.operations(
            dataflow, input_set=new_input_set, stage=stage
        ):
            # Generate all pairs of un-run input combinations
            async for parameter_set in ictx.gather_inputs(
                rctx, operation, dataflow, ctx=ctx
            ):
                yield operation, parameter_set


@entry_point("memory")
class MemoryOperationImplementationNetwork(
    BaseOperationImplementationNetwork, BaseMemoryDataFlowObject
):

    CONTEXT = MemoryOperationImplementationNetworkContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        # Enable the user to specify operation implementations to be loaded via
        # the entrypoint system (by ParseOperationImplementationAction)
        # TODO opimps should be operations
        cls.config_set(
            args,
            above,
            "opimps",
            Arg(type=OperationImplementation.load, nargs="+", default=[]),
        )
        # Add orig label to above since we are done loading
        above = cls.add_orig_label(*above)
        # Load all the opimps and add the arguments they might require
        # TODO(p4) Should we do this? If someone messes up their entrypoints in
        # one package it will mess up loading anytime this is called.
        """
        for loaded in OperationImplementation.load():
            loaded.args(args, *above)
        """
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return MemoryOperationImplementationNetworkConfig(
            operations={
                imp.op.name: imp
                for imp in [
                    Imp.withconfig(config, "opimp")
                    for Imp in cls.config_get(config, above, "opimps")
                ]
            }
        )


class MemoryOrchestratorConfig(BaseOrchestratorConfig):
    """
    Same as base orchestrator config
    """


class MemoryOrchestratorContextConfig(NamedTuple):
    uid: str
    dataflow: DataFlow
    # Context objects to reuse. If not present in this dict a new context object
    # will be created.
    reuse: Dict[str, BaseDataFlowObjectContext]


class MemoryOrchestratorContext(BaseOrchestratorContext):
    def __init__(
        self,
        config: MemoryOrchestratorContextConfig,
        parent: "BaseOrchestrator",
    ) -> None:
        super().__init__(config, parent)
        self._stack = None

    async def __aenter__(self) -> "BaseOrchestratorContext":
        # TODO(subflows) In all of these contexts we are about to enter, they
        # all reach into their parents and store things in the parents memory
        # (or similar). What should be done is to have them create their own
        # storage space, so that each context is unique (which seems quite
        # unsupprising now, not sure what I was thinking before). If an
        # operation wants to initiate a subflow. It will need to call a method
        # we have yet to write within the orchestrator context which will reach
        # up to the parent of that orchestrator context and create a new
        # orchestrator context, thus triggering this __aenter__ method for the
        # new context. The only case where an operation will not want to reach
        # up to the parent to get all new contexts, is when it's an output
        # operation which desires to execute a subflow. If the output operation
        # created new contexts, then there would be no inputs in them, so that
        # would be pointless.
        enter = {
            "rctx": self.parent.rchecker,
            "ictx": self.parent.input_network,
            "octx": self.parent.operation_network,
            "lctx": self.parent.lock_network,
            "nctx": self.parent.opimp_network,
        }
        # If we were told to reuse a context, don't enter it. Just set the
        # attribute now.
        for name, ctx in self.config.reuse.items():
            if name in enter:
                self.logger.debug("Reusing %s: %s", name, ctx)
                del enter[name]
                setattr(self, name, ctx)
        # Creat the exit stack and enter all the contexts we won't be reusing
        self._stack = AsyncExitStack()
        self._stack = await aenter_stack(self, enter)
        # Ensure that we can run the dataflow
        await self.initialize_dataflow(self.config.dataflow)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._stack.aclose()

    async def initialize_dataflow(self, dataflow: DataFlow) -> None:
        """
        Initialize a DataFlow by preforming the following steps.

        1. Add operations the operation network context
        2. Instantiate operation implementations which are not instantiated
           within the operation implementation network context
        3. Seed input network context with given inputs
        """
        self.logger.debug("Initializing dataflow: %s", dataflow)
        # Add operations to operations network context
        await self.octx.add(dataflow.operations.values())
        # Instantiate all operations
        for (instance_name, operation) in dataflow.operations.items():
            # Add and instantiate operation implementation if not
            # present
            if not await self.nctx.contains(operation):
                # We may have been provided with the implemenation. Attempt to
                # look it up from within the dataflow.
                opimp = dataflow.implementations.get(operation.name, None)
                # There is a possiblity the operation implemenation network will
                # be able to instantiate from the given operation implementation
                # if present. But we can't count on it.
                if not await self.nctx.instantiable(operation, opimp=opimp):
                    raise OperationImplementationNotInstantiable(
                        operation.name
                    )
                else:
                    opimp_config = dataflow.configs.get(
                        operation.instance_name, None
                    )
                    if opimp_config is None:
                        self.logger.debug(
                            "Instantiating operation implementation %s(%s) with base config",
                            operation.instance_name,
                            operation.name,
                        )
                        opimp_config = BaseConfig()
                    await self.nctx.instantiate(
                        operation, opimp_config, opimp=opimp
                    )

    async def seed_inputs(
        self,
        *,
        ctx: Optional[BaseInputSetContext] = None,
        input_set: Optional[Union[List[Input], BaseInputSet]] = None,
    ) -> BaseInputSetContext:
        self.logger.debug("Seeding dataflow with input_set: %s", input_set)
        if input_set is None:
            # Create a list if extra inputs were not given
            input_set: List[Input] = []
        if isinstance(input_set, list):
            # Do not modify the callers list if extra inputs were given
            input_set = input_set.copy()
            # Add seed values to the input set
            list(map(input_set.append, self.config.dataflow.seed))
        elif isinstance(input_set, BaseInputSet):
            # TODO Maybe allow setting it? Is there a usecase for this?
            if ctx is not None:
                self.logger.info(
                    "seed_inputs will not set the context of a BaseInputSet instance to the new context provided"
                )
            # Add all seed input_set to the input set
            for item in self.config.dataflow.seed:
                await input_set.add(item)
        # Add all the input sets
        if isinstance(input_set, list):
            if ctx is not None:
                # Add under existing context if given
                await self.ictx.cadd(ctx, *input_set)
            else:
                # Otherwise create new context
                ctx = await self.ictx.uadd(*input_set)
        else:
            # Add the input set
            await self.ictx.add(input_set)
            ctx = input_set.ctx
        return ctx

    # TODO(dfass) Get rid of run_operations, make it run_dataflow. Pass down the
    # dataflow to everything. Make inputs a list of InputSets or an
    # asyncgenerator of InputSets. Add a parameter which tells us if we should
    # exit when all operations are complete or continue to wait for more inputs
    # from the asyncgenerator. Make that parameter an asyncio.Event
    async def run(
        self,
        *input_sets: Union[List[Input], BaseInputSet],
        strict: bool = True,
        ctx: Optional[BaseInputSetContext] = None,
        halt: Optional[asyncio.Event] = None,
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        """
        Run a DataFlow.
        """
        # Lists of contexts we care about for this dataflow
        ctxs: List[BaseInputSetContext] = []
        self.logger.debug("Running %s: %s", self.config.dataflow, input_sets)
        if not input_sets:
            # If there are no input sets, add only seed inputs
            ctxs.append(await self.seed_inputs(ctx=ctx))
        if len(input_sets) == 1 and inspect.isasyncgen(input_sets[0]):
            # Check if inputs is an asyncgenerator
            # If it is, start a coroutine to wait for new inputs or input sets
            # from it. When new inputs are received, add the seed inputs from
            # the dataflow to the context.
            # TODO(dfass) Grab inputs from asyncgen, combine with seed
            raise NotImplementedError("asyncgen not yet supported")
        elif len(input_sets) == 1 and isinstance(input_sets[0], dict):
            # Helper to quickly add inputs under string context
            for ctx_string, input_set in input_sets[0].items():
                ctxs.append(
                    await self.seed_inputs(
                        ctx=StringInputSetContext(ctx_string),
                        input_set=input_set,
                    )
                )
        else:
            # For inputs sets that are of type BaseInputSetContext or list
            for input_set in input_sets:
                ctxs.append(
                    await self.seed_inputs(ctx=ctx, input_set=input_set)
                )
        # TODO Add check that ctx returned is the ctx corresponding to uadd.
        # We'll have to make uadd return the ctx so we can compare.
        # TODO Send the context back into some list maintained by
        # run_operations so that if there is another run_dataflow method
        # running on the same orchestrator context it will get the context
        # it's waiting for and return
        # BEGIN old run_operations
        # Set of tasks we are waiting on
        # TODO Make some way to cap the number of context's who have operations
        # executing. Or maybe just the number of operations. Or both.
        tasks = set()
        # Create tasks to wait on the results of each of the contexts submitted
        for ctx in ctxs:
            self.logger.debug(
                "kickstarting context: %s", (await ctx.handle()).as_string()
            )
            tasks.add(
                asyncio.create_task(
                    self.run_operations_for_ctx(ctx, strict=strict)
                )
            )
        try:
            # Return when outstanding operations reaches zero
            while tasks:
                # Wait for incoming events
                done, _pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for task in done:
                    # Remove the task from the set of tasks we are waiting for
                    tasks.remove(task)
                    # Get the tasks exception if any
                    exception = task.exception()
                    if strict and exception is not None:
                        raise exception
                    elif exception is not None:
                        # If there was an exception log it
                        output = io.StringIO()
                        task.print_stack(file=output)
                        self.logger.error("%s", output.getvalue().rstrip())
                        output.close()
                    else:
                        # All operations for a context completed
                        # Yield the context that completed and the results of its
                        # output operations
                        ctx, results = task.result()
                        yield ctx, results
                self.logger.debug("ctx.outstanding: %d", len(tasks) - 1)
        finally:
            # Cancel tasks which we don't need anymore now that we know we are done
            for task in tasks:
                if not task.done():
                    task.cancel()
                else:
                    task.exception()

    async def run_operations_for_ctx(
        self, ctx: BaseContextHandle, *, strict: bool = True
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        # Track if there are more inputs
        more = True
        # Set of tasks we are waiting on
        tasks = set()
        # String representing the context we are executing operations for
        ctx_str = (await ctx.handle()).as_string()
        # Create initial events to wait on
        # TODO(dfass) Make ictx.added(ctx) specific to dataflow
        input_set_enters_network = asyncio.create_task(self.ictx.added(ctx))
        tasks.add(input_set_enters_network)
        try:
            # Return when outstanding operations reaches zero
            while tasks:
                if (
                    not more
                    and len(tasks) == 1
                    and input_set_enters_network in tasks
                ):
                    break
                # Wait for incoming events
                done, _pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for task in done:
                    # Remove the task from the set of tasks we are waiting for
                    tasks.remove(task)
                    # Get the tasks exception if any
                    exception = task.exception()
                    if strict and exception is not None:
                        raise exception
                    elif exception is not None:
                        # If there was an exception log it
                        output = io.StringIO()
                        task.print_stack(file=output)
                        self.logger.error("%s", output.getvalue().rstrip())
                        output.close()
                    elif task is input_set_enters_network:
                        more, new_input_sets = (
                            input_set_enters_network.result()
                        )
                        for new_input_set in new_input_sets:
                            # Identify which operations have complete contextually
                            # appropriate input sets which haven't been run yet
                            async for operation, parameter_set in self.nctx.operations_parameter_set_pairs(
                                self.ictx,
                                self.octx,
                                self.rctx,
                                ctx,
                                self.config.dataflow,
                                new_input_set=new_input_set,
                            ):
                                # Add inputs and operation to redundancy checker before
                                # dispatch
                                await self.rctx.add(operation, parameter_set)
                                # Dispatch the operation and input set for running
                                dispatch_operation = await self.nctx.dispatch(
                                    self, operation, parameter_set
                                )
                                tasks.add(dispatch_operation)
                                self.logger.debug(
                                    "[%s]: dispatch operation: %s",
                                    ctx_str,
                                    operation.instance_name,
                                )
                        # Create a another task to waits for new input sets
                        input_set_enters_network = asyncio.create_task(
                            self.ictx.added(ctx)
                        )
                        tasks.add(input_set_enters_network)
        finally:
            # Cancel tasks which we don't need anymore now that we know we are done
            for task in tasks:
                if not task.done():
                    task.cancel()
                else:
                    task.exception()
            # Run cleanup
            async for _operation, _results in self.run_stage(
                ctx, Stage.CLEANUP
            ):
                pass
        # Set output to empty dict in case output operations fail
        output = {}
        # Run output operations and create a dict mapping the operation name to
        # the output of that operation
        try:
            output = {
                operation.instance_name: results
                async for operation, results in self.run_stage(
                    ctx, Stage.OUTPUT
                )
            }
        except:
            if strict:
                raise
            else:
                self.logger.error("%s", traceback.format_exc().rstrip())
        # If there is only one output operation, return only it's result instead
        # of a dict with it as the only key value pair
        if len(output) == 1:
            output = list(output.values())[0]
        # Return the context along with it's output
        return ctx, output

    async def run_stage(self, ctx: BaseInputSetContext, stage: Stage):
        # Identify which operations have complete contextually appropriate
        # input sets which haven't been run yet and are stage operations
        async for operation, parameter_set in self.nctx.operations_parameter_set_pairs(
            self.ictx,
            self.octx,
            self.rctx,
            ctx,
            self.config.dataflow,
            stage=stage,
        ):
            # Add inputs and operation to redundancy checker before dispatch
            await self.rctx.add(operation, parameter_set)
            # Run the operation, input set pair
            yield operation, await self.nctx.run(
                ctx, self, operation, await parameter_set._asdict()
            )


@entry_point("memory")
class MemoryOrchestrator(BaseOrchestrator, BaseMemoryDataFlowObject):

    CONTEXT = MemoryOrchestratorContext

    def __init__(self, config: "BaseConfig") -> None:
        super().__init__(config)
        self._stack = None

    async def __aenter__(self) -> "DataFlowFacilitator":
        self._stack = await aenter_stack(
            self,
            {
                "rchecker": self.config.rchecker,
                "input_network": self.config.input_network,
                "operation_network": self.config.operation_network,
                "lock_network": self.config.lock_network,
                "opimp_network": self.config.opimp_network,
            },
            call=False,
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._stack.aclose()

    def __call__(
        self, dataflow: DataFlow, **kwargs
    ) -> BaseDataFlowObjectContext:
        return self.CONTEXT(
            MemoryOrchestratorContextConfig(
                uid=secrets.token_hex(), dataflow=dataflow, reuse=kwargs
            ),
            self,
        )

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        # Extending above is done right before loading args of subclasses
        cls.config_set(
            args,
            above,
            "input",
            "network",
            Arg(type=BaseInputNetwork.load, default=MemoryInputNetwork),
        )
        cls.config_set(
            args,
            above,
            "operation",
            "network",
            Arg(
                type=BaseOperationNetwork.load, default=MemoryOperationNetwork
            ),
        )
        cls.config_set(
            args,
            above,
            "opimp",
            "network",
            Arg(
                type=BaseOperationImplementationNetwork.load,
                default=MemoryOperationImplementationNetwork,
            ),
        )
        cls.config_set(
            args,
            above,
            "lock",
            "network",
            Arg(type=BaseLockNetwork.load, default=MemoryLockNetwork),
        )
        cls.config_set(
            args,
            above,
            "rchecker",
            Arg(
                type=BaseRedundancyChecker.load,
                default=MemoryRedundancyChecker,
            ),
        )
        above = cls.add_orig_label(*above)
        for sub in [
            BaseInputNetwork,
            BaseOperationNetwork,
            BaseOperationImplementationNetwork,
            BaseLockNetwork,
            BaseRedundancyChecker,
        ]:
            for loaded in sub.load():
                loaded.args(args, *above)
        return args

    @classmethod
    def config(cls, config, *above):
        input_network = cls.config_get(config, above, "input", "network")
        operation_network = cls.config_get(
            config, above, "operation", "network"
        )
        opimp_network = cls.config_get(config, above, "opimp", "network")
        lock_network = cls.config_get(config, above, "lock", "network")
        rchecker = cls.config_get(config, above, "rchecker")
        above = cls.add_label(*above)
        return MemoryOrchestratorConfig(
            input_network=input_network.withconfig(config, *above),
            operation_network=operation_network.withconfig(config, *above),
            lock_network=lock_network.withconfig(config, *above),
            opimp_network=opimp_network.withconfig(config, *above),
            rchecker=rchecker.withconfig(config, *above),
        )

    @classmethod
    def basic_config(
        cls, *args: OperationImplementation, config: Dict[str, Any] = None
    ):
        """
        Creates a Memory Orchestrator which will be backed by other objects
        within dffml.df.memory.
        """
        if config is None:
            config = {}
        return MemoryOrchestrator(
            MemoryOrchestratorConfig(
                input_network=MemoryInputNetwork(BaseConfig()),
                operation_network=MemoryOperationNetwork(
                    MemoryOperationNetworkConfig(
                        operations=[Imp.op for Imp in args]
                    )
                ),
                lock_network=MemoryLockNetwork(BaseConfig()),
                rchecker=MemoryRedundancyChecker(
                    BaseRedundancyCheckerConfig(
                        key_value_store=MemoryKeyValueStore(BaseConfig())
                    )
                ),
                opimp_network=MemoryOperationImplementationNetwork(
                    MemoryOperationImplementationNetworkConfig(
                        operations={
                            imp.op.name: imp
                            for imp in [Imp.withconfig(config) for Imp in args]
                        }
                    )
                ),
            )
        )
