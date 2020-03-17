"""
Description of what this config does
"""
from typing import Dict
from io import BytesIO
from PIL import Image
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
        image_array = np.array(Image.open(BytesIO(resource)).convert("L"))
        img_pil = Image.fromarray(image_array)
        img_28x28 = np.array(img_pil.resize((28, 28), Image.ANTIALIAS))
        img_784 = tuple(img_28x28.flatten())
        return img_784

    async def dumpb(self, resource: Dict) -> bytes:
        raise NotImplementedError


@entrypoint("mnistpng")
class PNGConfigLoader(BaseConfigLoader):
    CONTEXT = PNGConfigLoaderContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return BaseConfig()
