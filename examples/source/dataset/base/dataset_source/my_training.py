import pathlib

from dffml.source.csv import CSVSource
from dffml.source.dataset import dataset_source
from dffml.util.net import cached_download, DEFAULT_PROTOCOL_ALLOWLIST


@dataset_source("my.training")
def my_training_dataset(
    url: str = "http://download.example.com/data/my_training.csv",
    expected_sha384_hash: str = "db9ec70abdc8b74bcf91a7399144dd15fc01e3dad91bbbe3c41fbbe33065b98a3e06e8e0ba053d850d7dc19e6837310e",
    cache_dir: pathlib.Path = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "my")
        .expanduser()
        .resolve()
    ),
):
    # Download the file from the url give, place the downloaded file at
    # ~/.cache/dffml/datasets/my/training.csv. Ensure the SHA 384 hash
    # of the download's contents is equal the the expected value
    with cached_download(
        url,
        cache_dir / "training.csv",
        expected_sha384_hash,
        protocol_allowlist=["http://"] + DEFAULT_PROTOCOL_ALLOWLIST,
    ) as filepath:
        # Create a source using downloaded file
        yield CSVSource(filename=str(filepath))
