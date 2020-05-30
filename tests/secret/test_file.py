import io
import os
import tempfile
import contextlib

from dffml.secret.file import FileSecret
from dffml.util.asynctestcase import AsyncTestCase


class TestFileSecret(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.secret_file = tempfile.NamedTemporaryFile(prefix="secret_",suffix=".ini")

    async def test_set_get(self):
        secret_store = FileSecret(
                filename = self.secret_file.name
            )
        async with secret_store() as secret_ctx:
            await secret_ctx.set(name="foo",value="bar")
            await secret_ctx.set(name="steins",value="gate")
            value = await secret_ctx.get(name="foo")
            self.assertEqual(value,"bar")
            value = await secret_ctx.get(name="steins")
            self.assertEqual(value,"gate")
            value = await secret_ctx.get(name="non_existent")
            self.assertFalse(value)
