# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Base class for Scikit models
"""
import json
import pathlib
import logging
import importlib

from typing import AsyncIterator, Tuple, Any, NamedTuple, Union

from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor

# https://intelpython.github.io/daal4py/sklearn.html
try:
    # HACK Fix for daal4py not maintaining docstring of roc_auc_score
    import sklearn.metrics.ranking

    correct_doc = sklearn.metrics.ranking.roc_auc_score.__doc__

    import daal4py.sklearn

    daal4py.sklearn.patch_sklearn()

    # HACK Fix for daal4py not maintaining docstring of roc_auc_score
    import daal4py.sklearn.metrics._ranking

    daal4py.sklearn.metrics._ranking._daal_roc_auc_score.__doc__ = correct_doc
except ImportError:
    # Ignore import errors, package is not installed
    pass
except Exception as error:
    LOGGER = logging.getLogger(__package__)
    LOGGER.error(error)

from dffml.record import Record
from dffml.model.accuracy import Accuracy
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained
from dffml.feature.feature import Features, Feature
from dffml.util.crypto import secure_hash


class NoMultiOutputSupport(Exception):
    pass


class ScikitConfig(ModelConfig, NamedTuple):
    location: pathlib.Path
    predict: Union[Feature, Features]
    features: Features


class Scikit(Model):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.saved = {}
        self.clf = None
        self.joblib = importlib.import_module("joblib")

    @property
    def _filepath(self):
        return (
            self.config.location
            if not hasattr(self, "temp_dir")
            else self.temp_dir
        )

    async def __aenter__(self) -> "Scikit":
        await super().__aenter__()
        self.saved_filepath = self._filepath / "Scikit.json"
        if self.saved_filepath.is_file():
            self.saved = json.loads(self.saved_filepath.read_text())
        self.clf_path = self._filepath / "ScikitFeatures.joblib"
        if self.clf_path.is_file():
            self.clf = self.joblib.load(str(self.clf_path))
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.saved_filepath.write_text(json.dumps(self.saved))
        if self.clf:
            self.joblib.dump(self.clf, str(self.clf_path))
        await super().__aexit__(exc_type, exc_value, traceback)


class ScikitUnsprvised(Scikit):
    async def __aenter__(self) -> "Scikit":
        await super().__aenter__()
        self.saved_filepath = self._filepath / "Scikit.json"
        if self.saved_filepath.is_file():
            self.saved = json.loads(self.saved_filepath.read_text())
        self.clf_path = self._filepath / "ScikitUnsupervised.json"
        if self.clf_path.is_file():
            self.clf = self.joblib.load(str(self.clf_path))

        return self


class ScikitContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.np = importlib.import_module("numpy")
        self.features = self.parent.config.features.names()
        self.is_multi = isinstance(self.parent.config.predict, Features)
        self.predictions = (
            self.parent.config.predict.names()
            if self.is_multi
            else self.parent.config.predict.name
        )
        self._features_hash = self._feature_predict_hash()

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
                if k not in ["features", "predict"]
            ]
        )
        return secure_hash(
            "".join([params] + self.features), algorithm="sha384"
        )

    async def __aenter__(self):
        if self.parent.clf is None:
            config = self.parent.config._asdict()
            del config["location"]
            del config["predict"]
            del config["features"]
            self.parent.clf = self.parent.SCIKIT_MODEL(**config)
        self.estimator_type = self.parent.clf._estimator_type
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def train(self, sources: Sources):
        xdata = []
        ydata = []
        ### np.hstack helps flatten the lists wihtout splitting strings.
        async for record in sources.with_features(
            list(self.np.hstack(self.features + [self.predictions]))
        ):
            feature_data = []
            predict_data = []
            for feature in record.features(self.features).values():
                feature_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            xdata.append(feature_data)
            if self.is_multi:
                for feature in record.features(self.predictions).values():
                    predict_data.extend(
                        [feature] if self.np.isscalar(feature) else feature
                    )
            else:
                predict_data = record.feature(self.predictions)
            ydata.append(predict_data)
        xdata = self.np.array(xdata)
        ydata = self.np.array(ydata)
        self.logger.info("Number of input records: {}".format(len(xdata)))
        if (
            self.is_multi
            and "MultiOutput" not in self.parent.clf.__class__.__name__
        ):
            if self.estimator_type == "regressor":
                self.parent.clf = MultiOutputRegressor(self.parent.clf)
            elif self.estimator_type == "classifier":
                self.parent.clf = MultiOutputClassifier(self.parent.clf)
            else:
                raise NoMultiOutputSupport(
                    "Model does not support multi-output. Please refer the docs to find a suitable model entrypoint."
                )
        self.parent.clf.fit(xdata, ydata)

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not self.parent.clf_path.is_file():
            raise ModelNotTrained("Train model before prediction.")
        async for record in sources.with_features(self.features):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            to_predict = self.np.array([record_data])
            self.logger.debug(
                "Predicted Value of {} for {}: {}".format(
                    self.parent.config.predict,
                    to_predict,
                    self.parent.clf.predict(to_predict),
                )
            )
            target = self.predictions
            if self.is_multi:
                for t in range(len(target)):
                    record.predicted(
                        target[t],
                        self.parent.clf.predict(to_predict)[0][t],
                        self.confidence,
                    )
            else:
                record.predicted(
                    target,
                    self.parent.config.predict.dtype(
                        self.parent.clf.predict(to_predict)[0]
                    )
                    if self.parent.config.predict.dtype is not str
                    else self.parent.clf.predict(to_predict)[0],
                    self.confidence,
                )
            yield record


class ScikitContextUnsprvised(ScikitContext):
    async def __aenter__(self):
        if self.parent.clf is None:
            config = self.parent.config._asdict()
            del config["location"]
            del config["features"]
            del config["predict"]
            self.parent.clf = self.parent.SCIKIT_MODEL(**config)
        return self

    async def train(self, sources: Sources):
        xdata = []
        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features)
            xdata.append(list(feature_data.values()))
        xdata = self.np.array(xdata)
        self.logger.info("Number of input records: {}".format(len(xdata)))
        self.parent.clf.fit(xdata)

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not self.parent.clf_path.is_file():
            raise ModelNotTrained("Train model before prediction.")
        estimator_type = self.parent.clf._estimator_type
        if estimator_type == "clusterer":
            if hasattr(self.parent.clf, "predict"):
                # inductive clusterer
                predictor = self.parent.clf.predict
            else:
                # transductive clusterer
                self.logger.critical(
                    "Predict found transductive clusterer, ensure data being passed is training data"
                )

                def yield_labels():
                    for label in self.parent.clf.labels_.astype(self.np.int):
                        yield label

                labels = yield_labels()
                predictor = lambda predict: [next(labels)]
        else:
            raise NotImplementedError(
                f"Model is not a clusterer: {self.parent.clf._estimator_type}"
            )

        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features)
            predict = self.np.array([list(feature_data.values())])
            prediction = predictor(predict)
            self.logger.debug(
                "Predicted cluster for {}: {}".format(predict, prediction)
            )
            target = self.parent.config.predict.name
            record.predicted(
                target,
                self.parent.config.predict.dtype(prediction[0])
                if self.parent.config.predict.dtype is not str
                else prediction[0],
                self.confidence,
            )
            yield record
