from dffml.util.data import traverse_get, traverse_set
from dffml.util.asynctestcase import AsyncTestCase


class TestTraverse(AsyncTestCase):
    def test_traverse_get(self):
        test_dict = {"who": {"am": "i"}}
        val = traverse_get(test_dict, "who", "am",)
        self.assertEqual(val, "i")

        val = traverse_get(test_dict, "who.am",)
        self.assertEqual(val, "i")

        test_dict = {"who.am": {"i": "u"}}
        val = traverse_get(test_dict, '"who.am".i',)
        self.assertEqual(val, "u")

        val = traverse_get(test_dict, "'who.am'.i",)
        self.assertEqual(val, "u")

    def test_traverse_set(self):
        test_dict = {"who": {"am": "i"}}

        traverse_set(test_dict, "who", "am", value="I")
        self.assertEqual(test_dict["who"]["am"], "I")

        traverse_set(test_dict, "who.am", value="I")
        self.assertEqual(test_dict["who"]["am"], "I")

        test_dict = {"who.am": {"i": "u"}}
        traverse_set(test_dict, "'who.am'.i", value="U")
        self.assertEqual(test_dict["who.am"]["i"], "U")
