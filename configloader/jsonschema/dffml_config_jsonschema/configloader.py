"""
Description of what this config does
"""
import ast
from typing import Dict

from dffml.util.entrypoint import entrypoint
from dffml.util.cli.arg import Arg
from dffml.base import BaseConfig
from dffml.configloader.configloader import (
    BaseConfigLoaderContext,
    BaseConfigLoader,
)


class JSONSchemaConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> Dict:
        return ast.literal_eval(resource.decode())

    async def dumpb(self, resource: Dict) -> bytes:
        return repr(resource).encode()


@entrypoint("jsonschema")
class JSONSchemaConfigLoader(BaseConfigLoader):
    CONTEXT = JSONSchemaConfigLoaderContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return BaseConfig()
