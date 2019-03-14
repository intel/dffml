# pylint: disable=missing-docstring,no-self-use
import sys
import inspect
import unittest

from dffml.feature import Feature, Features
from dffml.util.asynctestcase import AsyncTestCase

# feature_name based features
from dffml_feature_feature_name.feature.misc import MiscFeature

FEATURES = Features(*[feature() for _name, feature in \
                    inspect.getmembers(sys.modules[__name__], lambda feature: \
                                       bool(inspect.isclass(feature) and \
                                            issubclass(feature, Feature) and \
                                            feature is not Feature))])

class TestFeature(unittest.TestCase):
    '''
    Test that the model for this feature was pip installed an loads as a plugin
    to dffml.
    '''

    def test_load_builtin_features(self):
        features = Feature.load()
        for mustLoad in FEATURES:
            with self.subTest(mustLoad=mustLoad):
                self.assertIn(mustLoad.__class__, features)

class Testfeature_nameFeatures(AsyncTestCase):

    async def test_feature_name_evaluates(self):
        async with FEATURES:
            for src_url in ['key_that_evaluates_for_all']:
                with self.subTest(src_url=src_url):
                    features = await FEATURES.evaluate(src_url)
                    self.assertEqual(len(features.values()), len(FEATURES))

    async def test_feature_name_fails(self):
        async with FEATURES:
            for src_url in ['key_that_causes_failure_for_all']:
                with self.subTest(src_url=src_url):
                    features = await FEATURES.evaluate(src_url)
                    self.assertEqual(len(features.values()), 0)
