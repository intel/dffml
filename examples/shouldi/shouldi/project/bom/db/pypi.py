import json
import uuid
import dataclasses
import urllib.request
from typing import Dict, Union

from .base import DependencyDB
from ..base import Dependency, DependencyExtra, URL, License


@dataclasses.dataclass
class PyPiDependency(DependencyExtra):
    name: str
    url: URL
    license: License


class PyPiDB(DependencyDB):
    name: str = "pypi"
    uuid: "uuid.UUID" = uuid.UUID("3bdad2ca-3224-45d7-9035-a1f66e318baf")

    def lookup(self, dependency: Dependency) -> Dependency:
        # Grab the package data from PyPi
        with urllib.request.urlopen(
            f"https://pypi.org/pypi/{dependency.name}/json"
        ) as resp:
            package_json = json.load(resp)
        return Dependency.mkoverride(
            dependency,
            url=package_json["info"]["project_urls"]["Homepage"],
            license=package_json["info"]["license"],
            extra={
                self.name: PyPiDependency(
                    uuid=None,
                    euuid=uuid.uuid5(self.uuid, dependency.name),
                    name=dependency.name,
                    url=f"https://pypi.org/pypi/{dependency.name}",
                    license=package_json["info"]["license"],
                )
            },
        )

    def extra(self, dependency: Dependency) -> Union[None, Dependency]:
        raise NotImplementedError
        # TODO Implement 404 catch and return None
        url = f"https://pypi.org/pypi/{name}/json"
        with urllib.request.urlopen(url) as resp:
            package_json = json.load(resp)
            return PyPiDependency(
                uuid=None,
                euuid=uuid.uuid5(self.uuid, name),
                name=name,
                url=f"https://pypi.org/pypi/{name}",
                license=package_json["info"]["license"],
            )

    @classmethod
    def applicable(cls, config: str) -> bool:
        return bool(config == cls.name)
