import inspect
from typing import Dict, Any, Optional, List

from ..base import config
from ..df.base import op
from ..db.base import Conditions, BaseDatabase
from ..df.types import Definition


# definitions
QUERY_TABLE = Definition(name="query_table", primitive="str")
QUERY_DATA = Definition(name="query_data", primitive="Dict[str, Any]")
QUERY_CONDITIONS = Definition(name="query_conditions", primitive="Conditions")
QUERY_COLS = Definition(name="query_cols", primitive="Dict[str, str]")
QUERY_LOOKUPS = Definition(name="query_lookups", primitive="Dict[str, Any]")


@config
class DatabaseQueryConfig:
    database: BaseDatabase


# TODO Remove this?
# TODO Figure out a way to handle defaults so that all inputs need not be passed to the
# flow on execution
# Note : Add `query_type`:str to `DatabaseQueryConfig` before use.
@op(
    inputs={
        "table_name": QUERY_TABLE,
        "data": QUERY_DATA,
        "conditions": QUERY_CONDITIONS,
        "cols": QUERY_COLS,
    },
    outputs={"lookups": QUERY_LOOKUPS},
    config_cls=DatabaseQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def db_query(
    self,
    *,
    table_name: str,
    data: Dict[str, Any] = {},
    conditions: Conditions = [],
    cols: List[str] = [],
) -> Optional[Dict[str, Any]]:

    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)

    kwargs = {arg: values[arg] for arg in args[1:]}
    query_fn = self.config.query_type
    if "create" in query_fn:
        query_fn = "create_table"
    allowed = ["create_table", "remove", "update", "insert", "lookup"]
    if not query_fn in allowed:
        raise ValueError(f"Only queries of type {allowed} is allowed")

    query_fn = getattr(self.dbctx, query_fn)

    try:
        await query_fn(**kwargs)
        return {"lookups": {}}

    except TypeError as e:
        if "async_gen" in repr(e):
            result = query_fn(**kwargs)
            return {"lookups": [res async for res in result]}
        else:
            raise e


@op(
    inputs={"table_name": QUERY_TABLE, "cols": QUERY_COLS},
    outputs={},
    config_cls=DatabaseQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def db_query_create_table(
    self, *, table_name: str, cols: List[str] = []
):
    """
    Generates a create table query in the database.

    Parameters
    ----------
    table_name : str
        The name of the table to be created.
    cols : list[str]
        Columns of the table.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> sdb = SqliteDatabase(SqliteDatabaseConfig(filename="examples.db"))
    >>>
    >>> dataflow = DataFlow(
    ...     operations={"db_query_create": db_query_create_table.op,},
    ...     configs={"db_query_create": DatabaseQueryConfig(database=sdb),},
    ...     seed=[],
    ... )
    >>>
    >>> inputs = [
    ...     Input(
    ...         value="myTable1",
    ...         definition=db_query_create_table.op.inputs["table_name"],
    ...     ),
    ...     Input(
    ...         value={
    ...             "key": "real",
    ...             "firstName": "text",
    ...             "lastName": "text",
    ...             "age": "real",
    ...         },
    ...         definition=db_query_create_table.op.inputs["cols"],
    ...     ),
    ... ]
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         pass
    >>>
    >>> asyncio.run(main())
    """
    await self.dbctx.create_table(table_name=table_name, cols=cols)


@op(
    inputs={"table_name": QUERY_TABLE, "data": QUERY_DATA},
    outputs={},
    config_cls=DatabaseQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def db_query_insert(self, *, table_name: str, data: Dict[str, Any]):
    """
    Generates an insert query in the database.

    Parameters
    ----------
    table_name : str
        The name of the table to insert data in to.
    data : dict
        Data to be inserted into the table.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> sdb = SqliteDatabase(SqliteDatabaseConfig(filename="examples.db"))
    >>>
    >>> dataflow = DataFlow(
    ...     operations={
    ...         "db_query_insert": db_query_insert.op,
    ...         "db_query_lookup": db_query_lookup.op,
    ...         "get_single": GetSingle.imp.op,
    ...     },
    ...     configs={
    ...         "db_query_lookup": DatabaseQueryConfig(database=sdb),
    ...         "db_query_insert": DatabaseQueryConfig(database=sdb),
    ...     },
    ...     seed=[],
    ... )
    >>>
    >>> inputs = {
    ...     "insert": [
    ...         Input(
    ...             value="myTable", definition=db_query_insert.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...            value={"key": 10, "firstName": "John", "lastName": "Doe", "age": 16},
    ...             definition=db_query_insert.op.inputs["data"],
    ...         ),
    ...     ],
    ...     "lookup": [
    ...         Input(
    ...             value="myTable", definition=db_query_lookup.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...             value=["firstName", "lastName", "age"],
    ...             definition=db_query_lookup.op.inputs["cols"],
    ...         ),
    ...         Input(value=[], definition=db_query_lookup.op.inputs["conditions"],),
    ...         Input(
    ...             value=[db_query_lookup.op.outputs["lookups"].name],
    ...             definition=GetSingle.op.inputs["spec"],
    ...         ),
    ...     ]
    ... }
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         if result:
    ...             print(result)
    >>>
    >>> asyncio.run(main())
    {'query_lookups': [{'firstName': 'John', 'lastName': 'Doe', 'age': 16}]}
    """
    await self.dbctx.insert(table_name=table_name, data=data)


@op(
    inputs={
        "table_name": QUERY_TABLE,
        "data": QUERY_DATA,
        "conditions": QUERY_CONDITIONS,
    },
    outputs={},
    config_cls=DatabaseQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def db_query_update(
    self, *, table_name: str, data: Dict[str, Any], conditions: Conditions = []
):
    """
    Generates an Update table query in the database.

    Parameters
    ----------
    table_name : str
        The name of the table to insert data in to.
    data : dict
        Data to be updated into the table.
    conditions : list
        List of query conditions.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> sdb = SqliteDatabase(SqliteDatabaseConfig(filename="examples.db"))
    >>>
    >>> dataflow = DataFlow(
    ...     operations={
    ...         "db_query_update": db_query_update.op,
    ...         "db_query_lookup": db_query_lookup.op,
    ...         "get_single": GetSingle.imp.op,
    ...     },
    ...     configs={
    ...         "db_query_update": DatabaseQueryConfig(database=sdb),
    ...         "db_query_lookup": DatabaseQueryConfig(database=sdb),
    ...     },
    ...     seed=[],
    ... )
    >>>
    >>> inputs = {
    ...     "update": [
    ...         Input(
    ...             value="myTable",
    ...             definition=db_query_update.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...             value={
    ...                 "key": 10,
    ...                 "firstName": "John",
    ...                 "lastName": "Doe",
    ...                 "age": 17,
    ...             },
    ...             definition=db_query_update.op.inputs["data"],
    ...         ),
    ...         Input(value=[], definition=db_query_update.op.inputs["conditions"],),
    ...     ],
    ...     "lookup": [
    ...         Input(
    ...             value="myTable",
    ...             definition=db_query_lookup.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...             value=["firstName", "lastName", "age"],
    ...             definition=db_query_lookup.op.inputs["cols"],
    ...         ),
    ...         Input(value=[], definition=db_query_lookup.op.inputs["conditions"],),
    ...         Input(
    ...             value=[db_query_lookup.op.outputs["lookups"].name],
    ...             definition=GetSingle.op.inputs["spec"],
    ...         ),
    ...     ],
    ... }
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         if result:
    ...             print(result)
    >>>
    >>> asyncio.run(main())
    {'query_lookups': [{'firstName': 'John', 'lastName': 'Doe', 'age': 17}]}
    """
    await self.dbctx.update(
        table_name=table_name, data=data, conditions=conditions
    )


@op(
    inputs={"table_name": QUERY_TABLE, "conditions": QUERY_CONDITIONS},
    outputs={},
    config_cls=DatabaseQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def db_query_remove(
    self, *, table_name: str, conditions: Conditions = []
):
    """
    Generates a remove table query in the database.

    Parameters
    ----------
    table_name : str
        The name of the table to insert data in to.
    conditions : Conditions
        Query conditions.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> sdb = SqliteDatabase(SqliteDatabaseConfig(filename="examples.db"))
    >>>
    >>> dataflow = DataFlow(
    ...     operations={
    ...         "db_query_lookup": db_query_lookup.op,
    ...         "db_query_remove": db_query_remove.op,
    ...         "get_single": GetSingle.imp.op,
    ...     },
    ...     configs={
    ...         "db_query_remove": DatabaseQueryConfig(database=sdb),
    ...         "db_query_lookup": DatabaseQueryConfig(database=sdb),
    ...     },
    ...     seed=[],
    ... )
    >>>
    >>> inputs = {
    ...     "remove": [
    ...         Input(
    ...             value="myTable",
    ...             definition=db_query_remove.op.inputs["table_name"],
    ...         ),
    ...         Input(value=[],
    ...         definition=db_query_remove.op.inputs["conditions"],),
    ...     ],
    ...     "lookup": [
    ...         Input(
    ...             value="myTable",
    ...             definition=db_query_lookup.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...             value=["firstName", "lastName", "age"],
    ...             definition=db_query_lookup.op.inputs["cols"],
    ...         ),
    ...         Input(value=[], definition=db_query_lookup.op.inputs["conditions"],),
    ...         Input(
    ...             value=[db_query_lookup.op.outputs["lookups"].name],
    ...             definition=GetSingle.op.inputs["spec"],
    ...         ),
    ...     ],
    ... }
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         if result:
    ...             print(result)
    >>>
    >>> asyncio.run(main())
    {'query_lookups': []}
    """
    await self.dbctx.remove(table_name=table_name, conditions=conditions)


@op(
    inputs={
        "table_name": QUERY_TABLE,
        "cols": QUERY_COLS,
        "conditions": QUERY_CONDITIONS,
    },
    outputs={"lookups": QUERY_LOOKUPS},
    config_cls=DatabaseQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def db_query_lookup(
    self, *, table_name: str, cols: List[str] = [], conditions: Conditions = []
) -> Dict[str, Any]:
    """
    Generates a lookup query in the database.

    Parameters
    ----------
    table_name : str
        The name of the table.
    cols : list[str]
        Columns of the table.
    conditions : Conditions
        Query conditions.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> sdb = SqliteDatabase(SqliteDatabaseConfig(filename="examples.db"))
    >>>
    >>> dataflow = DataFlow(
    ...     operations={
    ...         "db_query_lookup": db_query_lookup.op,
    ...         "get_single": GetSingle.imp.op,
    ...     },
    ...     configs={"db_query_lookup": DatabaseQueryConfig(database=sdb),},
    ...     seed=[],
    ... )
    >>>
    >>> inputs = {
    ...     "lookup": [
    ...         Input(
    ...             value="myTable",
    ...             definition=db_query_lookup.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...             value=["firstName", "lastName", "age"],
    ...             definition=db_query_lookup.op.inputs["cols"],
    ...         ),
    ...         Input(value=[], definition=db_query_lookup.op.inputs["conditions"],),
    ...         Input(
    ...             value=[db_query_lookup.op.outputs["lookups"].name],
    ...             definition=GetSingle.op.inputs["spec"],
    ...         ),
    ...     ],
    ... }
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         if result:
    ...             print(result)
    >>>
    >>> asyncio.run(main())
    {'query_lookups': [{'firstName': 'John', 'lastName': 'Doe', 'age': 16}, {'firstName': 'John', 'lastName': 'Wick', 'age': 39}]}
    """
    result = self.dbctx.lookup(
        table_name=table_name, cols=cols, conditions=conditions
    )
    return {"lookups": [res async for res in result]}


@op(
    inputs={"table_name": QUERY_TABLE, "data": QUERY_DATA},
    outputs={},
    config_cls=DatabaseQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def db_query_insert_or_update(
    self, *, table_name: str, data: Dict[str, Any]
):
    """
    Automatically uses the better suited operation, insert query or update query.

    Parameters
    ----------
    table_name : str
        The name of the table to insert data in to.
    data : dict
        Data to be inserted or updated into the table.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> sdb = SqliteDatabase(SqliteDatabaseConfig(filename="examples.db"))
    >>>
    >>> person = {"key": 11, "firstName": "John", "lastName": "Wick", "age": 38}
    >>>
    >>> dataflow = DataFlow(
    ...     operations={
    ...         "db_query_insert_or_update": db_query_insert_or_update.op,
    ...         "db_query_lookup": db_query_lookup.op,
    ...         "get_single": GetSingle.imp.op,
    ...     },
    ...     configs={
    ...         "db_query_insert_or_update": DatabaseQueryConfig(database=sdb),
    ...         "db_query_lookup": DatabaseQueryConfig(database=sdb),
    ...     },
    ...     seed=[],
    ... )
    >>>
    >>> inputs = {
    ...     "insert_or_update": [
    ...         Input(
    ...             value="myTable", definition=db_query_update.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...             value=person,
    ...             definition=db_query_update.op.inputs["data"],
    ...         ),
    ...     ],
    ...     "lookup": [
    ...         Input(
    ...             value="myTable",
    ...             definition=db_query_lookup.op.inputs["table_name"],
    ...         ),
    ...         Input(
    ...             value=["firstName", "lastName", "age"],
    ...             definition=db_query_lookup.op.inputs["cols"],
    ...         ),
    ...         Input(value=[], definition=db_query_lookup.op.inputs["conditions"],),
    ...         Input(
    ...             value=[db_query_lookup.op.outputs["lookups"].name],
    ...             definition=GetSingle.op.inputs["spec"],
    ...         ),
    ...     ],
    ... }
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         if result:
    ...             print(result)
    >>>
    >>> asyncio.run(main())
    {'query_lookups': [{'firstName': 'John', 'lastName': 'Wick', 'age': 38}]}
    >>>
    >>> person["age"] += 1
    >>>
    >>> asyncio.run(main())
    {'query_lookups': [{'firstName': 'John', 'lastName': 'Wick', 'age': 39}]}
    """
    await self.dbctx.insert_or_update(table_name=table_name, data=data)
