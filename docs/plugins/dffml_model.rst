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


tfdnnc
~~~~~~

*Core*

Implemented using Tensorflow's DNNClassifier. Models are saved under the
``directory`` in subdirectories named after the hash of their feature names.

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
      -features \
        def:SepalLength:float:1 \
        def:SepalWidth:float:1 \
        def:PetalLength:float:1 \
        def:PetalWidth:float:1 \
      -log debug
    ... lots of output ...
    $ dffml accuracy \
      -model tfdnnc \
      -model-classification classification \
      -model-classifications 0 1 2 \
      -model-clstype int \
      -sources iris=csv \
      -source-filename iris_test.csv \
      -features \
        def:SepalLength:float:1 \
        def:SepalWidth:float:1 \
        def:PetalLength:float:1 \
        def:PetalWidth:float:1 \
      -log critical
    0.99996233782
    $ dffml predict all \
      -model tfdnnc \
      -model-classification classification \
      -model-classifications 0 1 2 \
      -model-clstype int \
      -sources iris=csv \
      -source-filename iris_test.csv \
      -features \
        def:SepalLength:float:1 \
        def:SepalWidth:float:1 \
        def:PetalLength:float:1 \
        def:PetalWidth:float:1 \
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

- directory: String

  - default: /home/user/.cache/dffml/tensorflow
  - Directory where state should be saved

- steps: Integer

  - default: 3000
  - Number of steps to train the model

- epochs: Integer

  - default: 30
  - Number of iterations to pass over all repos in a source

- hidden: List of integers

  - default: [12, 40, 15]
  - List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer

- classification: String

  - Feature name holding classification value

- classifications: List of strings

  - Options for value of classification

- clstype: locate

  - default: <class 'str'>
  - Data type of classifications values (default: str)

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
        -features def:Years:int:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename dataset.csv \
        -source-readonly \
        -log debug
    $ dffml accuracy \
        -model scratchslr \
        -features def:Years:int:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename dataset.csv \
        -source-readonly \
        -log debug
    1.0
    $ echo -e 'Years,Salary\n6,0\n' | \
      dffml predict all \
        -model scratchslr \
        -features def:Years:int:1 \
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

- directory: String

  - default: /home/user/.cache/dffml/scratch
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

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
        -features FEATURE_DEFINITION \
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
        -features FEATURE_DEFINITION \
        -model-predict TO_PREDICT \
        -sources f=TESTING_DATA_SOURCE_TYPE \
        -source-filename TESTING_DATA_FILE_NAME \
        -source-readonly \
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \
        -model SCIKIT_MODEL_ENTRYPOINT \
        -features FEATURE_DEFINITION \
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
+----------------+-------------------------------+----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


**Usage Example:**

Example below uses LinearRegression Model on a small dataset.

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
        -model scikitlr \
        -features def:Years:int:1 \
        -model-predict Salary \
        -model-n_jobs 2 \
        -sources f=csv \
        -source-filename dataset.csv \
        -source-readonly \
        -log debug
    $ dffml accuracy \
        -model scikitlr \
        -features def:Years:int:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename dataset.csv \
        -source-readonly \
        -log debug
    1.0
    $ echo -e 'Years,Salary\n6,0\n' | \
        dffml predict all \
        -model scikitlr \
        -features def:Years:int:1 \
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

scikitadaboost
~~~~~~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- base_estimator: BaseConfigurable.parser_helper

  - default: None

- n_estimators: Integer

  - default: 50

- learning_rate: float

  - default: 1.0

- algorithm: String

  - default: SAMME.R

- random_state: BaseConfigurable.parser_helper

  - default: None

scikitdtc
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- criterion: String

  - default: gini

- splitter: String

  - default: best

- max_depth: BaseConfigurable.parser_helper

  - default: None

- min_samples_split: Integer

  - default: 2

- min_samples_leaf: Integer

  - default: 1

- min_weight_fraction_leaf: float

  - default: 0.0

- max_features: BaseConfigurable.parser_helper

  - default: None

- random_state: BaseConfigurable.parser_helper

  - default: None

- max_leaf_nodes: BaseConfigurable.parser_helper

  - default: None

- min_impurity_decrease: float

  - default: 0.0

- min_impurity_split: BaseConfigurable.parser_helper

  - default: None

- class_weight: BaseConfigurable.parser_helper

  - default: None

- presort: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

scikitgnb
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- priors: BaseConfigurable.parser_helper

  - default: None

- var_smoothing: float

  - default: 1e-09

scikitgpc
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- kernel: BaseConfigurable.parser_helper

  - default: None

- optimizer: String

  - default: fmin_l_bfgs_b

- n_restarts_optimizer: Integer

  - default: 0

- max_iter_predict: Integer

  - default: 100

- warm_start: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- copy_X_train: BaseConfigurable.type_for.<locals>.<lambda>

  - default: True

- random_state: BaseConfigurable.parser_helper

  - default: None

- multi_class: String

  - default: one_vs_rest

- n_jobs: BaseConfigurable.parser_helper

  - default: None

scikitknn
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- n_neighbors: Integer

  - default: 5

- weights: String

  - default: uniform

- algorithm: String

  - default: auto

- leaf_size: Integer

  - default: 30

- p: Integer

  - default: 2

- metric: String

  - default: minkowski

- metric_params: BaseConfigurable.parser_helper

  - default: None

- n_jobs: BaseConfigurable.parser_helper

  - default: None

- kwargs: type

  - default: <class 'dffml_model_scikit.scikit_models.NoDefaultValue'>

scikitlr
~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- fit_intercept: BaseConfigurable.type_for.<locals>.<lambda>

  - default: True

- normalize: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- copy_X: BaseConfigurable.type_for.<locals>.<lambda>

  - default: True

- n_jobs: BaseConfigurable.parser_helper

  - default: None

scikitmlp
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- hidden_layer_sizes: tuple

  - default: (100,)

- activation: String

  - default: relu

- solver: String

  - default: adam

- alpha: float

  - default: 0.0001

- batch_size: String

  - default: auto

- learning_rate: String

  - default: constant

- learning_rate_init: float

  - default: 0.001

- power_t: float

  - default: 0.5

- max_iter: Integer

  - default: 200

- shuffle: BaseConfigurable.type_for.<locals>.<lambda>

  - default: True

- random_state: BaseConfigurable.parser_helper

  - default: None

- tol: float

  - default: 0.0001

- verbose: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- warm_start: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- momentum: float

  - default: 0.9

- nesterovs_momentum: BaseConfigurable.type_for.<locals>.<lambda>

  - default: True

- early_stopping: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- validation_fraction: float

  - default: 0.1

- beta_1: float

  - default: 0.9

- beta_2: float

  - default: 0.999

- epsilon: float

  - default: 1e-08

- n_iter_no_change: Integer

  - default: 10

scikitqda
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- priors: BaseConfigurable.parser_helper

  - default: None

- reg_param: float

  - default: 0.0

- store_covariance: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- tol: float

  - default: 0.0001

scikitrfc
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- n_estimators: String

  - default: warn

- criterion: String

  - default: gini

- max_depth: BaseConfigurable.parser_helper

  - default: None

- min_samples_split: Integer

  - default: 2

- min_samples_leaf: Integer

  - default: 1

- min_weight_fraction_leaf: float

  - default: 0.0

- max_features: String

  - default: auto

- max_leaf_nodes: BaseConfigurable.parser_helper

  - default: None

- min_impurity_decrease: float

  - default: 0.0

- min_impurity_split: BaseConfigurable.parser_helper

  - default: None

- bootstrap: BaseConfigurable.type_for.<locals>.<lambda>

  - default: True

- oob_score: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- n_jobs: BaseConfigurable.parser_helper

  - default: None

- random_state: BaseConfigurable.parser_helper

  - default: None

- verbose: Integer

  - default: 0

- warm_start: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- class_weight: BaseConfigurable.parser_helper

  - default: None

scikitsvc
~~~~~~~~~

*Core*

No description

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit-scikitlr
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted

- C: float

  - default: 1.0

- kernel: String

  - default: rbf

- degree: Integer

  - default: 3

- gamma: String

  - default: auto_deprecated

- coef0: float

  - default: 0.0

- shrinking: BaseConfigurable.type_for.<locals>.<lambda>

  - default: True

- probability: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- tol: float

  - default: 0.001

- cache_size: Integer

  - default: 200

- class_weight: BaseConfigurable.parser_helper

  - default: None

- verbose: BaseConfigurable.type_for.<locals>.<lambda>

  - default: False

- max_iter: Integer

  - default: -1

- decision_function_shape: String

  - default: ovr

- random_state: BaseConfigurable.parser_helper

  - default: None