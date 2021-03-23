import os
import json
import pathlib
from itertools import groupby
from operator import itemgetter
from typing import AsyncIterator, List, Tuple, Any

import numpy as np
import pandas as pd

from orion import Orion

from dffml import (
    config,
    field,
    entrypoint,
    ModelNotTrained,
    Accuracy,
    Sources,
    Features,
    SourcesContext,
    Record,
    Model,
    ModelContext,
)


@config
class OrionModelConfig:
    pipeline_name_or_path: str = field(
        "Name of a available pipeline or path to your custom pipeline json",
        default=None,
    )
    hyperparameters_path: str = field(
        "Path to json files containing hyperparameters for your pipeline",
        default="",
    )
    save_path: str = field(
        "Directory where model should be saved", default=os.getcwd()
    )

    def __post_init__(self):
        self.save_path = pathlib.Path(self.save_path)
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True)

        self.hyperparameters = None
        if os.path.isfile(self.hyperparameters_path):
            with open(self.hyperparameters_path) as fh:
                self.hyperparameters = json.load(fh)


class OrionModelContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = Orion(
            pipeline=self.parent.config.pipeline_name_or_path,
            hyperparameters=self.parent.config.hyperparameters,
        )
        self.input_features = ["timestamp", "value"]
        self.test_features = ["start", "end"]
        self.accuracy_features = self.input_features + ["is_anomaly"]
        self.predicted_features = self.test_features + ["severity"]
        self.model_name = self.model._pipeline + ".pkl"
        self.model_path = self.parent.config.save_path / self.model_name

    def _generate_ground_truth(self, test_data: pd.DataFrame) -> pd.DataFrame:
        is_anomaly_lst = test_data.is_anomaly.values
        anomalous_idxs = np.where(is_anomaly_lst == True)[0]
        ground_truth_dict = {key: [] for key in self.test_features}
        for _, g in groupby(enumerate(anomalous_idxs), lambda x: x[0] - x[1]):
            group = map(itemgetter(1), g)
            group = list(map(int, group))
            start_idx, end_idx = group[0], group[-1]
            start_ts = test_data.iloc[start_idx].timestamp
            end_ts = test_data.iloc[end_idx].timestamp
            ground_truth_dict[self.test_features[0]].append(start_ts)
            ground_truth_dict[self.test_features[1]].append(end_ts)
        ground_truth_df = pd.DataFrame(
            ground_truth_dict, columns=self.test_features
        )
        return ground_truth_df

    def _load_model(self, type_):
        action = {"acc": "assessing for accuracy", "pred": "prediction"}[type_]
        if not self.model_path.is_file():
            raise ModelNotTrained(f"Train model before {action}.")
        self.model = Orion.load(self.model_path)

    async def _generate_dataframe(
        self, sources: Sources, features_list: List[str]
    ) -> pd.DataFrame:
        data_source = sources.with_features(features_list)
        data_dict = {feature: [] for feature in features_list}
        async for data in data_source:
            for feature_name in features_list:
                data_dict[feature_name].append(data.feature(feature_name))
        dataframe = pd.DataFrame(data_dict, columns=features_list)
        # print(dataframe.info())
        # print(len(dataframe))
        return dataframe

    async def train(self, sources: Sources):
        train_data = await self._generate_dataframe(
            sources, self.input_features
        )
        self.model.fit(train_data)
        self.model.save(self.model_path)

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        self._load_model("acc")
        test_data = await self._generate_dataframe(
            sources, self.accuracy_features
        )
        ground_truth_data = self._generate_ground_truth(test_data)

        scores = self.model.evaluate(
            test_data[self.input_features], ground_truth_data
        )

        return Accuracy(scores.accuracy)

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, bool, float]]:
        self._load_model("pred")
        prediction_data = await self._generate_dataframe(
            sources, self.test_features
        )
        anomalies = self.model.detect(prediction_data)
        async for record in sources.records():
            timestamp = record.feature("timestamp")
            prediction = anomalies[
                (timestamp <= anomalies["end"])
                & (anomalies["start"] <= timestamp)
            ]
            if len(prediction):
                severity = prediction.iloc[0]["severity"]
                record.predicted("is_anomaly", True, severity)
                yield record


@entrypoint("orion")
class OrionModel(Model):
    CONFIG = OrionModelConfig
    CONTEXT = OrionModelContext
