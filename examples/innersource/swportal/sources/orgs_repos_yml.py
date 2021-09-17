import yaml
import pathlib

from dffml import (
    config,
    field,
    Record,
    MemorySource,
    entrypoint,
    Record,
    MemorySource,
)


@config
class OrgsReposYAMLSourceConfig:
    directory: pathlib.Path = field(
        "Top level directory containing GitHub orgs as subdirectories"
    )


@entrypoint("orgs.repos.yml")
class OrgsReposYAMLSource(MemorySource):
    r"""
    Reads from a SAP InnerSource Portal repos.json format. Each repo's
    data is stored as Record feature data in memory.

    Writing not implemented.
    """
    CONFIG = OrgsReposYAMLSourceConfig

    async def __aenter__(self):
        """
        Populate the source when it's context is entered
        """
        for yaml_path in self.config.directory.rglob("*.yml"):
            for doc in yaml.safe_load_all(yaml_path.read_text()):
                key = (
                    f'https://github.com/{yaml_path.parent.name}/{doc["name"]}'
                )
                self.mem[key] = Record(key, data={"features": doc})
        self.logger.debug("%r loaded %d records", self, len(self.mem))
        return self
