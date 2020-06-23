"""
Description of what this config does
"""
from typing import Dict
import cv2
import numpy as np

from dffml.util.entrypoint import entrypoint
from dffml.util.cli.arg import Arg
from dffml.base import BaseConfig
from dffml.configloader.configloader import (
    BaseConfigLoaderContext,
    BaseConfigLoader,
)


class PNGConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> list:
        image_array = cv2.imdecode(
            np.frombuffer(resource, np.uint8), cv2.IMREAD_COLOR
        )
        return image_array

    async def dumpb(self, resource: Dict) -> bytes:
        raise NotImplementedError


@entrypoint("png")
class PNGConfigLoader(BaseConfigLoader):
    CONTEXT = PNGConfigLoaderContext
    CONFIG = BaseConfig
