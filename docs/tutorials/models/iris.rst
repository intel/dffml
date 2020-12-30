.. _model_tutorial_iris:

Use a Model
===========

For this tutorial we'll be using :doc:`/plugins/dffml_model` that exist within
DFFML.

We're going to create a TensorFlow classification model, we'll need to install
the ``dffml-model-tensorflow`` plugin.

.. code-block:: console
    :test:

    $ python -m pip install dffml-model-tensorflow

Iris Dataset
------------

We're going to train the model on the iris dataset. Let's download the training
and test files now.

The ``sha384sum`` commands are do ensure we downloaded the correct data.

.. code-block:: console
    :test:

    $ wget http://download.tensorflow.org/data/iris_training.csv
    --2020-10-16 15:19:54--  http://download.tensorflow.org/data/iris_training.csv
    200 OK
    Length: 2194 (2.1K) [text/csv]
    Saving to: ‘iris_training.csv’

    iris_training.csv                                 100%[==========================================================================================================>]   2.14K  --.-KB/s    in 0s

    2020-10-16 15:19:54 (111 MB/s) - ‘iris_training.csv’ saved [2194/2194]
    $ wget http://download.tensorflow.org/data/iris_test.csv
    --2020-10-16 15:19:54--  http://download.tensorflow.org/data/iris_test.csv
    200 OK
    Length: 573 [text/csv]
    Saving to: ‘iris_test.csv’

    iris_test.csv                                     100%[==========================================================================================================>]    573   --.-KB/s    in 0s

    2020-10-16 15:19:54 (71.4 MB/s) - ‘iris_test.csv’ saved [573/573]
    $ echo '376c8ea3b7f85caff195b4abe62f34e8f4e7aece8bd087bbd746518a9d1fd60ae3b4274479f88ab0aa5c839460d535ef iris_training.csv' | sha384sum -c -
    iris_training.csv: OK
    $ echo '8c2cda42ce5ce6f977d17d668b1c98a45bfe320175f33e97293c62ab543b3439eab934d8e11b1208de1e4a9eb1957714 iris_test.csv' | sha384sum -c -
    iris_test.csv: OK
    $ sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' iris_training.csv iris_test.csv

Python Usage
------------

We can create a Tensorflow classification model from Python code as follows.

This example makes use of ``dffml.noasync`` which contains versions of
``train``, ``accuracy``, and ``predict`` which we don't have to be in an
``async`` function to call.

We use **iris_training.csv** to train the model, **iris_test.csv** to assess
it's accuracy, then we ask the models for predictions on two new records from
neither dataset.

**run.py**

.. literalinclude:: /../model/tensorflow/examples/tfdnnc/tfdnnc.py
    :test:
    :filepath: run.py

Run it to train the model

.. code-block:: console
    :test:

    $ python3 run.py
    Accuracy: 0.9666666388511658
    {'PetalLength': 4.2, 'PetalWidth': 1.5, 'SepalLength': 5.9, 'SepalWidth': 3.0, 'classification': 1}
    {'PetalLength': 5.4, 'PetalWidth': 2.1, 'SepalLength': 6.9, 'SepalWidth': 3.1, 'classification': 2}

Command Line Usage
------------------

Reference the
:ref:`TensorFlow Classifier <plugin_model_dffml_model_tensorflow_tfdnnc>` on
the Model plugins page for CLI usage examples.
