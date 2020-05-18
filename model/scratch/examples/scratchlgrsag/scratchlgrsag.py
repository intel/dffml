from dffml import CSVSource, Features, Feature
from dffml.noasync import train, accuracy, predict
from dffml_model_scratch.logisticregression import LogisticRegression

model = LogisticRegression(
    features=Features(Feature("f1", float, 1)), predict=Feature("ans", int, 1)
)

# Train the model
train(model, "dataset.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, CSVSource(filename="dataset.csv")))

# Make prediction
for i, features, prediction in predict(model, {"f1": 0.8, "ans": 0}):
    features["ans"] = prediction["ans"]["value"]
    print(features)
