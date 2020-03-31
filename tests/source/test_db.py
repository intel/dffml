import os
import sqlite3
import tempfile
from typing import Dict

from dffml.db.sqlite import SqliteDatabaseConfig, SqliteDatabase
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.testing.source import SourceTest
from dffml.source.db import DbSource, DbSourceConfig


class TestDbSource(AsyncTestCase, SourceTest):
    db_config: SqliteDatabaseConfig
    source_config: DbSourceConfig
    database_name: str
    cols: Dict[str, str]

    SQL_TEARDOWN = """
    DROP TABLE IF EXISTS `TestTable`;
    """
    SQL_SETUP = """
    CREATE TABLE `TestTable` (
      `key` varchar(100) NOT NULL,
      `feature_PetalLength` float DEFAULT NULL,
      `feature_PetalWidth` float DEFAULT NULL,
      `feature_SepalLength` float DEFAULT NULL,
      `feature_SepalWidth` float DEFAULT NULL,
      `target_name_confidence` float DEFAULT NULL,
      `target_name_value` varchar(100) DEFAULT NULL,
      PRIMARY KEY (`key`)
    );
    """

    @classmethod
    def setUpClass(cls):
        # SQL table info
        cls.table_name = "TestTable"
        cls.cols = {
            "key": "varchar(100) NOT NULL PRIMARY KEY",
            "feature_PetalLength": "float DEFAULT NULL",
            "feature_PetalWidth": "float DEFAULT NULL",
            "feature_SepalLength": "float DEFAULT NULL",
            "feature_SepalWidth": "float DEFAULT NULL",
            "target_name_confidence": "float DEFAULT NULL",
            "target_name_value": "varchar(100) DEFAULT NULL",
        }

        # Sqlite db file
        file, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(file)

        # Sqlite config
        cls.db_config = SqliteDatabaseConfig(cls.database_name)

        # DbSource config
        cls.source_config = DbSourceConfig(
            db=SqliteDatabase(cls.db_config),
            table_name=cls.table_name,
            model_columns="key feature_PetalLength feature_PetalWidth feature_SepalLength feature_SepalWidth target_name_confidence target_name_value".split(),
        )

        # Setup connection to reset state (different from the connection used in the tests)
        conn = sqlite3.connect(cls.database_name)
        db_cursor = conn.cursor()
        db_cursor.execute(cls.SQL_TEARDOWN)
        db_cursor.execute(cls.SQL_SETUP)
        conn.commit()
        db_cursor.close()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.database_name)

    async def setUpSource(self):
        return DbSource(self.source_config)


# TODO: Potential shortcoming: Is there a way to call this source from the CLI and pass the db object (e.g. SqliteDatabase)?
# dffml list records -sources primary=dbsource -source-db_implementation sqlite -source-table_name testTable -source-db ??? -source-model_columns "key feature_PetalLength feature_PetalWidth feature_SepalLength feature_SepalWidth target_name_confidence target_name_value"
