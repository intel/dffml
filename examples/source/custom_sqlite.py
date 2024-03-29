import aiosqlite
from collections import OrderedDict
from typing import AsyncIterator

from dffml import config, Record, BaseSource, BaseSourceContext


@config
class CustomSQLiteSourceConfig:
    filename: str


class CustomSQLiteSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        db = self.parent.db
        # Store feature data
        feature_cols = self.parent.FEATURE_COLS
        feature_data = OrderedDict.fromkeys(feature_cols)
        feature_data.update(record.features(feature_cols))
        await db.execute(
            "INSERT OR REPLACE INTO features (key, "
            + ", ".join(feature_cols)
            + ") "
            "VALUES(?, " + ", ".join("?" * len(feature_cols)) + ")",
            [record.key] + list(feature_data.values()),
        )
        # Store prediction
        try:
            prediction = record.prediction("target_name")
            prediction_cols = self.parent.PREDICTION_COLS
            prediction_data = OrderedDict.fromkeys(prediction_cols)
            prediction_data.update(prediction.dict())
            await db.execute(
                "INSERT OR REPLACE INTO prediction (key, "
                + ", ".join(prediction_cols)
                + ") "
                "VALUES(?, " + ", ".join("?" * len(prediction_cols)) + ")",
                [record.key] + list(prediction_data.values()),
            )
        except KeyError:
            pass

    async def records(self) -> AsyncIterator[Record]:
        # NOTE This logic probably isn't what you want. Only for demo purposes.
        keys = await self.parent.db.execute("SELECT key FROM features")
        for row in await keys.fetchall():
            yield await self.record(row["key"])

    async def record(self, key: str):
        db = self.parent.db
        record = Record(key)
        # Get features
        features = await db.execute(
            "SELECT " + ", ".join(self.parent.FEATURE_COLS) + " "
            "FROM features WHERE key=?",
            (record.key,),
        )
        features = await features.fetchone()
        if features is not None:
            record.evaluated(features)
        # Get prediction
        prediction = await db.execute(
            "SELECT * FROM prediction WHERE " "key=?", (record.key,)
        )
        prediction = await prediction.fetchone()
        if prediction is not None:
            record.predicted(
                "target_name", prediction["value"], prediction["confidence"]
            )
        return record

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.parent.db.commit()


class CustomSQLiteSource(BaseSource):

    CONFIG = CustomSQLiteSourceConfig
    CONTEXT = CustomSQLiteSourceContext
    FEATURE_COLS = ["PetalLength", "PetalWidth", "SepalLength", "SepalWidth"]
    PREDICTION_COLS = ["value", "confidence"]

    async def __aenter__(self) -> "BaseSourceContext":
        self.__db = aiosqlite.connect(self.config.filename)
        self.db = await self.__db.__aenter__()
        self.db.row_factory = aiosqlite.Row
        # Create table for feature data
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS features ("
            "key TEXT PRIMARY KEY NOT NULL, "
            + (" REAL, ".join(self.FEATURE_COLS))
            + " REAL"
            ")"
        )
        # Create table for predictions
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS prediction ("
            "key TEXT PRIMARY KEY, " + "value TEXT, "
            "confidence REAL"
            ")"
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__db.__aexit__(exc_type, exc_value, traceback)
