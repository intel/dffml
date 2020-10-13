from dffml import Feature
from dffml.noasync import train, accuracy, predict
from myslr import MySLRModel

# Configure the model
model = MySLRModel(
    feature=Feature("Years", int, 1),
    predict=Feature("Salary", int, 1),
    directory="model",
)

# Train the model
train(model, "train.csv")

# Assess accuracy
print("Accuracy:", accuracy(model, "test.csv"))

# Make predictions
for i, features, prediction in predict(model, "predict.csv"):
    features["Salary"] = prediction["Salary"]["value"]
    print(features)
