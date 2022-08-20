Using DFFML's AutoML model
==============================

Automated Machine Learning, abbreiviated as AutoML, is a process that automates away the time-consuming and tedious 
aspects of ML, by encapsulating common ML models and techniques within a single API. It allows users to approach ML 
from a high-level persepctive, abstracting away the minutae of statistical modelling, democratizing ML for 
both data scientists and citizenry alike. On the other hand, AutoML also provides users with a degree of flexibility
in the form of being able to select their preferred models and tuners, which maximizes the likelihood of discovering an
effective model within the search space. In this tutorial, we will see how DFFML's AutoML model can be utilized to yield 
the most out of a dataset.

AutoML is extremely simple to use. Simply provide your dataset, a list of models to iterate over, and a hyperparmater 
tuning technique to optimize your models with. The AutoML model will iterate over all the models provided, saving the 
model with the best results in the user-specified directory.


.. code-block:: console
    :test:
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split


    from dffml.accuracy import ClassificationAccuracy
    from dffml.tuner.parameter_grid import ParameterGrid
    from dffml.model.automl import AutoMLModel

    iris = load_iris()
    y = iris["target"]
    X = iris["data"]
    trainX, testX, trainy, testy = train_test_split(
        X, y, test_size=0.1, random_state=123
    )
    scorer = ClassificationAccuracy()

    # Configure the model
    model = AutoMLModel(
        predict="target",
        features=["data"],
        location="tempDir",
        tuner = ParameterGrid(),
        scorer = scorer,
        models = ["xgbclassifier", "scikitsvc"],
        objective="max",
        parameters = {
            "xgbclassifier":  {
                    "learning_rate": [0.01, 0.05, 0.1],
                    "n_estimators": [20, 100, 200],
                     "max_depth": [3,5,8]
            },
            "scikitsvc": {
                "gamma": [0.001, 0.1],
                 "C": [1, 10]
            }
        }
    )

  
    # Train the model. Note this is different from most other
    # dffml models, where you have to provide both a train/test set.
    train(model, [
        [{"data": x, "target": y} for x, y in zip(trainX, trainy)],
        [{"data": x, "target": y} for x, y in zip(testX, testy)]
    ])

    # Assess accuracy
    
    print(
        "Test accuracy:",
        score(
            model,
            scorer,
            Feature("target", float, 1),
            *[{"data": x, "target": y} for x, y in zip(testX, testy)],
        ),
    )
    
    print(
        "Training accuracy:",
        score(
            model,
            scorer,
            Feature("target", float, 1),
            *[{"data": x, "target": y} for x, y in zip(trainX, trainy)],
        ),
    )


Command Line Usage
------------------

First, we download the Iris dataset to the desired folder.

.. code-block:: console
    $ wget http://download.tensorflow.org/data/iris_training.csv 
    $ wget http://download.tensorflow.org/data/iris_test.csv 
    $ sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' iris_training.csv iris_test.csv

We create a JSON file with the hyperparameter search space:

parameters.json
.. code-block:: console
    {
        "xgbclassifier":  {"learning_rate": [0.01, 0.05, 0.1],
                    "n_estimators": [20, 100, 200],
                     "max_depth": [3,5,8]},
        "scikitsvc": {"gamma": [0.001, 0.1], "C": [1, 10]}
    }

Now, train the model:

.. code-block:: console
    $ dffml train \
        -model automl \
        -model-features \
            SepalLength:float:1 \
            SepalWidth:float:1 \
            PetalLength:float:1 \
        -model-predict classification \
        -model-location tempDir \
        -model-tuner parameter_grid \
        -model-scorer clf \
        -model-models xgbclassifier scikitsvc \
        -model-parameters @parameters.json \
        -model-objective max \
        -sources train=csv \
            -source-train-filename iris_training.csv 


Make predictions with the model:
    dffml predict all \
        -model automl \
        -model-features \
        SepalLength:float:1 \
        SepalWidth:float:1 \
        PetalLength:float:1 \
        -model-predict classification \
        -model-location tempDir \
        -model-tuner parameter_grid \
        -model-scorer clf \
        -model-objective max \
        -sources test=csv \
        -source-test-filename iris_test.csv
