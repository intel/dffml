from dffml import Feature, Features
from dffml.noasync import train, accuracy, predict

from REPLACE_IMPORT_PACKAGE_NAME.myslr import MySLRModel

model = MySLRModel(
    features=Features(Feature("x", float, 1)),
    predict=Feature("y", int, 1),
    directory="tempdir",
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, "test.csv"))

# Make prediction
for i, features, prediction in predict(model, "predict.csv"):
    features["y"] = prediction["y"]["value"]
    print(features)
