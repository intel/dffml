import json
import aiomysql
from typing import AsyncIterator, NamedTuple, Dict
from collections import OrderedDict

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
    table: str
    update_query: str
    repos_query: str
    repo_query: str
    model_columns: str


class MysqlSourceContext(BaseSourceContext):
    async def update(self, repo: Repo):
        update_query = self.parent.config.update_query
        if update_query == "":
            update_query = "insert into " + self.parent.config.table + "("
            values = "("
            column_value_pair = OrderedDict()
            for column_name in self.parent.config.model_columns.split():
                if column_name.startswith("feature_"):
                    key = column_name.replace("feature_", "")
                    if key in repo.data.features.keys():
                        values += str(repo.data.features[key]) + ","
                        column_value_pair[column_name] = repo.data.features[
                            key
                        ]
                        update_query += column_name + ","
                elif column_name.startswith("prediction_"):
                    key = column_name.replace("prediction_", "")
                    if (
                        "prediction" in repo.data.__dict__.keys()
                        and key in repo.data.prediction.keys()
                    ):
                        if key == "value":
                            values += (
                                "'" + str(repo.data.prediction[key]) + "',"
                            )
                            column_value_pair[column_name] = (
                                "'" + str(repo.data.prediction[key]) + "'"
                            )
                        else:
                            values += str(repo.data.prediction[key]) + ","
                            column_value_pair[
                                column_name
                            ] = repo.data.prediction[key]
                        update_query += column_name + ","
                else:
                    key = column_name
                    if key in repo.data.__dict__.keys():
                        values += repo.data.__dict__[key] + ","
                        column_value_pair[column_name] = repo.data.__dict__[
                            key
                        ]
                        update_query += column_name + ","
            update_query = update_query[:-1] + ")"
            values = values[:-1] + ")"
            update_query += " values " + values + "on duplicate key update "
            for key, value in column_value_pair.items():
                update_query += key + "=" + str(value) + ","
            update_query = update_query[:-1]
        db = self.conn
        await db.execute(update_query)
        self.logger.debug("update: %s", await self.repo(repo.src_url))

    async def repos(self) -> AsyncIterator[Repo]:
        if self.parent.config.repos_query != "":
            query = self.parent.config.repos_query
            await self.conn.execute(query)
            src_urls = set(map(lambda row: row[0], await self.conn.fetchall()))
            for src_url in src_urls:
                yield await self.repo(src_url)

    async def repo(self, src_url: str):
        if self.parent.config.repo_query != "":
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
        cls.config_set(args, above, "table", Arg())
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
        cls.config_set(
            args,
            above,
            "model_columns",
            Arg(type=OrderedDict, help="Order of Columns in table"),
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
            table=cls.config_get(config, above, "table"),
            repos_query=cls.config_get(config, above, "repos-query"),
            repo_query=cls.config_get(config, above, "repo-query"),
            update_query=cls.config_get(config, above, "update-query"),
            model_columns=cls.config_get(config, above, "model_columns"),
        )
