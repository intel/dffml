from dffml import Features, DefFeature, SLRModel
from dffml.noasync import train, accuracy, predict

model = SLRModel(
    features=Features(DefFeature("f1", float, 1)),
    predict=DefFeature("ans", int, 1),
)

# Train the model
train(model, "dataset.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, "dataset.csv"))

# Make prediction
for i, features, prediction in predict(model, {"f1": 0.8, "ans": 0}):
    features["ans"] = prediction["ans"]["value"]
    print(features)
