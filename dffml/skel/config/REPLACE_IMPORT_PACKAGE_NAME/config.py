"""
Description of what this config does
"""
import ast
from typing import Dict, Any

from dffml.util.entrypoint import entry_point
from dffml.util.cli.arg import Arg
from dffml.base import BaseConfig
from dffml.config.config import BaseConfigLoaderContext, BaseConfigLoader


class MiscConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> Dict:
        return ast.literal_eval(resource.decode())

    async def dumpb(self, resource: Dict) -> bytes:
        return repr(resource).encode()


@entry_point("misc")
class MiscConfigLoader(BaseConfigLoader):
    CONTEXT = MiscConfigLoaderContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return BaseConfig()
