from dffml import Feature, Features
from dffml.noasync import accuracy, predict, train
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

from dffml_model_h2oautoml.h2oautoml import (
    H2oAutoMLModel,
    H2oAutoMLModelConfig,
)

boston = load_boston()
y = boston["target"]
X = boston["data"]
trainX, testX, trainy, testy = train_test_split(
    X, y, test_size=0.1, random_state=123
)

model = H2oAutoMLModel(
    H2oAutoMLModelConfig(
        features=Features(Feature("x", float, 1)),
        predict=Feature("y", int, 1),
        directory="tempdir",
        max_models=5,
        max_runtime_secs_per_model=30,
    )
)


# Train the model
train(model, *[{"x": x, "y": y} for x, y in zip(trainX, trainy)])

# Assess Test root mean squared error (RMSE)
print(
    "Test RMSE:",
    accuracy(model, *[{"x": x, "y": y} for x, y in zip(testX, testy)]),
)

# Assess Training root mean squared error (RMSE)
print(
    "Training RMSE:",
    accuracy(model, *[{"x": x, "y": y} for x, y in zip(trainX, trainy)]),
)
