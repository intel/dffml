import json
import aiomysql
from typing import AsyncIterator, NamedTuple, Dict

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entrypoint


class DemoAppSourceConfig(BaseConfig, NamedTuple):
    host: str
    port: int
    user: str
    password: str
    db: str


class DemoAppSourceContext(BaseSourceContext):
    async def update(self, repo: Repo):
        db = self.conn
        # Just dump it (if you want a setup the queries easily, then you need to
        # massage the columns in this table to your liking, and perhaps add more
        # tables.
        marshall = json.dumps(repo.dict())
        await db.execute(
            "INSERT INTO ml_data (key, json) VALUES(%s, %s) "
            "ON DUPLICATE KEY UPDATE json = %s",
            (repo.key, marshall, marshall),
        )
        self.logger.debug("updated: %s", marshall)
        self.logger.debug("update: %s", await self.repo(repo.key))

    async def repos(self) -> AsyncIterator[Repo]:
        await self.conn.execute("SELECT key FROM `status`")
        keys = set(map(lambda row: row[0], await self.conn.fetchall()))
        await self.conn.execute("SELECT key FROM `ml_data`")
        list(map(lambda row: keys.add(row[0]), await self.conn.fetchall()))
        for key in keys:
            yield await self.repo(key)

    async def repo(self, key: str):
        repo = Repo(key)
        db = self.conn
        # Get features
        await db.execute("SELECT json FROM ml_data WHERE key=%s", (key,))
        dump = await db.fetchone()
        if dump is not None and dump[0] is not None:
            repo.merge(Repo(key, data=json.loads(dump[0])))
        await db.execute(
            "SELECT maintained FROM `status` WHERE key=%s", (key,)
        )
        maintained = await db.fetchone()
        if maintained is not None and maintained[0] is not None:
            repo.evaluated({"maintained": str(maintained[0])})
        return repo

    async def __aenter__(self) -> "DemoAppSourceContext":
        self.__conn = self.parent.db.cursor()
        self.conn = await self.__conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__conn.__aexit__(exc_type, exc_value, traceback)
        await self.parent.db.commit()


@entrypoint("demoapp")
class DemoAppSource(BaseSource):

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

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "host", Arg(default="127.0.0.1"))
        cls.config_set(args, above, "port", Arg(type=int, default=3306))
        cls.config_set(args, above, "user", Arg(default="user"))
        cls.config_set(args, above, "password", Arg(default="pass"))
        cls.config_set(args, above, "db", Arg(default="db"))
        return args

    @classmethod
    def config(cls, config, *above):
        return DemoAppSourceConfig(
            host=cls.config_get(config, above, "host"),
            port=cls.config_get(config, above, "port"),
            user=cls.config_get(config, above, "user"),
            password=cls.config_get(config, above, "password"),
            db=cls.config_get(config, above, "db"),
        )
