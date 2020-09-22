import collections
from typing import Type, AsyncIterator, List

from ..base import config, BaseConfig
from ..db.base import BaseDatabase, Condition
from ..record import Record
from ..source.source import BaseSource, BaseSourceContext
from ..util.entrypoint import entrypoint


@config
class DbSourceConfig(BaseConfig):
    db: BaseDatabase
    table_name: str
    model_columns: List[str]


class DbSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        model_columns = self.parent.config.model_columns
        key_value_pairs = collections.OrderedDict()
        for key in model_columns:
            if key.startswith("feature_"):
                modified_key = key.replace("feature_", "")
                key_value_pairs[key] = record.data.features[modified_key]
            elif "_value" in key:
                target = key.replace("_value", "")
                if record.data.prediction:
                    key_value_pairs[key] = record.data.prediction[target][
                        "value"
                    ]
                else:
                    key_value_pairs[key] = None
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
        async with self.parent.db() as db_ctx:
            await db_ctx.insert_or_update(
                self.parent.config.table_name, key_value_pairs
            )
        self.logger.debug("update: %s", await self.record(record.key))

    async def records(self) -> AsyncIterator[Record]:
        async with self.parent.db() as db_ctx:
            async for result in db_ctx.lookup(self.parent.config.table_name):
                yield self.convert_to_record(result)

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

    async def record(self, key: str):
        record = Record(key)
        async with self.parent.db() as db_ctx:
            try:
                row = await db_ctx.lookup(
                    self.parent.config.table_name,
                    cols=None,  # None turns into *. We want all rows
                    conditions=[[Condition("key", "=", key)]],
                ).__anext__()
            except StopAsyncIteration:
                # This would happen if there is no matching row, so the async generator reached the end
                return record

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


@entrypoint("db")
class DbSource(BaseSource):
    CONFIG = DbSourceConfig
    CONTEXT = DbSourceContext

    def __init__(self, cfg: Type[BaseConfig]) -> None:
        super().__init__(cfg)

    async def __aenter__(self) -> "DbSource":
        self.db = await self.config.db.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.db.__aexit__(exc_type, exc_value, traceback)
