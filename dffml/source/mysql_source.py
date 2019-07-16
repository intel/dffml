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
    update_query: str
    repos_query: str
    repo_query: str
    model_columns: list = [str]


class MysqlSourceContext(BaseSourceContext):
    async def update(self, repo: Repo):
        update_query = self.parent.config.update_query
        model_columns = self.parent.config.model_columns.split()
        key_value_pairs = OrderedDict()
        for key in model_columns:
            if key.startswith("feature_"):
                modified_key = key.replace("feature_","")
                key_value_pairs[modified_key] = repo.data.features[modified_key]
            elif key.startswith("prediction_"):
                modified_key = key.replace("prediction_","")
                key_value_pairs[modified_key] = repo.data.prediction[modified_key]
            else:
                key_value_pairs[key] =  repo.data.__dict__[key]
        db = self.conn
        await db.execute(update_query, (list(key_value_pairs.values()) +list(key_value_pairs.values())))
        self.logger.debug("update: %s", await self.repo(repo.src_url))

    def convert_to_repos(self, result):
        modified_repos = []
        for repo in result:
            modified_repo = {
                'src_url': "",
                'data' : {
                    'features' : {},
                    'prediction' : {}
                }

            }
            for key, value in repo.items():
                if key.startswith('feature_'):
                    modified_repo['data']['features'][key.replace("feature_","")] = value
                elif key.startswith('prediction_'):
                    modified_repo['data']['prediction'][key.replace("prediction_","")] = value
                else:
                    modified_repo[key] = value
            modified_repos.append(modified_repo)
        return modified_repos

    async def repos(self) -> AsyncIterator[Repo]:
        query = self.parent.config.repos_query
        await self.conn.execute(query)
        result = await self.conn.fetchall()
        repos_list = self.convert_to_repos(result)
        for repo in repos_list:
            yield Repo(repo['src_url'], data = repo['data'])


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
        cls.config_set(
            args,
            above,
            "model_columns",
            Arg(type=str, nargs="+", help="Order of Columns in table"),
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
            model_columns=cls.config_get(config, above, "model_columns"),
        )
