'''
Base classes for DFFML. All classes in DFFML should inherit from these so that
they follow a similar API for instantiation and usage.
'''
import abc
from typing import Dict, Any

from .util.entrypoint import Entrypoint

from .log import LOGGER

class LoggingLogger(object):
    '''
    Provide the logger property using Python's builtin logging module.
    '''

    @property
    def logger(self):
        prop_name = '__%s_logger' % (self.__class__.__qualname__,)
        logger = getattr(self, prop_name, False)
        if logger is False:
            logger = LOGGER.getChild(self.__class__.__qualname__)
            setattr(self, prop_name, logger)
        return logger

class BaseConfig(object):
    '''
    All DFFML Base Objects should take an object (likely a typing.NamedTuple) as
    as their config.
    '''
    pass

class BaseConfigurable(abc.ABC):
    '''
    Class which produces a config for itself by providing Args to a CMD (from
    dffml.util.cli.base) and then using a CMD after it contains parsed args to
    instantiate a config (deriving from BaseConfig) which will be used as the
    only parameter to the __init__ of a BaseDataFlowFacilitatorObject.
    '''

    def __init__(self, config: BaseConfig) -> None:
        '''
        BaseConfigurable takes only one argument to __init__,
        its config, which should inherit from BaseConfig. It shall be a object
        containing any information needed to configure the class and it's child
        context's.
        '''
        self.config = config

    @classmethod
    @abc.abstractmethod
    def args(cls) -> Dict[str, Any]:
        pass

    @classmethod
    @abc.abstractmethod
    def config(cls, cmd):
        pass

    @classmethod
    def withconfig(cls, cmd):
        return cls(cls.config(cmd))

class BaseDataFlowFacilitatorObjectContext(LoggingLogger):
    '''
    Base class for all Data Flow Facilitator object's contexts. These are
    classes which support async context management. Classes ending with
    ...Context are the most inner context's which are used in DFFML.

    >>> # Calling obj returns an instance which is a subclass of this class,
    >>> # BaseDataFlowFacilitatorObjectContext.
    >>> async with obj() as ctx:
    >>>     await ctx.method()
    '''

    async def __aenter__(self) -> 'BaseDataFlowFacilitatorObjectContext':
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

class BaseDataFlowFacilitatorObject(BaseDataFlowFacilitatorObjectContext, \
                                    BaseConfigurable, \
                                    Entrypoint,
                                    abc.ABC):
    '''
    Base class for all Data Flow Facilitator objects conforming to the
    instantiate -> enter context -> return context via __call__ -> enter
    returned context's context pattern. Therefore they must contain a CONTEXT
    property, set to the BaseDataFlowFacilitatorObjectContext which will be
    returned from a __call__ to this class.

    DFFML is plugin based using Python's setuptool's entry_point API. All
    classes inheriting from BaseDataFlowFacilitatorObject must have a property
    named ENTRY_POINT. In the form of `dffml.load_point` which will be used to
    load all classes registered to that entry point.

    >>> # Create the base object. Then enter it's context to preform any initial
    >>> # setup. Call obj to get an instance of obj.CONTEXT, which is a subclass
    >>> # of BaseDataFlowFacilitatorObjectContext. ctx, the inner context, does
    >>> # all the heavy lifting.
    >>> async with BaseDataFlowObject() as obj:
    >>>     async with obj() as ctx:
    >>>         await ctx.method()
    '''

    def __init__(self, config: BaseConfig) -> None:
        BaseConfigurable.__init__(self, config)
        # TODO figure out how to call these in __new__
        self.__ensure_property('CONTEXT')
        self.__ensure_property('ENTRY_POINT')

    @abc.abstractmethod
    def __call__(self) -> 'BaseDataFlowFacilitatorObjectContext':
        pass

    @classmethod
    def __ensure_property(cls, property_name):
        if getattr(cls, property_name, None) is None:
            raise ValueError('BaseDataFlowFacilitatorObject\'s may not be ' + \
                             'created without a `%s`. ' % (property_name,) + \
                             'Missing %s.%s' \
                             % (cls.__qualname__, property_name,))
