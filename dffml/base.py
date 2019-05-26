"""
Base classes for DFFML. All classes in DFFML should inherit from these so that
they follow a similar API for instantiation and usage.
"""
import abc
from argparse import ArgumentParser
from typing import Dict, Any, Tuple, NamedTuple

from .util.data import traverse_config_set, traverse_config_get

from .util.entrypoint import Entrypoint

from .log import LOGGER


class MissingArg(Exception):
    """
    Raised when a BaseConfigurable is missing an argument from the args dict it
    created with args(). If this exception is raised then the config() method is
    attempting to retrive an argument which was not set in the args() method.
    """


class MissingConfig(Exception):
    """
    Raised when a BaseConfigurable is missing an argument from the config dict.
    Also raised if there was no default value set and the argument is missing.
    """


class MissingRequiredProperty(Exception):
    """
    Raised when a BaseDataFlowFacilitatorObject is missing some property which
    should have been defined in the class.
    """


class LoggingLogger(object):
    """
    Provide the logger property using Python's builtin logging module.
    """

    @property
    def logger(self):
        prop_name = "__%s_logger" % (self.__class__.__qualname__,)
        logger = getattr(self, prop_name, False)
        if logger is False:
            logger = LOGGER.getChild(self.__class__.__qualname__)
            setattr(self, prop_name, logger)
        return logger


class BaseConfig(object):
    """
    All DFFML Base Objects should take an object (likely a typing.NamedTuple) as
    as their config.
    """


class ConfigurableParsingNamespace(object):
    def __init__(self):
        self.dest = None


class BaseConfigurable(abc.ABC):
    """
    Class which produces a config for itself by providing Args to a CMD (from
    dffml.util.cli.base) and then using a CMD after it contains parsed args to
    instantiate a config (deriving from BaseConfig) which will be used as the
    only parameter to the __init__ of a BaseDataFlowFacilitatorObject.
    """

    __argp = ArgumentParser()

    def __init__(self, config: BaseConfig) -> None:
        """
        BaseConfigurable takes only one argument to __init__,
        its config, which should inherit from BaseConfig. It shall be a object
        containing any information needed to configure the class and it's child
        context's.
        """
        self.config = config

    @classmethod
    def add_orig_label(cls, *above):
        return (
            list(above) + cls.ENTRY_POINT_NAME + [cls.ENTRY_POINT_ORIG_LABEL]
        )

    @classmethod
    def add_label(cls, *above):
        return list(above) + cls.ENTRY_POINT_NAME + [cls.ENTRY_POINT_LABEL]

    @classmethod
    def config_set(cls, args, above, *path) -> BaseConfig:
        return traverse_config_set(
            args, *(cls.add_orig_label(*above) + list(path))
        )

    @classmethod
    def config_get(cls, config, above, *path) -> BaseConfig:
        # unittest.mock.patch doesn't work if we cache args() output.
        args = cls.args({})
        args_above = cls.add_orig_label() + list(path)
        label_above = cls.add_label(*above) + list(path)
        no_label_above = cls.add_label(*above)[:-1] + list(path)
        try:
            arg = traverse_config_get(args, *args_above)
        except KeyError as error:
            raise MissingArg(
                "Arg %r missing from %s%s%s"
                % (
                    args_above[-1],
                    cls.__qualname__,
                    "." if args_above[:-1] else "",
                    ".".join(args_above[:-1]),
                )
            ) from error
        try:
            value = traverse_config_get(config, *label_above)
        except KeyError as error:
            try:
                value = traverse_config_get(config, *no_label_above)
            except KeyError as error:
                if "default" in arg:
                    return arg["default"]
                raise MissingConfig(
                    "%s missing %r from %s"
                    % (
                        cls.__qualname__,
                        label_above[-1],
                        ".".join(label_above[:-1]),
                    )
                ) from error

        if value is None and "default" in arg:
            return arg["default"]
        # TODO This is a oversimplification of argparse's nargs
        if not "nargs" in arg:
            value = value[0]
        if "type" in arg:
            # TODO This is a oversimplification of argparse's nargs
            if "nargs" in arg:
                value = list(map(arg["type"], value))
            else:
                value = arg["type"](value)
        if "action" in arg:
            if isinstance(arg["action"], str):
                # HACK This accesses _pop_action_class from ArgumentParser
                # which is prefaced with an underscore indicating it not an API
                # we can rely on
                arg["action"] = cls.__argp._pop_action_class(arg)
            namespace = ConfigurableParsingNamespace()
            action = arg["action"](dest="dest", option_strings="")
            action(None, namespace, value)
            value = namespace.dest
        return value

    @classmethod
    @abc.abstractmethod
    def args(cls, *above) -> Dict[str, Any]:
        """
        Return a dict containing arguments required for this class
        """

    @classmethod
    @abc.abstractmethod
    def config(cls, config, *above):
        """
        Create the BaseConfig required to instantiate this class by parsing the
        config dict.
        """

    @classmethod
    def withconfig(cls, config, *above):
        return cls(cls.config(config, *above))


class BaseDataFlowFacilitatorObjectContext(LoggingLogger):
    """
    Base class for all Data Flow Facilitator object's contexts. These are
    classes which support async context management. Classes ending with
    ...Context are the most inner context's which are used in DFFML.

    >>> # Calling obj returns an instance which is a subclass of this class,
    >>> # BaseDataFlowFacilitatorObjectContext.
    >>> async with obj() as ctx:
    >>>     await ctx.method()
    """

    async def __aenter__(self) -> "BaseDataFlowFacilitatorObjectContext":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass


class BaseDataFlowFacilitatorObject(
    BaseDataFlowFacilitatorObjectContext, BaseConfigurable, Entrypoint, abc.ABC
):
    """
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
    """

    def __init__(self, config: BaseConfig) -> None:
        BaseConfigurable.__init__(self, config)
        # TODO figure out how to call these in __new__
        self.__ensure_property("CONTEXT")
        self.__ensure_property("ENTRY_POINT")

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__qualname__, self.config)

    @abc.abstractmethod
    def __call__(self) -> "BaseDataFlowFacilitatorObjectContext":
        pass

    @classmethod
    def __ensure_property(cls, property_name):
        if getattr(cls, property_name, None) is None:
            raise MissingRequiredProperty(
                "BaseDataFlowFacilitatorObjects may not be "
                "created without a `%s`. Missing %s.%s"
                % (property_name, cls.__qualname__, property_name)
            )
