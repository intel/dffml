import json
from typing import Dict

from ..util.entrypoint import entrypoint
from ..util.cli.arg import Arg
from ..base import BaseConfig
from .configloader import BaseConfigLoaderContext, BaseConfigLoader


class JSONConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> Dict:
        return json.loads(resource.decode())

    async def dumpb(self, resource: Dict) -> bytes:
        return json.dumps(resource, sort_keys=True, indent=4).encode()


@entrypoint("json")
class JSONConfigLoader(BaseConfigLoader):
    CONTEXT = JSONConfigLoaderContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return BaseConfig()
