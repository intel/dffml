import uuid
import dataclasses
from typing import NewType, List, Dict, Optional


URL = NewType("URL", str)
License = NewType("License", str)


@dataclasses.dataclass
class Dependency:
    uuid: uuid.UUID
    name: str
    url: URL
    license: License
    extra: Dict[str, object]

    def override(self, other, *, extra={}):
        return dataclasses.replace(
            self,
            uuid=self.uuid if self.uuid else other.uuid,
            name=self.name if self.name else other.name,
            url=self.url if self.url else other.url,
            license=self.license if self.license else other.license,
            extra=other.extra.update(extra),
        )

    @classmethod
    def mkoverride(
        cls,
        other,
        *,
        uuid: uuid.UUID = None,
        name: str = None,
        url: URL = None,
        license: License = None,
        extra: Dict[str, object] = {},
    ):
        new_extra = other.extra.copy()
        new_extra.update(extra)
        return dataclasses.replace(
            other,
            uuid=uuid if uuid else other.uuid,
            name=name if name else other.name,
            url=url if url else other.url,
            license=license if license else other.license,
            extra=new_extra,
        )


@dataclasses.dataclass
class DependencyExtra:
    """
    Anytime something get's added to extra it should contain the authoritative
    UUID (if that database knows it). It should also contain the uuid for the
    dependency within the database.
    """

    uuid: uuid.UUID
    euuid: uuid.UUID


@dataclasses.dataclass
class BOM:
    dependencies: List[Dependency]
