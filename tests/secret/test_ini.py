import io
import os
import shutil
import pathlib
import inspect
import tempfile
import contextlib

from dffml.secret.ini import INISecret
from dffml.util.asynctestcase import AsyncTestCase


class TestINISecret(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        handle, cls.secret_file = tempfile.mkstemp(
            prefix="secret_", suffix=".ini", dir=cls.tmpdir
        )
        os.close(handle)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    async def test_set_get(self):
        async with INISecret(filename=self.secret_file) as secret_store:
            async with secret_store() as secret_ctx:
                await secret_ctx.set(name="foo", value="bar")
                await secret_ctx.set(name="steins", value="gate")

        contents = pathlib.Path(self.secret_file).read_text().strip()

        self.assertIn(
            "[secrets]", contents,
        )
        self.assertIn(
            "steins = gate", contents,
        )
        self.assertIn(
            "foo = bar", contents,
        )

        async with INISecret(filename=self.secret_file) as secret_store:
            async with secret_store() as secret_ctx:
                value = await secret_ctx.get(name="foo")
                self.assertEqual(value, "bar")
                value = await secret_ctx.get(name="steins")
                self.assertEqual(value, "gate")
                value = await secret_ctx.get(name="non_existent")
                self.assertFalse(value)
