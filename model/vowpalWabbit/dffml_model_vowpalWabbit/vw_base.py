# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Base class for VW models
"""
import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict, namedtuple
from typing import (
    AsyncIterator,
    Tuple,
    Any,
    NamedTuple,
    List,
    Dict,
    DefaultDict,
)

import numpy as np
import pandas as pd
from vowpalwabbit import pyvw
from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score, r2_score

from dffml.repo import Repo
from dffml.accuracy import Accuracy
from dffml.source.source import Sources
from dffml.util.entrypoint import entrypoint
from dffml.base import BaseConfig, config, field
from dffml.feature.feature import Features, Feature
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained

from .util.data import df_to_vw_format


class InputError(Exception):
    pass


# TODO override input, and output options
@config
class VWConfig:
    features: Features

    def applicable_features(self, features):
        usable = []
        for feature in features:
            usable.append(feature.NAME)
        return sorted(usable)

    predict: Feature = field("Feature to predict")
    namespace: List[str] = field(
        "Dict containing `namespace` for each feature used in conversion of input data to vowpal wabbit input format",
        default_factory=lambda: [],
    )
    importance: str = field(
        "Feature containing `importance` of each example, used in conversion of input data to vowpal wabbit input format",
        default=None,
    )
    base: str = field(
        "Feature containing `base` for each example, used for residual regression",
        default=None,
    )
    tag: str = field(
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
    # vwcmd: List[str] = field("Command Line Arguements as per vowpal wabbit convention", default_factory = lambda:["--l2", "0.01"])
    vwcmd: str = field(
        "Command Line Arguements as per vowpal wabbit convention",
        default="--loss_function logistic --link logistic --l2 0.04",
    )

    def __post_init__(self):
        self.vwcmd = " ".join(self.vwcmd.split()).split()
        if "--passes" in self.vwcmd:
            if "--bgfs" in self.vwcmd:
                self.passes = 1
            else:
                idx = self.vwcmd.index("--passes")
                self.passes = int(self.vwcmd[idx + 1])
                del self.vwcmd[idx + 1]
                del self.vwcmd[idx]
        else:
            self.passes = 1
        for arg in ["-d", "--data", "--daemon"]:
            if arg in self.vwcmd:
                raise InputError(
                    f"Passing data through {arg} option is not supported. Pass the input data using dffml sources."
                )
            # if not vwcmd[0].startswith('-'):
            #     raise InputError(f"Passing filename in vwcmd is not supported. Pass the input data using dffml sources.")
        # TODO handle --save_resume
        if "--examples" in self.vwcmd:
            raise InputError(
                "Currently dffml sources do not support reading specified number of rows."
            )
        namespace = dict()
        for nsinfo in self.namespace:
            ns, cols = nsinfo.split("_", 1)
            if ns in namespace.keys():
                namespace[ns].extend(cols.split("_"))
            else:
                namespace[ns] = cols.split("_")
        self.namespace = namespace


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

    def _feature_predict_hash(self):
        params = "".join(
            [
                "{}{}".format(k, v)
                for k, v in self.parent.config._asdict().items()
                if k not in ["directory", "features", "predict", "vwcmd"]
            ]
        )
        return hashlib.sha384(
            "".join([params] + self.features).encode()
        ).hexdigest()

    def applicable_features(self, features):
        usable = []
        for feature in features:
            usable.append(feature.NAME)
        return sorted(usable)

    def modify_config(self):
        idx = None
        vwcmd = self.parent.config.vwcmd
        direc = self.parent.config.directory
        # direct all output files to a single folder
        # unless full path for respective outputs is provided
        for arg in [
            "--final_regressor",
            "-f",
            "--raw_predictions",
            "-r",
            "--predictions",
            "-p",
            "--readable_model",
            "--invert_hash",
            "--audit_regressor",
            "--output_feature_regularizer_binary",
            "--output_feature_regularizer_text",
        ]:
            if arg in vwcmd:
                idx = vwcmd.index(arg)
                file_path = vwcmd[idx + 1]
                head, tail = os.path.split(file_path)
                if not head.strip():
                    vwcmd[idx + 1] = os.path.join(direc, tail)
        return vwcmd

    def _filename(self):
        return os.path.join(
            self.parent.config.directory, self._features_hash + ".vw"
        )

    def _load_model(self):
        arg_list = self.parent.config.vwcmd
        arg_str = " ".join(self.parent.config.vwcmd)
        for arg in ["--initial_regressor", "-i"]:
            if arg in arg_list:
                self.logger.info(
                f"Using model weights from {arg_list[arg_list.index(arg) + 1]}"
            )
            return pyvw.vw(arg_str)

        if os.path.isfile(self._filename()):
            arg_str = arg_str + f" --initial_regressor {self._filename()}"
            self.logger.info(f"Using model weights from {self._filename()}")
        return pyvw.vw(arg_str)

    def _save_model(self):
        _vwcmd = self.parent.config.vwcmd
        if "--final_regressor" in _vwcmd:
            self.logger.info(
                f"Saving model weights to {_vwcmd[_vwcmd.index('--final_regressor') + 1]}"
            )
        elif "-f" in self.parent.config.vwcmd:
            self.logger.info(
                f"Saving model weights to {_vwcmd[_vwcmd.index('-f') + 1]}"
            )
        else:
            self.logger.info(f"Saving model weights to {self._filename()}")
            self.clf.save(self._filename())
        return

    async def __aenter__(self):
        # TODO remove `vw` being passed in vwcmd
        self.parent.config.vwcmd = self.modify_config()
        self.clf = self._load_model()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def train(self, sources: Sources):
        data = []
        async for repo in sources.with_features(
            self.features + [self.parent.config.predict.NAME]
        ):
            feature_data = repo.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        vw_data = df_to_vw_format(
            df,
            target=self.parent.config.predict.NAME,
            namespace=self.parent.config.namespace,
            importance=self.parent.config.importance,
            tag=self.parent.config.tag,
            base=self.parent.config.base,
        )
        self.logger.info("Number of input repos: {}".format(len(vw_data)))
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
        async for repo in sources.with_features(self.features):
            feature_data = repo.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = df.drop([self.parent.config.predict.NAME], 1)
        self.logger.debug("Number of input repos: {}".format(len(xdata)))
        if self.parent.config.convert_to_vw:
            xdata = df_to_vw_format(
                xdata,
                target=None,
                namespace=self.parent.config.namespace,
                importance=self.parent.config.importance,
                tag=self.parent.config.tag,
                base=self.parent.config.base,
            )
        ydata = np.array(df[self.parent.config.predict.NAME])
        # shape = [num_samples]
        # if 'oaa' in self.params and 'probabilities' in self.params:
        #     shape.append(self.params['oaa'])
        # y = np.empty(shape)
        y_pred = np.empty([len(xdata)])
        for idx, x in enumerate(xdata):
            y_pred[idx] = self.clf.predict(x)
        # TODO VW doesn't have a scorer, need to build it
        self.confidence = r2_score(ydata, y_pred)
        self.logger.debug("Model Accuracy: {}".format(self.confidence))
        return self.confidence

    async def predict(
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before prediction.")
        async for repo in repos:
            feature_data = repo.features(self.features)
            data = pd.DataFrame(feature_data, index=[0])
            if self.parent.config.convert_to_vw:
                data = df_to_vw_format(
                    data,
                    target=None,
                    namespace=self.parent.config.namespace,
                    importance=self.parent.config.importance,
                    tag=self.parent.config.tag,
                    base=self.parent.config.base,
                )
            prediction = self.clf.predict(data[0])
            self.logger.debug(
                "Predicted Value of {} for {}: {}".format(
                    self.parent.config.predict.NAME, data, prediction,
                )
            )
            target = self.parent.config.predict.NAME
            repo.predicted(target, prediction, self.confidence)
            yield repo


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
