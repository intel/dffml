# pylint: disable=missing-docstring,no-self-use
import unittest

from dffml_feature_git.feature.release import GitReleaseFeature

class TestReleaseFeature(unittest.TestCase):

    VALID = [
            '1.0.0',
            'v1.0.0',
            'curl-7_19_7',
            'miniupnpc_2_1',
            '2_7_5',
            ]
    NOT_VALID = [
            'asdf1',
            'as.df1',
            ]

    def setUp(self):
        self.feature = GitReleaseFeature()

    def test_valid(self):
        for line in self.VALID:
            with self.subTest(line=line):
                self.assertTrue(self.feature.valid_version(line))

    def test_not_valid(self):
        for line in self.NOT_VALID:
            with self.subTest(line=line):
                self.assertFalse(self.feature.valid_version(line))
