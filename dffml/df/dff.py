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
                 opimpn: BaseOperationImplementationNetwork,
                 orchestrator: BaseOrchestrator) -> None:
        self.input_network = input_network
        self.operation_network = operation_network
        self.lock_network = lock_network
        self.rchecker = rchecker
        self.opimp_network = opimpn
        self.orchestrator = orchestrator
        self.logger = LOGGER.getChild(self.__class__.__qualname__)
        self.__stack = None

    async def evaluate(self):
        # Orchestrate the running of these operations
        async with self.orchestrator(self.ictx, self.octx, self.lctx, self.nctx,
                                     self.rctx) as orchestrate:
            async for ctx, results in orchestrate.run_until_complete():
                yield ctx, results

    async def __aenter__(self) -> 'DataFlowFacilitatorContext':
        '''
        Ahoy matey, enter if ye dare into the management of the contexts. Eh
        well not sure if there's really any context being managed here...
        '''
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.rctx = await self.__stack.enter_async_context(
                self.rchecker())
        self.ictx = await self.__stack.enter_async_context(
                self.input_network())
        self.octx = await self.__stack.enter_async_context(
                self.operation_network())
        self.lctx = await self.__stack.enter_async_context(
                self.lock_network())
        self.nctx = await self.__stack.enter_async_context(
                self.opimp_network())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__stack.aclose()

class DataFlowFacilitator(object):
    '''
    Data Flow Facilitator-tots
    '''

    def __init__(self) -> None:
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    def __call__(self,
                 input_network: BaseInputNetwork,
                 operation_network: BaseOperationNetwork,
                 lock_network: BaseLockNetwork,
                 rchecker: BaseRedundancyChecker,
                 opimpn: BaseOperationImplementationNetwork,
                 orchestrator: BaseOrchestrator) \
                         -> 'DataFlowFacilitatorContext':
        return DataFlowFacilitatorContext(input_network,
                                          operation_network,
                                          lock_network,
                                          rchecker,
                                          opimpn,
                                          orchestrator)
