"""
Expose Pandas DataFrame as DFFML Source
"""
from collections import OrderedDict
from typing import Dict, List, AsyncIterator


from ..base import config, field
from ..record import Record
from .source import BaseSourceContext, BaseSource
from ..util.entrypoint import entrypoint


class DataFrameSourceContext(BaseSourceContext):
    async def update(self, record: Record):

        df = self.parent.config.dataframe

        # Store feature data
        feature_cols = self.parent.FEATURE_COLS
        feature_data = OrderedDict.fromkeys(feature_cols)
        feature_data.update(record.features(feature_cols))

        for col in feature_cols:
            df.loc[record.key, col] = feature_data[col]

        # Store prediction
        try:
            prediction = record.prediction("target_name")
            prediction_cols = self.parent.PREDICTION_COLS
            prediction_data = OrderedDict.fromkeys(prediction_cols)
            prediction_data.update(prediction.dict())

            for col in prediction_cols:
                df.loc[record.key, col] = prediction_data[col]

        except KeyError:
            pass

    async def records(self) -> AsyncIterator[Record]:
        for row in self.parent.config.dataframe.itertuples():
            features = row._asdict()
            del features["Index"]
            yield Record(str(row.Index), data={"features": features})

    async def record(self, key: str) -> Record:
        return Record(
            str(key),
            data={"features": {**self.parent.config.dataframe.iloc[int(key)]}},
        )


@config
class DataFrameSourceConfig:
    dataframe: "pandas.DataFrame" = field("The pandas DataFrame to proxy")
    FEATURE_COLS: List[str] = field(
        "Feature columns whose values we have to update"
    )
    PREDICTION_COLS: List[str] = field(
        "Prediction columns whose values we have to update"
    )


@entrypoint("dataframe")
class DataFrameSource(BaseSource):
    """
    Proxy for a pandas DataFrame
    """

    CONFIG = DataFrameSourceConfig
    CONTEXT = DataFrameSourceContext
