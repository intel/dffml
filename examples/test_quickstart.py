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
        rows = list(filter(lambda line: "value:" in line, lines))
        rows = list(map(
                lambda line:line.replace("value:","").replace("\t","").split(",")[0] ,
                rows)
                )
        row0,row1 = rows
        # Ensure predictions are floats
        float(row0.split()[0])
        float(row1.split()[0])
