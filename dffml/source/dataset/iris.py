import pathlib

from ..csv import CSVSource
from .base import dataset_source
from ...util.net import cached_download
from ...util.file import find_replace_with_hash_validation


@dataset_source("iris.training")
async def iris_training(
    cache_dir: pathlib.Path = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "iris")
        .expanduser()
        .resolve()
    )
):
    """
    Examples
    --------

    .. code-block:: console
        :test:

        $ dffml list records -sources training=iris.training

    >>> from dffml.noasync import load
    >>> from dffml import iris_training
    >>>
    >>> records = list(load(iris_training.source()))
    >>> print(len(records))
    120
    >>> records[0].export()
    {'key': '0', 'features': {'SepalLength': 6.4, 'SepalWidth': 2.8, 'PetalLength': 5.6, 'PetalWidth': 2.2, 'classification': 2}, 'extra': {}}
    """
    original_path = await cached_download(
        "http://download.tensorflow.org/data/iris_training.csv",
        cache_dir / "training_original.csv",
        "376c8ea3b7f85caff195b4abe62f34e8f4e7aece8bd087bbd746518a9d1fd60ae3b4274479f88ab0aa5c839460d535ef",
        protocol_allowlist=["http://"],
    )
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
