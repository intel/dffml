import json
import pathlib
import hashlib

from dffml.util.asynctestcase import AsyncTestCase
from dffml_config_image.configloader import PNGConfigLoader

IMAGE1_HASH = "6faf9050c6d387bc6a68d9e12127f883011add2ec994b8e66c7c0996636f2789af8d28fc11e6528a327a6383c1473e72"


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
                    / "image1.png"
                ).read_bytes()
                original = await ctx.loadb(image_bytes)
                hash_original = hashlib.sha384(
                    json.dumps(original.flatten().tolist()).encode()
                ).hexdigest()
                self.assertEqual(original.shape, (280, 280, 3))
                self.assertEqual(hash_original, IMAGE1_HASH)
