from dffml import Feature, Features
from dffml.noasync import accuracy, predict, train

from dffml_model_scratch.anomalydetection import AnomalyModel

# Configure the model

model = AnomalyModel(
    features=Features(Feature("A", int, 2),),
    predict=Feature("Y", int, 1),
    directory="model",
)


# Train the model
train(model, "trainex.csv")

# Assess accuracy for test set
print("Test set F1 score :", accuracy(model, "testex.csv"))

# Assess accuracy for training set
print("Training set F1 score :", accuracy(model, "trainex.csv"))
