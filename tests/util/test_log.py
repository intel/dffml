import re
import time

from dffml.util.log import log_time
from dffml.util.asynctestcase import AsyncTestCase


class TestTimeLog(AsyncTestCase):
    def test_function(self):
        @log_time
        def dummy_function():
            time.sleep(0.1)
            return True

        with self.assertLogs(level="DEBUG") as captured_logs:
            dummy_function()

        self.assertEqual(len(captured_logs.records), 1)
        self.assertTrue(
            re.match(
                " dummy_function took [0-9]*.[0-9]+ seconds",
                captured_logs.records[0].getMessage(),
            )
        )

    async def test_coroutine(self):
        @log_time
        async def dummy_coroutine():
            time.sleep(0.1)
            return True

        with self.assertLogs(level="DEBUG") as captured_logs:
            await dummy_coroutine()

        self.assertEqual(len(captured_logs.records), 1)

        self.assertTrue(
            re.match(
                " dummy_coroutine took [0-9]*.[0-9]+ seconds",
                captured_logs.records[0].getMessage(),
            )
        )
