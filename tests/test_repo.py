# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import unittest

from dffml.repo import RepoPrediction, RepoData, Repo


class TestRepoPrediction(unittest.TestCase):
    def setUp(self):
        self.value = "good"
        self.confidence = 0.42
        self.full = RepoPrediction(
            confidence=self.confidence, value=self.value
        )
        self.null = RepoPrediction()

    def test_full_property_confidence(self):
        self.assertEqual(self.confidence, self.full["confidence"])
        self.assertEqual(self.full.confidence, self.full["confidence"])

    def test_full_property_value(self):
        self.assertEqual(self.value, self.full["value"])
        self.assertEqual(self.full.value, self.full["value"])

    def test_full_dict_returns_self(self):
        self.assertEqual(self.full, self.full.dict())

    def test_full_len_2(self):
        self.assertEqual(2, len(self.full))

    def test_full_bool_true(self):
        self.assertTrue(self.full)

    def test_null_dict_empty_array(self):
        self.assertEqual([], self.null.dict())

    def test_null_len_0(self):
        self.assertEqual(0, len(self.null))

    def test_null_bool_false(self):
        self.assertFalse(self.null)


class TestRepoData(unittest.TestCase):
    def setUp(self):
        self.full = RepoData(
            src_url=None, features=None, prediction=None, last_updated=None
        )
        self.null = RepoData()

    def test_null_dict_no_prediction(self):
        self.assertNotIn("prediction", self.null.dict())


class TestRepo(unittest.TestCase):
    def setUp(self):
        self.null = Repo("null")
        self.full = Repo(
            "full",
            data=dict(
                features=dict(dead="beef"),
                extra=dict(extra="read all about it"),
            ),
            extra=dict(half=True),
        )

    def test_dict(self):
        data = self.full.dict()
        self.assertIn("extra", data)

    def test_repr(self):
        repr(self.full)

    def test_str(self):
        self.full.prediction = RepoPrediction()
        self.assertIn("Undetermined", str(self.full))
        self.full.data.prediction = RepoPrediction(value="Good")
        self.assertIn("Good", str(self.full))
        self.full.extra.update(dict(hi=5))
        self.assertIn("5", str(self.full))
        self.full.extra = dict()
        self.assertNotIn("5", str(self.full))

    def test_merge(self):
        null = Repo("null")
        null.merge(self.full)
        self.assertIn("half", null.extra)
        self.assertTrue(null.extra["half"])

    def test_src_url(self):
        return self.full.data.src_url

    def test_evaluated(self):
        old_last_updated = self.full.data.last_updated
        results = {"new": "feature"}
        self.full.evaluated({"feed": "face"})
        self.assertIn("feed", self.full.data.features)
        self.assertEqual("face", self.full.data.features["feed"])
        self.full.evaluated(results, overwrite=True)
        self.assertEqual(self.full.data.features, results)
        self.assertNotEqual(old_last_updated, self.full.data.last_updated)

    def test_features(self):
        self.assertIn("dead", self.full.features())
        self.assertIn("dead", self.full.features(["dead"]))
        self.assertFalse(self.full.features(["dead", "beaf"]))

    def test_predicted(self):
        old_prediction = self.full.data.prediction
        old_last_updated = self.full.data.last_updated
        self.full.predicted("feed", 1.00)
        self.assertNotEqual(old_prediction, self.full.data.prediction)
        self.assertNotEqual(old_last_updated, self.full.data.last_updated)

    def test_prediction(self):
        self.full.predicted("feed", 1.00)
        self.assertTrue(self.full.prediction())
