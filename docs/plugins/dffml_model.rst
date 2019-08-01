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


scikitlr
~~~~~~~~

*Core*

Linear Regression Model implemented using scikit. Models are saved under the
``directory`` in subdirectories named after the hash of their feature names.

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
        -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename train.csv \
        -source-readonly \
        -log debug
    $ dffml accuracy \
        -model scikitlr \
        -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \
        -model-predict Salary \
        -sources f=csv \
        -source-filename test.csv \
        -source-readonly \
        -log debug
    1.0
    $ echo -e 'Years,Expertise,Trust\n6,13,1.4\n' | \
      dffml predict all \
        -model scikitlr \
        -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \
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
            "last_updated": "2019-07-31T08:40:59Z",
            "prediction": {
                "confidence": 1.0,
                "value": 70.0
            },
            "src_url": "0"
        }
    ]

**Args**

- directory: String

  - default: /home/user/.cache/dffml/scikit
  - Directory where state should be saved

- predict: String

  - Label or the value to be predicted