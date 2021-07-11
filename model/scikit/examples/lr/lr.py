from dffml import CSVSource, Features, Feature
from dffml.noasync import train, accuracy, predict
from dffml_model_scikit import LinearRegressionModel

model = LinearRegressionModel(
    features=Features(
        Feature("Years", int, 1),
        Feature("Expertise", int, 1),
        Feature("Trust", float, 1),
    ),
    predict=Feature("Salary", int, 1),
    location="tempdir",
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, CSVSource(filename="test.csv")))

# Make prediction
for i, features, prediction in predict(
    model,
    {"Years": 6, "Expertise": 13, "Trust": 0.7},
    {"Years": 7, "Expertise": 15, "Trust": 0.8},
):
    features["Salary"] = prediction["Salary"]["value"]
    print(features)
