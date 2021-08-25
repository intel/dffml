import abc
import inspect
import pathlib
import importlib
from dataclasses import dataclass
from typing import List, Dict, Any

from dffml.base import field
from dffml.feature.feature import Feature, Features
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelContext, Model, ModelNotTrained


@dataclass
class TensorflowBaseConfig:
    predict: Feature = field("Feature name holding target values")
    features: Features = field("Features to train on")
    location: pathlib.Path = field("Location where state should be saved")
    steps: int = field("Number of steps to train the model", default=3000)
    epochs: int = field(
        "Number of iterations to pass over all records in a source", default=30
    )
    hidden: List[int] = field(
        "List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer",
        default_factory=lambda: [12, 40, 15],
    )


class TensorflowModelContext(ModelContext):
    """
    Tensorflow based model contexts should derive from this model context. As it
    provides much of the bootstrapping such as mapping data types to feature
    columns.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.tf = importlib.import_module("tensorflow")
        self.np = importlib.import_module("numpy")

    async def predict_input_fn(self, sources: SourcesContext, **kwargs):
        """
        Uses the numpy input function with data from record features.
        """
        x_cols: Dict[str, Any] = {
            feature: [] for feature in self.parent.features
        }
        ret_records = []
        async for record in sources.with_features(self.parent.features):
            ret_records.append(record)
            for feature, results in record.features(
                self.parent.features
            ).items():
                x_cols[feature].append(self.np.array(results))
        for feature in x_cols:
            x_cols[feature] = self.np.array(x_cols[feature])
        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("-----------------------")
        input_fn = self.tf.compat.v1.estimator.inputs.numpy_input_fn(
            x_cols, shuffle=False, num_epochs=1, **kwargs
        )
        return input_fn, ret_records

    async def train(self, sources: Sources):
        """
        Train on data submitted via classify.
        """
        input_fn = await self.training_input_fn(sources)
        self.parent.model.train(
            input_fn=input_fn, steps=self.parent.config.steps
        )

    async def get_predictions(self, sources: SourcesContext):
        if not self.parent.base_path.exists():
            raise ModelNotTrained("Train model before prediction.")
        # Create the input function
        input_fn, predict = await self.predict_input_fn(sources)
        # Makes predictions on classifications
        predictions = self.parent.model.predict(input_fn=input_fn)
        target = self.parent.config.predict.name

        return predict, predictions, target


class TensorflowModel(Model):
    def __init__(self, config):
        super().__init__(config)
        self._model = None
        self.tf = importlib.import_module("tensorflow")
        self.feature_columns = self._feature_columns()
        self.features = self._applicable_features()

    def _feature_columns(self):
        """
        Converts records into training data
        """
        cols: Dict[str, Any] = {}
        for feature in self.config.features:
            col = self._feature_feature_column(feature)
            if not col is None:
                cols[feature.name] = col
        return cols

    def _feature_feature_column(self, feature: Feature):
        """
        Creates a feature column for a feature
        """
        dtype = feature.dtype
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
            return self.tf.feature_column.numeric_column(
                feature.name, shape=feature.length
            )
        self.logger.warning(
            "Unknown dtype %r. Cound not create column" % (dtype)
        )
        return None

    def _applicable_features(self):
        return [
            name
            for name in self.config.features.names()
            if name in self.feature_columns
        ]

    @property
    def base_path(self):
        return (
            self.config.location
            if not hasattr(self, "temp_dir")
            else self.temp_dir
        )

    @property
    def model_path(self):
        return self.base_path / "DNNModel"

    async def __aenter__(self):
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await super().__aexit__(exc_type, exc_value, traceback)

    @property
    @abc.abstractmethod
    def model(self):
        """
        Create the model and return the handle to it.
        """
        raise (NotImplementedError("Cannot use model from base class."))
