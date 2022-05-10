import pathlib
import os
from zipfile import ZipFile 

from ..csv import CSVSource
from .base import dataset_source
from ...util.net import cached_download, DEFAULT_PROTOCOL_ALLOWLIST
from ...util.file import find_replace_with_hash_validation

@dataset_source("daily_train_m4.training")
async def daily_train_m4(
        cache_dir: pathlib.Path = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "m4")
        .expanduser()
        .resolve()
        )
    ):
        original_path = await cached_download(
        "https://www.kaggle.com/datasets/yogesh94/m4-forecasting-competition-dataset/download",
        cache_dir / "m4.zip",
        "11e9849387efdd2c69387f927ac84142dde3847fcad8247b1fbff2624f3fb00705215541a37eed6d4deca3479cbff353",
        protocol_allowlist=["http://"] + DEFAULT_PROTOCOL_ALLOWLIST
        )
        os.chdir(cache_dir)
        async with ZipFile("m4.zip", "r") as zipobj: 
            zipobj.extractall()
        
        original_path = cache_dir / "Daily-train.csv"

        yield CSVSource(filename=str(original_path))