from dffml.util.asynctestcase import AsyncTestCase

# from dffml_config_jsonschema.configloader import JSONSchemaConfigLoader
# ------------------- BEGIN dffml_config_jsonschema.configloader ------------------
import ast
import json
import enum
from typing import Dict

from dffml.base import config
from dffml.util.entrypoint import entrypoint
from dffml.util.cli.arg import Arg
from dffml.base import BaseConfig
from dffml.configloader.configloader import (
    BaseConfigLoaderContext,
    BaseConfigLoader,
)

from pydantic import BaseModel, Field


class FooBar(BaseModel):
    count: int
    size: float = None


class Gender(str, enum.Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'


class MainModel(BaseModel):
    """
    This is the description of the main model
    """

    foo_bar: FooBar = Field(...)
    gender: Gender = Field(None, alias='Gender')
    snap: int = Field(
        42,
        title='The Snap',
        description='this is the value of snap',
        gt=30,
        lt=50,
    )

    class Config:
        title = 'Main'
        schema_extra = {
            "$schema": "https://intel.github.io/dffml/manifest-format-name.0.0.2.schema.json",
        }


@config
class JSONSchemaConfigLoaderConfig:
    pass


class JSONSchemaConfigLoaderContext(BaseConfigLoaderContext):
    async def loadb(self, resource: bytes) -> Dict:
        return json.loads(resource.decode())

    async def dumpb(self, resource: Dict) -> bytes:
        return MainModel.schema_json(indent=2).encode()


@entrypoint("jsonschema")
class JSONSchemaConfigLoader(BaseConfigLoader):
    CONTEXT = JSONSchemaConfigLoaderContext
    CONFIG = JSONSchemaConfigLoaderConfig


# -------------------  END  dffml_config_jsonschema.configloader ------------------


TEST_0_SCHEMA_SHOULD_BE = {
  "title": "Main",
  "description": "This is the description of the main model",
  "type": "object",
  "properties": {
    "foo_bar": {
      "$ref": "#/definitions/FooBar"
    },
    "Gender": {
      "$ref": "#/definitions/Gender"
    },
    "snap": {
      "title": "The Snap",
      "description": "this is the value of snap",
      "default": 42,
      "exclusiveMinimum": 30,
      "exclusiveMaximum": 50,
      "type": "integer"
    }
  },
  "required": [
    "foo_bar"
  ],
  "definitions": {
    "FooBar": {
      "title": "FooBar",
      "type": "object",
      "properties": {
        "count": {
          "title": "Count",
          "type": "integer"
        },
        "size": {
          "title": "Size",
          "type": "number"
        }
      },
      "required": [
        "count"
      ]
    },
    "Gender": {
      "title": "Gender",
      "description": "An enumeration.",
      "enum": [
        "male",
        "female",
        "other",
        "not_given"
      ],
      "type": "string"
    }
  }
}


class TestConfig(AsyncTestCase):
    async def test_0_dumpb_loadb(self):
        async with JSONSchemaConfigLoader.withconfig({}) as configloader:
            async with configloader() as ctx:
                original = {"Test": ["dict"]}
                reloaded = await ctx.loadb(await ctx.dumpb(original))
                self.assertEqual(original, TEST_0_SCHEMA_SHOULD_BE)
