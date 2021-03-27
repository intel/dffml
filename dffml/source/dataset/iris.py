import pathlib

from ..csv import CSVSource
from .base import dataset_source
from ...util.net import cached_download
from ...util.file import find_replace_with_hash_validation


@dataset_source("iris.training")
def iris_training(
    cache_dir: pathlib.Path = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "iris")
        .expanduser()
        .resolve()
    )
):
    """
    Examples
    --------

    >>> from dffml.noasync import load
    >>> from dffml import iris_training
    >>>
    >>> records = list(load(iris_training.source()))
    >>> print(len(records))
    120
    >>> records[0].export()
    {'key': '0', 'features': {'SepalLength': 6.4, 'SepalWidth': 2.8, 'PetalLength': 5.6, 'PetalWidth': 2.2, 'classification': 2}, 'extra': {}}
    """
    with cached_download(
        "http://download.tensorflow.org/data/iris_training.csv",
        cache_dir / "training_original.csv",
        "376c8ea3b7f85caff195b4abe62f34e8f4e7aece8bd087bbd746518a9d1fd60ae3b4274479f88ab0aa5c839460d535ef",
    ) as original_path:
        # Create a CSV source using header replaced file
        yield CSVSource(
            filename=str(
                find_replace_with_hash_validation(
                    original_path,
                    cache_dir / "training.csv",
                    r".*setosa,versicolor,virginica",
                    "SepalLength,SepalWidth,PetalLength,PetalWidth,classification",
                    expected_sha384_hash="946d1bb691d6a2ca5037028a0c6ac29d68f4026e293fd64f985a61cf31fb72b19d50baa61038398442430db8af926bbd",
                )
            )
        )


@dataset_source("iris.test")
def iris_test(
    cache_dir: pathlib.Path = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "iris")
        .expanduser()
        .resolve()
    )
):
    """
    Examples
    --------

    >>> from dffml.noasync import load
    >>> from dffml import iris_test
    >>>
    >>> records = list(load(iris_test.source()))
    >>> print(len(records))
    30
    >>> records[0].export()
    {'key': '0', 'features': {'SepalLength': 5.9, 'SepalWidth': 3.0, 'PetalLength': 4.2, 'PetalWidth': 1.5, 'classification': 1}, 'extra': {}}
    """
    with cached_download(
        "http://download.tensorflow.org/data/iris_test.csv",
        cache_dir / "test_original.csv",
        "8c2cda42ce5ce6f977d17d668b1c98a45bfe320175f33e97293c62ab543b3439eab934d8e11b1208de1e4a9eb1957714",
        protocol_allowlist=["http://"],
    ) as original_path:
        # Create a CSV source using header replaced file
        yield CSVSource(
            filename=str(
                find_replace_with_hash_validation(
                    original_path,
                    cache_dir / "test.csv",
                    r".*setosa,versicolor,virginica",
                    "SepalLength,SepalWidth,PetalLength,PetalWidth,classification",
                    expected_sha384_hash="4c6c65ca1d0420196626d1a7fb961a4ab770fc2306dad2742f7b08a918bbdfb8ca47a0217cab513f0be18633dc8d5fab",
                )
            )
        )
