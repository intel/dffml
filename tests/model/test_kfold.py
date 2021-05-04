import unittest
from random import randrange

from dffml import *


class Kfold:
    async def split(
        self, source, fold_size, shuffle=False, *args
    ):  # Will split the data into required number of folds
        fold = list()
        split_data = list()
        async for record in load(source):
            if len(fold) < fold_size:
                fold.append(record.export())
            else:
                split_data.append(fold)
                fold = []
        return split_data


class TestKfoldTechnique(unittest.TestCase):
    def test_split(self):
        test_input = [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]]
        fold = 2
        folds = Kfold(dataset)
        test_output = folds.split(test_input)
        self.assertEqual(len(test_ouput), fold)
