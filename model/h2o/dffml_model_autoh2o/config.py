import pathlib
from pathlib import Path
from typing import AsyncIterator, List
from dffml.base import config, field

from dffml import (
    Feature,
    Features,
    field,

)

@config
class AutoH2OConfig:
    features: Features
    predict: Feature = field("Feature to predict")
    location: Path = field("Location where state should be saved")
    #TO-DO: split into separate regression/classification models
    task: str = field(
        "Task to perform, possible values are `classification`, `regression`",
        default="regression",
    )
    max_runtime_secs: int = field(
        "The maximum time that the AutoML process will run", default=0
    )
    max_models: int = field(
        "Maximum number of models to build in AutoML run", default=10
    )
    nfolds: int = field(
        "Number of folds for k-fold cross-validation", default=5
    )
    balance_classes: bool = field(
        "Oversampling on minority classes should be performed or not",
        default=False,
    )
    max_after_balance_size: int = field(
        "Maximum relative size of training set after performing oversampling",
        default=5,
    )
    max_runtime_secs_per_model: int = field(
        "Maximum time to train individual model in AutoML", default=0
    )
    stopping_metric: str = field(
        "Metric used for stopping criteria", default="AUTO"
    )
    stopping_tolerance: float = field(
        "Specifies the relative tolerance for the metric-based stopping",
        default=0.001,
    )
    stopping_rounds: int = field(
        "Stop training when metric doesn't improve max of stopping_rounds",
        default=3,
    )
    sort_metric: str = field(
        "Metric used to sort the leaderboard", default="AUTO"
    )
    exclude_algos: List[str] = field(
        "Algorithm to skip during training", default=None
    )
    include_algos: List[str] = field(
        "Algorithm to be used during training", default=None
    )
    verbosity: str = field("Print the backend messages", default=None)
    show_leaderboard: bool = field(
        "Print the leaderboard after the building the models in AutoML",
        default=True,
    )
