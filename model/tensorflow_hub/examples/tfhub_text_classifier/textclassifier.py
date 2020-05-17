from dffml import CSVSource, Features, Feature
from dffml.noasync import train, accuracy, predict
from dffml_model_tensorflow_hub.text_classifier import TextClassificationModel

model = TextClassificationModel(
    features=Features(Feature("sentence", str, 1)),
    predict=Feature("sentiment", int, 1),
    classifications=[0, 1, 2],
    clstype=int,
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, CSVSource(filename="test.csv")))

# Make prediction
for i, features, prediction in predict(
    model, {"sentence": "This track is horrible"},
):
    features["sentiment"] = prediction["sentiment"]["value"]
    print(features)
