# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import sys
import json
import asyncio
import logging
import unittest
from unittest.mock import patch

from dffml.repo import Repo
from dffml.port import Port
from dffml.feature import Feature, Features
from dffml.source import Source, Sources
from dffml.model import Model

from dffml.util.cli import \
        ParseSourcesAction, \
        ParseFeaturesAction, \
        ParseModelAction, \
        ParsePortAction, \
        ParseLoggingAction, \
        Arg, \
        JSONEncoder, \
        CMD, \
        Parser, \
        ListEntrypoint, \
        FeaturesCMD, \
        ModelCMD

from dffml.util.asynctestcase import AsyncTestCase

def Namespace(**kwargs):
    class MakeNamespace(object):
        pass
    for key, value in kwargs.items():
        setattr(MakeNamespace, key, value)
    return MakeNamespace

class TestParseActions(unittest.TestCase):

    def test_sources(self):
        def load_from_dict(toload):
            return toload
        namespace = Namespace(sources=False)
        with patch.object(Source, 'load_from_dict',
                          new=load_from_dict) \
                          as mock_method:
            action = ParseSourcesAction(dest='sources', option_strings='')
            action(None, namespace, ['first=src0', 'second=src1'])
            self.assertEqual(len(namespace.sources), 2)
            self.assertEqual(namespace.sources[0], 'first')
            self.assertEqual(namespace.sources[1], 'second')
            action(None, namespace, 'second=src2')
            self.assertEqual(len(namespace.sources), 1)
            self.assertEqual(namespace.sources[0], 'second')

    def test_features(self):
        dest, cls, parser = ('features', Features, ParseFeaturesAction)
        namespace = Namespace(**{dest: False})
        with patch.object(cls, 'load') as mock_method:
            action = parser(dest=dest, option_strings='')
            action(None, namespace, 'fake_%s' % (dest,))
            mock_method.assert_called_once_with(*('fake_%s' % (dest,)))
            self.assertTrue(getattr(namespace, dest, False))

    def test_features_model_port(self):
        for dest, cls, parser in [('model', Model, ParseModelAction),
                                  ('port', Port, ParsePortAction)]:
            namespace = Namespace(**{dest: False})
            with self.subTest(dest=dest, cls=cls, parser=parser):
                with patch.object(cls, 'load',
                                  return_value=lambda: True) as mock_method:
                    action = parser(dest=dest, option_strings='')
                    action(None, namespace, 'fake_%s' % (dest,))
                    mock_method.assert_called_once_with('fake_%s' % (dest,))
                    self.assertTrue(getattr(namespace, dest, False))

    def test_logging(self):
        namespace = Namespace(log=False)
        action = ParseLoggingAction(dest='log', option_strings='')
        with patch.object(logging, 'basicConfig') as mock_method:
            action(None, namespace, 'DEBUG')
            mock_method.assert_called_once_with(level=logging.DEBUG)
        with patch.object(logging, 'basicConfig') as mock_method:
            action(None, namespace, 'WARNING')
            mock_method.assert_called_once_with(level=logging.WARNING)

class TestArg(unittest.TestCase):

    def test_init(self):
        arg = Arg('-test', key='value')
        self.assertEqual(arg.name, '-test')
        self.assertIn('key', arg)
        self.assertEqual(arg['key'], 'value')

    def test_modify(self):
        arg = Arg('-test', key='value')
        first = arg.modify(name='-first')
        second = arg.modify(key='new_value')
        self.assertEqual(arg.name, '-test')
        self.assertEqual(first.name, '-first')
        self.assertEqual(second.name, '-test')
        self.assertEqual(second['key'], 'new_value')

class TestJSONEncoder(unittest.TestCase):

    def test_default(self):
        class UnregisteredObject(object):
            pass
        with self.assertRaisesRegex(TypeError, 'not JSON serializable'):
            json.dumps(UnregisteredObject, cls=JSONEncoder)

    def test_repo(self):
        self.assertIn('face', json.dumps(Repo('face'), cls=JSONEncoder))

    def test_feature(self):
        class FaceFeature(Feature):
            NAME = 'face'
        self.assertIn('face', json.dumps(FaceFeature(), cls=JSONEncoder))

class TestCMD(AsyncTestCase):

    def test_init(self):
        class CMDTest(CMD):
            arg_nope_present = Arg('nope', default=False)
            arg_ignored = Arg('ignored')
        cmd = CMDTest(nope=True)
        self.assertTrue(getattr(cmd, 'log', False))
        self.assertTrue(getattr(cmd, 'nope', False))

    async def test_async_context_management(self):
        async with CMD():
            pass

    async def test_parse_args(self):
        with patch.object(Parser, 'add_subs') as mock_method:
            await CMD.parse_args()
            mock_method.assert_called_once_with(CMD)

    async def test_cli_no_sub_command(self):
        with patch.object(Parser, 'print_help') as mock_method:
            await CMD.cli()
            mock_method.assert_called_once()

    async def test_cli_sub_command_without_run(self):
        class Secondary(CMD):
            pass
        class Primary(CMD):
            secondary = Secondary
        with patch.object(Parser, 'print_help') as mock_method:
            await Primary.cli('secondary')
            mock_method.assert_called_once()

    async def test_cli_run_sub_command_asyncgen(self):
        class Secondary(CMD):
            async def run(self):
                yield 1
        class Primary(CMD):
            secondary = Secondary
        self.assertEqual(sum(await Primary.cli('secondary')), 1)

    async def test_cli_run_sub_command(self):
        class Secondary(CMD):
            async def run(self):
                return 2
        class Primary(CMD):
            secondary = Secondary
        self.assertEqual(await Primary.cli('secondary'), 2)

    def test_sanitize_args(self):
        args = {'cmd': True, 'non_internal': True}
        args = CMD().sanitize_args(args)
        self.assertNotIn('cmd', args)
        self.assertIn('non_internal', args)

    def test_main_result_none(self):
        class Secondary(CMD):
            async def run(self):
                return None
        class Primary(CMD):
            secondary = Secondary
        Primary.main(loop=asyncio.new_event_loop(), argv=['t', 'secondary'])

    def test_main_result_not_none(self):
        class Secondary(CMD):
            async def run(self):
                return True
        class Primary(CMD):
            secondary = Secondary
        with patch.object(json, 'dump') as mock_method:
            Primary.main(loop=asyncio.new_event_loop(), argv=['t', 'secondary'])
            mock_method.assert_called_once()

class TestParser(unittest.TestCase):

    def test_add_subs(self):
        class FakeSubCMD(CMD):
            arg_test = Arg('-test')
        class FakeCMD(CMD):
            sub_cmd = FakeSubCMD
        parser = Parser()
        with patch.object(parser, 'add_subparsers') as mock_method:
            parser.add_subs(FakeCMD)
            mock_method.assert_called_once()
        parser = Parser()
        with patch.object(parser, 'add_subparsers') as mock_method:
            parser.add_subs(FakeSubCMD)
            with self.assertRaisesRegex(AssertionError, 'Called 0 times'):
                mock_method.assert_called_once()

class TestListEntrypoint(AsyncTestCase):

    def test_display_no_docstring(self):
        class FakeClass(CMD):
            pass
        with patch.object(sys.stdout, 'write') as mock_method:
            ListEntrypoint().display(FakeClass)
            with self.assertRaisesRegex(AssertionError, 'call not found'):
                mock_method.assert_any_call('docstring!')

    def test_display_docstring(self):
        class FakeClass(CMD):
            'docstring!'
        with patch.object(sys.stdout, 'write') as mock_method:
            ListEntrypoint().display(FakeClass)
            mock_method.assert_any_call('docstring!')

    async def test_run(self):
        class FakeClass(CMD):
            'docstring!'
        class FakeEntrypoint(object):
            @classmethod
            def load(cls):
                return [FakeClass]
        class FakeListEntrypoint(ListEntrypoint):
            ENTRYPOINT = FakeEntrypoint
        with patch.object(sys.stdout, 'write') as mock_method:
            await FakeListEntrypoint().run()
            mock_method.assert_any_call('docstring!')

class TestFeaturesCMD(unittest.TestCase):

    def test_set_timeout(self):
        cmd = FeaturesCMD(timeout=5)
        self.assertEqual(cmd.features.timeout, 5)

class TestModelCMD(unittest.TestCase):

    def test_set_model_dir(self):
        with patch.multiple(Model, __abstractmethods__=set()):
            cmd = ModelCMD(model_dir='feed', model=Model)
            self.assertEqual(cmd.model.model_dir, 'feed')
