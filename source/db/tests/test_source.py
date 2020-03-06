import os
import tempfile
from typing import Dict

from dffml.db.sqlite import SqliteDatabaseConfig, SqliteDatabase
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.testing.source import SourceTest
from source.db.dffml_source_db.source import DbSource, DbSourceConfig


class TestDbSource(AsyncTestCase, SourceTest):
    db_config: SqliteDatabaseConfig
    source_config: DbSourceConfig
    database_name: str
    cols: Dict[str, str]

    @classmethod
    def setUpClass(cls):
        # SQL table info
        # TODO: This implies that the database is SQL and potentially excludes some SQL variants
        # TODO: We need a more abstract way to handle the testing database/table setup/creation
        cls.table_name = "testTable"
        cls.cols = {
            "key": "varchar(100) NOT NULL PRIMARY KEY",
            "feature_PetalLength": "float DEFAULT NULL",
            "feature_PetalWidth": "float DEFAULT NULL",
            "feature_SepalLength": "float DEFAULT NULL",
            "feature_SepalWidth": "float DEFAULT NULL",
            "target_name_confidence": "float DEFAULT NULL",
            "target_name_value": "varchar(100) DEFAULT NULL",
        }

        # TODO: We could either manually create the table and test each new db implementation
        # TODO: or we could add a hook after setUpSource() to use the abstract db.create_table()
        # TODO: Add in Docker environment stuff?

        # Sqlite db file
        file, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(file)

        # Sqlite config
        cls.db_config = SqliteDatabaseConfig("sqlite_config")

        # DbSource config
        cls.source_config = DbSourceConfig(
            db_implementation="sqlite",
            db_config=cls.db_config,
            table_name=cls.table_name,
            model_columns="key feature_PetalLength feature_PetalWidth feature_SepalLength feature_SepalWidth target_name_confidence target_name_value",
        )

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.database_name)

    async def setUpSource(self):
        return DbSource(self.source_config)

    async def setUp(self):
        self.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=self.database_name)
        )
