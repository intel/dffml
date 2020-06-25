"""
Description of what this config does
"""
import yaml
from typing import Dict

from dffml.util.entrypoint import entrypoint
from dffml.util.cli.arg import Arg
from dffml.base import BaseConfig
from dffml.configloader.configloader import (
    BaseConfigLoaderContext,
    BaseConfigLoader,
)


class YamlConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> Dict:
        return yaml.safe_load(resource.decode())

    async def dumpb(self, resource: Dict) -> bytes:
        return yaml.dump(resource, default_flow_style=False).encode()


@entrypoint("yaml")
class YamlConfigLoader(BaseConfigLoader):
    CONTEXT = YamlConfigLoaderContext
    CONFIG = BaseConfig
