"""
Loads an image from file
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


class ImageConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> list:
        image_array = cv2.imdecode(
            np.frombuffer(resource, np.uint8), cv2.IMREAD_COLOR
        )
        return image_array

    async def dumpb(self, resource: Dict) -> bytes:
        raise NotImplementedError


@entrypoint("png")
class PNGConfigLoader(BaseConfigLoader):
    CONTEXT = ImageConfigLoaderContext
    CONFIG = BaseConfig


@entrypoint("jpg")
class JPGConfigLoader(BaseConfigLoader):
    CONTEXT = ImageConfigLoaderContext
    CONFIG = BaseConfig


@entrypoint("jpeg")
class JPEGConfigLoader(BaseConfigLoader):
    CONTEXT = ImageConfigLoaderContext
    CONFIG = BaseConfig


@entrypoint("tiff")
class TIFFConfigLoader(BaseConfigLoader):
    CONTEXT = ImageConfigLoaderContext
    CONFIG = BaseConfig
