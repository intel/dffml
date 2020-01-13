# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import ast
import sys
import json
import enum
import logging
import inspect
import asyncio
import argparse
from typing import Tuple, Dict, Any

from ...repo import Repo
from ...feature import Feature

from .arg import Arg, parse_unknown

DisplayHelp = "Display help message"


class ParseLoggingAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(
            namespace, self.dest, getattr(logging, value.upper(), logging.INFO)
        )
        logging.basicConfig(level=getattr(namespace, self.dest))


class JSONEncoder(json.JSONEncoder):
    """
    Encodes dffml types to JSON representation.
    """

    def default(self, obj):
        typename_lower = str(type(obj)).lower()
        if isinstance(obj, Repo):
            return obj.dict()
        elif isinstance(obj, Feature):
            return obj.NAME
        elif isinstance(obj, enum.Enum):
            return str(obj.value)
        elif isinstance(obj, type):
            return str(obj.__qualname__)
        elif "numpy." in typename_lower:
            if ".int" in typename_lower or ".uint" in typename_lower:
                return int(obj)
            elif typename_lower.startswith("float"):
                return float(obj)
        elif str(obj).startswith("typing."):
            return str(obj).split(".")[-1]
        return json.JSONEncoder.default(self, obj)


class Parser(argparse.ArgumentParser):
    def add_subs(self, add_from: "CMD"):
        """
        Add sub commands and arguments recursively
        """
        # Only one subparser should be created even if multiple sub commands
        subparsers = None
        for name, method in [
            (name.lower().replace("_", ""), method)
            for name, method in inspect.getmembers(add_from)
        ]:
            if inspect.isclass(method) and issubclass(method, CMD):
                if subparsers is None:  # pragma: no cover
                    subparsers = self.add_subparsers()  # pragma: no cover
                parser = subparsers.add_parser(
                    name,
                    description=None
                    if method.__doc__ is None
                    else method.__doc__,
                    formatter_class=getattr(
                        method,
                        "CLI_FORMATTER_CLASS",
                        argparse.ArgumentDefaultsHelpFormatter,
                    ),
                )
                parser.set_defaults(cmd=method)
                parser.set_defaults(parser=parser)
                parser.add_subs(method)  # type: ignore
            elif isinstance(method, Arg):
                try:
                    self.add_argument(method.name, **method)
                except argparse.ArgumentError as error:
                    raise Exception(repr(add_from)) from error


class CMD(object):

    JSONEncoder = JSONEncoder
    EXTRA_CONFIG_ARGS = {}

    arg_log = Arg(
        "-log",
        help="Logging level",
        action=ParseLoggingAction,
        required=False,
        default=logging.INFO,
    )

    def __init__(self, extra_config=None, **kwargs) -> None:
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(
                "%s.%s"
                % (self.__class__.__module__, self.__class__.__qualname__)
            )
        if extra_config is None:
            extra_config = {}
        self.extra_config = extra_config
        for name, method in [
            (name.lower().replace("arg_", ""), method)
            for name, method in inspect.getmembers(self)
            if isinstance(method, Arg)
        ]:
            if not name in kwargs and method.name in kwargs:
                name = method.name
            if not name in kwargs and "default" in method:
                kwargs[name] = method["default"]
            if name in kwargs and not hasattr(self, name):
                self.logger.debug("Setting %s = %r", name, kwargs[name])
                setattr(self, name, kwargs[name])
            else:
                self.logger.debug("Ignored %s", name)

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @classmethod
    async def parse_args(cls, *args):
        parser = Parser(
            description=cls.__doc__,
            formatter_class=getattr(
                cls,
                "CLI_FORMATTER_CLASS",
                argparse.ArgumentDefaultsHelpFormatter,
            ),
        )
        parser.add_subs(cls)
        return parser, parser.parse_known_args(args)

    async def do_run(self):
        async with self:
            if inspect.isasyncgenfunction(self.run):
                return [res async for res in self.run()]
            else:
                return await self.run()

    @classmethod
    async def cli(cls, *args):
        parser, (args, unknown) = await cls.parse_args(*args)
        args.extra_config = parse_unknown(*unknown)
        if (
            getattr(cls, "run", None) is not None
            and getattr(args, "cmd", None) is None
        ):
            args.cmd = cls
        if getattr(args, "cmd", None) is None:
            parser.print_help()
            return DisplayHelp
        if getattr(args.cmd, "run", None) is None:
            args.parser.print_help()
            return DisplayHelp
        cmd = args.cmd(**cls.sanitize_args(vars(args)))
        return await cmd.do_run()

    @classmethod
    def sanitize_args(cls, args):
        """
        Remove CMD internals from arguments passed to subclasses of CMD.
        """
        for rm in ["cmd", "parser", "log"]:
            if rm in args:
                del args[rm]
        return args

    @classmethod
    async def _main(cls, *args):
        result = await cls.cli(*args)
        if not result is None and result is not DisplayHelp:
            json.dump(
                result,
                sys.stdout,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
                cls=cls.JSONEncoder,
            )
            print()

    @classmethod
    def main(cls, loop=None, argv=sys.argv):
        """
        Runs cli commands in asyncio loop and outputs in appropriate format
        """
        if loop is None:
            loop = asyncio.get_event_loop()
            # In Python 3.8 ThreadedChildWatcher becomes the default which
            # should work fine for us. However, in Python 3.7 SafeChildWatcher
            # is the default and may cause BlockingIOErrors when many
            # subprocesses are created
            # https://docs.python.org/3/library/asyncio-policy.html#asyncio.FastChildWatcher
            if sys.version_info.major == 3 and sys.version_info.minor == 7:
                watcher = asyncio.FastChildWatcher()
                asyncio.set_child_watcher(watcher)
                watcher.attach_loop(loop)
        result = None
        try:
            result = loop.run_until_complete(cls._main(*argv[1:]))
        except KeyboardInterrupt:  # pragma: no cover
            pass  # pragma: no cover
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    def __call__(self):
        return asyncio.run(self.do_run())

    @classmethod
    def args(cls, args, *above) -> Dict[str, Any]:
        """
        For compatibility with scripts/docs.py. Nothing else at the moment so if
        it doesn't work with other things that's why.
        """
        return args
