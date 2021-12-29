import urllib.parse
from typing import AsyncIterator, Dict, List

from dffml.base import BaseConfig
from dffml.record import Record
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entrypoint
from dffml.base import config


import motor.motor_asyncio


@config
class MongoDBSourceConfig:
    uri: str
    db: str = None
    collection: str = None
    tlsInsecure: bool = False
    log_collection_names: bool = False

    def __post_init__(self):
        uri = urllib.parse.urlparse(self.uri)
        if uri.path:
            self.db = uri.path[1:]


# TODO Investigate use of
# https://pymongo.readthedocs.io/en/3.12.0/api/pymongo/client_session.html#pymongo.client_session.ClientSession
# for Context.
class MongoDBSourceContext(BaseSourceContext):
    async def update(self, record):
        self.logger.debug("update: %s: %r", record.key, record.export())
        await self.parent.collection.replace_one(
            {"_id": record.key},
            {"_id": record.key, **record.export()},
            upsert=True,
        )

    def document_to_record(self, document):
        self.logger.debug("document: %r", document)
        key = document["key"]
        del document["_id"]
        del document["key"]
        return Record(key, data=document)

    async def records(self) -> AsyncIterator[Record]:
        async for document in self.parent.collection.find():
            yield self.document_to_record(document)

    async def record(self, key: str) -> Record:
        document = await self.parent.collection.find_one({"_id": key})
        return self.document_to_record(document)


@entrypoint("mongodb")
class MongoDBSource(BaseSource):
    """
    Stores records ... somewhere! (skeleton template is in memory)
    """

    CONFIG = MongoDBSourceConfig
    CONTEXT = MongoDBSourceContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.client = None

    async def __aenter__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.config.uri,
                tlsInsecure=self.config.tlsInsecure)
        self.db = self.client[self.config.db]
        # Thought: Plugins as dataflows. Is a method call an event? Is it an
        # input?
        if self.config.log_collection_names:
            self.logger.info("Collection names: %r", await self.db.list_collection_names())
        self.collection = self.db[self.config.collection]
        return self

    async def __aexec__(self, _exc_type, _exc_value, _traceback):
        self.client = None
