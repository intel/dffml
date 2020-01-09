import os
import io
import unittest
import contextlib
import unittest.mock
import importlib.util


class TestQuickstart(unittest.TestCase):
    def run_quickstart(self):
        """
        The quickstart code doesn't have a if __name__ == "__main__" block, so
        importing it will cause it to run.
        """
        spec = importlib.util.spec_from_file_location(
            "quickstart",
            os.path.join(os.path.dirname(__file__), "quickstart.py"),
        )
        common = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(common)

    def test_quickstart(self):
        # Capture output
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.run_quickstart()
        lines = stdout.getvalue().split("\n")
        # Check output of Accuracy
        self.assertIn("Accuracy ", lines[0])
        self.assertIn(".", lines[0])
        # Check that repos have predictions
        row0 = list(filter(lambda line: "confidence) 0" in line, lines))[0]
        row1 = list(filter(lambda line: "confidence) 1" in line, lines))[0]
        # Ensure predictions are floats
        float(row0.split()[0])
        float(row1.split()[0])
