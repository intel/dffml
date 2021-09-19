from dffml import CSVSource, Features, Feature
from dffml.noasync import train, score, predict
from dffml_model_scikit import LinearRegressionModel
from dffml.accuracy import MeanSquaredErrorAccuracy

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
train(model, "training.csv")

# Assess accuracy (alternate way of specifying data source)
scorer = MeanSquaredErrorAccuracy()
print(
    "Accuracy:",
    score(
        model,
        scorer,
        Feature("Salary", int, 1),
        CSVSource(filename="test.csv"),
    ),
)

# Make prediction
for i, features, prediction in predict(
    model,
    {"Years": 6, "Expertise": 13, "Trust": 0.7},
    {"Years": 7, "Expertise": 15, "Trust": 0.8},
):
    features["Salary"] = prediction["Salary"]["value"]
    print(features)
