from contextlib import asynccontextmanager, AsyncExitStack

from .base import BaseInputNetwork, \
                  BaseOperationNetwork, \
                  BaseLockNetwork, \
                  BaseRedundancyChecker, \
                  BaseOperationImplementationNetwork, \
                  BaseOrchestrator

from .log import LOGGER

class DataFlowFacilitatorContext(object):

    def __init__(self,
                 input_network: BaseInputNetwork,
                 operation_network: BaseOperationNetwork,
                 lock_network: BaseLockNetwork,
                 rchecker: BaseRedundancyChecker,
                 opimp_network: BaseOperationImplementationNetwork,
                 orchestrator: BaseOrchestrator) -> None:
        self.input_network = input_network
        self.operation_network = operation_network
        self.lock_network = lock_network
        self.rchecker = rchecker
        self.opimp_network = opimp_network
        self.orchestrator = orchestrator
        self.logger = LOGGER.getChild(self.__class__.__qualname__)
        self.__stack = None

    async def evaluate(self, strict=False):
        # Orchestrate the running of these operations
        async with self.orchestrator(self.ictx, self.octx, self.lctx, self.nctx,
                                     self.rctx) as orchestrate:
            async for ctx, results in orchestrate.run_operations(strict=strict):
                yield ctx, results

    async def __aenter__(self) -> 'DataFlowFacilitatorContext':
        '''
        Ahoy matey, enter if ye dare into the management of the contexts. Eh
        well not sure if there's really any context being managed here...
        '''
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.rctx = await self.__stack.enter_async_context(
                self.rchecker)
        self.ictx = await self.__stack.enter_async_context(
                self.input_network)
        self.octx = await self.__stack.enter_async_context(
                self.operation_network)
        self.lctx = await self.__stack.enter_async_context(
                self.lock_network)
        self.nctx = await self.__stack.enter_async_context(
                self.opimp_network)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__stack.aclose()

class DataFlowFacilitator(object):
    '''
    Data Flow Facilitator-tots
    '''

    def __init__(self,
                 input_network: BaseInputNetwork,
                 operation_network: BaseOperationNetwork,
                 lock_network: BaseLockNetwork,
                 rchecker: BaseRedundancyChecker,
                 opimp_network: BaseOperationImplementationNetwork,
                 orchestrator: BaseOrchestrator) -> None:
        self.rchecker = rchecker
        self.input_network = input_network
        self.operation_network = operation_network
        self.lock_network = lock_network
        self.opimp_network = opimp_network
        self.orchestrator = orchestrator
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    def __call__(self) -> 'DataFlowFacilitatorContext':
        return DataFlowFacilitatorContext(self.input_network(),
                                          self.operation_network(),
                                          self.lock_network(),
                                          self.rchecker(),
                                          self.opimp_network(),
                                          self.orchestrator)

    async def __aenter__(self) -> 'DataFlowFacilitator':
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.rchecker = await self.__stack.enter_async_context(
                self.rchecker)
        self.input_network = await self.__stack.enter_async_context(
                self.input_network)
        self.operation_network = await self.__stack.enter_async_context(
                self.operation_network)
        self.lock_network = await self.__stack.enter_async_context(
                self.lock_network)
        self.opimp_network = await self.__stack.enter_async_context(
                self.opimp_network)
        self.orchestrator = await self.__stack.enter_async_context(
                self.orchestrator)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__stack.aclose()
