from testbook import testbook
import unittest


class TestNotebook(unittest.TestCase):
    # Giving testbook the path to notebook
    @testbook("examples/notebooks/moving_between_models.ipynb")
    def test_stdout(tb, self):
        # Execute specific cells using a range
        tb.execute_cell(range(0, 6))
        # Using inject function to insert and execute our own code during the execution of the notebook.
        # Here, we use it to mock the cached_download() call to change the directory of saving the dataset
        # to be able to gitignore it later on and avoid spam.
        tb.inject(
            """
            data_path = await cached_download(
                "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv",
                "tests/notebooks/data/wine_quality.csv",
                "789e98688f9ff18d4bae35afb71b006116ec9c529c1b21563fdaf5e785aea8b3937a55a4919c91ca2b0acb671300072c",
            )
            """
        )
        # Insert and execute an assertion.
        tb.inject(
            "assert 'tests/notebooks/data/wine_quality.csv' in str(data_path)"
        )
        # Execute the rest of the cells.
        tb.execute_cell(range(8, 21))
        # Get the output of specific cells and make assertions.
        assert tb.cell_output_text(13) == "1599 1279 320"
        assert "Accuracy1" and "Accuracy2" in tb.cell_output_text(19)
        assert "confidence" and "value" in tb.cell_output_text(21)
        assert "confidence" and "value" in tb.cell_output_text(22)
