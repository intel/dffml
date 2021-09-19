from dffml import CSVSource, Features, Feature
from dffml.noasync import train, score, predict
from dffml_model_tensorflow.dnnc import DNNClassifierModel
from dffml.accuracy import ClassificationAccuracy

model = DNNClassifierModel(
    features=Features(
        Feature("SepalLength", float, 1),
        Feature("SepalWidth", float, 1),
        Feature("PetalLength", float, 1),
        Feature("PetalWidth", float, 1),
    ),
    predict=Feature("classification", int, 1),
    epochs=3000,
    steps=20000,
    classifications=[0, 1, 2],
    clstype=int,
    location="tempdir",
)

# Train the model
train(model, "iris_training.csv")

# Assess accuracy (alternate way of specifying data source)
scorer = ClassificationAccuracy()
print(
    "Accuracy:",
    score(
        model,
        scorer,
        Feature("classification", int, 1),
        CSVSource(filename="iris_test.csv"),
    ),
)

# Make prediction
for i, features, prediction in predict(
    model,
    {
        "PetalLength": 4.2,
        "PetalWidth": 1.5,
        "SepalLength": 5.9,
        "SepalWidth": 3.0,
    },
    {
        "PetalLength": 5.4,
        "PetalWidth": 2.1,
        "SepalLength": 6.9,
        "SepalWidth": 3.1,
    },
):
    features["classification"] = prediction["classification"]["value"]
    print(features)
