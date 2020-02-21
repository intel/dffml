import io
import contextlib

from dffml.util.asynctestcase import AsyncTestCase

from REPLACE_IMPORT_PACKAGE_NAME.misc import MiscService


class TestMiscService(AsyncTestCase):
    async def test_run(self):
        check_num = 42
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            cli = MiscService(integer=check_num)
            await cli.run()
        self.assertIn(f"Your integer was: {check_num}", output.getvalue())
