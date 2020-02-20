import os
import json
import pathlib
import tempfile

from dffml.util.asynctestcase import AsyncTestCase
from dffml.config.config import ConfigLoaders


class TestConfigLoader(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.TemporaryDirectory()

        cls.config_folder_name = "the_config_name"
        cls.config_folder_path = os.path.join(
            cls.test_dir.name, cls.config_folder_name
        )
        os.mkdir(cls.config_folder_path)
        temp_path = cls.config_folder_path
        pathlib.Path(
            cls.test_dir.name, cls.config_folder_name + ".dirconf.json"
        ).write_text(json.dumps({"hello": "there"}))
        pathlib.Path(temp_path, "deadbeef.json").write_text(
            json.dumps({"massive": "hax"})
        )
        os.mkdir(os.path.join(temp_path, "feed"))
        pathlib.Path(temp_path, "feed", "face.json").write_text(
            json.dumps({"so": "secure"})
        )

    @classmethod
    def tearDown(cls):
        cls.test_dir.cleanup()

    def setUp(self):
        self.config_loader = ConfigLoaders()

    async def test_run(self):
        expected = {
            "hello": "there",
            "deadbeef": {"massive": "hax"},
            "feed": {"face": {"so": "secure"}},
        }
        temp_path = self.config_folder_path
        async with self.config_loader as cfgl:
            _, conf_dict = await cfgl.load_file(
                os.path.join(
                    self.test_dir.name, "the_config_name.dirconf.json"
                )
            )
            self.assertEqual(expected, conf_dict)

        expected = {"massive": "hax"}
        temp_path = self.config_folder_path
        async with self.config_loader as cfgl:
            _, conf_dict = await cfgl.load_file(
                os.path.join(temp_path, "deadbeef.json")
            )
            self.assertEqual(expected, conf_dict)
