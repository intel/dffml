import aiosqlite
from collections import OrderedDict
from typing import AsyncIterator, NamedTuple, Dict

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg


class CustomSQLiteSourceConfig(BaseConfig, NamedTuple):
    filename: str


class CustomSQLiteSourceContext(BaseSourceContext):
    async def update(self, repo: Repo):
        db = self.parent.db
        # Store feature data
        feature_cols = self.parent.FEATURE_COLS
        feature_data = OrderedDict.fromkeys(feature_cols)
        feature_data.update(repo.features(feature_cols))
        await db.execute(
            "INSERT OR REPLACE INTO features (key, "
            + ", ".join(feature_cols)
            + ") "
            "VALUES(?, " + ", ".join("?" * len(feature_cols)) + ")",
            [repo.key] + list(feature_data.values()),
        )
        # Store prediction
        try:
            prediction = repo.prediction("target_name")
            prediction_cols = self.parent.PREDICTION_COLS
            prediction_data = OrderedDict.fromkeys(prediction_cols)
            prediction_data.update(prediction.dict())
            await db.execute(
                "INSERT OR REPLACE INTO prediction (key, "
                + ", ".join(prediction_cols)
                + ") "
                "VALUES(?, " + ", ".join("?" * len(prediction_cols)) + ")",
                [repo.key] + list(prediction_data.values()),
            )
        except KeyError:
            pass
    async def repos(self) -> AsyncIterator[Repo]:
        # NOTE This logic probably isn't what you want. Only for demo purposes.
        keys = await self.parent.db.execute("SELECT key FROM features")
        for row in await keys.fetchall():
            yield await self.repo(row["key"])

    async def repo(self, key: str):
        db = self.parent.db
        repo = Repo(key)
        # Get features
        features = await db.execute(
            "SELECT " + ", ".join(self.parent.FEATURE_COLS) + " "
            "FROM features WHERE key=?",
            (repo.key,),
        )
        features = await features.fetchone()
        if features is not None:
            repo.evaluated(features)
        # Get prediction
        prediction = await db.execute(
            "SELECT * FROM prediction WHERE " "key=?", (repo.key,)
        )
        prediction = await prediction.fetchone()
        if prediction is not None:
            repo.predicted("target_name",prediction["value"], prediction["confidence"])
        return repo

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.parent.db.commit()


class CustomSQLiteSource(BaseSource):

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

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "filename", Arg())
        return args

    @classmethod
    def config(cls, config, *above):
        return CustomSQLiteSourceConfig(
            filename=cls.config_get(config, above, "filename")
        )
