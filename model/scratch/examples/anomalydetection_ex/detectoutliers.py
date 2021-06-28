from dffml import Feature, Features
from dffml.noasync import accuracy, predict, train

from dffml_model_scratch.anomalydetection import AnomalyModel
from dffml_model_scratch.anomaly_detection_scorer import (
    AnomalyDetectionAccuracy,
)

# Configure the model

model = AnomalyModel(
    features=Features(Feature("A", int, 2),),
    predict=Feature("Y", int, 1),
    directory="model",
)


# Train the model
train(model, "trainex.csv")

# Assess accuracy for test set
scorer = AnomalyDetectionAccuracy()
print("Test set F1 score :", accuracy(model, scorer, "testex.csv"))

# Assess accuracy for training set
print("Training set F1 score :", accuracy(model, scorer, "trainex.csv"))
