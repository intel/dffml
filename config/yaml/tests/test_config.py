from dffml.util.asynctestcase import AsyncTestCase

from dffml_config_yaml.config import YamlConfigLoader


class TestConfig(AsyncTestCase):
    async def test_dumpb_loadb(self):
        async with YamlConfigLoader.withconfig({}) as configloader:
            async with configloader() as ctx:
                original = {"Test": ["dict"]}
                reloaded = await ctx.loadb(await ctx.dumpb(original))
                self.assertEqual(original, reloaded)
