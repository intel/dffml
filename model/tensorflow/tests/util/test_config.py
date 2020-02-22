import unittest

import tensorflow.keras.layers

from dffml_model_tensorflow.util.config.tensorflow import (
    tensorflow_docstring_args,
    parse_layers,
)


class TestMakeConfig(unittest.TestCase):
    def test_tensorflow_docstring_args(self):
        args = tensorflow_docstring_args(tensorflow.keras.layers.Dense)
        self.assertIn("units", args)
        dtype, field = args["units"]
        self.assertEqual(dtype, int)
        self.assertEqual(
            field.metadata["description"],
            "Positive integer, dimensionality of the output space.",
        )

        self.assertIn("activation", args)
        dtype, field = args["activation"]
        self.assertEqual(dtype, str)
        self.assertEqual(
            field.metadata["description"],
            "Activation function to use. If you don't specify anything, no activation is applied",
        )


class TestLayerParsing(unittest.TestCase):
    def test_parse_layers(self):
        dead_layers = [
            "Conv2D(filters = 3,kernel_size=3, strides=[6,1], padding='valid', dilation_rate=(1,1), use_bias=True)",
            "InputLayer(input_shape=(32,1))",
        ]

        live_layers = parse_layers(dead_layers)
        l1, l2 = live_layers[0], live_layers[1]

        self.assertEqual(l1.filters, 3)
        self.assertEqual(l1.kernel_size, (3, 3))
        self.assertEqual(l1.strides, (6, 1))
        self.assertEqual(l1.padding, "valid")
        self.assertEqual(l1.dilation_rate, (1, 1))
        self.assertEqual(l1.use_bias, True)
        self.assertEqual(l2.input_shape, [(None, 32, 1)])
