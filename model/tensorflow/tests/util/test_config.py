import unittest

import tensorflow.keras.layers

from dffml_model_tensorflow.util.config.tensorflow import tensorflow_docstring_args


class TestMakeConfig(unittest.TestCase):
    def test_tensorflow_docstring_args(self):
        args = tensorflow_docstring_args(tensorflow.keras.layers.Dense)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",args)

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
