import json
import uuid
import pathlib
from typing import Union

import yaml

from .base import DependencyDB
from ..base import Dependency, DependencyExtra


class YAMLDB(DependencyDB):
    def __init__(self, config: str):
        super().__init__(config)
        self.path = pathlib.Path(config)
        self.name = self.path.name
        self.data = {}
        self.uuid = uuid.UUID("245a532c-2940-4b76-8cbe-b2b82b0389b9")
        self.dependencies = {}
        if not self.path.is_file():
            return
        self.data = yaml.safe_load(self.path.read_text())
        if "uuid" in self.data:
            self.uuid = uuid.UUID(self.data["uuid"])
        for key, value in self.data["dependencies"].items():
            extra = value.get("extra", {})
            if "extra" in value:
                del value["extra"]
            if key.count("-") == 4:
                key = uuid.UUID(key)
            elif "uuid" in value:
                key = value["uuid"] = uuid.UUID(value["uuid"])
            else:
                key = value["uuid"] = uuid.uuid5(
                    self.uuid, json.dumps(value, sort_keys=True)
                )
            value["extra"] = extra
            self.dependencies[key] = Dependency(**value)

    def lookup(self, dependency: Dependency) -> Dependency:
        found = self.dependencies.get(dependency.uuid, None)
        if not found:
            return dependency
        extra = self.extra(found)
        if not extra:
            extra = {}
        return found.override(dependency, extra=extra)

    def extra(self, dependency: Dependency) -> Union[None, DependencyExtra]:
        if not dependency.uuid in self.dependencies:
            return
        return self.dependencies[dependency.uuid].extra.get(self.name, None)

    @classmethod
    def applicable(cls, config: str) -> bool:
        return config.endswith(".yaml")
