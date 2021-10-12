import sys
import dataclasses
import importlib.util

from ..util.asynctestcase import AsyncTestCase
from ..util.config.inspect import make_config_inspect


class TestGitHubOperations(AsyncTestCase):
    async def test_create_status(self):
        file_path = "/home/johnsa1/Documents/python/dffml/.venv/lib/python3.7/site-packages/github/Commit.py"
        module_name = "github.commit"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        print(module.Commit.create_status)

        config = make_config_inspect(
            "GitHubCommitCreateStatusConfig", module.Commit.create_status
        )

        import pprint

        pprint.pprint(list(dataclasses.fields(config)))

        print(config())
