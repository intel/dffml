"""
Uses Tensorflow to create a generic DNN which learns on all of the features in a
repo.
"""
import os
import abc
import pydoc
import hashlib
import inspect
from dataclasses import dataclass
from typing import List, Dict, Any, AsyncIterator, Tuple, Optional, Type

import numpy as np
import tensorflow

from dffml.repo import Repo
from dffml.feature import Feature, Features
from dffml.source.source import Sources
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained
from dffml.accuracy import Accuracy
from dffml.util.entrypoint import entry_point
from dffml.base import BaseConfig
from dffml.util.cli.arg import Arg


class TensorflowModelContext(ModelContext):
    """
    Tensorflow based model contexts should derive from this model context. As it
    provides much of the bootstrapping such as mapping data types to feature
    columns.
    """

    def __init__(self, parent, features):
        super().__init__(parent, features)
        self._model = None
        self.feature_columns = self._feature_columns()
        self.all_features = self.features
        self.features = self._applicable_features()

    def _feature_columns(self):
        """
        Converts repos into training data
        """
        cols: Dict[str, Any] = {}
        for feature in self.features:
            col = self._feature_feature_column(feature)
            if not col is None:
                cols[feature.NAME] = col
        return cols

    def _feature_feature_column(self, feature: Feature):
        """
        Creates a feature column for a feature
        """
        dtype = feature.dtype()
        if not inspect.isclass(dtype):
            self.logger.warning(
                "Unknown dtype %r. Cound not create column" % (dtype)
            )
            return None
        if (
            dtype is int
            or issubclass(dtype, int)
            or dtype is float
            or issubclass(dtype, float)
        ):
            return tensorflow.feature_column.numeric_column(
                feature.NAME, shape=feature.length()
            )
        self.logger.warning(
            "Unknown dtype %r. Cound not create column" % (dtype)
        )
        return None

    def _applicable_features(self):
        return [
            name
            for name in self.features.names()
            if name in self.feature_columns
        ]

    def _model_dir_path(self):
        """
        Creates the path to the model dir by using the provided model dir and
        the sha384 hash of the concatenated feature names.
        """
        if self.parent.config.directory is None:
            return None
        _to_hash = self.features + list(map(str, self.parent.config.hidden))
        model = hashlib.sha384("".join(_to_hash).encode("utf-8")).hexdigest()
        if not os.path.isdir(self.parent.config.directory):
            raise NotADirectoryError(
                "%s is not a directory" % (self.parent.config.directory)
            )
        return os.path.join(self.parent.config.directory, model)

    async def predict_input_fn(self, repos: AsyncIterator[Repo], **kwargs):
        """
        Uses the numpy input function with data from repo features.
        """
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        ret_repos = []
        async for repo in repos:
            if not repo.features(self.features):
                continue
            ret_repos.append(repo)
            for feature, results in repo.features(self.features).items():
                x_cols[feature].append(np.array(results))
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])
        self.logger.info("------ Repo Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("-----------------------")
        input_fn = tensorflow.estimator.inputs.numpy_input_fn(
            x_cols, shuffle=False, num_epochs=1, **kwargs
        )
        return input_fn, ret_repos

    async def train(self, sources: Sources):
        """
        Train on data submitted via classify.
        """
        input_fn = await self.training_input_fn(
            sources,
            batch_size=20,
            shuffle=True,
            epochs=self.parent.config.epochs,
        )
        self.model.train(input_fn=input_fn, steps=self.parent.config.steps)

    @property
    @abc.abstractmethod
    def model(self):
        """
        Create the model and return the handle to it.
        """


@dataclass(init=True, eq=True)
class DNNClassifierModelConfig:
    directory: str
    steps: int
    epochs: int
    hidden: List[int]
    classification: str
    classifications: List[str]
    clstype: Type

    def __post_init__(self):
        self.classifications = list(map(self.clstype, self.classifications))


class DNNClassifierModelContext(TensorflowModelContext):
    """
    Model using tensorflow to make predictions. Handels creation of feature
    columns for real valued, string, and list of real valued features.
    """

    def __init__(self, features, parent) -> None:
        super().__init__(features, parent)
        self.cids = self._mkcids(self.parent.config.classifications)
        self.classifications = self._classifications(self.cids)
        self.model_dir_path = self._model_dir_path()

    @property
    def classification(self):
        return self.parent.config.classification

    def _mkcids(self, classifications):
        """
        Create an index, possible classification mapping and sort the list of
        classifications first.
        """
        cids = dict(
            zip(range(0, len(classifications)), sorted(classifications))
        )
        self.logger.debug("cids(%d): %r", len(cids), cids)
        return cids

    def _classifications(self, cids):
        """
        Map classifications to numeric values
        """
        classifications = {value: key for key, value in cids.items()}
        self.logger.debug(
            "classifications(%d): %r", len(classifications), classifications
        )
        return classifications

    @property
    def model(self):
        """
        Generates or loads a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug(
            "Loading model with classifications(%d): %r",
            len(self.classifications),
            self.classifications,
        )
        self._model = tensorflow.estimator.DNNClassifier(
            feature_columns=list(self.feature_columns.values()),
            hidden_units=self.parent.config.hidden,
            n_classes=len(self.parent.config.classifications),
            model_dir=self.model_dir_path,
        )
        return self._model

    async def training_input_fn(
        self,
        sources: Sources,
        batch_size=20,
        shuffle=False,
        epochs=1,
        **kwargs,
    ):
        """
        Uses the numpy input function with data from repo features.
        """
        self.logger.debug("Training on features: %r", self.features)
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []
        for repo in [
            repo
            async for repo in sources.with_features(
                self.features + [self.classification]
            )
            if repo.feature(self.classification) in self.classifications
        ]:
            for feature, results in repo.features(self.features).items():
                x_cols[feature].append(np.array(results))
            y_cols.append(
                self.classifications[repo.feature(self.classification)]
            )
        if not y_cols:
            raise ValueError("No repos to train on")
        y_cols = np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])
        self.logger.info("------ Repo Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        input_fn = tensorflow.estimator.inputs.numpy_input_fn(
            x_cols,
            y_cols,
            batch_size=batch_size,
            shuffle=shuffle,
            num_epochs=epochs,
            **kwargs,
        )
        return input_fn

    async def accuracy_input_fn(
        self,
        sources: Sources,
        batch_size=20,
        shuffle=False,
        epochs=1,
        **kwargs,
    ):
        """
        Uses the numpy input function with data from repo features.
        """
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []
        for repo in [
            repo
            async for repo in sources.with_features(
                self.features + [self.classification]
            )
            if repo.feature(self.classification) in self.classifications
        ]:
            for feature, results in repo.features(self.features).items():
                x_cols[feature].append(np.array(results))
            y_cols.append(
                self.classifications[repo.feature(self.classification)]
            )
        y_cols = np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])
        self.logger.info("------ Repo Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        input_fn = tensorflow.estimator.inputs.numpy_input_fn(
            x_cols,
            y_cols,
            batch_size=batch_size,
            shuffle=shuffle,
            num_epochs=epochs,
            **kwargs,
        )
        return input_fn

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        """
        if not os.path.isdir(self.model_dir_path):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        input_fn = await self.accuracy_input_fn(
            sources, batch_size=20, shuffle=False, epochs=1
        )
        accuracy_score = self.model.evaluate(input_fn=input_fn)
        return Accuracy(accuracy_score["accuracy"])

    async def predict(self, repos: AsyncIterator[Repo]) -> AsyncIterator[Repo]:
        """
        Uses trained data to make a prediction about the quality of a repo.
        """
        if not os.path.isdir(self.model_dir_path):
            raise ModelNotTrained("Train model before prediction.")
        # Create the input function
        input_fn, predict = await self.predict_input_fn(repos)
        # Makes predictions on classifications
        predictions = self.model.predict(input_fn=input_fn)
        for repo, pred_dict in zip(predict, predictions):
            class_id = pred_dict["class_ids"][0]
            probability = pred_dict["probabilities"][class_id]
            repo.predicted(self.cids[class_id], probability)
            yield repo


@entry_point("tfdnnc")
class DNNClassifierModel(Model):
    """
    Implemented using Tensorflow's DNNClassifier.

    .. code-block:: console

        $ wget http://download.tensorflow.org/data/iris_training.csv
        $ wget http://download.tensorflow.org/data/iris_test.csv
        $ head iris_training.csv
        $ sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
        $ head iris_training.csv
        $ dffml train \\
            -model tfdnnc \\
            -model-epochs 3000 \\
            -model-steps 20000 \\
            -model-classification classification \\
            -model-classifications 0 1 2 \\
            -model-clstype int \\
            -sources iris=csv \\
            -source-filename iris_training.csv \\
            -features \\
              def:SepalLength:float:1 \\
              def:SepalWidth:float:1 \\
              def:PetalLength:float:1 \\
              def:PetalWidth:float:1 \\
            -log debug
        ... lots of output ...
        $ dffml accuracy \\
            -model tfdnnc \\
            -model-classification classification \\
            -model-classifications 0 1 2 \\
            -model-clstype int \\
            -sources iris=csv \\
            -source-filename iris_test.csv \\
            -features \\
              def:SepalLength:float:1 \\
              def:SepalWidth:float:1 \\
              def:PetalLength:float:1 \\
              def:PetalWidth:float:1 \\
            -log critical
        0.99996233782
        $ dffml predict all \\
            -model tfdnnc \\
            -model-classification classification \\
            -model-classifications 0 1 2 \\
            -model-clstype int \\
            -sources iris=csv \\
            -source-filename iris_test.csv \\
            -features \\
              def:SepalLength:float:1 \\
              def:SepalWidth:float:1 \\
              def:PetalLength:float:1 \\
              def:PetalWidth:float:1 \\
            -caching \\
            -log critical \\
          > results.json
        $ head -n 33 results.json
        [
            {
                "extra": {},
                "features": {
                    "PetalLength": 4.2,
                    "PetalWidth": 1.5,
                    "SepalLength": 5.9,
                    "SepalWidth": 3.0,
                    "classification": 1
                },
                "last_updated": "2019-07-31T02:00:12Z",
                "prediction": {
                    "confidence": 0.9999997615814209,
                    "value": 1
                },
                "src_url": "0"
            },
            {
                "extra": {},
                "features": {
                    "PetalLength": 5.4,
                    "PetalWidth": 2.1,
                    "SepalLength": 6.9,
                    "SepalWidth": 3.1,
                    "classification": 2
                },
                "last_updated": "2019-07-31T02:00:12Z",
                "prediction": {
                    "confidence": 0.9999984502792358,
                    "value": 2
                },
                "src_url": "1"
            },

    """

    CONTEXT = DNNClassifierModelContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args,
            above,
            "directory",
            Arg(
                default=os.path.join(
                    os.path.expanduser("~"), ".cache", "dffml", "tensorflow"
                ),
                help="Directory where state should be saved",
            ),
        )
        cls.config_set(
            args,
            above,
            "steps",
            Arg(
                type=int,
                default=3000,
                help="Number of steps to train the model",
            ),
        )
        cls.config_set(
            args,
            above,
            "epochs",
            Arg(
                type=int,
                default=30,
                help="Number of iterations to pass over all repos in a source",
            ),
        )
        cls.config_set(
            args,
            above,
            "hidden",
            Arg(
                type=int,
                nargs="+",
                default=[12, 40, 15],
                help="List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer",
            ),
        )
        cls.config_set(
            args,
            above,
            "classification",
            Arg(help="Feature name holding classification value"),
        )
        cls.config_set(
            args,
            above,
            "classifications",
            Arg(nargs="+", help="Options for value of classification"),
        )
        cls.config_set(
            args,
            above,
            "clstype",
            Arg(
                type=pydoc.locate,
                default=str,
                help="Data type of classifications values (default: str)",
            ),
        )
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return DNNClassifierModelConfig(
            directory=cls.config_get(config, above, "directory"),
            steps=cls.config_get(config, above, "steps"),
            epochs=cls.config_get(config, above, "epochs"),
            hidden=cls.config_get(config, above, "hidden"),
            classification=cls.config_get(config, above, "classification"),
            classifications=cls.config_get(config, above, "classifications"),
            clstype=cls.config_get(config, above, "clstype"),
        )
