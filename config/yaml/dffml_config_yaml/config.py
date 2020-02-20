"""
Description of what this config does
"""
from typing import Dict

import yaml

from dffml.util.entrypoint import entrypoint
from dffml.util.cli.arg import Arg
from dffml.base import BaseConfig
from dffml.config.config import BaseConfigLoaderContext, BaseConfigLoader


class YamlConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> Dict:
        return yaml.safe_load(resource.decode())

    async def dumpb(self, resource: Dict) -> bytes:
        return yaml.dump(resource, default_flow_style=False).encode()


@entrypoint("yaml")
class YamlConfigLoader(BaseConfigLoader):
    CONTEXT = YamlConfigLoaderContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return BaseConfig()
