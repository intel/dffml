import os
import ssl
import collections
from typing import AsyncIterator, NamedTuple, Dict, List

import aiomysql

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entry_point


class MySQLSourceConfig(BaseConfig, NamedTuple):
    host: str
    port: int
    user: str
    password: str
    db: str
    update_query: str
    repos_query: str
    repo_query: str
    model_columns: List[str]
    ca: str = None


class MySQLSourceContext(BaseSourceContext):
    async def update(self, repo: Repo):
        update_query = self.parent.config.update_query
        model_columns = self.parent.config.model_columns.split()
        key_value_pairs = collections.OrderedDict()
        for key in model_columns:
            if key.startswith("feature_"):
                modified_key = key.replace("feature_", "")
                key_value_pairs[modified_key] = repo.data.features[
                    modified_key
                ]
            elif key.startswith("prediction_"):
                modified_key = key.replace("prediction_", "")
                key_value_pairs[modified_key] = repo.data.prediction[
                    modified_key
                ]
            else:
                key_value_pairs[key] = repo.data.__dict__[key]
        db = self.conn
        await db.execute(
            update_query,
            (list(key_value_pairs.values()) + list(key_value_pairs.values())),
        )
        self.logger.debug("update: %s", await self.repo(repo.src_url))

    def convert_to_repo(self, result):
        modified_repo = {
            "src_url": "",
            "data": {"features": {}, "prediction": {}},
        }
        for key, value in result.items():
            if key.startswith("feature_"):
                modified_repo["data"]["features"][
                    key.replace("feature_", "")
                ] = value
            elif key.startswith("prediction_"):
                modified_repo["data"]["prediction"][
                    key.replace("prediction_", "")
                ] = value
            else:
                modified_repo[key] = value
        return Repo(modified_repo["src_url"], data=modified_repo["data"])

    async def repos(self) -> AsyncIterator[Repo]:
        query = self.parent.config.repos_query
        await self.conn.execute(query)
        result = await self.conn.fetchall()
        for repo in result:
            yield self.convert_to_repo(repo)

    async def repo(self, src_url: str):
        query = self.parent.config.repo_query
        repo = Repo(src_url)
        db = self.conn
        await db.execute(query, (src_url,))
        row = await db.fetchone()
        if row is not None:
            repo.merge(
                Repo(
                    row["src_url"],
                    data={
                        "features": {
                            key.replace("feature_", ""): value
                            for key, value in row.items()
                            if key.startswith("feature_")
                        },
                        "prediction": {
                            key.replace("prediction_", ""): value
                            for key, value in row.items()
                            if key.startswith("prediction_")
                        },
                    },
                )
            )
        return repo

    async def __aenter__(self) -> "MySQLSourceContext":
        self.__conn = self.parent.db.cursor(aiomysql.DictCursor)
        self.conn = await self.__conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__conn.__aexit__(exc_type, exc_value, traceback)
        await self.parent.db.commit()


@entry_point("mysql")
class MySQLSource(BaseSource):

    CONTEXT = MySQLSourceContext

    async def __aenter__(self) -> "MySQLSource":
        # Verify MySQL connection using provided certificate, if given
        ssl_ctx = None
        if self.config.ca is not None:
            self.logger.debug(
                f"Secure connection to MySQL: CA file: {self.config.ca}"
            )
            ssl_ctx = ssl.create_default_context(cafile=self.config.ca)
        else:
            self.logger.critical("Insecure connection to MySQL")
        # Connect to MySQL
        self.pool = await aiomysql.create_pool(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            db=self.config.db,
            ssl=ssl_ctx,
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
                help="SELECT `key` as src_url, data_1 as feature_1, data_2 as feature_2 FROM repo_data",
            ),
        )
        cls.config_set(
            args,
            above,
            "repo-query",
            Arg(
                type=str,
                help="SELECT `key` as src_url, data_1 as feature_1, data_2 as feature_2 FROM repo_data WHERE `key`=%s",
            ),
        )
        cls.config_set(
            args,
            above,
            "update-query",
            Arg(
                type=str,
                help="INSERT INTO repo_data (`key`, data_1, data_2) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE data_1 = %s, data_2=%s",
            ),
        )
        cls.config_set(
            args,
            above,
            "model-columns",
            Arg(type=str, nargs="+", help="Order of Columns in table"),
        )
        cls.config_set(
            args,
            above,
            "ca",
            Arg(type=str, help="Path to server TLS certificate", default=None),
        )
        return args

    @classmethod
    def config(cls, config, *above):
        return MySQLSourceConfig(
            host=cls.config_get(config, above, "host"),
            port=cls.config_get(config, above, "port"),
            user=cls.config_get(config, above, "user"),
            password=cls.config_get(config, above, "password"),
            db=cls.config_get(config, above, "db"),
            repos_query=cls.config_get(config, above, "repos-query"),
            repo_query=cls.config_get(config, above, "repo-query"),
            update_query=cls.config_get(config, above, "update-query"),
            model_columns=cls.config_get(config, above, "model-columns"),
            ca=cls.config_get(config, above, "ca"),
        )
