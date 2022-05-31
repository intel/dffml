"""

**system_contexts/__init__.py**

"""
from typing import Any, Dict, NewType, Type, List, Union, Callable

from ..base import (
    config,
    field,
    replace_config,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..df.types import Stage, DataFlow, Input, Definition
from ..operation.output import remap
from ..df.memory import MemoryOrchestrator
from ..df.base import op
from ..util.data import merge as _merge
from ..util.entrypoint import base_entry_point, Entrypoint


class _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT:
    pass


LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT = _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT()


class ActiveSystemContext(BaseDataFlowFacilitatorObjectContext):
    parent: "SystemContext"

    async def __aenter__(self) -> "ActiveSystemContext":
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.octx = await self.__stack.enter_async_context(
            self.parent.orchestrator()
        )
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        await self.__stack.aclose()


@config
class SystemContextConfig:
    # parent: Input
    # parent.value = SystemContextConfig()
    # parent.definition = SystemContextConfig
    # inputs: List[Input] # inputs can be added to overlay
    # architecture: OpenArchitecture
    upstream: "SystemContextConfig" = field(
        "The system context which created this system context, or which this system context is to be derived from, or duplicated exactly (aka re-run or something)"
    )
    # When we run the overlay we should pass the system context / system context
    # config.
    # Links live within overlay
    # links: 'SystemContextConfig'
    overlay: "SystemContextConfig" = field(
        "The overlay we will apply with any overlays to merge within it (see default overlay usage docs)"
    )
    orchestrator: "SystemContextConfig" = field(
        "The system context who's default flow will be used to produce an orchestrator which will be used to execute this system context including application of overlays"
    )


# TODO Check validity on instantiation within __post_init__ (do we know all
# origins for all inputs used, and is all I/O declared unused exlicity or
# used somewhere.
# valid: bool = False
# SystemContext aka the DataFlowFacilitatorObject, the generic implementation of
# the base class.
@base_entry_point("dffml.sysctx", "sysctx")
class SystemContext(BaseDataFlowFacilitatorObject):
    """
    >>> SystemContext(
    ...     links=[None],
    ...     upstream=,
    ...     overlay=,
    ...     orchestrator=,
    ... )
    """

    CONFIG = SystemContextConfig
    CONTEXT = ActiveSystemContext

    async def __aenter__(self) -> "SystemContext":
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        # TODO Ensure orchestrators are reentrant
        self.orchestrator = await self.__stack.enter_async_context(
            self.parent.config.orchestrator
        )
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        await self.__stack.aclose()

    def __call__(self):
        return self.CONTEXT(self)

    def deployment(
        self,
        deployment_environment: Union[
            _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT, str
        ] = LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT,
    ) -> Callable[Any, Any]:
        return

    @classmethod
    def config_as_defaults_for_subclass(
        cls, new_class_name: str, **kwargs,
    ) -> "SystemContext":
        return entrypoint(new_class_name)(
            type(
                new_class_name,
                (cls,),
                {
                    "CONFIG": replace_config(
                        new_class_name + "Config",
                        cls.CONFIG,
                        {
                            key: {"default_factory": lambda: value}
                            for key, value in kwargs.items()
                        },
                    ),
                },
            ),
        )


for sysctx in SystemContext.load():
    # Ideally we would have load not setting propreties on the loaded classes.
    # TODO for name, sysctx in SystemContext.load_dict().items():
    name = sysctx.ENTRY_POINT_LABEL
    """
    sysctx.parents
    sysctx.upstream
    sysctx.overlay
    sysctx.orchestrator
    """

    # sysctx.variable_name('python')
    # sysctx.add_to_namespace(sys.modules[__name__])

    # In the event the deployment enviornment requested as not found
    # (aka an auto start operation when condition
    # "string.sysctx.deployment.unknown" is present as an input)

    def make_correct_python_callable(name, sysctx):
        sysctx.deployment("python")
        # TODO, if deployment has non-auto start operatations with
        def func():
            func.__name__ = name

        return func

    setattr(sys.modules[__name__], name, make_correct_python_callable(syctx))


# END **system_contexts/__init__.py** END
# END **wonderland/async.py** END

# from wonderland import Alice, alice
# from wonderland.async import Alice

# async with AliceSystemContext() as alice:
#     async with alice() as alice_ctx:
#         async for thought in alice_ctx.thoughts():
#         # async for thought in alice_ctx(): # .thoughts is the default

# async with Alice() as alice:
#     async for thought in alice:

# for thought in alice:
#     print(thought)

# alice = Alice()
# for thought in alice:
#     print(thought)
