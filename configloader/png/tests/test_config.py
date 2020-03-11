from dffml.util.asynctestcase import AsyncTestCase

from dffml_config_png.configloader import PNGConfigLoader


class TestConfig(AsyncTestCase):
    async def test_dumpb_loadb(self):
        async with PNGConfigLoader.withconfig({}) as configloader:
            async with configloader() as ctx:
                original = {"Test": ["dict"]}
                reloaded = await ctx.loadb(await ctx.dumpb(original))
                self.assertEqual(original, reloaded)
