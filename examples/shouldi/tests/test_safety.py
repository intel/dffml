from dffml import AsyncTestCase

from shouldi.python.safety import safety_check


class TestSafetyCheck(AsyncTestCase):
    async def test_run(self):
        results = await safety_check("insecure-package", "0.1.0")
        self.assertEqual(results, 1)
