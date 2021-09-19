from dffml import CSVSource, Features, Feature
from dffml.noasync import train, score, predict
from dffml_model_tensorflow_hub.text_classifier import TextClassificationModel
from dffml_model_tensorflow_hub.text_classifier_accuracy import (
    TextClassifierAccuracy,
)

model = TextClassificationModel(
    features=Features(Feature("sentence", str, 1)),
    predict=Feature("sentiment", int, 1),
    classifications=[0, 1, 2],
    clstype=int,
    location="tempdir",
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
scorer = TextClassifierAccuracy()
print(
    "Accuracy:",
    score(
        model,
        scorer,
        Feature("sentiment", int, 1),
        CSVSource(filename="test.csv"),
    ),
)

# Make prediction
for i, features, prediction in predict(
    model, {"sentence": "This track is horrible"},
):
    features["sentiment"] = prediction["sentiment"]["value"]
    print(features)
