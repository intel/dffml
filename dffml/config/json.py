import json
import pathlib
from typing import Dict, Any

from ..util.entrypoint import entry_point
from ..util.cli.arg import Arg
from ..base import BaseConfig
from .config import BaseConfigLoaderContext, BaseConfigLoader


class JSONConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> Dict:
        return json.loads(resource.decode())

    async def dumpb(self, resource: Dict) -> bytes:
        return json.dumps(resource, sort_keys=True, indent=4).encode()


@entry_point("json")
class JSONConfigLoader(BaseConfigLoader):
    CONTEXT = JSONConfigLoaderContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return BaseConfig()
