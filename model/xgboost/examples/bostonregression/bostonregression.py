from dffml.feature.feature import Feature, Features
from dffml.noasync import train, accuracy, predict
from dffml_model_xgboost.xdgregressor import XDGRegressorModel
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

boston = load_boston()
y = boston["target"]
X = boston["data"]
trainX = X[: int(0.8 * len(X)), :]
testX = X[int(0.8 * len(X)) :, :]
trainy = y[: int(0.8 * len(y))]
testy = y[int(0.8 * len(y)) :]
trainX, textX, trainy, texty = train_test_split(
    X, y, test_size=0.2, random_state=123
)

# Configure the model
model = XDGRegressorModel(
    features=Features(Feature("data", float, 13)),
    predict=Feature("target", float, 1),
    directory="model",
    max_depth=8,
    reg_lambda=200,
    reg_alpha=2,
    learning_rate=0.05,
    n_estimators=2000,
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

