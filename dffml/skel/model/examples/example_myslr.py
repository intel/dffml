from dffml import Feature, Features
from dffml.noasync import train, score, predict
from dffml.accuracy import MeanSquaredErrorAccuracy

from REPLACE_IMPORT_PACKAGE_NAME.myslr import MySLRModel

model = MySLRModel(
    features=Features(Feature("x", float, 1)),
    predict=Feature("y", int, 1),
    location="tempdir",
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
scorer = MeanSquaredErrorAccuracy()
print("Accuracy:", score(model, scorer, Feature("y", int, 1), "test.csv"))

# Make prediction
for i, features, prediction in predict(model, "predict.csv"):
    features["y"] = prediction["y"]["value"]
    print(features)
