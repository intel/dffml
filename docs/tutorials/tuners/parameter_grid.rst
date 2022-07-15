Tuning a DFFML model with ParameterGrid
===============

For this tutorial, we'll be performing hyperparameter tuning on a DFFML model using DFFML's integrated "tune" method. 
We will be using the XGBClassifier model and ParameterGrid tuner for this example, but note that these are 
interchangeale for any DFFML Model and Tuner respectively. 

As we know, a machine learning model yields accurate predictions to unseen data by fitting itself to the 
training dataset. However, different initial configurations to certain model parameters will affect the performance 
of the trained model. For instance, a neural network that is allowed to train for several epochs on a dataset
typically outperforms another that has only trained a single epoch. We call these parameters to be modified in
pre-training "hyperparameters", and it is normally the job of the ML engineer to try many different hyperparameter 
configuratons to find the best-performing model. 

This process can be automated using a hyperparameter tuning method, which tries a series of configurations on your 
behalf, and includes random search, grid search, bayesian optimization and more. Here, we will be using 
ParameterGrid, otherwise known as grid search, where the tuner tries all possible combinations of hyperparameters 
provided by the user, a selects the best model based on a given metric. We will be tuning for the XGBClassifier 
model based on a dictionary of values provied in a JSON file, and return the one with the highest accuracy on a 
holdout validation set. 

First, download the xgboost plugin for the DFFML library, which can be done via pip: 

.. code-block:: console
    :test:
    $ pip install -U dffml-model-xgboost

We can utilize DFFML's tune method either via the Python API. In the following code, we demonstrate its usage in a Python
file:

.. code-block:: console
    :test:
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split

    from dffml import Feature, Features
    from dffml.noasync import  tune
    from dffml.accuracy import ClassificationAccuracy
    from dffml.tuner.parameter_grid import ParameterGrid
    from dffml_model_xgboost.xgbclassifier import (
        XGBClassifierModel,
        XGBClassifierModelConfig,
    )

    iris = load_iris()
    y = iris["target"]
    X = iris["data"]
    trainX, testX, trainy, testy = train_test_split(
        X, y, test_size=0.1, random_state=123
    )

    # Configure the model
    model = XGBClassifierModel(
        XGBClassifierModelConfig(
            features=Features(Feature("data", float,)),
            predict=Feature("target", float, 1),
            location="model",
            max_depth=3,
            learning_rate=0.01,
            n_estimators=200,
            reg_lambda=1,
            reg_alpha=0,
            gamma=0,
            colsample_bytree=0,
            subsample=1,
        )
    )

    # Configure the tuner search space in a dictionary
    # All combinations will be tried, even if the parameter's
    # value has been set in the model.
    tuner = ParameterGrid(
        parameters = {
            "learning_rate": [0.01, 0.05, 0.1],
            "n_estimators": [20, 100, 200],
            "max_depth": [3,5,8]

        },
        objective = "max"
    )

    # Tune function saves the best model and returns its score
    print("Tuning accuracy:",
        tune(
            model,
            tuner,
            scorer,
            Feature("target", float, 1),
            [{"data": x, "target": y} for x, y in zip(trainX, trainy)],
            [{"data": x, "target": y} for x, y in zip(testX, testy)],

        )
    )

The tune function takes in 6 arguments: 

    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.

    tuner: Tuner
        Hyperparameter tuning method to use. See :doc:`/plugins/dffml_tuner` for
        tuner options.

    scorer: Scorer
        Method to evaluate the performance of the model, inheriting from AccuracyScorer
        class.

    predict_feature: Union[Features, Feature]
        A feature indicating the feature you wish to predict.

    train_ds : list
        Input data for training. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.
        
    valid_ds : list
        Validation data for testing. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.   

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
        "learning_rate": [0.01, 0.05, 0.1],
        "n_estimators": [20, 100, 200],
        "max_depth": [3,5,8]
    }

In the same folder, we perform the CLI tune command.

.. code-block:: console
    $ dffml tune \
    -model xgbclassifier \
    -model-features \
    SepalLength:float:1 \
    SepalWidth:float:1 \
    PetalLength:float:1 \
    -model-predict classification \
    -model-location tempDir \
    -tuner parameter_grid \
    -tuner-parameters @parameters.json \
    -tuner-objective max \
    -scorer clf \
    -sources train=csv test=csv \
    -source-train-filename iris_training.csv \
    -source-test-filename iris_test.csv \
    -source-train-tag train \
    -source-test-tag test \
    -features classification:int:1