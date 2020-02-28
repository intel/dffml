import os
import unittest

from dffml.util.os import prepend_to_path


class TestOS(unittest.TestCase):
    def test_prepend_to_path(self):
        old_path = os.environ["PATH"]
        with prepend_to_path("jellybeans", "fritos"):
            self.assertEqual(
                os.environ["PATH"], "jellybeans:fritos:" + old_path
            )
