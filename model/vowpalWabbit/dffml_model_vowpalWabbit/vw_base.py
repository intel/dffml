# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Base class for VW models
"""
import os
import json
import hashlib
from pathlib import Path
from typing import (
    AsyncIterator,
    Tuple,
    Any,
    List,
)

import numpy as np
import pandas as pd
from vowpalwabbit import pyvw
from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score, r2_score

from dffml.record import Record
from dffml.model.accuracy import Accuracy
from dffml.source.source import Sources
from dffml.util.entrypoint import entrypoint
from dffml.base import config, field
from dffml.feature.feature import Features, Feature
from dffml.model.model import ModelContext, Model, ModelNotTrained

from .util.data import df_to_vw_format, create_input_pair


class InputError(Exception):
    pass


# TODO override input, and output options
@config
class VWConfig:
    features: Features
    predict: Feature = field("Feature to predict")
    class_cost: Features = field(
        "Features with name `Cost_{class}` contaning cost of `class` for each input example, used when `csoaa` is used",
        default=None,
    )
    task: str = field(
        "Task to perform, possible values are `classification`, `regression`",
        default="regression",
    )
    use_binary_label: bool = field(
        "Convert target labels to -1 and 1 for binary classification",
        default=False,
    )
    vwcmd: List[str] = field(
        "Command Line Arguements as per vowpal wabbit convention",
        default_factory=lambda: [
            "loss_function",
            "logistic",
            "link",
            "logistic",
            "l2",
            "0.04",
        ],
    )

    namespace: List[str] = field(
        "Namespace for input features. Should be in format {namespace}_{feature name}",
        default_factory=lambda: [],
    )
    importance: Feature = field(
        "Feature containing `importance` of each example, used in conversion of input data to vowpal wabbit input format",
        default=None,
    )
    base: Feature = field(
        "Feature containing `base` for each example, used for residual regression",
        default=None,
    )
    tag: Feature = field(
        "Feature to be used as `tag` in conversion of data to vowpal wabbit input format",
        default=None,
    )
    convert_to_vw: bool = field(
        "Convert the input to vowpal wabbit standard input format",
        default=False,
    )
    directory: str = field(
        "Directory where state should be saved",
        default=os.path.join(
            os.path.expanduser("~"), ".cache", "dffml", "vowpalWabbit"
        ),
    )

    def __post_init__(self):
        self.extra_cols = []
        namespace = dict()
        itr = iter(self.vwcmd)
        self.vwcmd = dict(zip(itr, itr))
        self.passes = int(self.vwcmd.pop("passes", 1))
        if "bgfs" in self.vwcmd:
            raise NotImplementedError("Using bgfs optimizer is not supported")
        for arg in ["d", "data"]:
            if arg in self.vwcmd:
                raise InputError(
                    f"Passing data through {arg} option is not supported. Pass the input data using dffml sources."
                )
        # TODO handle --save_resume
        if "examples" in self.vwcmd:
            raise InputError(
                "Currently dffml sources do not support reading specified number of rows."
            )
        for nsinfo in self.namespace:
            ns, cols = nsinfo.split("_", 1)
            if ns in namespace.keys():
                namespace[ns].extend(cols.split("_"))
            else:
                namespace[ns] = cols.split("_")
        self.namespace = namespace

        if self.class_cost:
            self.extra_cols += [feature.NAME for feature in self.class_cost]
        for col in [self.importance, self.base, self.tag]:
            if col is not None:
                self.extra_cols.append(col.NAME)


class VWContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.features = self.applicable_features(self.parent.config.features)
        self._features_hash = self._feature_predict_hash()
        self.clf = None

    @property
    def confidence(self):
        return self.parent.saved.get(self._features_hash, float("nan"))

    @confidence.setter
    def confidence(self, confidence):
        self.parent.saved[self._features_hash] = confidence

    # TODO decide what to hash
    def _feature_predict_hash(self):
        params = sorted(
            [
                "{}{}".format(k, v)
                for k, v in self.parent.config._asdict().items()
                if k
                not in [
                    "directory",
                    "features",
                    "predict",
                    "vwcmd",
                    "class_cost",
                    "importance",
                    "tag",
                    "base",
                ]
            ]
        )
        params = "".join(params)
        return hashlib.sha384(
            "".join([params] + self.features).encode()
        ).hexdigest()

    def applicable_features(self, features):
        usable = []
        for feature in features:
            usable.append(feature.NAME)
        return sorted(usable)

    def modify_config(self):
        vwcmd = self.parent.config.vwcmd
        direc = self.parent.config.directory
        # direct all output files to a single folder
        # unless full path for respective outputs is provided
        for arg in [
            "final_regressor",
            "f",
            "raw_predictions",
            "r",
            "predictions",
            "p",
            "readable_model",
            "invert_hash",
            "audit_regressor",
            "output_feature_regularizer_binary",
            "output_feature_regularizer_text",
        ]:
            if arg in vwcmd:
                file_path = vwcmd[arg]
                head, tail = os.path.split(file_path)
                # Let pyvw.vw() throw error if `head` is not a valid directory
                if not head.strip():
                    vwcmd[arg] = os.path.join(direc, tail)
        return vwcmd

    def _filename(self):
        return os.path.join(
            self.parent.config.directory, self._features_hash + ".vw"
        )

    def _load_model(self):
        formatted_args = ""
        for key, value in self.parent.config.vwcmd.items():
            formatted_args = (
                formatted_args + " " + create_input_pair(key, value)
            )
        for arg in ["initial_regressor", "i"]:
            if arg in self.parent.config.vwcmd:
                self.logger.info(
                    f"Using model weights from {self.parent.config.vwcmd[arg]}"
                )
                return pyvw.vw(formatted_args)
        if os.path.isfile(self._filename()):
            self.parent.config.vwcmd["initial_regressor"] = self._filename()
            formatted_args += f" --initial_regressor {self._filename()}"
            self.logger.info(f"Using model weights from {self._filename()}")
        return pyvw.vw(formatted_args)

    def _save_model(self):
        for arg in ["final_regressor", "f"]:
            if arg in self.parent.config.vwcmd:
                self.logger.info(
                    f"Saving model weights to {self.parent.config.vwcmd[arg]}"
                )
                return
        self.logger.info(f"Saving model weights to {self._filename()}")
        self.clf.save(self._filename())
        return

    async def __aenter__(self):
        self.parent.config.vwcmd = self.modify_config()
        self.clf = self._load_model()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def train(self, sources: Sources):
        data = []
        importance, tag, base, class_cost = None, None, None, None
        if self.parent.config.importance:
            importance = self.parent.config.importance.NAME

        if self.parent.config.tag:
            tag = self.parent.config.tag.NAME

        if self.parent.config.base:
            base = self.parent.config.base.NAME
        if self.parent.config.class_cost:
            class_cost = [
                feature.NAME for feature in self.parent.config.class_cost
            ]
        async for record in sources.with_features(
            self.features
            + [self.parent.config.predict.NAME]
            + self.parent.config.extra_cols
        ):
            feature_data = record.features(
                self.features
                + [self.parent.config.predict.NAME]
                + self.parent.config.extra_cols
            )
            data.append(feature_data)
        vw_data = pd.DataFrame(data)
        if self.parent.config.convert_to_vw:
            vw_data = df_to_vw_format(
                vw_data,
                vwcmd=self.parent.config.vwcmd,
                target=self.parent.config.predict.NAME,
                namespace=self.parent.config.namespace,
                importance=importance,
                tag=tag,
                base=base,
                task=self.parent.config.task,
                use_binary_label=self.parent.config.use_binary_label,
                class_cost=class_cost,
            )
        self.logger.info("Number of input records: {}".format(len(vw_data)))
        for n in range(self.parent.config.passes):
            if n > 1:
                X = shuffle(vw_data)
            else:
                X = vw_data
            for x in X:
                self.clf.learn(x)
        self._save_model()

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        data = []
        importance, tag, base, class_cost = None, None, None, None
        if self.parent.config.importance:
            importance = self.parent.config.importance.NAME

        if self.parent.config.tag:
            tag = self.parent.config.tag.NAME

        if self.parent.config.base:
            base = self.parent.config.base.NAME
        async for record in sources.with_features(self.features):
            feature_data = record.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = df.drop([self.parent.config.predict.NAME], 1)
        self.logger.debug("Number of input records: {}".format(len(xdata)))
        if self.parent.config.convert_to_vw:
            xdata = df_to_vw_format(
                xdata,
                vwcmd=self.parent.config.vwcmd,
                target=None,
                namespace=self.parent.config.namespace,
                importance=importance,
                tag=tag,
                base=base,
                task=self.parent.config.task,
                use_binary_label=self.parent.config.use_binary_label,
            )
        ydata = np.array(df[self.parent.config.predict.NAME])
        shape = [len(xdata)]
        # TODO support probabilites
        # if 'oaa' in self.parent.config.vwcmd and 'probabilities' in self.parent.config.vwcmd:
        #     shape.append(self.parent.config.vwcmd['oaa'])
        y_pred = np.empty(shape)
        for idx, x in enumerate(xdata):
            y_pred[idx] = self.clf.predict(x)

        if self.parent.config.task in ["regression"]:
            self.confidence = r2_score(ydata, y_pred)
        elif self.parent.config.task in ["classification"]:
            self.confidence = accuracy_score(ydata, y_pred)
        self.logger.debug("Model Accuracy: {}".format(self.confidence))
        return self.confidence

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before prediction.")
        importance, tag, base, class_cost = None, None, None, None
        if self.parent.config.importance:
            importance = self.parent.config.importance.NAME

        if self.parent.config.tag:
            tag = self.parent.config.tag.NAME

        if self.parent.config.base:
            base = self.parent.config.base.NAME
        async for record in records:
            feature_data = record.features(self.features)
            data = pd.DataFrame(feature_data, index=[0])
            if self.parent.config.convert_to_vw:
                data = df_to_vw_format(
                    data,
                    vwcmd=self.parent.config.vwcmd,
                    target=None,
                    namespace=self.parent.config.namespace,
                    importance=importance,
                    tag=tag,
                    base=base,
                    task=self.parent.config.task,
                    use_binary_label=self.parent.config.use_binary_label,
                )
            prediction = self.clf.predict(data[0])
            self.logger.debug(
                "Predicted Value of {} for {}: {}".format(
                    self.parent.config.predict.NAME, data, prediction,
                )
            )
            target = self.parent.config.predict.NAME
            record.predicted(target, prediction, self.confidence)
            yield record


@entrypoint("vwmodel")
class VWModel(Model):
    CONTEXT = VWContext
    CONFIG = VWConfig

    def __init__(self, config) -> None:
        super().__init__(config)
        self.saved = {}

    def _filename(self):
        return os.path.join(
            self.config.directory,
            hashlib.sha384(self.config.predict.NAME.encode()).hexdigest()
            + ".json",
        )

    async def __aenter__(self) -> "VWModel":
        path = Path(self._filename())
        if path.is_file():
            self.saved = json.loads(path.read_text())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        Path(self._filename()).write_text(json.dumps(self.saved))
