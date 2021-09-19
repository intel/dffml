from dffml import CSVSource, Features, Feature
from dffml.noasync import train, score, predict
from dffml_model_tensorflow.dnnr import DNNRegressionModel
from dffml.accuracy import MeanSquaredErrorAccuracy

model = DNNRegressionModel(
    features=Features(
        Feature("Feature1", float, 1), Feature("Feature2", float, 1)
    ),
    predict=Feature("TARGET", float, 1),
    epochs=300,
    steps=2000,
    hidden=[8, 16, 8],
    location="tempdir",
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
scorer = MeanSquaredErrorAccuracy()
print(
    "Accuracy:",
    score(
        model,
        scorer,
        Feature("TARGET", float, 1),
        CSVSource(filename="test.csv"),
    ),
)

# Make prediction
for i, features, prediction in predict(
    model, {"Feature1": 0.21, "Feature2": 0.18, "TARGET": 0.84}
):
    features["TARGET"] = prediction["TARGET"]["value"]
    print(features)
