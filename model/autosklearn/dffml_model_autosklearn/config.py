import pathlib

import autosklearn.estimators

from dffml import (
    Feature,
    Features,
    field,
    make_config_numpy,
)


AutoSklearnConfig = make_config_numpy(
    "AutoSklearnConfig",
    autosklearn.estimators.AutoSklearnEstimator.__init__,
    properties={
        "features": (Features, field("Features to train on")),
        "predict": (Feature, field("Label or the value to be predicted")),
        "location": (
            pathlib.Path,
            field("Location where state should be saved",),
        ),
    },
)
