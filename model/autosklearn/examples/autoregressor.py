from dffml import Features, Feature
from dffml.noasync import train, accuracy, predict
from dffml_model_autosklearn import AutoSklearnRegressorModel

model = AutoSklearnRegressorModel(
    features=Features(
        Feature("Feature1", float, 1), Feature("Feature2", float, 1),
    ),
    predict=Feature("TARGET", float, 1),
    directory="tempdir-python",
    time_left_for_this_task=120,
)


def main():
    # Train the model
    train(model, "train.csv")

    # Assess accuracy
    print("Accuracy:", accuracy(model, "test.csv"))

    # Make prediction
    for i, features, prediction in predict(model, "predict.csv"):
        features["TARGET"] = prediction["TARGET"]
        print(features)


if __name__ == "__main__":
    main()
