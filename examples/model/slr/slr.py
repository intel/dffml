from dffml import Features, Feature, SLRModel
from dffml.noasync import train, accuracy, predict
from dffml.accuracy import MeanSquaredErrorAccuracy

model = SLRModel(
    features=Features(Feature("f1", float, 1)),
    predict=Feature("ans", int, 1),
    directory="tempdir",
)

# Train the model
train(model, "dataset.csv")

# Assess accuracy (alternate way of specifying data source)
scorer = MeanSquaredErrorAccuracy()
print("Accuracy:", accuracy(model, scorer, "dataset.csv"))

# Make prediction
for i, features, prediction in predict(model, {"f1": 0.8, "ans": 0}):
    features["ans"] = prediction["ans"]["value"]
    print(features)
