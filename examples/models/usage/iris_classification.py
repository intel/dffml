import sys

from dffml import Feature, Features, Model, BaseSource
from dffml.noasync import train, accuracy

# Load the model
ClassificationModel = Model.load(sys.argv[-1])

# Configure the model
model = ClassificationModel(
    features=Features(
        Feature("PetalWidth", float, 1),
        Feature("SepalWidth", float, 1),
        Feature("SepalLength", float, 1),
        Feature("PetalLength", float, 1),
    ),
    predict=Feature("classification", float, 1),
    directory="model",
)

# Train the model
train(model, "iris_training.csv")

# Assess accuracy
print("Test accuracy:", accuracy(model, "iris_test.csv"))
