# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import unittest

from dffml.record import (
    RecordData,
    Record,
)


class TestRecordData(unittest.TestCase):
    def setUp(self):
        self.full = RecordData(
            key=None,
            features=None,
            predictions=None,
            confidences=None,
            last_updated=None,
        )
        self.null = RecordData()

    def test_null_dict_no_prediction(self):
        self.assertNotIn("predictions", self.null.dict())


class TestRecord(unittest.TestCase):
    def setUp(self):
        self.null = Record("null")
        self.full = Record(
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
        self.assertIn("Undetermined", str(self.full))
        self.full.data.predictions = {"Prediction": "Good"}
        self.assertIn("Good", str(self.full.data))
        self.full.extra.update(dict(hi=5))
        self.assertIn("5", str(self.full))
        self.full.extra = dict()
        self.assertNotIn("5", str(self.full))

    def test_merge(self):
        null = Record("null")
        null.merge(self.full)
        self.assertIn("half", null.extra)
        self.assertTrue(null.extra["half"])

    def test_key(self):
        return self.full.data.key

    def test_evaluated(self):
        old_last_updated = self.full.data.last_updated
        results = {"new": "feature"}
        self.full.evaluated({"feed": "face"})
        self.assertIn("feed", self.full.data.features)
        self.assertEqual("face", self.full.data.features["feed"])
        self.full.evaluated(results, overwrite=True)
        self.assertEqual(self.full.data.features, results)
        self.assertLessEqual(old_last_updated, self.full.data.last_updated)

    def test_features(self):
        self.assertIn("dead", self.full.features())
        self.assertIn("dead", self.full.features(["dead"]))
        self.assertFalse(self.full.features(["dead", "beaf"]))

    def test_predicted(self):
        old_prediction = self.full.data.predictions.copy()
        old_last_updated = self.full.data.last_updated
        self.full.predicted("target_name", "feed", 1.00)
        self.assertNotEqual(old_prediction, self.full.data.predictions)
        self.assertLessEqual(old_last_updated, self.full.data.last_updated)

    def test_prediction(self):
        self.full.predicted("target_name", "feed", 1.00)
        self.assertTrue(self.full.prediction("target_name"))

    def test_confidence(self):
        self.full.predicted("target_name", "feed", 1.00)
        self.assertTrue(self.full.confidence("target_name"))
