import abc
import pathlib
from typing import Optional, AsyncIterator, List, Dict, Any

import pandas as pd
import joblib as joblib
import sklearn as sklearn

from dffml.base import config, field
from dffml.model.accuracy import Accuracy
from dffml import Feature, Features, Sources, Record
from dffml.model.model import ModelContext, ModelNotTrained


@config
class AutoSklearnConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features on which to train the model")
    directory: pathlib.Path = field("Directory where model should be saved")
    time_left_for_this_task: int = field(
        "Time limit in seconds for the search of appropriate models",
        default=3600,
    )
    per_run_time_limit: int = field(
        "Time limit for the single call to the machine learning model",
        default=360,
    )
    initial_configurations_via_metalearning: int = field(
        "Initialize the hyperparameter optimization algorithm with this many configurations which worked well on previously seen datasets",
        default=25,
    )
    ensemble_size: int = field(
        "Number of models added to the ensemble built by Ensemble selection from libraries of models. Models are drawn with replacement",
        default=50,
    )
    ensemble_nbest: int = field(
        "Only consider the ensemble_nbest models when building an ensemble",
        default=50,
    )
    max_models_on_disc: int = field(
        "Defines the maximum number of models that are kept in the disc",
        default=50,
    )
    ensemble_memory_limit: int = field(
        "Memory limit in MB for the ensemble building process", default=1024
    )
    seed: int = field(
        "Used to seed SMAC. Will determine the output file names", default=1
    )
    ml_memory_limit: int = field(
        "Memory limit in MB for the machine learning algorithm", default=3072
    )
    include_estimators: List[str] = field(
        "Specify the set of estimators to use", default=None
    )
    exclude_estimators: List[str] = field(
        "Specify the set of estimators not to use", default=None
    )
    include_preprocessors: List[str] = field(
        "Specify the set of preprocessors to use", default=None
    )
    exclude_preprocessors: List[str] = field(
        "Specify the set of preprocessors not to use", default=None
    )
    resampling_strategy: str = field(
        "How to to handle overfitting", default="holdout"
    )
    resampling_strategy_arguments: Dict[str, int] = field(
        "Additional arguments for resampling_strategy",
        default_factory=lambda: {"train_size default": 0.67},
    )
    tmp_folder: str = field(
        "Folder to store configuration output and log files", default=None
    )
    output_folder: str = field(
        "Folder to store predictions for optional test set", default=None
    )
    delete_tmp_folder_after_terminate: bool = field(
        "Remove tmp_folder, when finished", default=True
    )
    delete_output_folder_after_terminate: bool = field(
        "Remove output_folder, when finished", default=True
    )
    shared_mode: bool = field("Run smac in shared-model-node", default=False)
    n_jobs: Optional[int] = field(
        "The number of jobs to run in parallel for fit()", default=None
    )
    disable_evaluator_output: bool = field(
        "Disable model and prediction output", default=False
    )
    get_smac_object_callback: callable = field(
        "Callback function to create an object of class smac.optimizer.smbo.SMBO",
        default=None,
    )
    smac_scenario_args: Dict[str, str] = field(
        "Additional arguments inserted into the scenario of SMAC", default=None
    )
    logging_config: Dict[str, Any] = field(
        "dictionary object specifying the logger configuration", default=None
    )
    metadata_directory: str = field(
        "Path to the metadata directory", default=None
    )


class AutoSklearnModelContext(ModelContext):
    """
    Auto-Sklearn based model contexts should derive
    from this model context.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._model = None
        self.features = self._get_feature_names()
        self.path = self.filepath(
            self.parent.config.directory, "trained_model.sav"
        )
        self.load_model()

    def _get_feature_names(self):
        return [name for name in self.parent.config.features.names()]

    async def get_test_records(self, records: AsyncIterator[Record]):
        ret_record = []
        async for record in records:
            if not record.features(self.features):
                continue
            ret_record.append(record)
        return ret_record

    def filepath(self, directory, file):
        return directory / file

    def load_model(self):
        if self.path.is_file():
            self.model = joblib.load(self.path)

    async def get_predictions(self, data):
        return self.model.predict(data)

    async def get_probabilities(self, data):
        return self.model.predict_proba(data)

    async def train(self, sources: Sources):
        all_data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            all_data.append(record.features())
        df = pd.DataFrame(all_data)
        y_train = df[[self.parent.config.predict.name]]
        x_train = df.drop(columns=[self.parent.config.predict.name])
        self.model.fit(x_train, y_train)
        self.model.fit_ensemble(
            y_train, ensemble_size=self.parent.config.ensemble_size
        )
        joblib.dump(self.model, self.path)

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Record]:
        if not self.model:
            raise ModelNotTrained(
                "Train the model first before getting preictions"
            )
        test_records = await self.get_test_records(records)
        x_test = pd.DataFrame([record.features() for record in test_records])
        predictions = await self.get_predictions(x_test)
        probability = await self.get_probabilities(x_test)
        target = self.parent.config.predict.name
        for record, predict, prob in zip(
            test_records, predictions, probability
        ):
            record.predicted(target, predict, max(prob))
            yield record

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not self.model:
            raise ModelNotTrained("Train the model before assessing accuracy")
        test_data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            test_data.append(record.features())
        df = pd.DataFrame(test_data)
        y_test = df[[self.parent.config.predict.name]]
        x_test = df.drop(columns=[self.parent.config.predict.name])
        predictions = await self.get_predictions(x_test)
        accuracy = sklearn.metrics.accuracy_score(y_test, predictions)
        return Accuracy(accuracy)

    @property
    @abc.abstractmethod
    def model(self):
        """
        Create the model and return the handle to it.
        """
