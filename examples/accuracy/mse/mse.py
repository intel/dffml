from dffml import Features, Feature, SLRModel
from dffml.noasync import score, train
from dffml.accuracy import MeanSquaredErrorAccuracy

model = SLRModel(
    features=Features(Feature("f1", float, 1)),
    predict=Feature("ans", int, 1),
    location="tempdir",
)

# Train the model
train(model, "dataset.csv")

# Choose the accuracy plugin
mse_accuracy = MeanSquaredErrorAccuracy()

# Assess accuracy (alternate way of specifying data source)
print(
    "Accuracy:",
    score(model, mse_accuracy, Feature("ans", int, 1), "dataset.csv"),
)
