import ssl
import itertools
import collections
from typing import AsyncIterator, NamedTuple, Dict, List, Tuple

import aiomysql

from dffml import config, field
from dffml.base import BaseConfig
from dffml.record import Record
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entrypoint


class InsecureMySQLConnection(Exception):
    """
    Raised when the asynchronous context of the MySQL source is entered without
    a server CA file in it's config AND without the insecure property of it's
    config being set to True. This is to prevent users from unknowingly making
    insecure connections.
    """


@config
class MySQLSourceConfig:
    user: str = field("Username")
    password: str = field("Password")
    db: str = field("Name of database to use")
    key: str = field("Column name of record key")
    features: Dict[str, str] = field(
        "Mapping of feature names to column names"
    )
    predictions: Dict[str, Tuple[str, str]] = field(
        "Mapping of prediction names to tuples of (value, confidence) column names"
    )
    update: str = field("Query to update a single record")
    record: str = field("Query to get a single record")
    records: str = field("Query to get a single record")
    init: str = field("Query to run on initial connection", default=None)
    host: str = field("Host/address to connect to", default="127.0.0.1")
    port: int = field("Port to connect to", default=3306)
    ca: str = field(
        "Server certificate to use for TLS validation", default=None
    )
    insecure: bool = field(
        "Must be true to accept risks of non-TLS connection", default=False
    )


class MySQLSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        # Column name of value mapping
        bindings = {self.parent.config.key: record.key}
        # Features
        features = record.features(self.parent.config.features.keys())
        for feature_name, column_name in self.parent.config.features.items():
            bindings[column_name] = features.get(feature_name, None)
        # Predictions
        predictions = record.predictions(self.parent.config.predictions.keys())
        for (
            feature_name,
            (value_column_name, confidence_column_name),
        ) in self.parent.config.predictions.items():
            bindings[value_column_name] = None
            if confidence_column_name is not None:
                bindings[confidence_column_name] = None
            if feature_name in predictions:
                bindings[value_column_name] = predictions[feature_name][
                    "value"
                ]
                if confidence_column_name is not None:
                    bindings[confidence_column_name] = predictions[
                        feature_name
                    ]["confidence"]
        # Bindings should be the values for each column, where the value for the
        # key is not repeated for the UPDATE. If useing REPLACE INTO, don't
        # repeat values
        values = list(bindings.values())
        if not "REPLACE" in self.parent.config.update.upper():
            values += list(bindings.values())[1:]
        # Execute the update query
        await self.conn.execute(self.parent.config.update, values)
        self.logger.debug("Updated: %s: %r", record.key, bindings)

    def row_to_record(self, row):
        features = {}
        predictions = {}
        # Features
        for feature_name, column_name in self.parent.config.features.items():
            features[feature_name] = row[column_name]
        # Predictions
        for (
            feature_name,
            (value_column_name, confidence_column_name),
        ) in self.parent.config.predictions.items():
            predictions[feature_name] = {
                "value": row[value_column_name],
                # Set confidence to Not A Number if not given
                "confidence": row.get(confidence_column_name, float("nan")),
            }
        return Record(
            row[self.parent.config.key],
            data={"features": features, "prediction": predictions},
        )

    async def records(self) -> AsyncIterator[Record]:
        # Execute the query to get all records
        await self.conn.execute(self.parent.config.records)
        # Grab records batch by batch until none are left
        result = [True]
        while result:
            # Grab another batch
            result = await self.conn.fetchmany()
            if not result:
                continue
            # Convert row objects to Record objects
            for row in result:
                yield self.row_to_record(row)

    async def record(self, key: str):
        # Create a blank record in case it doesn't exist within the source
        record = Record(key)
        # Execute the query to get a single record from a key
        await self.conn.execute(self.parent.config.record, (key,))
        # Retrieve the result
        row = await self.conn.fetchone()
        # Convert it to a record if it exists and populate the previously blank
        # record by merging the two
        if row is not None:
            record.merge(self.row_to_record(row))
        self.logger.debug("Got: %s: %r", record.key, record.export())
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
    """
    .. warning::

        - ``update`` config property is a SQL query which MUST handle insersion
          or update. Columns to be updated should list feature columns first,
          followed by prediction columns.

        - ``features`` config property MUST have keys in same order as they
          appear within ``update`` query.

        - ``prediction`` config property MUST have keys in same order as they
          appear within ``update`` query.

    Examples
    --------

    Read MySQL or MariaDB's documentation to understand how to properly setup
    your server for encrypted connections.

    - `Configuring MySQL to Use Encrypted Connections <https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html>`_
    """

    CONTEXT = MySQLSourceContext
    CONFIG = MySQLSourceConfig

    async def __aenter__(self) -> "MySQLSource":
        # Verify MySQL connection using provided certificate, if given
        ssl_ctx = None
        if self.config.ca is not None:
            self.logger.debug(
                f"Secure connection to MySQL: CA file: {self.config.ca}"
            )
            ssl_ctx = ssl.create_default_context(cafile=self.config.ca)
        elif self.config.insecure:
            self.logger.critical("INSECURE connection to MySQL")
        else:
            raise InsecureMySQLConnection(
                "Attempted connection with insecure as false and no ca file"
            )
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
        # Run initial connection SQL if given
        if self.config.init is not None:
            async with self.db.cursor(aiomysql.DictCursor) as conn:
                await conn.execute(self.config.init)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__db.__aexit__(exc_type, exc_value, traceback)
        self.pool.close()
        await self.pool.wait_closed()
