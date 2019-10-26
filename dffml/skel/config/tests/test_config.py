from dffml.util.asynctestcase import AsyncTestCase

from REPLACE_IMPORT_PACKAGE_NAME.config import MiscConfigLoader


class TestConfig(AsyncTestCase):
    async def test_dumpb_loadb(self):
        async with MiscConfigLoader.withconfig({}) as configloader:
            async with configloader() as ctx:
                original = {"Test": ["dict"]}
                reloaded = await ctx.loadb(await ctx.dumpb(original))
                self.assertEqual(original, reloaded)
