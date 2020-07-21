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

# Choose the accuracy plugin
mse_accuracy = MeanSquaredErrorAccuracy()

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, mse_accuracy, "dataset.csv"))
