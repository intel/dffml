from dffml import CSVSource, Features, Feature
from dffml.noasync import train, accuracy, predict
from dffml_model_daal4py.daal4pylr import DAAL4PyLRModel

model = DAAL4PyLRModel(
    features=Features(Feature("f1", float, 1)),
    predict=Feature("ans", int, 1),
    directory="tempdir",
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, CSVSource(filename="test.csv")))

# Make prediction
for i, features, prediction in predict(model, {"f1": 0.8, "ans": 0}):
    features["ans"] = prediction["ans"]["value"]
    print(features)
