from dffml.util.asynctestcase import AsyncTestCase

from shouldi.safety import safety_check


class TestSafetyCheck(AsyncTestCase):
    async def test_run(self):
        results = await safety_check("insecure-package", "0.1.0")
        self.assertEqual(results["issues"], 1)
