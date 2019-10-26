# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import sys
import copy
import json
import asyncio
import logging
import unittest
from unittest.mock import patch

from dffml.repo import Repo
from dffml.port import Port
from dffml.feature import Feature, Features
from dffml.source.source import BaseSource
from dffml.model import Model

from dffml.util.cli.arg import Arg, parse_unknown

from dffml.util.cli.cmd import JSONEncoder, CMD, Parser

from dffml.util.cli.parser import (
    list_action,
    ParseLoggingAction,
    ParseOutputSpecsAction,
    ParseInputsAction,
    ParseRemapAction,
)

from dffml.util.cli.cmds import ListEntrypoint, FeaturesCMD, ModelCMD

from dffml.util.asynctestcase import AsyncTestCase


def Namespace(**kwargs):
    class MakeNamespace(object):
        pass

    for key, value in kwargs.items():
        setattr(MakeNamespace, key, value)
    return MakeNamespace


class TestParseActions(unittest.TestCase):
    def test_list_action(self):
        dest, cls, parser = ("features", Features, list_action(Features))
        namespace = Namespace(**{dest: False})
        with self.subTest(single=dest):
            action = parser(dest=dest, option_strings="")
            action(None, namespace, "feed")
            self.assertEqual(getattr(namespace, dest, False), Features("feed"))
        with self.subTest(multiple=dest):
            action = parser(dest=dest, option_strings="")
            action(None, namespace, ["feed", "face"])
            self.assertEqual(
                getattr(namespace, dest, False), Features("feed", "face")
            )

    def test_logging(self):
        namespace = Namespace(log=False)
        action = ParseLoggingAction(dest="log", option_strings="")
        with patch.object(logging, "basicConfig") as mock_method:
            action(None, namespace, "DEBUG")
            mock_method.assert_called_once_with(level=logging.DEBUG)
        with patch.object(logging, "basicConfig") as mock_method:
            action(None, namespace, "WARNING")
            mock_method.assert_called_once_with(level=logging.WARNING)

    def test_output_specs(self):
        namespace = Namespace(output_specs=False)
        action = ParseOutputSpecsAction(dest="output_specs", option_strings="")
        action(None, namespace, ["['result']=get_single_spec"])
        self.assertEqual(len(namespace.output_specs), 1)
        self.assertEqual(
            namespace.output_specs[0], (["result"], "get_single_spec")
        )
        action(None, namespace, "['result']=get_single_spec")
        self.assertEqual(len(namespace.output_specs), 1)
        self.assertEqual(
            namespace.output_specs[0], (["result"], "get_single_spec")
        )

    def test_inputs(self):
        namespace = Namespace(inputs=False)
        action = ParseInputsAction(dest="inputs", option_strings="")
        action(None, namespace, ["['result']=get_single_spec"])
        self.assertEqual(len(namespace.inputs), 1)
        self.assertEqual(namespace.inputs[0], (["result"], "get_single_spec"))
        action(None, namespace, "['result']=get_single_spec")
        self.assertEqual(len(namespace.inputs), 1)
        self.assertEqual(namespace.inputs[0], (["result"], "get_single_spec"))

    def test_remap(self):
        namespace = Namespace(inputs=False)
        action = ParseRemapAction(dest="inputs", option_strings="")
        action(None, namespace, ["get_single.result=string_calculator"])
        self.assertEqual(len(namespace.inputs), 1)
        self.assertEqual(
            namespace.inputs[0], ("get_single", "result", "string_calculator")
        )
        action(None, namespace, "get_single.result=string_calculator")
        self.assertEqual(len(namespace.inputs), 1)
        self.assertEqual(
            namespace.inputs[0], ("get_single", "result", "string_calculator")
        )


class TestJSONEncoder(unittest.TestCase):
    def test_default(self):
        class UnregisteredObject(object):
            pass

        self.assertIn(
            "UnregisteredObject",
            json.dumps(UnregisteredObject, cls=JSONEncoder),
        )

    def test_repo(self):
        self.assertIn("face", json.dumps(Repo("face"), cls=JSONEncoder))

    def test_feature(self):
        class FaceFeature(Feature):
            NAME = "face"

        self.assertIn("face", json.dumps(FaceFeature(), cls=JSONEncoder))


class TestCMD(AsyncTestCase):
    def test_init(self):
        class CMDTest(CMD):
            arg_nope_present = Arg("nope", default=False)
            arg_ignored = Arg("ignored")

        cmd = CMDTest(nope=True)
        self.assertTrue(getattr(cmd, "log", False))
        self.assertTrue(getattr(cmd, "nope", False))

    async def test_async_context_management(self):
        async with CMD():
            pass

    async def test_parse_args(self):
        with patch.object(Parser, "add_subs") as mock_method:
            await CMD.parse_args()
            mock_method.assert_called_once_with(CMD)

    async def test_cli_no_sub_command(self):
        with patch.object(Parser, "print_help") as mock_method:
            await CMD.cli()
            mock_method.assert_called_once()

    async def test_cli_sub_command_without_run(self):
        class Secondary(CMD):
            pass

        class Primary(CMD):
            secondary = Secondary

        with patch.object(Parser, "print_help") as mock_method:
            await Primary.cli("secondary")
            mock_method.assert_called_once()

    async def test_cli_run_sub_command_asyncgen(self):
        class Secondary(CMD):
            async def run(self):
                yield 1

        class Primary(CMD):
            secondary = Secondary

        self.assertEqual(sum(await Primary.cli("secondary")), 1)

    async def test_cli_run_sub_command(self):
        class Secondary(CMD):
            async def run(self):
                return 2

        class Primary(CMD):
            secondary = Secondary

        self.assertEqual(await Primary.cli("secondary"), 2)

    async def test_cli_run_single(self):
        class Primary(CMD):
            async def run(self):
                return 2

        self.assertEqual(await Primary.cli(), 2)

    def test_sanitize_args(self):
        args = {"cmd": True, "non_internal": True}
        args = CMD().sanitize_args(args)
        self.assertNotIn("cmd", args)
        self.assertIn("non_internal", args)

    def test_main_result_none(self):
        class Secondary(CMD):
            async def run(self):
                return None

        class Primary(CMD):
            secondary = Secondary

        Primary.main(loop=asyncio.new_event_loop(), argv=["t", "secondary"])

    def test_main_result_not_none(self):
        class Secondary(CMD):
            async def run(self):
                return True

        class Primary(CMD):
            secondary = Secondary

        with patch.object(json, "dump") as mock_method, patch(
            "builtins.print"
        ):
            Primary.main(
                loop=asyncio.new_event_loop(), argv=["t", "secondary"]
            )
            mock_method.assert_called_once()


class TestArg(unittest.TestCase):
    def test_init(self):
        arg = Arg("-test", key="value")
        self.assertEqual(arg.name, "-test")
        self.assertIn("key", arg)
        self.assertEqual(arg["key"], "value")

    def test_modify(self):
        arg = Arg("-test", key="value")
        first = arg.modify(name="-first")
        second = arg.modify(key="new_value")
        self.assertEqual(arg.name, "-test")
        self.assertEqual(first.name, "-first")
        self.assertEqual(second.name, "-test")
        self.assertEqual(second["key"], "new_value")

    def test_parse_unknown(self):
        parsed = parse_unknown(
            "-rchecker-memory-kvstore",
            "withargs",
            "-rchecker-memory-kvstore-withargs-filename",
            "somefile",
        )
        self.assertEqual(
            parsed,
            {
                "rchecker": {
                    "arg": None,
                    "config": {
                        "memory": {
                            "arg": None,
                            "config": {
                                "kvstore": {
                                    "arg": ["withargs"],
                                    "config": {
                                        "withargs": {
                                            "arg": None,
                                            "config": {
                                                "filename": {
                                                    "arg": ["somefile"],
                                                    "config": {},
                                                }
                                            },
                                        }
                                    },
                                }
                            },
                        }
                    },
                }
            },
        )


class TestParser(unittest.TestCase):
    def test_add_subs(self):
        class FakeSubCMD(CMD):
            arg_test = Arg("-test")

        class FakeCMD(CMD):
            sub_cmd = FakeSubCMD

        parser = Parser()
        with patch.object(parser, "add_subparsers") as mock_method:
            parser.add_subs(FakeCMD)
            mock_method.assert_called_once()
        parser = Parser()
        with patch.object(parser, "add_subparsers") as mock_method:
            parser.add_subs(FakeSubCMD)
            with self.assertRaisesRegex(AssertionError, "Called 0 times"):
                mock_method.assert_called_once()


class TestListEntrypoint(AsyncTestCase):
    def test_display_no_docstring(self):
        class FakeClass(CMD):
            pass

        with patch.object(sys.stdout, "write") as mock_method:
            ListEntrypoint().display(FakeClass)
            with self.assertRaisesRegex(AssertionError, "call not found"):
                mock_method.assert_any_call("docstring!")

    def test_display_docstring(self):
        class FakeClass(CMD):
            "docstring!"

        with patch.object(sys.stdout, "write") as mock_method:
            ListEntrypoint().display(FakeClass)
            mock_method.assert_any_call("docstring!")

    async def test_run(self):
        class FakeClass(CMD):
            "docstring!"

        class FakeEntrypoint(object):
            @classmethod
            def load(cls):
                return [FakeClass]

        class FakeListEntrypoint(ListEntrypoint):
            ENTRYPOINT = FakeEntrypoint

        with patch.object(sys.stdout, "write") as mock_method:
            await FakeListEntrypoint().run()
            mock_method.assert_any_call("docstring!")


class TestFeaturesCMD(unittest.TestCase):
    def test_set_timeout(self):
        cmd = FeaturesCMD(timeout=5, features=Features())
        self.assertEqual(cmd.features.timeout, 5)
