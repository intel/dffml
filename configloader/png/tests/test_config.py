import json
import pathlib
import hashlib

from dffml.util.asynctestcase import AsyncTestCase
from dffml_config_png.configloader import PNGConfigLoader

IMAGE1_HASH = "d8dd06cd1e9b9ed9f1e85ba2e91031faee142de66f8e02556d6590223038288c970d93bbc31fd6c655188632aa72b62c"


class TestConfig(AsyncTestCase):
    async def test_dumpb_loadb(self):
        async with PNGConfigLoader.withconfig({}) as configloader:
            async with configloader() as ctx:
                image_bytes = (
                    pathlib.Path(__file__).parent
                    / ".."
                    / ".."
                    / ".."
                    / "examples"
                    / "MNIST"
                    / "image1.mnistpng"
                ).read_bytes()
                original = await ctx.loadb(image_bytes)
                original = tuple([int(i) for i in original])
                hash_original = hashlib.sha384(
                    json.dumps(original).encode()
                ).hexdigest()
                self.assertEqual(len(original), 784)
                self.assertEqual(hash_original, IMAGE1_HASH)
