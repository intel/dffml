"""
Base classes for DFFML. All classes in DFFML should inherit from these so that
they follow a similar API for instantiation and usage.
"""
import abc
import ast
import copy
import inspect
import argparse
import functools
import contextlib
import collections
import dataclasses
import collections.abc
from argparse import ArgumentParser
from typing import Dict, Any, Type, Optional, Union

from .util.data import get_args, get_origin
from .util.cli.arg import Arg
from .util.data import (
    traverse_config_set,
    traverse_config_get,
    type_lookup,
    export_dict,
    parser_helper,
)

from .util.entrypoint import Entrypoint

from .log import LOGGER


ARGP = ArgumentParser()


class ParseExpandAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        setattr(namespace, self.dest, self.LIST_CLS(*values))


# Maps classes to their ParseClassNameAction
LIST_ACTIONS: Dict[Type, Type] = {}


def list_action(list_cls):
    """
    Action to take a list of values and make them values in the list of type
    list_class. Which will be a class descendent from AsyncContextManagerList.
    """
    LIST_ACTIONS.setdefault(
        list_cls,
        type(
            f"Parse{list_cls.__qualname__}Action",
            (ParseExpandAction,),
            {"LIST_CLS": list_cls},
        ),
    )
    return LIST_ACTIONS[list_cls]


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


def mkarg(field):
    if field.type != bool:
        arg = Arg(type=field.type)
    else:
        arg = Arg()
    arg.annotation = field.type
    # HACK For detecting dataclasses._MISSING_TYPE
    if "dataclasses._MISSING_TYPE" not in repr(field.default):
        arg["default"] = field.default
    if "dataclasses._MISSING_TYPE" not in repr(field.default_factory):
        arg["default"] = field.default_factory()
    if field.type == bool:
        arg["action"] = "store_true"
    elif inspect.isclass(field.type):
        if issubclass(field.type, (list, collections.UserList)):
            arg["nargs"] = "+"
            if not hasattr(field.type, "SINGLETON"):
                raise AttributeError(
                    f"{field.type.__qualname__} missing attribute SINGLETON"
                )
            arg["action"] = list_action(field.type)
            arg["type"] = field.type.SINGLETON
        if hasattr(arg["type"], "load_labeled") and field.metadata.get(
            "labeled", False
        ):
            arg["type"] = arg["type"].load_labeled
        if hasattr(arg["type"], "load"):
            # TODO (python3.8) Use Protocol
            arg["type"] = arg["type"].load
    elif get_origin(field.type) in (list, tuple):
        arg["type"] = get_args(field.type)[0]
        arg["nargs"] = "+"
    if "description" in field.metadata:
        arg["help"] = field.metadata["description"]
    if field.metadata.get("action"):
        arg["action"] = field.metadata["action"]
    if field.metadata.get("required"):
        arg["required"] = field.metadata["required"]
    return arg


PRIMITIVE_TYPES = (int, float, str, bool, dict, list, bytes)


def typing_type_cls(param_annotation):
    if get_origin(param_annotation) in [
        Union,
        collections.abc.AsyncIterator,
    ]:
        # If the annotation is of the form Optional
        return list(get_args(param_annotation))[0]
    elif (
        get_origin(param_annotation) is list
        or get_origin(param_annotation) is dict
    ):
        # If the annotation are of the form List[MyDataClass] or Dict[str, MyDataClass]
        # Return list or dict (probably should do more here)
        return get_origin(param_annotation)
    return param_annotation


def convert_value(arg, value):
    if value is None:
        # Return default if not found and available
        if "default" in arg:
            return copy.deepcopy(arg["default"])
        raise MissingConfig

    if not "nargs" in arg and isinstance(value, list):
        value = value[0]
    if "type" in arg:
        type_cls = arg["type"]
        if type_cls == Type:
            type_cls = type_lookup
        # TODO This is a oversimplification of argparse's nargs
        if "nargs" in arg:
            value = list(map(type_cls, value))
        elif getattr(type_cls, "CONFIGLOADABLE", False):
            pass
        else:
            if not ".load" in str(type_cls):
                type_cls = typing_type_cls(type_cls)
            if isinstance(value, str) and type_cls is not str:
                value = parser_helper(value)
            # dict -> dataclass of namedtuple
            if (
                dataclasses.is_dataclass(type_cls)
                or bool(
                    inspect.isclass(type_cls)
                    and issubclass(type_cls, tuple)
                    and hasattr(type_cls, "_asdict")
                )
                and isinstance(value, dict)
            ):
                value = type_cls(**value)
            else:
                value = type_cls(value)
        # list -> tuple
        if arg.annotation is not None and get_origin(arg.annotation) is tuple:
            value = get_origin(arg.annotation)(value)
    if "action" in arg:
        if isinstance(arg["action"], str):
            # HACK This accesses _pop_action_class from ArgumentParser
            # which is prefaced with an underscore indicating it not an API
            # we can rely on
            arg["action"] = ARGP._pop_action_class(arg)
        namespace = ConfigurableParsingNamespace()
        action = arg["action"](dest="dest", option_strings="")
        action(None, namespace, value)
        value = namespace.dest
    return value


def is_config_dict(value):
    return bool(
        isinstance(value, dict)
        and "plugin" in value
        and "config" in value
        and isinstance(value["config"], dict)
    )


def _fromdict(cls, **kwargs):
    for field in dataclasses.fields(cls):
        if field.name in kwargs:
            value = kwargs[field.name]
            config = {}
            if is_config_dict(value):
                value, config = value["plugin"], value["config"]
            value = convert_value(mkarg(field), value)
            if inspect.isclass(value) and issubclass(value, BaseConfigurable):
                # TODO This probably isn't 100% correct. Figure out what we need
                # to do with nested configs.
                value = value.withconfig(
                    {
                        value.ENTRY_POINT_NAME[-1]: {
                            "plugin": None,
                            "config": {
                                key: value
                                if is_config_dict(value)
                                else {"plugin": value, "config": {}}
                                for key, value in config.items()
                            },
                        }
                    }
                )
            kwargs[field.name] = value
    return cls(**kwargs)


def field(
    description: str,
    *args,
    action=None,
    required: bool = False,
    labeled: bool = False,
    metadata: Optional[dict] = None,
    **kwargs,
):
    """
    Creates an instance of :py:func:`dataclasses.field`. The first argument,
    ``description`` is the description of the field, and will be set as the
    ``"description"`` key in the metadata ``dict``.
    """
    if not metadata:
        metadata = {}
    metadata["description"] = description
    metadata["required"] = required
    metadata["labeled"] = labeled
    metadata["action"] = action
    return dataclasses.field(*args, metadata=metadata, **kwargs)


def config_asdict(self, *args, **kwargs):
    return export_dict(**dataclasses.asdict(self, *args, **kwargs))


def config(cls):
    """
    Decorator to create a dataclass
    """
    datacls = dataclasses.dataclass(eq=True, init=True)(cls)
    datacls._fromdict = classmethod(_fromdict)
    datacls._replace = lambda self, *args, **kwargs: dataclasses.replace(
        self, *args, **kwargs
    )
    datacls._asdict = config_asdict
    return datacls


def make_config(cls_name: str, fields, *args, namespace=None, **kwargs):
    """
    Function to create a dataclass
    """
    if namespace is None:
        namespace = {}
    namespace.setdefault("_fromdict", classmethod(_fromdict))
    namespace.setdefault(
        "_replace",
        lambda self, *args, **kwargs: dataclasses.replace(
            self, *args, **kwargs
        ),
    )
    namespace.setdefault("_asdict", config_asdict)
    kwargs["eq"] = True
    kwargs["init"] = True
    # Ensure non-default arguments always come before default arguments
    fields_non_default = []
    fields_default = []
    for name, cls, field in fields:
        if (
            field.default is not dataclasses.MISSING
            or field.default_factory is not dataclasses.MISSING
        ):
            fields_default.append((name, cls, field))
        else:
            fields_non_default.append((name, cls, field))
    fields = fields_non_default + fields_default
    # Create dataclass
    return dataclasses.make_dataclass(
        cls_name, fields, *args, namespace=namespace, **kwargs
    )


@config
class BaseConfig:
    """
    All DFFML Base Objects should take an object (likely a typing.NamedTuple) as
    as their config.
    """

    def __repr__(self):
        return "BaseConfig()"

    def __str__(self):
        return repr(self)


class ConfigurableParsingNamespace(object):
    def __init__(self):
        self.dest = None


class ConfigAndKWArgsMutuallyExclusive(Exception):
    """
    Raised when both kwargs and config are specified.
    """


class BaseConfigurableMetaClass(type, abc.ABC):
    def __new__(cls, name, bases, props, module=None):
        # Create the class
        cls = super(BaseConfigurableMetaClass, cls).__new__(
            cls, name, bases, props
        )
        # Wrap __init__
        setattr(cls, "__init__", cls.wrap(cls.__init__))
        return cls

    @classmethod
    def wrap(cls, func):
        """
        If a subclass of BaseConfigurable is passed keyword arguments, convert
        them into the instance of the CONFIG class.
        """

        @functools.wraps(func)
        def wrapper(self, config: Optional[BaseConfig] = None, **kwargs):
            if config is not None and len(kwargs):
                raise ConfigAndKWArgsMutuallyExclusive
            elif config is None and hasattr(self, "CONFIG"):
                if kwargs:
                    try:
                        config = self.CONFIG(**kwargs)
                    except TypeError as error:
                        error.args = (
                            error.args[0].replace(
                                "__init__", f"{self.CONFIG.__qualname__}"
                            ),
                        )
                        raise
                else:
                    use_CONFIG = True
                    for field in dataclasses.fields(self.CONFIG):
                        if (
                            field.default is dataclasses.MISSING
                            and field.default_factory is dataclasses.MISSING
                        ):
                            use_CONFIG = False
                            break
                    if use_CONFIG:
                        config = self.CONFIG()
                    else:
                        raise TypeError(
                            "__init__() missing 1 required positional argument: 'config'"
                        )
            elif config is None:
                raise TypeError(
                    "__init__() missing 1 required positional argument: 'config'"
                )
            return func(self, config)

        return wrapper


class BaseConfigurable(metaclass=BaseConfigurableMetaClass):
    """
    Class which produces a config for itself by providing Args to a CMD (from
    dffml.util.cli.base) and then using a CMD after it contains parsed args to
    instantiate a config (deriving from BaseConfig) which will be used as the
    only parameter to the __init__ of a BaseDataFlowFacilitatorObject.
    """

    def __init__(self, config: Type[BaseConfig]) -> None:
        """
        BaseConfigurable takes only one argument to __init__,
        its config, which should inherit from BaseConfig. It shall be a object
        containing any information needed to configure the class and it's child
        context's.
        """
        self.config = config
        str_config = str(self.config)
        self.logger.debug(
            str_config if len(str_config) < 512 else (str_config[:512] + "...")
        )

    def __eq__(self, other: "BaseConfigurable") -> bool:
        if inspect.isclass(other) or not isinstance(other, self.__class__):
            return
        return self.config == other.config

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
    def type_for(cls, param: inspect.Parameter):
        """
        Guess the type based off the default value of the parameter, for when a
        parameter doesn't have a type annotation.
        """
        if param.annotation != inspect._empty:
            return param.annotation
        elif param.default is None:
            return parser_helper
        else:
            type_of = type(param.default)
            if type_of is bool:
                return lambda value: bool(parser_helper(value))
            return type_of

    @classmethod
    def config_get(cls, config, above, *path) -> BaseConfig:
        # unittest.mock.patch doesn't work if we cache args() output.
        args = cls.args({})
        args_above = cls.add_orig_label() + list(path)
        label_above = cls.add_label(*above) + list(path)
        no_label_above = cls.add_label(*above)[:-1] + list(path)

        arg = None
        try:
            arg = traverse_config_get(args, *args_above)
        except KeyError as error:
            pass

        if arg is None:
            raise MissingArg(
                "Arg %r missing from %s%s%s"
                % (
                    args_above[-1],
                    cls.__qualname__,
                    "." if args_above[:-1] else "",
                    ".".join(args_above[:-1]),
                )
            )

        value = None
        # Try to get the value specific to this label
        with contextlib.suppress(KeyError):
            value = traverse_config_get(config, *label_above)

        # Try to get the value specific to this plugin
        if value is None:
            with contextlib.suppress(KeyError):
                value = traverse_config_get(config, *no_label_above)

        try:
            return convert_value(arg, value)
        except MissingConfig as error:
            error.args = (
                (
                    "%s missing %r from %s"
                    % (
                        cls.__qualname__,
                        label_above[-1],
                        ".".join(label_above[:-1]),
                    )
                ),
            )
            raise

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        """
        Return a dict containing arguments required for this class
        """
        if getattr(cls, "CONFIG", None) is None:
            raise AttributeError(
                f"{cls.__qualname__} requires CONFIG property or implementation of args() classmethod"
            )
        for field in dataclasses.fields(cls.CONFIG):
            cls.config_set(args, above, field.name, mkarg(field))
        return args

    @classmethod
    def config(cls, config, *above):
        """
        Create the BaseConfig required to instantiate this class by parsing the
        config dict.
        """
        if getattr(cls, "CONFIG", None) is None:
            raise AttributeError(
                f"{cls.__qualname__} requires CONFIG property or implementation of config() classmethod"
            )
        # Build the arguments to the CONFIG class
        kwargs: Dict[str, Any] = {}
        for field in dataclasses.fields(cls.CONFIG):
            kwargs[field.name] = got = cls.config_get(
                config, above, field.name
            )
            if inspect.isclass(got) and issubclass(got, BaseConfigurable):
                try:
                    kwargs[field.name] = got.withconfig(
                        config, *above, *cls.add_label()[:-1]
                    )
                except MissingConfig:
                    kwargs[field.name] = got.withconfig(
                        config, *above, *cls.add_label()
                    )
        return cls.CONFIG(**kwargs)

    @classmethod
    def withconfig(cls, config, *above):
        return cls(cls.config(config, *above))


class BaseDataFlowFacilitatorObjectContext(LoggingLogger):
    """
    Base class for all Data Flow Facilitator object's contexts. These are
    classes which support async context management. Classes ending with
    ...Context are the most inner context's which are used in DFFML.

    See the :class:BaseDataFlowFacilitatorObject for example usage.
    """

    async def __aenter__(self) -> "BaseDataFlowFacilitatorObjectContext":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass


class BaseDataFlowFacilitatorObject(
    BaseDataFlowFacilitatorObjectContext, BaseConfigurable, Entrypoint
):
    """
    Base class for all Data Flow Facilitator objects conforming to the
    instantiate -> enter context -> return context via __call__ -> enter
    returned context's context pattern. Therefore they must contain a CONTEXT
    property, set to the BaseDataFlowFacilitatorObjectContext which will be
    returned from a __call__ to this class.

    DFFML is plugin based using Python's setuptool's entrypoint API. All
    classes inheriting from BaseDataFlowFacilitatorObject must have a property
    named ENTRYPOINT. In the form of `dffml.load_point` which will be used to
    load all classes registered to that entry point.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> # Create the base object. Then enter it's context to preform any initial
    >>> # setup. Call obj to get an instance of obj.CONTEXT, which is a subclass
    >>> # of BaseDataFlowFacilitatorObjectContext. ctx, the inner context, does
    >>> # all the heavy lifting.
    >>>
    >>> class Context(BaseDataFlowFacilitatorObjectContext):
    ...     async def method(self):
    ...         return
    >>>
    >>> class Object(BaseDataFlowFacilitatorObject):
    ...     CONTEXT = Context
    ...     def __call__(self):
    ...         return Context()
    >>>
    >>> async def main():
    ...     async with Object(BaseConfig()) as obj:
    ...         async with obj() as ctx:
    ...             await ctx.method()
    >>>
    >>> asyncio.run(main())
    """

    def __init__(self, config: Type[BaseConfig]) -> None:
        BaseConfigurable.__init__(self, config)
        # TODO figure out how to call these in __new__
        self.__ensure_property("CONTEXT")
        self.__ensure_property("ENTRYPOINT")

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
