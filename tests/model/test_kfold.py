from random import randrange

import pandas as pd


class Kfold:
    def split(
        self, data, folds=3, shuffle=False
    ):  # Will split the data into required number of folds
        fold_size = int(len(data) / folds)
        if shuffle == True:
            data_duplicate = data.sample(frac=1).reset_index(drop=True)
        else:
            data_duplicate = data
        split_data = list()
        for i in range(folds):
            x = i * fold_size
            fold = list()
            for j in range(x, x + fold_size):
                fold.append(data[j])
            split_data.append(fold)
        return split_data


class TestKfoldTechnique(unittest.TestCase):
    def test_split(self):
        test_input = [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]]
        fold = 2
        folds = Kfold(dataset)
        test_output = folds.split(test_input)
        self.assertEqual(len(test_ouput), fold)
