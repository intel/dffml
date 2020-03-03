from dffml import CSVSource, Features, DefFeature
from dffml.noasync import train, accuracy, predict
from dffml_model_tensorflow.dnnc import DNNClassifierModel

model = DNNClassifierModel(
    features=Features(
        DefFeature("SepalLength", float, 1),
        DefFeature("SepalWidth", float, 1),
        DefFeature("PetalLength", float, 1),
        DefFeature("PetalWidth", float, 1),
    ),
    predict=DefFeature("classification", int, 1),
    epochs=3000,
    steps=20000,
    classifications=[0, 1, 2],
    clstype=int,
)

# Train the model
train(model, "iris_training.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, CSVSource(filename="iris_test.csv")))

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
