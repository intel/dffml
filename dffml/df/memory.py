import io
import abc
import copy
import asyncio
import secrets
import hashlib
import inspect
import itertools
import traceback
import concurrent.futures
from itertools import product, chain
from contextlib import asynccontextmanager, AsyncExitStack, ExitStack
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
    Callable,
)

from .exceptions import (
    ContextNotPresent,
    DefinitionNotInContext,
    ValidatorMissing,
    MultipleAncestorsFoundError,
)
from .types import (
    Input,
    Parameter,
    Definition,
    Operation,
    Stage,
    DataFlow,
    NO_DEFAULT,
)
from .base import (
    OperationException,
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

from ..base import config, field
from ..util.entrypoint import entrypoint
from ..util.cli.arg import Arg
from ..util.data import ignore_args
from ..util.asynchelper import aenter_stack, concurrently

from .log import LOGGER


@config
class MemoryDataFlowObjectContextConfig:
    # Unique ID of the context, in other implementations this might be a JWT or
    # something
    uid: str


class BaseMemoryDataFlowObject(BaseDataFlowObject):
    def __call__(self) -> BaseDataFlowObjectContext:
        return self.CONTEXT(
            MemoryDataFlowObjectContextConfig(uid=secrets.token_hex()), self
        )


@config
class MemoryKeyValueStoreConfig:
    pass


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

    async def conditional_set(
        self,
        key: str,
        value,
        *,
        checker: Optional[Callable[[bytes], bool]] = lambda value: value
        is not None,
    ) -> bool:
        async with self.lock:
            if checker(self.memory.get(key)):
                self.memory[key] = value
                return True
        return False


@entrypoint("memory")
class MemoryKeyValueStore(BaseKeyValueStore, BaseMemoryDataFlowObject):
    """
    Key Value store backed by dict
    """

    CONTEXT = MemoryKeyValueStoreContext
    CONFIG = MemoryKeyValueStoreConfig


@config
class MemoryInputSetConfig:
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

    async def remove_input(self, item: Input):
        for x in self.__inputs[:]:
            if x.uid == item.uid:
                self.__inputs.remove(x)
                break

    async def remove_unvalidated_inputs(self) -> "MemoryInputSet":
        """
        Removes `unvalidated` inputs from internal list and returns the same.
        """
        unvalidated_inputs = []
        for x in self.__inputs[:]:
            if not x.validated:
                unvalidated_inputs.append(x)
                self.__inputs.remove(x)
        unvalidated_input_set = MemoryInputSet(
            MemoryInputSetConfig(ctx=self.ctx, inputs=unvalidated_inputs)
        )
        return unvalidated_input_set


@config
class MemoryParameterSetConfig:
    ctx: BaseInputSetContext
    parameters: List[Parameter]


class MemoryParameterSet(BaseParameterSet):
    def __init__(self, config: MemoryParameterSetConfig) -> None:
        super().__init__(config)
        self.__parameters = config.parameters

    async def parameters(self) -> AsyncIterator[Parameter]:
        for parameter in self.__parameters:
            yield parameter

    async def inputs_and_parents_recursive(self) -> AsyncIterator[Input]:
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

    async def add(self, notification_item: Any):
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


@config
class MemoryInputNetworkConfig:
    pass


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

    async def receive_from_parent_flow(self, inputs: List[Input]):
        """
        Takes input from parent dataflow and adds it to every active context
        """
        if not inputs:
            return
        async with self.ctxhd_lock:
            ctx_keys = list(self.ctxhd.keys())
        self.logger.debug(f"Receiving {inputs} from parent flow")
        self.logger.debug(f"Forwarding inputs to contexts {ctx_keys}")
        for ctx in ctx_keys:
            await self.sadd(ctx, *inputs)

    async def add(self, input_set: BaseInputSet):
        # Grab the input set context handle
        handle = await input_set.ctx.handle()
        handle_string = handle.as_string()
        # TODO These ctx.add calls should probably happen after inputs are in
        # self.ctxhd

        # remove unvalidated inputs
        unvalidated_input_set = await input_set.remove_unvalidated_inputs()

        # If the context for this input set does not exist create a
        # NotificationSet for it to notify the orchestrator
        if not handle_string in self.input_notification_set:
            self.input_notification_set[handle_string] = NotificationSet()
            async with self.ctx_notification_set() as ctx:
                await ctx.add((None, input_set.ctx))
        # Add the input set to the incoming inputs
        async with self.input_notification_set[handle_string]() as ctx:
            await ctx.add((unvalidated_input_set, input_set))
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

        >>> import asyncio
        >>> from dffml import *
        >>>
        >>> async def main():
        ...     async with MemoryOrchestrator() as orchestrator:
        ...         async with orchestrator(DataFlow.auto()) as octx:
        ...             await octx.ictx.sadd("Hi")
        >>>
        >>> asyncio.run(main())
        """
        ctx = StringInputSetContext(context_handle_string)
        await self.add(
            MemoryInputSet(MemoryInputSetConfig(ctx=ctx, inputs=list(args)))
        )
        return ctx

    async def cadd(self, ctx, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with an existing context.

        >>> import asyncio
        >>> from dffml import *
        >>>
        >>> async def main():
        ...     async with MemoryOrchestrator() as orchestrator:
        ...         async with orchestrator(DataFlow.auto()) as octx:
        ...             await octx.ictx.sadd(StringInputSetContext("Hi"))
        >>>
        >>> asyncio.run(main())
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

    async def check_conditions(
        self,
        operation: Operation,
        dataflow: DataFlow,
        ctx: BaseInputSetContext,
    ) -> bool:
        async with self.ctxhd_lock:
            # Grab the input set context handle
            handle_string = (await ctx.handle()).as_string()
            # Ensure that the handle_string is present in ctxhd
            if not handle_string in self.ctxhd:
                return
            # Limit search to given context via context handle
            return await self._check_conditions(
                operation, dataflow, self.ctxhd[handle_string].by_origin
            )

    async def _check_conditions(
        self,
        operation: Operation,
        dataflow: DataFlow,
        by_origin: Dict[Union[str, Tuple[str, str]], List[Input]],
    ) -> bool:
        # Grab the input flow to check for definition overrides
        input_flow = dataflow.flow[operation.instance_name]
        # Return that all conditions are satisfied if there are none to satisfy
        if not input_flow.conditions:
            return True
        # Check that all conditions are present and logicly True
        for i, condition_source in enumerate(input_flow.conditions):
            # We must check if we found an Input where the definition
            # matches the definition of the condition in addition to
            # checking that the Input's value is True. If we were not
            # to check that we found a definition we would be effectively
            # saying that the lack of presence equates with the
            # condition being True.
            condition_found_and_true = False
            # Create a list of places this input originates from
            origins = []
            if isinstance(condition_source, dict):
                for origin in condition_source.items():
                    origins.append(origin)
            else:
                origins.append(condition_source)
            # Ensure all conditions from all origins are True
            for origin in origins:
                # See comment in input_flow.inputs section
                (
                    alternate_definitions,
                    origin,
                ) = input_flow.get_alternate_definitions(origin)
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
                    if alternate_definitions:
                        if item.definition.name not in alternate_definitions:
                            continue
                    elif isinstance(condition_source, str):
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
                    condition_found_and_true = bool(item.value)
            # Ensure we were able to find a condition within the input
            # network, and that when we found it it's value was True.
            if condition_found_and_true:
                return True
        return False

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
                # Ensure we were able to find a condition within the input
                # network, and that when we found it it's value was True.
                if not await self._check_conditions(
                    operation, dataflow, by_origin
                ):
                    return
                # Grab the input flow to check for definition overrides
                input_flow = dataflow.flow[operation.instance_name]
                # Gather all inputs with matching definitions and contexts
                for input_name, input_sources in input_flow.inputs.items():
                    # Create parameters for all the inputs
                    gather[input_name] = []
                    for input_source in input_sources:
                        # Create a list of places this input originates from
                        origins = []
                        # Handle the case where we look at the first instance in
                        # the list for the immediate alternate definition then
                        # trace back through input origins to make sure they all
                        # match
                        if isinstance(input_source, list):
                            # TODO Refactor this since we have duplicate code
                            if isinstance(input_source[0], dict):
                                for origin in input_source[0].items():
                                    origins.append(origin)
                            else:
                                origins.append(input_source[0])
                        elif isinstance(input_source, dict):
                            for origin in input_source.items():
                                origins.append(origin)
                        else:
                            origins.append(input_source)
                        for origin in origins:
                            # Check if the origin is a tuple where the first
                            # value is the origin (such as "seed") and the
                            # second value is an array of allowed alternate
                            # Definition's (their names) within that origin.
                            # These definitions will be used instead of the
                            # default one the input specified for the
                            # operation).
                            (
                                alternate_definitions,
                                origin,
                            ) = input_flow.get_alternate_definitions(origin)
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
                                if alternate_definitions:
                                    if (
                                        item.definition.name
                                        not in alternate_definitions
                                    ):
                                        continue
                                elif isinstance(origin, str):
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
                                # When the input_source is a list of alternate
                                # definitions we need to check each parent to
                                # verity that it's origin matches with the list
                                # given by input_source
                                if isinstance(input_source, list):
                                    all_parent_origins_match = True
                                    # Make a list of all the origins
                                    ancestor_origins = []
                                    for ancestor_origin in input_source:
                                        if isinstance(ancestor_origin, dict):
                                            for (
                                                ancestor_origin
                                            ) in ancestor_origin.items():
                                                ancestor_origins.append(
                                                    ancestor_origin
                                                )
                                        else:
                                            ancestor_origins.append(
                                                ancestor_origin
                                            )
                                    i = 1
                                    current_parent = item
                                    while i < len(ancestor_origins):
                                        ancestor_origin = ancestor_origins[i]
                                        # Go through all the parents. Create a
                                        # list of possible parents based on if
                                        # their origin matches the alternate
                                        # definition
                                        possible_parents = [
                                            parent
                                            for parent in current_parent.parents
                                            # If the input source is a dict then
                                            # we need to convert it to a tuple
                                            # for comparison to the origin
                                            if parent.origin == ancestor_origin
                                        ]
                                        if not possible_parents:
                                            all_parent_origins_match = False
                                            break
                                        elif len(possible_parents) > 1:
                                            # TODO Go through each option and
                                            # check if either is a viable
                                            # option. Our current implementation
                                            # only allows for valeting one path,
                                            # due to a single current_parent
                                            # If there is more than one option
                                            # raise an error since we don't know
                                            # who to choose
                                            raise MultipleAncestorsFoundError(
                                                (
                                                    operation.instance_name,
                                                    input_name,
                                                    ancestor_origin,
                                                    [
                                                        parent.__dict__
                                                        for parent in possible_parents
                                                    ],
                                                )
                                            )
                                        # Move on to the next origin to validate
                                        i += 1
                                        # The current_parent becomes the only
                                        # possible parent
                                        current_parent = possible_parents[0]
                                    # If we didn't find any ancestor paths that
                                    # matched then we don't use this Input
                                    if not all_parent_origins_match:
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
                    # There is no data in the network for an input
                    if not gather[input_name]:
                        # Check if there is a default value for the parameter,
                        # if so use it. That default will either come from the
                        # definition attached to input_name, or it will come
                        # from one of the alternate definition given within the
                        # input flow for the input_name.
                        check_for_default_value = [
                            operation.inputs[input_name]
                        ] + alternate_definitions
                        for definition in check_for_default_value:
                            # Check if the definition has a default value that is not _NO_DEFAULT
                            if "dffml.df.types._NO_DEFAULT" not in repr(
                                definition.default
                            ):
                                gather[input_name].append(
                                    Parameter(
                                        key=input_name,
                                        value=definition.default,
                                        origin=item,
                                        definition=operation.inputs[
                                            input_name
                                        ],
                                    )
                                )
                                break
                        # If there is no default value, we don't have a complete
                        # paremeter set, so we bail out
                        else:
                            return
        # Generate all possible permutations of applicable inputs
        # Create the parameter set for each
        products = list(
            map(
                lambda permutation: MemoryParameterSet(
                    MemoryParameterSetConfig(ctx=ctx, parameters=permutation)
                ),
                product(*list(gather.values())),
            )
        )
        # Check if each permutation has been executed before
        async for parameter_set, taken in rctx.take_if_non_existant(
            operation, *products
        ):
            # If taken then yield the permutation
            if taken:
                yield parameter_set


@entrypoint("memory")
class MemoryInputNetwork(BaseInputNetwork, BaseMemoryDataFlowObject):
    """
    Inputs backed by a set
    """

    CONTEXT = MemoryInputNetworkContext
    CONFIG = MemoryInputNetworkConfig


@config
class MemoryOperationNetworkConfig:
    # Starting set of operations
    operations: List[Operation] = field(
        "Starting set of operations", default_factory=lambda: []
    )


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


@entrypoint("memory")
class MemoryOperationNetwork(BaseOperationNetwork, BaseMemoryDataFlowObject):
    """
    Operations backed by a set
    """

    CONTEXT = MemoryOperationNetworkContext
    CONFIG = MemoryOperationNetworkConfig


@config
class MemoryRedundancyCheckerConfig:
    kvstore: BaseKeyValueStore = field(
        "Key value store to use", default_factory=lambda: MemoryKeyValueStore()
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
            self.parent.kvstore()
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__stack.aclose()

    @staticmethod
    def _unique(instance_name: str, handle: str, *uids: str) -> str:
        """
        SHA384 hash of the parameter set context handle as a string, the
        operation.instance_name, and the sorted list of input uuids.
        """
        uid_list = [instance_name, handle] + sorted(uids)
        return hashlib.sha384("".join(uid_list).encode("utf-8")).hexdigest()

    async def unique(
        self, operation: Operation, parameter_set: BaseParameterSet
    ) -> str:
        """
        SHA384 hash of the parameter set context handle as a string, the
        operation.instance_name, and the sorted list of input uuids.
        """
        return self._unique(
            operation.instance_name,
            (await parameter_set.ctx.handle()).as_string(),
            *[item.origin.uid async for item in parameter_set.parameters()],
        )

    async def _take(self, coro) -> bool:
        return await self.kvctx.conditional_set(
            await coro, "\x01", checker=lambda value: value != "\x01"
        )

    async def take_if_non_existant(
        self, operation: Operation, *parameter_sets: BaseParameterSet
    ) -> bool:
        # TODO(p4) Run tests to choose an optimal threaded vs non-threaded value
        if len(parameter_sets) < 4:
            for parameter_set in parameter_sets:
                yield parameter_set, await self._take(
                    self.unique(operation, parameter_set)
                )
        else:
            async for parameter_set, taken in concurrently(
                {
                    asyncio.create_task(
                        self._take(
                            self.parent.loop.run_in_executor(
                                self.parent.pool,
                                self._unique,
                                operation.instance_name,
                                (await parameter_set.ctx.handle()).as_string(),
                                *[
                                    item.origin.uid
                                    async for item in parameter_set.parameters()
                                ],
                            )
                        )
                    ): parameter_set
                    for parameter_set in parameter_sets
                }
            ):
                yield parameter_set, taken


@entrypoint("memory")
class MemoryRedundancyChecker(BaseRedundancyChecker, BaseMemoryDataFlowObject):
    """
    Redundancy Checker backed by Memory Key Value Store
    """

    CONTEXT = MemoryRedundancyCheckerContext
    CONFIG = MemoryRedundancyCheckerConfig

    def __init__(self, config):
        super().__init__(config)
        self.loop = None
        self.pool = None
        self.__pool = None

    async def __aenter__(self) -> "MemoryRedundancyCheckerContext":
        self.__stack = AsyncExitStack()
        self.__exit_stack = ExitStack()
        self.__exit_stack.__enter__()
        await self.__stack.__aenter__()
        self.kvstore = await self.__stack.enter_async_context(
            self.config.kvstore
        )
        self.loop = asyncio.get_event_loop()
        self.pool = self.__exit_stack.enter_context(
            concurrent.futures.ThreadPoolExecutor()
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__exit_stack.__exit__(exc_type, exc_value, traceback)
        await self.__stack.__aexit__(exc_type, exc_value, traceback)


@config
class MemoryLockNetworkConfig:
    pass


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
            inputs = [
                item
                async for item in parameter_set.inputs_and_parents_recursive()
            ]
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


@entrypoint("memory")
class MemoryLockNetwork(BaseLockNetwork, BaseMemoryDataFlowObject):

    CONTEXT = MemoryLockNetworkContext
    CONFIG = MemoryLockNetworkConfig


@config
class MemoryOperationImplementationNetworkConfig:
    operations: Dict[str, OperationImplementation] = field(
        "Operation implementations to load on initialization",
        default_factory=lambda: {},
    )


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
        self,
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
        # Set the correct instance_name
        opimp = copy.deepcopy(opimp)
        opimp.op = operation
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

    async def run_no_retry(
        self,
        ctx: BaseInputSetContext,
        octx: BaseOrchestratorContext,
        operation: Operation,
        inputs: Dict[str, Any],
    ) -> Union[bool, Dict[str, Any]]:
        """
        Run an operation in our network without retry if it fails
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
            str_inputs = str(inputs)
            self.logger.debug(
                "Inputs: %s",
                str_inputs
                if len(str_inputs) < 512
                else (str_inputs[:512] + "..."),
            )
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
            str_outputs = str(outputs)
            self.logger.debug(
                "Outputs: %s",
                str_outputs
                if len(str_outputs) < 512
                else (str_outputs[:512] + "..."),
            )
            self.logger.debug("---")
            return outputs

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
        if not operation.retry:
            return await self.run_no_retry(ctx, octx, operation, inputs)
        for retry in range(0, operation.retry):
            try:
                return await self.run_no_retry(ctx, octx, operation, inputs)
            except Exception:
                # Raise if no more tries left
                if (retry + 1) == operation.retry:
                    raise
                # Otherwise if there was an exception log it
                self.logger.error(
                    "%r: try %d: %s",
                    operation.instance_name,
                    retry + 1,
                    traceback.format_exc().rstrip(),
                )

    async def operation_completed(self):
        await self.completed_event.wait()
        self.completed_event.clear()

    async def run_dispatch(
        self,
        octx: BaseOrchestratorContext,
        operation: Operation,
        parameter_set: BaseParameterSet,
        set_valid: bool = True,
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
                return
            if not inspect.isasyncgen(outputs):

                async def to_async_gen(x):
                    yield x

                outputs = to_async_gen(outputs)
        async for an_output in outputs:
            # Create a list of inputs from the outputs using the definition mapping
            try:
                inputs = []
                if operation.expand:
                    expand = operation.expand
                else:
                    expand = []
                parents = [
                    item.origin async for item in parameter_set.parameters()
                ]
                for key, output in an_output.items():
                    if not key in expand:
                        output = [output]
                    for value in output:
                        new_input = Input(
                            value=value,
                            definition=operation.outputs[key],
                            parents=parents,
                            origin=(operation.instance_name, key),
                        )
                        new_input.validated = set_valid
                        inputs.append(new_input)
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


@entrypoint("memory")
class MemoryOperationImplementationNetwork(
    BaseOperationImplementationNetwork, BaseMemoryDataFlowObject
):

    CONTEXT = MemoryOperationImplementationNetworkContext
    CONFIG = MemoryOperationImplementationNetworkConfig


MEMORYORCHESTRATORCONFIG_MAX_CTXS: int = None


@config
class MemoryOrchestratorConfig:
    input_network: BaseInputNetwork = field(
        "Input network to use", default_factory=lambda: MemoryInputNetwork()
    )
    operation_network: BaseOperationNetwork = field(
        "Operation network to use",
        default_factory=lambda: MemoryOperationNetwork(),
    )
    lock_network: BaseLockNetwork = field(
        "Lock network to use", default_factory=lambda: MemoryLockNetwork()
    )
    opimp_network: BaseOperationImplementationNetwork = field(
        "Operation implementation network to use",
        default_factory=lambda: MemoryOperationImplementationNetwork(),
    )
    rchecker: BaseRedundancyChecker = field(
        "Redundancy checker to use",
        default_factory=lambda: MemoryRedundancyChecker(),
    )
    # Maximum number of contexts to run concurrently
    max_ctxs: int = MEMORYORCHESTRATORCONFIG_MAX_CTXS


@config
class MemoryOrchestratorContextConfig:
    uid: str
    dataflow: DataFlow
    # Context objects to reuse. If not present in this dict a new context object
    # will be created.
    reuse: Dict[str, BaseDataFlowObjectContext] = None
    # Maximum number of contexts to run concurrently
    max_ctxs: int = MEMORYORCHESTRATORCONFIG_MAX_CTXS

    def __post_init__(self):
        if self.reuse is None:
            self.reuse = {}


class MemoryOrchestratorContext(BaseOrchestratorContext):
    def __init__(
        self,
        config: MemoryOrchestratorContextConfig,
        parent: "BaseOrchestrator",
    ) -> None:
        super().__init__(config, parent)
        self._stack = None
        # Maps instance_name to OrchestratorContext
        self.subflows = {}

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
                    else:
                        self.logger.debug(
                            "Instantiating operation implementation %s(%s) with provided config %r",
                            operation.instance_name,
                            operation.name,
                            opimp_config,
                        )
                    if isinstance(opimp_config, dict) and hasattr(
                        getattr(opimp, "CONFIG", False), "_fromdict"
                    ):
                        opimp_config = opimp.CONFIG._fromdict(**opimp_config)
                    await self.nctx.instantiate(
                        operation, opimp_config, opimp=opimp
                    )

    async def seed_inputs(
        self,
        *,
        ctx: Optional[BaseInputSetContext] = None,
        input_set: Optional[Union[List[Input], BaseInputSet]] = None,
    ) -> BaseInputSetContext:
        if ctx is not None and not isinstance(ctx, BaseInputSetContext):
            raise TypeError(
                f"ctx {ctx} is of type {type(ctx)}, should be BaseInputSetContext"
            )
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

    async def forward_inputs_to_subflow(self, inputs: List[Input]):
        if not inputs:
            return
        # Go through input set,find instance_names of registered subflows which
        # have definition of the current input listed in `forward`.
        # If found,add `input` to list of inputs to forward for that instance_name
        forward = self.config.dataflow.forward
        if not forward.book:
            return
        inputs_to_forward = {}
        for item in inputs:
            instance_list = forward.get_instances_to_forward(item.definition)
            for instance_name in instance_list:
                inputs_to_forward.setdefault(instance_name, []).append(item)
        self.logger.debug(
            f"Forwarding inputs from {inputs_to_forward} to {self.subflows}"
        )
        for instance_name, inputs in inputs_to_forward.items():
            if instance_name in self.subflows:
                await self.subflows[
                    instance_name
                ].ictx.receive_from_parent_flow(inputs)

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
            await self.forward_inputs_to_subflow(self.config.dataflow.seed)
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
                await self.forward_inputs_to_subflow(input_set)
                ctxs.append(
                    await self.seed_inputs(
                        ctx=StringInputSetContext(ctx_string)
                        if isinstance(ctx_string, str)
                        else ctx_string,
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
        # Track the number of contexts running
        num_ctxs = 0
        # If the max_ctxs is more than the total number of contexts, then set max_ctxs to None
        if self.config.max_ctxs is not None and self.config.max_ctxs > len(
            ctxs
        ):
            self.config.max_ctxs = None
        # Create tasks to wait on the results of each of the contexts submitted
        for ctxs_index in range(0, len(ctxs)):
            if (
                self.config.max_ctxs is not None
                and num_ctxs >= self.config.max_ctxs
            ):
                break
            # Grab the context by its index
            ctx = ctxs[ctxs_index]
            self.logger.debug(
                "kickstarting context: %s", (await ctx.handle()).as_string()
            )
            tasks.add(
                asyncio.create_task(
                    self.run_operations_for_ctx(ctx, strict=strict)
                )
            )
            # Ensure we don't run more contexts conncurrently than requested
            num_ctxs += 1
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
                    num_ctxs -= 1
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
                    # Create more tasks to wait on the results of each of the
                    # contexts submitted if we are caping the number of them
                    while (
                        self.config.max_ctxs is not None
                        and num_ctxs <= self.config.max_ctxs
                        and ctxs_index < len(ctxs)
                    ):
                        # Grab the context by it's index
                        ctx = ctxs[ctxs_index]
                        self.logger.debug(
                            "kickstarting context: %s",
                            (await ctx.handle()).as_string(),
                        )
                        tasks.add(
                            asyncio.create_task(
                                self.run_operations_for_ctx(ctx, strict=strict)
                            )
                        )
                        # Keep track of which index we're at
                        ctxs_index += 1
                        # Ensure we don't run more contexts conncurrently than requested
                        num_ctxs += 1
                self.logger.debug("ctx.outstanding: %d", len(tasks) - 1)
        finally:
            # Cancel tasks which we don't need anymore now that we know we are done
            for task in tasks:
                if not task.done():
                    task.cancel()
                else:
                    task.exception()

    async def operations_parameter_set_pairs(
        self,
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
        async for operation in self.octx.operations(
            dataflow, input_set=new_input_set, stage=stage
        ):
            # Generate all pairs of un-run input combinations
            async for parameter_set in self.ictx.gather_inputs(
                self.rctx, operation, dataflow, ctx=ctx
            ):
                yield operation, parameter_set

    async def validator_target_set_pairs(
        self,
        ctx: BaseInputSetContext,
        dataflow: DataFlow,
        unvalidated_input_set: BaseInputSet,
    ):
        async for unvalidated_input in unvalidated_input_set.inputs():
            validator_instance_name = unvalidated_input.definition.validate
            validator = dataflow.validators.get(validator_instance_name, None)
            if validator is None:
                raise ValidatorMissing(
                    "Validator with instance_name {validator_instance_name} not found"
                )
            # There is only one `input` in `validators`
            input_name, input_definition = list(validator.inputs.items())[0]
            parameter = Parameter(
                key=input_name,
                value=unvalidated_input.value,
                origin=unvalidated_input,
                definition=input_definition,
            )
            parameter_set = MemoryParameterSet(
                MemoryParameterSetConfig(ctx=ctx, parameters=[parameter])
            )
            async for parameter_set, taken in self.rctx.take_if_non_existant(
                validator, parameter_set
            ):
                if taken:
                    yield validator, parameter_set

    async def dispatch_auto_starts(self, ctx):
        """
        Schedule the running of all operations without inputs
        """
        for operation in self.config.dataflow.operations.values():
            if operation.inputs or not await self.ictx.check_conditions(
                operation, self.config.dataflow, ctx
            ):
                continue
            parameter_set = MemoryParameterSet(
                MemoryParameterSetConfig(ctx=ctx, parameters=[])
            )
            task = await self.nctx.dispatch(self, operation, parameter_set)
            task.operation = operation
            task.parameter_set = parameter_set
            yield task

    async def run_operations_for_ctx(
        self, ctx: BaseContextHandle, *, strict: bool = True
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        # Track if there are more inputs
        more = True
        # Set of tasks we are waiting on
        tasks = set()
        # String representing the context we are executing operations for
        ctx_str = (await ctx.handle()).as_string()
        # schedule running of operations with no inputs
        async for task in self.dispatch_auto_starts(ctx):
            tasks.add(task)
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
                        if task is input_set_enters_network:
                            raise exception
                        raise OperationException(
                            "{}({}): {}".format(
                                task.operation.instance_name,
                                task.operation.inputs,
                                {
                                    parameter.key: parameter.value
                                    async for parameter in task.parameter_set.parameters()
                                },
                            )
                        ) from exception
                    elif exception is not None:
                        # If there was an exception log it
                        output = io.StringIO()
                        task.print_stack(file=output)
                        self.logger.error("%s", output.getvalue().rstrip())
                        output.close()

                    elif task is input_set_enters_network:
                        (
                            more,
                            new_input_sets,
                        ) = input_set_enters_network.result()
                        for (
                            unvalidated_input_set,
                            new_input_set,
                        ) in new_input_sets:
                            async for operation, parameter_set in self.validator_target_set_pairs(
                                ctx,
                                self.config.dataflow,
                                unvalidated_input_set,
                            ):
                                dispatch_operation = await self.nctx.dispatch(
                                    self, operation, parameter_set
                                )
                                dispatch_operation.operation = operation
                                dispatch_operation.parameter_set = (
                                    parameter_set
                                )
                                tasks.add(dispatch_operation)
                                self.logger.debug(
                                    "[%s]: dispatch operation: %s",
                                    ctx_str,
                                    operation.instance_name,
                                )
                            # forward inputs to subflow
                            await self.forward_inputs_to_subflow(
                                [x async for x in new_input_set.inputs()]
                            )
                            # Identify which operations have completed contextually
                            # appropriate input sets which haven't been run yet
                            async for operation, parameter_set in self.operations_parameter_set_pairs(
                                ctx,
                                self.config.dataflow,
                                new_input_set=new_input_set,
                            ):
                                # Validation operations shouldn't be run here
                                if operation.validator:
                                    continue
                                # Dispatch the operation and input set for running
                                dispatch_operation = await self.nctx.dispatch(
                                    self, operation, parameter_set
                                )
                                dispatch_operation.operation = operation
                                dispatch_operation.parameter_set = (
                                    parameter_set
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
            output = {}
            async for operation, results in self.run_stage(ctx, Stage.OUTPUT):
                output.setdefault(operation.instance_name, {})
                output[operation.instance_name].update(results)
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
        async for operation, parameter_set in self.operations_parameter_set_pairs(
            ctx, self.config.dataflow, stage=stage
        ):
            # Run the operation, input set pair
            yield operation, await self.nctx.run(
                ctx, self, operation, await parameter_set._asdict()
            )


@entrypoint("memory")
class MemoryOrchestrator(BaseOrchestrator, BaseMemoryDataFlowObject):

    CONTEXT = MemoryOrchestratorContext
    CONFIG = MemoryOrchestratorConfig

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
        self,
        dataflow: Union[DataFlow, MemoryOrchestratorContextConfig],
        **kwargs,
    ) -> BaseDataFlowObjectContext:
        config = dataflow
        if isinstance(dataflow, DataFlow):
            kwargs.setdefault("max_ctxs", self.config.max_ctxs)
            config = MemoryOrchestratorContextConfig(
                uid=secrets.token_hex(), dataflow=dataflow, **kwargs
            )
        return self.CONTEXT(config, self)
