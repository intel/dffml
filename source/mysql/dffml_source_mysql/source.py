import ssl
import collections
from typing import AsyncIterator, NamedTuple, Dict, List

import aiomysql

from dffml.base import BaseConfig
from dffml.record import Record
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entrypoint


class MySQLSourceConfig(BaseConfig, NamedTuple):
    host: str
    port: int
    user: str
    password: str
    db: str
    update_query: str
    records_query: str
    record_query: str
    model_columns: List[str]
    ca: str = None


class MySQLSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        update_query = self.parent.config.update_query
        model_columns = self.parent.config.model_columns.split()
        key_value_pairs = collections.OrderedDict()
        for key in model_columns:
            if key.startswith("feature_"):
                modified_key = key.replace("feature_", "")
                key_value_pairs[modified_key] = record.data.features[
                    modified_key
                ]
            elif "_value" in key:
                target = key.replace("_value", "")
                if record.data.prediction:
                    key_value_pairs[key] = record.data.prediction[target][
                        "value"
                    ]
                else:
                    key_value_pairs[key] = "undetermined"
            elif "_confidence" in key:
                target = key.replace("_confidence", "")
                if record.data.prediction:
                    key_value_pairs[key] = record.data.prediction[target][
                        "confidence"
                    ]
                else:
                    key_value_pairs[key] = 1
            else:
                key_value_pairs[key] = record.data.__dict__[key]
        db = self.conn
        await db.execute(
            update_query,
            (list(key_value_pairs.values()) + list(key_value_pairs.values())),
        )
        self.logger.debug("update: %s", await self.record(record.key))

    def convert_to_record(self, result):
        modified_record = {
            "key": "",
            "data": {"features": {}, "prediction": {}},
        }
        for key, value in result.items():
            if key.startswith("feature_"):
                modified_record["data"]["features"][
                    key.replace("feature_", "")
                ] = value
            elif ("_value" in key) or ("_confidence" in key):
                target = key.replace("_value", "").replace("_confidence", "")
                modified_record["data"]["prediction"][target] = {
                    "value": result[target + "_value"],
                    "confidence": result[target + "_confidence"],
                }
            else:
                modified_record[key] = value
        return Record(modified_record["key"], data=modified_record["data"])

    async def records(self) -> AsyncIterator[Record]:
        query = self.parent.config.records_query
        await self.conn.execute(query)
        result = await self.conn.fetchall()
        for record in result:
            yield self.convert_to_record(record)

    async def record(self, key: str):
        query = self.parent.config.record_query
        record = Record(key)
        db = self.conn
        await db.execute(query, (key,))
        row = await db.fetchone()

        if row is not None:
            features = {}
            predictions = {}
            for key, value in row.items():
                if key.startswith("feature_"):
                    features[key.replace("feature_", "")] = value
                elif "_value" in key:
                    target = key.replace("_value", "")
                    predictions[target] = {
                        "value": row[target + "_value"],
                        "confidence": row[target + "_confidence"],
                    }
            record.merge(
                Record(
                    row["key"],
                    data={"features": features, "prediction": predictions},
                )
            )
        return record

    async def __aenter__(self) -> "MySQLSourceContext":
        self.__conn = self.parent.db.cursor(aiomysql.DictCursor)
        self.conn = await self.__conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__conn.__aexit__(exc_type, exc_value, traceback)
        await self.parent.db.commit()


@entrypoint("mysql")
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
            "records-query",
            Arg(
                type=str,
                help="SELECT `key` as key, data_1 as feature_1, data_2 as feature_2 FROM record_data",
            ),
        )
        cls.config_set(
            args,
            above,
            "record-query",
            Arg(
                type=str,
                help="SELECT `key` as key, data_1 as feature_1, data_2 as feature_2 FROM record_data WHERE `key`=%s",
            ),
        )
        cls.config_set(
            args,
            above,
            "update-query",
            Arg(
                type=str,
                help="INSERT INTO record_data (`key`, data_1, data_2) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE data_1 = %s, data_2=%s",
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
            records_query=cls.config_get(config, above, "records-query"),
            record_query=cls.config_get(config, above, "record-query"),
            update_query=cls.config_get(config, above, "update-query"),
            model_columns=cls.config_get(config, above, "model-columns"),
            ca=cls.config_get(config, above, "ca"),
        )
