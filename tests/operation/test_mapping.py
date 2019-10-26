import unittest

from dffml.operation.mapping import mapping_extract_value, create_mapping


class TestMapping(unittest.TestCase):
    def test_extract_value(self):
        self.assertEqual(
            mapping_extract_value({"key1": {"key2": 42}}, ["key1", "key2"]),
            {"value": 42},
        )

    def test_create(self):
        self.assertEqual(create_mapping("key1", 42), {"mapping": {"key1": 42}})
