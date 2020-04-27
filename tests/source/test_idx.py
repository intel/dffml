import json
import pathlib
import hashlib

from dffml.util.net import cached_download
from dffml.util.asynctestcase import AsyncTestCase

from dffml.source.idx1 import IDX1SourceConfig, IDX1Source
from dffml.source.idx3 import IDX3SourceConfig, IDX3Source


IDX1_FILE = (
    "https://github.com/intel/dffml/files/4283897/train-labels-idx1-ubyte.gz",
    pathlib.Path(__file__).parent / "train-labels-idx1-ubyte.gz",
    "ba9c11bf9a7f7c2c04127b8b3e568cf70dd3429d9029ca59b7650977a4ac32f8ff5041fe42bc872097487b06a6794e00",
)
IDX3_FILE = (
    "https://github.com/intel/dffml/files/4283898/train-images-idx3-ubyte.gz",
    pathlib.Path(__file__).parent / "train-images-idx3-ubyte.gz",
    "f40eb179f7c3d2637e789663bde56d444a23e4a0a14477a9e6ed88bc39c8ad6eaff68056c0cd9bb60daf0062b70dc8ee",
)

IDX3_FIRST_LAST = [
    "e6d19cf499d52c0d7e74c9b907ba23a67b68b23e8c2b8cfd85255c9862bfdf599a7f1e33b1fd4f847236a17fa9942ecd",
    "d6e2df55d7aa248f4e69714ea46fc57acbbe783d9206541b028268e8c947df8641c5c28f7e4c209f588d8aa0fad49372",
]


class TestIDXSources(AsyncTestCase):
    @cached_download(*IDX1_FILE)
    async def test_idx1(self, filename):
        feature_name = "label"
        async with IDX1Source(
            IDX1SourceConfig(filename=str(filename), feature=feature_name)
        ) as source:
            async with source() as sctx:
                records = [record async for record in sctx.records()]
                self.assertEqual(len(records), 60000)
                self.assertIn(feature_name, records[0].features())
                self.assertEqual(records[0].feature(feature_name), 5)

    @cached_download(*IDX3_FILE)
    async def test_idx3(self, filename):
        feature_name = "image"
        async with IDX3Source(
            IDX3SourceConfig(filename=str(filename), feature=feature_name)
        ) as source:
            async with source() as sctx:
                records = [record async for record in sctx.records()]
                self.assertEqual(len(records), 60000)
                self.assertIn(feature_name, records[0].features())
                for i in range(-1, 1):
                    with self.subTest(index=i):
                        is_hash = hashlib.sha384(
                            json.dumps(
                                records[i].feature(feature_name)
                            ).encode()
                        ).hexdigest()
                        self.assertEqual(is_hash, IDX3_FIRST_LAST[i])
