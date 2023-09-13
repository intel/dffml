from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split

from dffml import Feature, Features
from dffml.noasync import train, score, tune
from dffml_model_xgboost.xgbregressor import (
    XGBRegressorModel,
    XGBRegressorModelConfig,
)
from dffml.tuner.parameter_grid import ParameterGrid
from dffml.accuracy import MeanSquaredErrorAccuracy


diabetes = load_diabetes()
y = diabetes["target"]
X = diabetes["data"]
trainX, testX, trainy, testy = train_test_split(
    X, y, test_size=0.1, random_state=123
)

# Configure the model
model = XGBRegressorModel(
    XGBRegressorModelConfig(
        features=Features(Feature("data", float, 10)),
        predict=Feature("target", float, 1),
        location="model",
        max_depth=3,
        learning_rate=0.05,
        n_estimators=400,
        reg_lambda=10,
        reg_alpha=0,
        gamma=10,
        colsample_bytree=0.3,
        subsample=0.8,
    )
)

tuner = ParameterGrid(
    parameters = {
        "learning_rate": [0.01, 0.05, 0.1],
        "n_estimators": [20, 100, 200],
        "max_depth": [3,5,8]

    },
    objective = "min"
)

# Train the model
train(model, *[{"data": x, "target": y} for x, y in zip(trainX, trainy)])

# Assess accuracy
scorer = MeanSquaredErrorAccuracy()
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

