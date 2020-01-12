from dffml.cli.ml import Train, Accuracy, PredictAll
from dffml.feature.feature import Features, DefFeature
from dffml.source.csv import CSVSource, CSVSourceConfig
from dffml_model_tensorflow.dnnr import (
    DNNRegressionModel,
    DNNRegressionModelConfig,
)

training_data = CSVSource(
    CSVSourceConfig(filename="training.csv", readwrite=False)
)
test_data = CSVSource(CSVSourceConfig(filename="test.csv", readwrite=False))
predict_data = CSVSource(
    CSVSourceConfig(filename="predict.csv", readwrite=False)
)

model = DNNRegressionModel(
    DNNRegressionModelConfig(
        features=Features(
            DefFeature("Years", int, 1),
            DefFeature("Expertise", int, 1),
            DefFeature("Trust", float, 1),
        ),
        predict=DefFeature("Salary", float, 1),
    )
)

Train(model=model, sources=[training_data])()

accuracy = Accuracy(model=model, sources=[test_data])()

row0, row1 = PredictAll(model=model, sources=[predict_data])()

print("Accuracy", accuracy)
print(row0)
print(row1)
