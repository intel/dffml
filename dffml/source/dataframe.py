"""
Expose Pandas DataFrame as DFFML Source
"""
from collections import OrderedDict
from typing import Dict, List, AsyncIterator


from ..record import Record
from ..base import config, field
from ..util.entrypoint import entrypoint
from .source import BaseSourceContext, BaseSource


class DataFrameSourceContext(BaseSourceContext):
    async def update(self, record: Record):

        df = self.parent.config.dataframe

        feature_columns = []
        for col in df.columns:
            feature_columns.append(col)

        # Store feature data
        feature_data = OrderedDict.fromkeys(feature_columns)
        feature_data.update(record.features(feature_columns))
        for col in feature_columns:
            df.loc[record.key, col] = feature_data[col]

        # Store prediction
        for col in self.parent.config.predictions:

            prediction = record.prediction(col)
            prediction_columns = self.parent.config.predictions
            prediction_data = OrderedDict.fromkeys(prediction_columns)
            prediction_data.update(prediction.dict())

            df.loc[record.key, col] = prediction_data[col]

    async def records(self) -> AsyncIterator[Record]:
        for row in self.parent.config.dataframe.itertuples():
            features = row._asdict()
            del features["Index"]
            yield Record(str(row.Index), data={"features": features})

    async def record(self, key: str) -> Record:
        data = self.parent.config.dataframe.iloc[int(key)]
        predictions = {
            key: data[key] for key in self.parent.config.predictions
        }
        features = {
            key: value for key in data.items() if key not in predictions
        }
        return Record(
            str(key), data={"features": features, "predictions": predictions},
        )


@config
class DataFrameSourceConfig:
    dataframe: "pandas.DataFrame" = field("The pandas DataFrame to proxy")
    predictions: List[str] = field(
        "Prediction columns whose values we have to update"
    )


@entrypoint("dataframe")
class DataFrameSource(BaseSource):
    """
    Proxy for a pandas DataFrame
    """

    CONFIG = DataFrameSourceConfig
    CONTEXT = DataFrameSourceContext
