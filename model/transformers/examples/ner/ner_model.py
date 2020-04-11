from dffml import CSVSource, DefFeature
from dffml.noasync import train, accuracy, predict
from dffml_model_transformers.ner.ner_model import NERModel

model = NERModel(
    sid=DefFeature("SentenceId", int, 1),
    words=DefFeature("Words", str, 1),
    predict=DefFeature("Tag", str, 1),
    model_architecture_type="distilbert",
    model_name_or_path="distilbert-base-cased",
    epochs=1,
    no_cuda=True,
)

# Train the model
train(model, "train.csv")

# Assess accuracy (alternate way of specifying data source)
print("Accuracy:", accuracy(model, CSVSource(filename="train.csv")))

# Make prediction
for i, features, prediction in predict(
    model,
    {"SentenceID": 1, "Words": "DFFML models can do NER"},
    {"SentenceID": 2, "Words": "DFFML models can do regression"},
):
    features["Tag"] = prediction["Tag"]["value"]
    print(features)
