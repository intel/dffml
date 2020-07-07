import sys
import pathlib
import unittest
import subprocess


ROOT = pathlib.Path(__file__).parents[3]
EXAMPLE_PATH = ROOT / "examples" / "dataflow" / "locking" / "example.py"


class TestLocking(unittest.TestCase):
    def test_run(self):
        stdout = subprocess.check_output([sys.executable, str(EXAMPLE_PATH)])
        lines = stdout.decode().strip().split("\n")
        lines = lines[-4:]
        self.assertEqual(len(lines), 4)
        for line in lines:
            # set i = 1, got i = 1
            # set i = 2, got i = 2
            line = line.split()
            self.assertEqual(line[3].replace(",", ""), line[-1])
