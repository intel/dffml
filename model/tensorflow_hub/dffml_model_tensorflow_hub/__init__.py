"""

from dffml import CSVSource, Features, DefFeature
from dffml.noasync import train, accuracy, predict
from dffml_model_tensorflow_hub.text_classifier import TextClassificationModel


model = TextClassificationModel(
    features=Features(DefFeature("Sentence", str, 1)),
    predict=DefFeature("Sentiment", int, 1),
    classifications=[0, 1, 2],
    clstype=int,
)

#train the model
train(
    model,
    {"Sentence": "I hate you!!", "Sentiment": 2},
    {"Sentence": "Okay , so what do we do now?", "Sentiment": 0},
    {"Sentence": "I find this dish incredibly tasty", "Sentiment": 1},
    {"Sentence": "This movie is horrible", "Sentiment": 2},
    {"Sentence": "You look beautiful", "Sentiment": 1},
    {
        "Sentence": "I think your project could use more collabaration",
        "Sentiment": 0,
    },
    {"Sentence": "I cannot see any effort put here", "Sentiment": 2},
    {"Sentence": "This is exactly what I wanted", "Sentiment": 1},
)

# Assess accuracy (alternate way of specifying data source)
print(
    accuracy(
        model,
        {"Sentence": "This is horrific", "Sentiment": 2},
        {"Sentence": "Its okay never mind", "Sentiment": 0},
        {"Sentence": "This time could not have been better", "Sentiment": 1},
    )
)

# Make prediction
for i, features, prediction in predict(
    model,
    {"Sentence": "This is horrific"},
    {"Sentence": "Its okay never mind"},
    {"Sentence": "This time could not have been better"},
):
    features["Sentiment"] = prediction["Sentiment"]["value"]
    print(features)
    
"""
