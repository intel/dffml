Tuning a DFFML model with Bayesian Optimization
===============

For an introduction to hyperparameter tuning with the DFFML API, view the :ref:`parameter_grid` tutorial.

For this tutorial, we'll be performing hyperparameter tuning using a BayesOptGP tuner, which is somewhat different
from the typical grid search/random search variants. As per normal, we will be using XGBClassifier as our model to 
tune. 

Unlike grid search/random search, bayesian optimization is an intelligent hyperparameter selection process, 
where the hyperparameters selected in the next iteration are dependent on the results of the previous iteration. 
In the current iteration, the bayesian optimization process updates a surrogate model (which is a probability
distribution of scores | hypeparameters),  selects a set of hyperparameters to maximize expected improvement of the 
score based on this surrogate model, and repeats the process all over again. This allows one to efficiently search
the hyperparameter space, which is especially apt when the model to be tuned is expensive to evaluate. (For instance,
medium/large neural networks)

The BayesOptGP tuner uses the BayesianOptimization library, which utilizes gaussian processes as the surrogate model, 
hence the name of our tuner.


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
    from dffml_tuner_bayes_opt_gp.bayes_opt_gp import BayesOptGP
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
    tuner = BayesOptGP(
        parameters = {
            "learning_rate": [0.01, 0.1],
            "n_estimators": [20, 200],
            "max_depth": [3,8]

        },
        objective = "max",
        
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


Note that because of its different nature, our BayesOptGP tuner only accepts a specific structure for its hyperparameter search
space configuration. For each hyperparameter, we accept two values representing the minimum and maximum bounds of that 
hypeparameter which the tuner searches over. Also, Bayesian optimization only works on numerical hyperparameters (
technically it should only work on floats, but we made some modfiications so it works on discrete values). This is because 
the selection of the next set of hypeparameters derives from a closed-form integral which exepcts a continuous search space. 

Examples of non-legitimate hyperparameter configurations:

.. code-block:: console
    {
        "learning_rate": [0.01, 0.1, 0.2], // too many values
        "n_estimators": [20, 200],
        "max_depth": [3] // too few values

    }


.. code-block:: console
    {
        "learning_rate": [0.01, 0.1], 
        "sampling_method": ["uniform", "gradient_based"], //no strings
        "validate_parameters": [True, False] //no booleans

    }

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
        "learning_rate": [0.01, 0.1],
        "n_estimators": [20, 200],
        "max_depth": [3,8]
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
    -tuner bayes_opt_gp \
    -tuner-parameters @parameters.json \
    -tuner-objective max \
    -scorer clf \
    -sources train=csv test=csv \
    -source-train-filename iris_training.csv \
    -source-test-filename iris_test.csv \
    -source-train-tag train \
    -source-test-tag test \
    -features classification:int:1