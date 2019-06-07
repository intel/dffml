import io
import asyncio
import hashlib
import itertools
from datetime import datetime
from itertools import product
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
from .types import Input, Parameter, Definition, Operation, Stage
from .base import (
    OperationImplementation,
    BaseConfig,
    BaseContextHandle,
    BaseKeyValueStoreContext,
    BaseKeyValueStore,
    BaseInputSetContext,
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
    BaseOperationImplementationNetworkContext,
    BaseOperationImplementationNetwork,
    BaseOrchestratorConfig,
    BaseOrchestratorContext,
    BaseOrchestrator,
)

from ..util.entrypoint import entry_point
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.data import ignore_args
from ..util.asynchelper import context_stacker, aenter_stack

from .log import LOGGER


class MemoryKeyValueStoreContext(BaseKeyValueStoreContext):
    async def get(self, key: str) -> Union[bytes, None]:
        async with self.parent.lock:
            return self.parent.memory.get(key)

    async def set(self, key: str, value: bytes):
        async with self.parent.lock:
            self.parent.memory[key] = value


@entry_point("memory")
class MemoryKeyValueStore(BaseKeyValueStore):
    """
    Key Value store backed by dict
    """

    CONTEXT = MemoryKeyValueStoreContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.memory: Dict[str, bytes] = {}
        self.lock = asyncio.Lock()


class MemoryInputSetConfig(NamedTuple):
    ctx: BaseInputSetContext
    inputs: List[Input]


class MemoryInputSet(BaseInputSet):
    def __init__(self, config: MemoryInputSetConfig) -> None:
        super().__init__(config)
        self.__inputs = config.inputs

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
            map(self.parent.memory.add, set_items)
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
        self.memory = set()
        self.lock = asyncio.Lock()
        self.event_added = asyncio.Event()
        self.event_added_lock = asyncio.Lock()
        self.notification_items = []

    def __call__(self) -> NotificationSetContext:
        return NotificationSetContext(self)


class MemoryInputNetworkContextEntry(NamedTuple):
    ctx: BaseInputSetContext
    definitions: Dict[Definition, List[Input]]


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
    async def add(self, input_set: BaseInputSet):
        # Grab the input set context handle
        handle = await input_set.ctx.handle()
        handle_string = handle.as_string()
        # If the context for this input set does not exist create a
        # NotificationSet for it to notify the orchestrator
        if not handle_string in self.parent.input_notification_set:
            self.parent.input_notification_set[
                handle_string
            ] = NotificationSet()
            async with self.parent.ctx_notification_set() as ctx:
                await ctx.add(input_set.ctx, [])
        # Add the input set to the incoming inputs
        async with self.parent.input_notification_set[handle_string]() as ctx:
            await ctx.add(
                input_set, [item async for item in input_set.inputs()]
            )
        # Associate inputs with their context handle grouped by definition
        async with self.parent.ctxhd_lock:
            # Create dict for handle_string if not present
            if not handle_string in self.parent.ctxhd:
                self.parent.ctxhd[
                    handle_string
                ] = MemoryInputNetworkContextEntry(
                    ctx=input_set.ctx, definitions={}
                )
            # Go through each item in the input set
            async for item in input_set.inputs():
                # Create set for item definition if not present
                if (
                    not item.definition
                    in self.parent.ctxhd[handle_string].definitions
                ):
                    self.parent.ctxhd[handle_string].definitions[
                        item.definition
                    ] = []
                # Add input to by defintion set
                self.parent.ctxhd[handle_string].definitions[
                    item.definition
                ].append(item)

    async def ctx(self) -> Tuple[bool, BaseInputSetContext]:
        async with self.parent.ctx_notification_set() as ctx:
            return await ctx.added()

    async def added(
        self, watch_ctx: BaseInputSetContext
    ) -> Tuple[bool, BaseInputSet]:
        # Grab the input set context handle
        handle_string = (await watch_ctx.handle()).as_string()
        # Notify whatever is listening for new inputs in this context
        async with self.parent.input_notification_set[handle_string]() as ctx:
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
        async with self.parent.ctxhd_lock:
            # Grab the input set context handle
            handle_string = (await ctx.handle()).as_string()
            # Ensure that the handle_string is present in ctxhd
            if not handle_string in self.parent.ctxhd:
                raise ContextNotPresent(handle_string)
            # Search through the definitions to find one with a matching name
            found = list(
                filter(
                    lambda check: check.name == definition,
                    self.parent.ctxhd[handle_string].definitions,
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
        return MemoryDefinitionSetContext(self.parent, ctx)

    async def gather_inputs(
        self,
        rctx: "BaseRedundancyCheckerContext",
        operation: Operation,
        ctx: Optional[BaseInputSetContext] = None,
    ) -> AsyncIterator[BaseParameterSet]:
        # Create a mapping of definitions to inputs for that definition
        gather: Dict[str, List[Parameter]] = {}
        async with self.parent.ctxhd_lock:
            # If no context is given we will generate input pairs for all
            # contexts
            contexts = self.parent.ctxhd.values()
            # If a context is given only search definitions within that context
            if not ctx is None:
                # Grab the input set context handle
                handle_string = (await ctx.handle()).as_string()
                # Ensure that the handle_string is present in ctxhd
                if not handle_string in self.parent.ctxhd:
                    return
                # Limit search to given context via context handle
                contexts = [self.parent.ctxhd[handle_string]]
            for ctx, definitions in contexts:
                # Check that all conditions are present and logicly True
                if not all(
                    map(
                        lambda definition: (
                            definition in definitions
                            and all(
                                map(
                                    lambda item: bool(item.value),
                                    definitions[definition],
                                )
                            )
                        ),
                        operation.conditions,
                    )
                ):
                    return
                # Gather all inputs with matching definitions and contexts
                for key, definition in operation.inputs.items():
                    # Return if any inputs are missing
                    if not definition in definitions:
                        return
                    else:
                        # Generate parameters from inputs
                        gather[key] = [
                            Parameter(
                                key=key,
                                value=item.value,
                                origin=item,
                                definition=definition,
                            )
                            for item in definitions[definition]
                        ]
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
class MemoryInputNetwork(BaseInputNetwork):
    """
    Inputs backed by a set
    """

    CONTEXT = MemoryInputNetworkContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.ctx_notification_set = NotificationSet()
        self.input_notification_set = {}
        # Organize by context handle string then by definition within that
        self.ctxhd: Dict[str, Dict[Definition, Any]] = {}
        # TODO Create ctxhd_locks dict to manage a per context lock
        self.ctxhd_lock = asyncio.Lock()


class MemoryOperationNetworkConfig(NamedTuple):
    # Starting set of operations
    operations: List[Operation]


class MemoryOperationNetworkContext(BaseOperationNetworkContext):
    async def add(self, operations: List[Operation]):
        async with self.parent.lock:
            map(self.parent.memory.add, operations)

    async def operations(
        self,
        input_set: Optional[BaseInputSet] = None,
        stage: Stage = Stage.PROCESSING,
    ) -> AsyncIterator[Operation]:
        # Set list of needed input definitions if given
        if not input_set is None:
            input_definitions = await input_set.definitions()
        # Yield all operations with an input in the input set
        for operation in self.parent.memory:
            # Only run operations of the requested stage
            if operation.stage != stage:
                continue
            # If there is a given input set check each definition in it against
            # the operation's inputs to verify we are only looking at the subset
            if input_set is not None:
                if not [
                    item
                    for item in operation.inputs.values()
                    if item in input_definitions
                ] and not [
                    item
                    for item in operation.conditions
                    if item in input_definitions
                ]:
                    continue
            yield operation


@entry_point("memory")
class MemoryOperationNetwork(BaseOperationNetwork):
    """
    Operations backed by a set
    """

    CONTEXT = MemoryOperationNetworkContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.memory = config.operations.copy()
        self.lock = asyncio.Lock()

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "ops", Arg(type=Operation.load, nargs="+"))
        return args

    @classmethod
    def config(cls, config, *above) -> MemoryOperationNetworkConfig:
        return MemoryOperationNetworkConfig(
            operations=cls.config_get(config, above, "ops")
        )


class MemoryRedundancyCheckerContext(BaseRedundancyCheckerContext):
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
        operation name, and the sorted list of input uuids.
        """
        uid_list = sorted(
            map(
                lambda x: x.uid,
                [item async for item in parameter_set.inputs()],
            )
        )
        uid_list.insert(0, (await parameter_set.ctx.handle()).as_string())
        uid_list.insert(0, operation.name)
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
class MemoryRedundancyChecker(BaseRedundancyChecker):
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
        await self.__stack.aclose()

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
    @asynccontextmanager
    async def acquire(self, parameter_set: BaseParameterSet):
        """
        Acquire the lock for each input in the input set which must be locked
        prior to running an operation using the input.
        """
        need_lock = {}
        # Acquire the master lock to find and or create needed locks
        async with self.parent.lock:
            # Get all the inputs up the ancestry tree
            inputs = [item async for item in parameter_set.inputs()]
            # Only lock the ones which require it
            for item in filter(lambda item: item.definition.lock, inputs):
                # Create the lock for the input if not present
                if not item.uid in self.parent.locks:
                    self.parent.locks[item.uid] = asyncio.Lock()
                # Retrieve the lock
                need_lock[item.uid] = (item, self.parent.locks[item.uid])
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
class MemoryLockNetwork(BaseLockNetwork):

    CONTEXT = MemoryLockNetworkContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.lock = asyncio.Lock()
        self.locks: Dict[str, asyncio.Lock] = {}


class MemoryOperationImplementationNetworkConfig(NamedTuple):
    operations: Dict[str, OperationImplementation]


class MemoryOperationImplementationNetworkContext(
    BaseOperationImplementationNetworkContext
):
    async def contains(self, operation: Operation) -> bool:
        """
        Checks if operation in is operations we have loaded in memory
        """
        return operation.name in self.parent.operations

    async def instantiable(self, operation: Operation) -> bool:
        """
        Looks for class registered with ____ entrypoint using pkg_resources.
        """
        raise NotImplementedError()

    async def instantiate(
        self, operation: Operation, config: BaseConfig
    ) -> bool:
        """
        Instantiate class registered with ____ entrypoint using pkg_resources.
        Return true if instantiation was successful.
        """
        raise NotImplementedError()

    async def run(
        self,
        ctx: BaseInputSetContext,
        ictx: BaseInputNetworkContext,
        operation: Operation,
        inputs: Dict[str, Any],
    ) -> Union[bool, Dict[str, Any]]:
        """
        Run an operation in our network.
        """
        async with self.parent.operations[operation.name](ctx, ictx) as opctx:
            self.logger.debug("---")
            self.logger.debug(
                "Stage: %s: %s", operation.stage.value.upper(), operation.name
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
        await self.parent.completed_event.wait()
        self.parent.completed_event.clear()

    async def run_dispatch(
        self,
        ictx: BaseInputNetworkContext,
        lctx: BaseLockNetworkContext,
        operation: Operation,
        parameter_set: BaseParameterSet,
    ):
        """
        Run an operation in the background and add its outputs to the input
        network when complete
        """
        # Lock all inputs which cannot be used simultaneously
        async with lctx.acquire(parameter_set):
            # Run the operation
            outputs = await self.run(
                parameter_set.ctx,
                ictx,
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
                        )
                    )
        except KeyError as error:
            raise KeyError(
                "Value %s missing from output:definition mapping %s(%s)"
                % (
                    str(error),
                    operation.name,
                    ", ".join(operation.outputs.keys()),
                )
            ) from error
        # Add the input set made from the outputs to the input set network
        await ictx.add(
            MemoryInputSet(
                MemoryInputSetConfig(ctx=parameter_set.ctx, inputs=inputs)
            )
        )
        return inputs

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
        self.logger.debug("[DISPATCH] %s", operation.name)
        task = asyncio.create_task(
            self.run_dispatch(ictx, lctx, operation, parameter_set)
        )
        task.add_done_callback(ignore_args(self.parent.completed_event.set))
        return task

    async def operations_parameter_set_pairs(
        self,
        ictx: BaseInputNetworkContext,
        octx: BaseOperationNetworkContext,
        rctx: BaseRedundancyCheckerContext,
        ctx: BaseInputSetContext,
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
            input_set=new_input_set, stage=stage
        ):
            # Generate all pairs of un-run input combinations
            async for parameter_set in ictx.gather_inputs(
                rctx, operation, ctx=ctx
            ):
                yield operation, parameter_set


@entry_point("memory")
class MemoryOperationImplementationNetwork(BaseOperationImplementationNetwork):

    CONTEXT = MemoryOperationImplementationNetworkContext

    def __init__(
        self, config: MemoryOperationImplementationNetworkConfig
    ) -> None:
        super().__init__(config)
        self.opimps = self.config.operations
        self.operations = {}
        self.completed_event = asyncio.Event()

    async def __aenter__(
        self
    ) -> "MemoryOperationImplementationNetworkContext":
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.operations = {
            opimp.op.name: await self.__stack.enter_async_context(opimp)
            for opimp in self.opimps.values()
        }
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.__stack is not None:
            await self.__stack.aclose()
            self.__stack = None

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        # Enable the user to specify operation implementations to be loaded via
        # the entrypoint system (by ParseOperationImplementationAction)
        cls.config_set(
            args,
            above,
            "opimps",
            Arg(type=OperationImplementation.load, nargs="+"),
        )
        # Add orig label to above since we are done loading
        above = cls.add_orig_label(*above)
        # Load all the opimps and add the arguments they might require
        for loaded in OperationImplementation.load():
            loaded.args(args, *above)
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


class MemoryOrchestratorContext(BaseOrchestratorContext):
    def __init__(self, parent: "BaseOrchestrator") -> None:
        super().__init__(parent)
        self._stack = None

    async def __aenter__(self) -> "BaseOrchestratorContext":
        self._stack = AsyncExitStack()
        self._stack = await aenter_stack(
            self,
            {
                "rctx": self.parent.rchecker,
                "ictx": self.parent.input_network,
                "octx": self.parent.operation_network,
                "lctx": self.parent.lock_network,
                "nctx": self.parent.opimp_network,
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._stack.aclose()

    async def run_operations(
        self, strict: bool = False
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        # Track if there are more contexts
        more = True
        # Set of tasks we are waiting on
        tasks = set()
        # Create initial events to wait on
        new_context_enters_network = asyncio.create_task(self.ictx.ctx())
        tasks.add(new_context_enters_network)
        try:
            # Return when outstanding operations reaches zero
            while tasks:
                if (
                    not more
                    and len(tasks) == 1
                    and new_context_enters_network in tasks
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
                    elif task is new_context_enters_network:
                        # TODO Make some way to cap the number of context's who have
                        # operations executing. Or maybe just the number of
                        # operations. Or both.
                        # A new context entered the network
                        more, new_ctx = new_context_enters_network.result()
                        self.logger.debug(
                            "new_context_enters_network: %s",
                            (await new_ctx.handle()).as_string(),
                        )
                        # Add a task which will run operations for the new context
                        tasks.add(
                            asyncio.create_task(
                                self.run_operations_for_ctx(
                                    new_ctx, strict=strict
                                )
                            )
                        )
                        # Create a another task to waits for a new context
                        new_context_enters_network = asyncio.create_task(
                            self.ictx.ctx()
                        )
                        tasks.add(new_context_enters_network)
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
        self, ctx: BaseContextHandle, *, strict: bool = False
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        # Track if there are more inputs
        more = True
        # Set of tasks we are waiting on
        tasks = set()
        # String representing the context we are executing operations for
        ctx_str = (await ctx.handle()).as_string()
        # Create initial events to wait on
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
                                new_input_set=new_input_set,
                            ):
                                # Add inputs and operation to redundancy checker before
                                # dispatch
                                await self.rctx.add(operation, parameter_set)
                                # Dispatch the operation and input set for running
                                dispatch_operation = await self.nctx.dispatch(
                                    self.ictx,
                                    self.lctx,
                                    operation,
                                    parameter_set,
                                )
                                tasks.add(dispatch_operation)
                                self.logger.debug(
                                    "[%s]: dispatch operation: %s",
                                    ctx_str,
                                    operation.name,
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
        # Run output and return context along with output
        return (
            ctx,
            {
                operation.name: results
                async for operation, results in self.run_stage(
                    ctx, Stage.OUTPUT
                )
            },
        )

    async def run_stage(self, ctx: BaseInputSetContext, stage: Stage):
        # Identify which operations have complete contextually appropriate
        # input sets which haven't been run yet and are stage operations
        async for operation, parameter_set in self.nctx.operations_parameter_set_pairs(
            self.ictx, self.octx, self.rctx, ctx, stage=stage
        ):
            # Add inputs and operation to redundancy checker before dispatch
            await self.rctx.add(operation, parameter_set)
            # Run the operation, input set pair
            yield operation, await self.nctx.run(
                ctx, self.ictx, operation, await parameter_set._asdict()
            )


@entry_point("memory")
class MemoryOrchestrator(BaseOrchestrator):

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
        cls, operations: List[Operation], opimps: List[OperationImplementation]
    ):
        """
        Creates a Memory Orchestrator which will be backed by other objects
        within dffml.df.memory.
        """
        return MemoryOrchestrator(
            MemoryOrchestratorConfig(
                input_network=MemoryInputNetwork(BaseConfig()),
                operation_network=MemoryOperationNetwork(
                    MemoryOperationNetworkConfig(operations=operations)
                ),
                lock_network=MemoryLockNetwork(BaseConfig()),
                rchecker=MemoryRedundancyChecker(
                    BaseRedundancyCheckerConfig(
                        key_value_store=MemoryKeyValueStore(BaseConfig())
                    )
                ),
                opimp_network=MemoryOperationImplementationNetwork(
                    MemoryOperationImplementationNetworkConfig(
                        operations=opimps
                    )
                ),
            )
        )
