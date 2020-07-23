import json
import aiomysql
from typing import AsyncIterator, NamedTuple, Dict

from dffml import config, entrypoint, Record, BaseSourceContext, BaseSource


@config
class DemoAppSourceConfig:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "user"
    password: str = "pass"
    db: str = "db"


class DemoAppSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        db = self.conn
        # Just dump it (if you want a setup the queries easily, then you need to
        # massage the columns in this table to your liking, and perhaps add more
        # tables.
        marshall = json.dumps(record.dict())
        await db.execute(
            "INSERT INTO ml_data (`key`, json) VALUES(%s, %s) "
            "ON DUPLICATE KEY UPDATE json = %s",
            (record.key, marshall, marshall),
        )
        self.logger.debug("updated: %s", marshall)
        self.logger.debug("update: %s", await self.record(record.key))

    async def records(self) -> AsyncIterator[Record]:
        await self.conn.execute("SELECT `key` FROM `status`")
        keys = set(map(lambda row: row[0], await self.conn.fetchall()))
        await self.conn.execute("SELECT `key` FROM `ml_data`")
        list(map(lambda row: keys.add(row[0]), await self.conn.fetchall()))
        for key in keys:
            yield await self.record(key)

    async def record(self, key: str):
        record = Record(key)
        db = self.conn
        # Get features
        await db.execute("SELECT json FROM ml_data WHERE `key`=%s", (key,))
        dump = await db.fetchone()
        if dump is not None and dump[0] is not None:
            record.merge(Record(key, data=json.loads(dump[0])))
        await db.execute(
            "SELECT maintained FROM `status` WHERE `key`=%s", (key,)
        )
        maintained = await db.fetchone()
        if maintained is not None and maintained[0] is not None:
            record.evaluated({"maintained": str(maintained[0])})
        return record

    async def __aenter__(self) -> "DemoAppSourceContext":
        self.__conn = self.parent.db.cursor()
        self.conn = await self.__conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__conn.__aexit__(exc_type, exc_value, traceback)
        await self.parent.db.commit()


@entrypoint("demoapp")
class DemoAppSource(BaseSource):

    CONFIG = DemoAppSourceConfig
    CONTEXT = DemoAppSourceContext

    async def __aenter__(self) -> "DemoAppSource":
        self.pool = await aiomysql.create_pool(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            db=self.config.db,
        )
        self.__db = self.pool.acquire()
        self.db = await self.__db.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__db.__aexit__(exc_type, exc_value, traceback)
        self.pool.close()
        await self.pool.wait_closed()
