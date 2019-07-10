import json
import aiomysql
from typing import AsyncIterator, NamedTuple, Dict

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entry_point


class MysqlSourceConfig(BaseConfig, NamedTuple):
    host: str
    port: int
    user: str
    password: str
    db: str
    query: str


class MysqlSourceContext(BaseSourceContext):
    async def update(self, repo: Repo):
        db = self.conn
        marshall = json.dumps(repo.dict())
        await db.execute(
            self.config.update_query, (repo.src_url, marshall, marshall)
        )
        self.logger.debug("updated: %s", marshall)
        self.logger.debug("update: %s", await self.repo(repo.src_url))

    async def repos(self) -> AsyncIterator[Repo]:
        query = self.config.repos_query
        await self.conn.execute(query)
        src_urls = set(map(lambda row: row[0], await self.conn.fetchall()))
        for src_url in src_urls:
            yield await self.repo(src_url)

    async def repo(self, src_url: str):
        query = self.config.repo_query
        repo = Repo(src_url)
        db = self.conn
        await db.execute(query, (src_url,))
        dump = await db.fetchone()
        if dump is not None and dump[0] is not None:
            repo.merge(Repo(src_url, data=json.loads(dump[0])))
        return repo

    async def __aenter__(self) -> "MysqlSourceContext":
        self.__conn = self.parent.db.cursor(aiomysql.DictCursor)
        self.conn = await self.__conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__conn.__aexit__(exc_type, exc_value, traceback)
        await self.parent.db.commit()


@entry_point("dffml.source")
class MysqlSource(BaseSource):

    CONTEXT = MysqlSourceContext

    async def __aenter__(self) -> "MysqlSource":
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
        cls.config_set(args, above, "user", Arg())
        cls.config_set(args, above, "password", Arg())
        cls.config_set(args, above, "db", Arg())
        cls.config_set(
            args,
            above,
            "repos-query",
            Arg(
                type=str,
                help="SELECT key as src_url, data_1 as feature_1, data_2 as feature_2 FROM list_of_all_repos",
            ),
        )
        cls.config_set(
            args,
            above,
            "repo-query",
            Arg(
                type=str,
                help="SELECT key as src_url, data_1 as feature_1, data_2 as feature_2 FROM list_of_all_repos WHERE key=%s",
            ),
        )
        cls.config_set(
            args,
            above,
            "update-query",
            Arg(
                type=str,
                help="INSERT INTO source_data (src_url, json) VALUES(%s, %s) ON DUPLICATE KEY UPDATE json = %s",
            ),
        )
        return args

    @classmethod
    def config(cls, config, *above):
        return MysqlSourceConfig(
            host=cls.config_get(config, above, "host"),
            port=cls.config_get(config, above, "port"),
            user=cls.config_get(config, above, "user"),
            password=cls.config_get(config, above, "password"),
            db=cls.config_get(config, above, "db"),
            repos_query=cls.config_get(config, above, "repos-query"),
            repo_query=cls.config_get(config, above, "repo-query"),
            update_query=cls.config_get(config, above, "update-query"),
        )
