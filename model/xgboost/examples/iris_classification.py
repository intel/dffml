from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from dffml import Feature, Features
from dffml.noasync import train, score, tune
from dffml.accuracy import ClassificationAccuracy
from dffml.tuner.parameter_grid import ParameterGrid
from dffml_model_xgboost.xgbclassifier import (
    XGBClassifierModel,
    XGBClassifierModelConfig,
)

iris = load_iris()
y = iris["target"]
X = iris["data"]
trainX, testX, trainy, testy = train_test_split(
    X, y, test_size=0.1, random_state=123
)

# Configure the model
model = XGBClassifierModel(
    XGBClassifierModelConfig(
        features=Features(Feature("data", float,)),
        predict=Feature("target", float, 1),
        location="model",
        max_depth=3,
        learning_rate=0.01,
        n_estimators=200,
        reg_lambda=1,
        reg_alpha=0,
        gamma=0,
        colsample_bytree=0,
        subsample=1,
    )
)

tuner = ParameterGrid(
    parameters = {
        "learning_rate": [0.01, 0.05, 0.1],
        "n_estimators": [20, 100, 200],
        "max_depth": [3,5,8]

    },
    objective = "max"
)

# Train the model
train(model, *[{"data": x, "target": y} for x, y in zip(trainX, trainy)])

# Assess accuracy
scorer = ClassificationAccuracy()
print(
    "Test accuracy:",
    score(
        model,
        scorer,
        Feature("target", float, 1),
        *[{"data": x, "target": y} for x, y in zip(testX, testy)],
    ),
)
print(
    "Training accuracy:",
    score(
        model,
        scorer,
        Feature("target", float, 1),
        *[{"data": x, "target": y} for x, y in zip(trainX, trainy)],
    ),
)
print("Tuning accuracy:",
    tune(
        model,
        tuner,
        scorer,
        Feature("target", float, 1),
        [{"data": x, "target": y} for x, y in zip(trainX, trainy)],
        [{"data": x, "target": y} for x, y in zip(testX, testy)],

    )
)
