import asyncio
import sqlite3
from typing import Dict, Any, List, Optional, AsyncIterator


from .base import BaseDatabase, Conditions
from .sql import SQLDatabaseContext
from ..base import config
from ..util.entrypoint import entrypoint


@config
class SqliteDatabaseConfig:
    filename: str


class SqliteDatabaseContext(SQLDatabaseContext):
    async def create_table(
        self, table_name: str, cols: Dict[str, str]
    ) -> None:
        query = self.create_table_query(table_name, cols)
        self.logger.debug(query)
        self.parent.cursor.execute(query)

    async def insert(self, table_name: str, data: Dict[str, Any]) -> None:
        query, query_values = self.insert_query(table_name, data)
        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, list(data.values()))

    async def update(
        self,
        table_name: str,
        data: Dict[str, Any],
        conditions: Optional[Conditions] = None,
    ) -> None:
        query, query_values = self.update_query(
            table_name, data, conditions=conditions
        )
        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, query_values)

    async def lookup(
        self,
        table_name: str,
        cols: Optional[List[str]] = None,
        conditions: Optional[Conditions] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        query, query_values = self.lookup_query(
            table_name, cols=cols, conditions=conditions
        )
        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, query_values)
                for row in self.parent.cursor.fetchall():
                    yield dict(row)

    async def remove(
        self, table_name: str, conditions: Optional[Conditions] = None
    ):
        query, query_values = self.remove_query(
            table_name, conditions=conditions
        )
        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, query_values)

    async def insert_or_update(self, table_name: str, data: Dict[str, Any]):
        try:
            await self.insert(table_name, data)
        except sqlite3.IntegrityError as e:
            # Hack to get primary key out of error message
            # Error : ` UNIQUE constraint failed: myTable.id `
            e = repr(e)
            replaces = "'`()"
            for s in replaces:
                e = e.replace(s, "")
            _key = e.split("UNIQUE constraint failed:")[-1]
            _key = _key.split(table_name + ".")[-1]

            _keyval = data.pop(_key)
            conditions = [[[_key, "=", _keyval]]]
            await self.update(table_name, data, conditions)


@entrypoint("sqlite")
class SqliteDatabase(BaseDatabase):
    CONFIG = SqliteDatabaseConfig
    CONTEXT = SqliteDatabaseContext

    def __init__(self, cfg):
        super().__init__(cfg)
        self.lock = None
        self.db = None
        self.cursor = None

    async def __aenter__(self):
        self.lock = asyncio.Lock()
        self.db = sqlite3.connect(self.config.filename)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        return await super().__aenter__()

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        self.db.close()
