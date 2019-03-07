# pylint: disable=missing-docstring,no-self-use
import unittest

from dffml.feature import Feature, Features
from dffml.source import MemorySource
from dffml.util.asynctestcase import AsyncTestCase

# Git Repo based features
from dffml_feature_git.feature.git import GitFeature
from dffml_feature_git.feature.cloc import GitClocFeature
from dffml_feature_git.feature.lang import GitLangsFeature, GitLangFeature
from dffml_feature_git.feature.work import GitWorkFeature
from dffml_feature_git.feature.release import GitReleaseFeature
from dffml_feature_git.feature.commits import GitCommitsFeature
from dffml_feature_git.feature.authors import GitAuthorsFeature

FEATURES = [
    # Git repo features
    GitCommitsFeature,
    GitAuthorsFeature,
    GitWorkFeature,
    GitClocFeature,
    GitReleaseFeature,
]
GIT_FEATURES = Features(
        *[feature() for feature in FEATURES if issubclass(feature, GitFeature)])

class TestFeature(unittest.TestCase):

    def test_load_builtin_features(self):
        features = Feature.load()
        for mustLoad in FEATURES:
            with self.subTest(mustLoad=mustLoad):
                self.assertIn(mustLoad, features)

class TestGitFeatures(AsyncTestCase):

    async def test_git_features(self):
        async with GIT_FEATURES:
            for src_url in ['https://github.com/tpm2-software/tpm2-tss',
                    'https://github.com/github/gitignore']:
                with self.subTest(src_url=src_url):
                    features = await GIT_FEATURES.evaluate(src_url)
                    self.assertEqual(len(features.values()), len(GIT_FEATURES))
                    for results in features.values():
                        self.assertEqual(len(results), 10)

    async def test_git_feature_fail(self):
        async with GIT_FEATURES:
            for src_url in ['https://github.com/github/nope',
                    'https://google.com']:
                with self.subTest(src_url=src_url):
                    features = await GIT_FEATURES.evaluate(src_url)
                    self.assertEqual(len(features.values()), 0)

class TestLangs(AsyncTestCase):

    def setUp(self):
        self.src_url = 'https://github.com/tpm2-software/tpm2-tss'
        self.features = Features(GitLangsFeature())

    async def test_langs(self):
        async with self.features:
            features = await self.features.evaluate(self.src_url)
            self.assertIn('langs', features)
            self.assertIn('c', features['langs'])
            self.assertGreater(features['langs']['c'], 0.1)

class TestLang(AsyncTestCase):

    def setUp(self):
        self.src_url = 'https://github.com/tpm2-software/tpm2-tss'
        self.features = Features(GitLangFeature())

    async def test_lang(self):
        async with self.features:
            features = await self.features.evaluate(self.src_url)
            self.assertIn('lang', features)
            self.assertEqual('c', features['lang'])
