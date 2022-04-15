import pathlib

from ..source import Sources
from ..idx3 import IDX3Source
from ..idx1 import IDX1Source
from .base import dataset_source
from ...util.net import cached_download


@dataset_source("mnist.training")
async def mnist_training(
    cache_dir: pathlib.Path = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "mnist")
        .expanduser()
        .resolve()
    )
):
    """
    Examples
    --------

    .. code-block:: console
        :test:

        $ dffml list records -sources training=mnist.training

    >>> from dffml.noasync import load
    >>> from dffml import mnist_training
    >>>
    >>> records = list(load(mnist_training.source()))
    >>> print(len(records))
    120
    >>> records[0].export()
    {'key': '0', 'features': {'SepalLength': 6.4, 'SepalWidth': 2.8, 'PetalLength': 5.6, 'PetalWidth': 2.2, 'classification': 2}, 'extra': {}}
    """
    # Download features
    features_path = await cached_download(
        "http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz",
        cache_dir / "training_original_features.gz",
        "1bf45877962fd391f7abb20534a30fd2203d0865309fec5f87d576dbdbefdcb16adb49220afc22a0f3478359d229449c",
        protocol_allowlist=["http://"],
    )
    # Download labels
    labels_path = await cached_download(
        "http://yann.lecun.com/exdb/mnist/train-images-idx1-ubyte.gz",
        cache_dir / "training_original_labels.gz",
        "ccc1ee70f798a04e6bfeca56a4d0f0de8d8eeeca9f74641c1e1bfb00cf7cc4aa4d023f6ea1b40e79bb4707107845479d",
        protocol_allowlist=["http://"],
    )
    # Create a source object which is acctualy two sources combined.
    # This will expose the seperate features and labels files we downloaded as a
    # single source.
    yield Sources(
        IDX3Source(filename=features_path, feature="image"),
        IDX1Source(filename=labels_path, feature="label"),
    )
