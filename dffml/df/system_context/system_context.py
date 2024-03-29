"""

**system_contexts/__init__.py**

"""
import inspect
import warnings
import itertools
import contextlib
from typing import Any, Dict, NewType, Type, List, Union, Callable

from ...base import (
    config,
    field,
    replace_config,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..types import (
    Stage,
    DataFlow,
    Input,
    Definition,
    APPLY_INSTALLED_OVERLAYS,
)
from ..memory import MemoryOrchestrator
from ..base import op, BaseOrchestrator, BaseDataFlowObjectContext
from ...util.data import merge as _merge
from ...util.entrypoint import base_entry_point, Entrypoint


class DuplicateInputShortNames(Exception):
    """
    Raised when default system context execution cannot be hanlded gracefully
    due to duplicate input values with same shared short name within different
    operations.
    """


class _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT:
    pass


LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT = _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT()


class ActiveSystemContext(BaseDataFlowObjectContext):
    # SystemContextConfig for ActiveSystemContext should not have overlay, and
    # only upstream, since overlay should have already been applied, resulting
    # in the context config being used here, where output of applied is now
    # upstream and there is no more overlay to apply.
    config: "SystemContextConfig"
    parent: "SystemContext"

    def __init__(self, config, parent) -> None:
        super().__init__(config, parent)
        if config is parent.config:
            warnings.warn(
                "ActiveSystemContext.config as SystemContext.config support will be deprecated ASAP",
                DeprecationWarning,
                stacklevel=2,
            )

    async def __aenter__(self) -> "ActiveSystemContext":
        self.__stack = contextlib.AsyncExitStack()
        await self.__stack.__aenter__()
        self.octx = await self.__stack.enter_async_context(
            self.parent.orchestrator(self.config.upstream)
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
    upstream: Union["SystemContextConfig", DataFlow] = field(
        "The system context which created this system context, or which this system context is to be derived from, or duplicated exactly (aka re-run or something)",
    )
    # When we run the overlay we should pass the system context / system context
    # config.
    # Links live within overlay
    # links: 'SystemContextConfig'
    overlay: Union["SystemContextConfig", DataFlow] = field(
        "The overlay we will apply with any overlays to merge within it (see default overlay usage docs)",
        default=APPLY_INSTALLED_OVERLAYS,
    )
    orchestrator: Union["SystemContextConfig", BaseOrchestrator] = field(
        "The system context who's default flow will be used to produce an orchestrator which will be used to execute this system context including application of overlays",
        default_factory=lambda: MemoryOrchestrator,
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
        self.__stack = contextlib.AsyncExitStack()
        await self.__stack.__aenter__()
        # TODO Ensure orchestrators are reentrant
        if inspect.isclass(self.config.orchestrator):
            orchestrator = self.config.orchestrator()
        else:
            orchestrator = self.config.orchestrator
        self.orchestrator = await self.__stack.enter_async_context(
            orchestrator
        )
        # TODO(alice) Apply overlay
        if self.config.overlay not in (None, APPLY_INSTALLED_OVERLAYS):
            breakpoint()
            raise NotImplementedError(
                "Application of overlays within SystemContext class entry not yet supported"
            )
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        await self.__stack.aclose()

    def __call__(self):
        return self.CONTEXT(self.config, self,)

    def deployment(
        self,
        *,
        origin: str = "seed",
        deployment_environment: Union[
            _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT, str
        ] = LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT,
    ) -> Callable[[Any], Any]:
        # TODO Fixup inspect function signature on yielded func including return
        # type annotation
        return self.deployment_async_iter_func(
            deployment_environment=deployment_environment, origin=origin
        )

    def deployment_async_iter_func(
        self,
        *,
        origin: str = "seed",
        deployment_environment: Union[
            _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT, str
        ] = LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT,
    ) -> Callable[[Any], Any]:
        # deployment_environment aka method for dataflow as class aka output
        # aka operation to run
        if not isinstance(self.config.upstream, DataFlow):
            raise NotImplementedError(
                "deployment_async_iter_func only operates on datalfows."
            )
        # NOTE This assumes we are in a system context which has only an
        # upstream and we have already derived the upstream from application of
        # an overlay.
        # TODO(alice) We cannot know the deployment environments available for a
        # dataflow unless we apply overlays. We could execute an incorrect
        # default and then hook via overlays to take control.
        return self.deployment_dataflow_async_iter_func(
            origin=origin, deployment_environment=deployment_environment,
        )

    def deployment_dataflow_async_iter_func(
        self,
        *,
        origin: str = "seed",
        deployment_environment: Union[
            _LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT, str
        ] = LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT,
    ) -> Callable[[Any], Any]:
        # TODO Merge where applicable with related dataflow as class PR
        # https://github.com/intel/dffml/pull/1330/files#diff-8cb812e38e5c575a07ab74c8a9d7e1f0d3f2b81db17cc3da5fe9b6aef694a821R88-R400
        # Create a new function
        async def func(**kwargs):
            # See 4cd70c6ff421fbc902db3499f4bfe4ebe0e6480f for CachedDownloadWrapper
            # Run the top level system context for CLI commands.
            # TODO Allowlist for dataflow inputs from each origin, dataflow
            # including what origin values are for acceptable inputs. For now
            # we consult DataFlow.flow, this is potentiall correct already, but
            # let's just double check.
            if deployment_environment == LOAD_DEFAULT_DEPLOYMENT_ENVIONRMENT:
                # If we are to load the default deployment enviornment, that
                # means we are not running any specific operation, we are going
                # to analyze DataFlow.flow can also be found in a more
                # convenitent form for this task restrucutred by stage and
                # origin within DataFlow.by_origin
                input_definitions_list = list(
                    itertools.chain(
                        *[
                            itertools.chain(
                                *[
                                    operation.inputs.items()
                                    for operation in origins.get(origin, [])
                                ]
                            )
                            for _stage, origins in self.config.upstream.by_origin.items()
                        ]
                    )
                )
                input_definitions = dict(input_definitions_list)
                if len(input_definitions) != len(input_definitions_list):
                    # Raise on duplicate keys
                    raise DuplicateInputShortNames(input_definitions_list)
            else:
                # TODO(alice) Figure out how we should maybe add conditional on
                # target operation via overlay?
                raise NotImplementedError(
                    "No support for calling specific operations within system contexts / different deployment environment yet via system context deployment helpers"
                )
                input_definitions = [
                    operation.inputs
                    for operation in self.config.upstream.by_origin.values()[
                        origin
                    ]
                    if deployment_environment == operation.instance_name
                ][0]

            # Create the active system context and add inputs as needed
            async with self as system_context:
                async with system_context as active_system_context:
                    async for ctx, results in active_system_context.orchestrator.run(
                        self.config.upstream,
                        [
                            Input(
                                value=value,
                                definition=input_definitions[key],
                                origin=origin,
                            )
                            for key, value in kwargs.items()
                        ],
                        overlay=self.config.overlay,
                    ):
                        yield ctx, results

        return func

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
