import unittest

from dffml.util.config.numpy import numpy_docstring_args

from .double_ret import double_ret as numpy_double_ret


class TestMakeConfig(unittest.TestCase):
    def test_numpy_docstring_args(self):
        args = numpy_docstring_args(numpy_double_ret)

        self.assertIn("super_cool_arg", args)
        dtype, field = args["super_cool_arg"]
        self.assertEqual(dtype, str)
        self.assertEqual(
            field.metadata["description"],
            "Argument we want the string value of.",
        )

        self.assertIn("other_very_cool_arg", args)
        dtype, field = args["other_very_cool_arg"]
        self.assertEqual(dtype, dict)
        self.assertEqual(
            field.metadata["description"],
            "Dictionary we want to turn into a tuple of (keys, values).",
        )
