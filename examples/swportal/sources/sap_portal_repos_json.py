import json

from dffml import (
    export,
    Record,
    MemorySource,
    entrypoint,
    Record,
    MemorySource,
    FileSource,
    FileSourceConfig,
)


class SAPPortalReposJSONSourceConfig(FileSourceConfig):
    pass  # pragma: no cov


@entrypoint("sap.portal.repos.json")
class SAPPortalReposJSONSource(FileSource, MemorySource):
    r"""
    Reads and write from a SAP InnerSource Portal repos.json format. Each repo's
    data is stored as Record feature data in memory.
    """
    CONFIG = SAPPortalReposJSONSourceConfig

    async def load_fd(self, fd):
        # No predictions here, each repo's data is treated as a record with only
        # feature data.
        self.mem = {
            record["html_url"]: Record(
                record["html_url"], data={"features": record}
            )
            for record in json.load(fd)
        }
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        # Dump all records to the array format
        json.dump(
            [export(record.features()) for record in self.mem.values()], fd
        )
        self.logger.debug("%r saved %d records", self, len(self.mem))
