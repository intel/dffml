.. _plugin_models:

Models
======

Models are implementations of :class:`dffml.model.model.Model`, they
abstract the usage of machine learning models.

If you want to get started creating your own model, check out the
:ref:`model_tutorial`.

dffml_model_tensorflow
----------------------

.. code-block:: console

    pip install dffml-model-tensorflow


.. note::

    It's important to keep the hidden layer config and feature config the same
    across invocations of train, predict, and accuracy methods.

    Models are saved under the ``directory`` parameter in subdirectories named
    after the hash of their feature names and hidden layer config. Which means
    if any of those parameters change between invocations, it's being told to
    look for a different saved model.

tfdnnc
~~~~~~

*Core*

Implemented using Tensorflow's DNNClassifier.

.. code-block:: console

    $ wget http://download.tensorflow.org/data/iris_training.csv
    $ wget http://download.tensorflow.org/data/iris_test.csv
    $ head iris_training.csv
    $ sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
    $ head iris_training.csv
    $ dffml train \
        -model tfdnnc \
        -model-epochs 3000 \
        -model-steps 20000 \
        -model-classification classification \
        -model-classifications 0 1 2 \
        -model-clstype int \
        -sources iris=csv \
        -source-filename iris_training.csv \
        -model-features \
          SepalLength:float:1 \
          SepalWidth:float:1 \
          PetalLength:float:1 \
          PetalWidth:float:1 \
        -log debug
    ... lots of output ...
    $ dffml accuracy \
        -model tfdnnc \
        -model-classification classification \
        -model-classifications 0 1 2 \
        -model-clstype int \
        -sources iris=csv \
        -source-filename iris_test.csv \
        -model-features \
          SepalLength:float:1 \
          SepalWidth:float:1 \
          PetalLength:float:1 \
          PetalWidth:float:1 \
        -log critical
    0.99996233782
    $ dffml predict all \
        -model tfdnnc \
        -model-classification classification \
        -model-classifications 0 1 2 \
        -model-clstype int \
        -sources iris=csv \
        -source-filename iris_test.csv \
        -model-features \
          SepalLength:float:1 \
          SepalWidth:float:1 \
          PetalLength:float:1 \
          PetalWidth:float:1 \
        -caching \
        -log critical \
      > results.json
    $ head -n 33 results.json
    [
        {
            "extra": {},
            "features": {
                "PetalLength": 4.2,
                "PetalWidth": 1.5,
                "SepalLength": 5.9,
                "SepalWidth": 3.0,
                "classification": 1
            },
            "last_updated": "2019-07-31T02:00:12Z",
            "prediction": {
                "confidence": 0.9999997615814209,
                "value": 1
            },
            "src_url": "0"
        },
        {
            "extra": {},
            "features": {
                "PetalLength": 5.4,
                "PetalWidth": 2.1,
                "SepalLength": 6.9,
                "SepalWidth": 3.1,
                "classification": 2
            },
            "last_updated": "2019-07-31T02:00:12Z",
            "prediction": {
                "confidence": 0.9999984502792358,
                "value": 2
            },
            "src_url": "1"
        },

**Args**

- classification: String

  - Feature name holding classification value

- classifications: List of strings

  - Options for value of classification

- features: List of features

  - Features to train on

- clstype: Type

  - default: <class 'str'>
  - Data type of classifications values

- steps: Integer

  - default: 3000
  - Number of steps to train the model

- epochs: Integer

  - default: 30
  - Number of iterations to pass over all repos in a source

- directory: String

  - default: /home/user/.cache/dffml/tensorflow
  - Directory where state should be saved

- hidden: List of integers

  - default: [12, 40, 15]
  - List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer

tfdnnr
~~~~~~

*Core*

Implemented using Tensorflow's DNNEstimator.

Usage:

* predict: Name of the feature we are trying to predict or using for training.

Generating train and test data

* This creates files `train.csv` and `test.csv`,
  make sure to take a BACKUP of files with same name in the directory
  from where this command is run as it overwrites any existing files.

.. code-block:: console

    $ cat > train.csv << EOF
    Feature1,Feature2,TARGET
    0.93,0.68,3.89
    0.24,0.42,1.75
    0.36,0.68,2.75
    0.53,0.31,2.00
    0.29,0.25,1.32
    0.29,0.52,2.14
    EOF
    $ cat > test.csv << EOF
    Feature1,Feature2,TARGET
    0.57,0.84,3.65
    0.95,0.19,2.46
    0.23,0.15,0.93
    EOF
    $ dffml train \
        -model tfdnnr \
        -model-epochs 300 \
        -model-steps 2000 \
        -model-predict TARGET \
        -model-hidden 8 16 8 \
        -sources s=csv \
        -source-readonly \
        -source-filename train.csv \
        -model-features \
          Feature1:float:1 \
          Feature2:float:1 \
        -log debug
    Enabling debug log shows tensorflow losses...
    $ dffml accuracy \
        -model tfdnnr \
        -model-predict TARGET \
        -model-hidden 8 16 8 \
        -sources s=csv \
        -source-readonly \
        -source-filename test.csv \
        -model-features \
          Feature1:float:1 \
          Feature2:float:1 \
        -log critical
    0.9468210011
    $ echo -e 'Feature1,Feature2,TARGET\n0.21,0.18,0.84\n' | \
      dffml predict all \
        -model tfdnnr \
        -model-predict TARGET \
        -model-hidden 8 16 8 \
        -sources s=csv \
        -source-readonly \
        -source-filename /dev/stdin \
        -model-features \
          Feature1:float:1 \
          Feature2:float:1 \
        -log critical
    [
        {
            "extra": {},
            "features": {
                "Feature1": 0.21,
                "Feature2": 0.18,
                "TARGET": 0.84
            },
            "last_updated": "2019-10-24T15:26:41Z",
            "prediction": {
                "confidence": NaN,
                "value": 1.1983429193496704
            },
            "src_url": 0
        }
    ]

The ``NaN`` in ``confidence`` is the expected behaviour. (See TODO in
predict).

**Args**

- predict: String

  - Feature name holding target values

- features: List of features

  - Features to train on

- steps: Integer

  - default: 3000
  - Number of steps to train the model

- epochs: Integer

  - default: 30
  - Number of iterations to pass over all repos in a source

- directory: String

  - default: /home/user/.cache/dffml/tensorflow
  - Directory where state should be saved

- hidden: List of integers

  - default: [12, 40, 15]
  - List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer

dffml_model_scratch
-------------------

.. code-block:: console

    pip install dffml-model-scratch


scratchslr
~~~~~~~~~~

*Core*

Simple Linear Regression Model for 2 variables implemented from scratch.
Models are saved under the ``directory`` in subdirectories named after the
hash of their feature names.

.. code-block:: console

    $ cat > dataset.csv << EOF
    Years,Salary
    1,40
    2,50
    3,60
    4,70
    5,80
    EOF
    $ dffml train \
        -model scratchslr \
        -model-features Years:int:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename dataset.csv \
        -source-readonly \
        -log debug
    $ dffml accuracy \
        -model scratchslr \
        -model-features Years:int:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename dataset.csv \
        -source-readonly \
        -log debug
    1.0
    $ echo -e 'Years,Salary\n6,0\n' | \
      dffml predict all \
        -model scratchslr \
        -model-features Years:int:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename /dev/stdin \
        -source-readonly \
        -log debug
    [
        {
            "extra": {},
            "features": {
                "Salary": 0,
                "Years": 6
            },
            "last_updated": "2019-07-19T09:46:45Z",
            "prediction": {
                "confidence": 1.0,
                "value": 90.0
            },
            "src_url": "0"
        }
    ]

**Args**

- predict: String

  - Label or the value to be predicted

- features: List of features

  - Features to train on

- directory: String

  - default: /home/user/.cache/dffml/scratch
  - Directory where state should be saved

dffml_model_scikit
------------------

.. code-block:: console

    pip install dffml-model-scikit


Machine Learning models implemented with `scikit-learn <https://scikit-learn.org/stable/>`_.
Models are saved under the directory in subdirectories named after the hash of
their feature names.

**General Usage:**

Training:

.. code-block:: console

    $ dffml train \
        -model SCIKIT_MODEL_ENTRYPOINT \
        -model-features FEATURE_DEFINITION \
        -model-predict TO_PREDICT \
        -model-SCIKIT_PARAMETER_NAME SCIKIT_PARAMETER_VALUE \
        -sources f=TRAINING_DATA_SOURCE_TYPE \
        -source-filename TRAINING_DATA_FILE_NAME \
        -source-readonly \
        -log debug

Testing and Accuracy:

.. code-block:: console

    $ dffml accuracy \
        -model SCIKIT_MODEL_ENTRYPOINT \
        -model-features FEATURE_DEFINITION \
        -model-predict TO_PREDICT \
        -sources f=TESTING_DATA_SOURCE_TYPE \
        -source-filename TESTING_DATA_FILE_NAME \
        -source-readonly \
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \
        -model SCIKIT_MODEL_ENTRYPOINT \
        -model-features FEATURE_DEFINITION \
        -model-predict TO_PREDICT \
        -sources f=PREDICT_DATA_SOURCE_TYPE \
        -source-filename PREDICT_DATA_FILE_NAME \
        -source-readonly \
        -log debug


**Models Available:**

+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Type           | Model                         | Entrypoint     | Parameters                                                                                                                                                                                    |
+================+===============================+================+===============================================================================================================================================================================================+
| Regression     | LinearRegression              | scikitlr       | `scikitlr <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html#sklearn.linear_model.LinearRegression/>`_                                             |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | ElasticNet                    | scikiteln      | `scikiteln <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html#sklearn.linear_model.ElasticNet/>`_                                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | BayesianRidge                 | scikitbyr      | `scikitbyr <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.BayesianRidge.html#sklearn.linear_model.BayesianRidge/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | Lasso                         | scikitlas      | `scikitlas <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html#sklearn.linear_model.Lasso/>`_                                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | ARDRegression                 | scikitard      | `scikitard <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ARDRegression.html#sklearn.linear_model.ARDRegression/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | RANSACRegressor               | scikitrsc      | `scikitrsc <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RANSACRegressor.html#sklearn.linear_model.RANSACRegressor/>`_                                              |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | DecisionTreeRegressor         | scikitdtr      | `scikitdtr <https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html#sklearn.tree.DecisionTreeRegressor/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GaussianProcessRegressor      | scikitgpr      | `scikitgpr <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html#sklearn.gaussian_process.GaussianProcessRegressor/>`_                    |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | OrthogonalMatchingPursuit     | scikitomp      | `scikitomp <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.OrthogonalMatchingPursuit.html#sklearn.linear_model.OrthogonalMatchingPursuit/>`_                          |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | Lars                          | scikitlars     | `scikitlars <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lars.html#sklearn.linear_model.Lars/>`_                                                                   |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | Ridge                         | scikitridge    | `scikitridge <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html#sklearn.linear_model.Ridge/>`_                                                                |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Classification | KNeighborsClassifier          | scikitknn      | `scikitknn <https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html#sklearn.neighbors.KNeighborsClassifier/>`_                                          |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | AdaBoostClassifier            | scikitadaboost | `scikitadaboost <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html#sklearn.ensemble.AdaBoostClassifier/>`_                                           |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GaussianProcessClassifier     | scikitgpc      | `scikitgpc <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html#sklearn.gaussian_process.GaussianProcessClassifier/>`_                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | DecisionTreeClassifier        | scikitdtc      | `scikitdtc <https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier/>`_                                                |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | RandomForestClassifier        | scikitrfc      | `scikitrfc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier/>`_                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | QuadraticDiscriminantAnalysis | scikitqda      | `scikitqda <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis.html#sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis/>`_|
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | MLPClassifier                 | scikitmlp      | `scikitmlp <https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier/>`_                                              |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GaussianNB                    | scikitgnb      | `scikitgnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html#sklearn.naive_bayes.GaussianNB/>`_                                                          |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | SVC                           | scikitsvc      | `scikitsvc <https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC/>`_                                                                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | LogisticRegression            | scikitlor      | `scikitlor <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html#sklearn.linear_model.LogisticRegression/>`_                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | GradientBoostingClassifier    | scikitgbc      | `scikitgbc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html#sklearn.ensemble.GradientBoostingClassifier/>`_                                |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | BernoulliNB                   | scikitbnb      | `scikitbnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html#sklearn.naive_bayes.BernoulliNB/>`_                                                        |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | ExtraTreesClassifier          | scikitetc      | `scikitetc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html#sklearn.ensemble.ExtraTreesClassifier/>`_                                            |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | BaggingClassifier             | scikitbgc      | `scikitbgc <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.BaggingClassifier.html#sklearn.ensemble.BaggingClassifier/>`_                                                  |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | LinearDiscriminantAnalysis    | scikitlda      | `scikitlda <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html#sklearn.discriminant_analysis.LinearDiscriminantAnalysis/>`_      |
|                +-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                | MultinomialNB                 | scikitmnb      | `scikitmnb <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html#sklearn.naive_bayes.MultinomialNB/>`_                                                    |
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


**Usage Example:**

Example below uses LinearRegression Model on a small dataset.

Let us take a simple example:

+----------------------+------------+--------------+--------+
| Years of Experience  |  Expertise | Trust Factor | Salary |
+======================+============+==============+========+
|          0           |     01     |      0.2     |   10   |
+----------------------+------------+--------------+--------+
|          1           |     03     |      0.4     |   20   |
+----------------------+------------+--------------+--------+
|          2           |     05     |      0.6     |   30   |
+----------------------+------------+--------------+--------+
|          3           |     07     |      0.8     |   40   |
+----------------------+------------+--------------+--------+
|          4           |     09     |      1.0     |   50   |
+----------------------+------------+--------------+--------+
|          5           |     11     |      1.2     |   60   |
+----------------------+------------+--------------+--------+

.. code-block:: console

    $ cat > train.csv << EOF
    Years,Expertise,Trust,Salary
    0,1,0.2,10
    1,3,0.4,20
    2,5,0.6,30
    3,7,0.8,40
    EOF
    $ cat > test.csv << EOF
    Years,Expertise,Trust,Salary
    4,9,1.0,50
    5,11,1.2,60
    EOF
    $ dffml train \
        -model scikitlr \
        -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename train.csv \
        -source-readonly \
        -log debug
    $ dffml accuracy \
        -model scikitlr \
        -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename test.csv \
        -source-readonly \
        -log debug
    1.0
    $ echo -e 'Years,Expertise,Trust\n6,13,1.4\n' | \
      dffml predict all \
        -model scikitlr \
        -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename /dev/stdin \
        -source-readonly \
        -log debug
    [
        {
            "extra": {},
            "features": {
                "Expertise": 13,
                "Trust": 1.4,
                "Years": 6
            },
            "last_updated": "2019-09-18T19:04:18Z",
            "prediction": {
                "confidence": 1.0,
                "value": 70.00000000000001
            },
            "src_url": 0
        }
    ]

