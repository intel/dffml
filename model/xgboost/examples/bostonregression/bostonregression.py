from dffml import Feature, Features
from dffml.noasync import train, accuracy
from dffml_model_xgboost.xdgregressor import (
    XDGRegressorModel,
    XDGRegressorModelConfig,
)
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split

diabetes = load_diabetes()
y = diabetes["target"]
X = diabetes["data"]
trainX, testX, trainy, testy = train_test_split(
    X, y, test_size=0.2, random_state=123
)

# Configure the model
model = XDGRegressorModel(
    XDGRegressorModelConfig(
        features=Features(Feature("data", float, 13)),
        predict=Feature("target", float, 1),
        directory="model",
        max_depth=5,
        reg_lambda=200,
        reg_alpha=2,
        learning_rate=0.05,
        n_estimators=1000,
    )
)

# Train the model
train(model, *[{"data": x, "target": y} for x, y in zip(trainX, trainy)])

# Assess accuracy
print(
    "Test accuracy:",
    accuracy(model, *[{"data": x, "target": y} for x, y in zip(testX, testy)]),
)
print(
    "Training accuracy:",
    accuracy(
        model, *[{"data": x, "target": y} for x, y in zip(trainX, trainy)]
    ),
)
