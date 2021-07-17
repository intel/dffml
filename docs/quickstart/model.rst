Quickstart
==========

In this example we have employee data telling us the employee's years of
experience, our level of trust in them, their level of expertise, and their
salary. Our goal will be to predict what the salary of a new hire should be,
given their years of experience, our level of trust in them, and their level of
expertise.

The model we'll be using is a part of ``dffml-model-scikit``, which is
another separate Python package from DFFML which we can install via ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-scikit

We will be using scikit's linear regression model. Other available models can be
found on the :doc:`/plugins/dffml_model` plugin page.

Example Dataset
---------------

We'll be using the following simple dataset for this example.

+----------------------+------------+--------------+--------+
| Years of Experience  |  Expertise | Trust Factor | Salary |
+======================+============+==============+========+
|          0           |      1     |      0.1     |   10   |
+----------------------+------------+--------------+--------+
|          1           |      3     |      0.2     |   20   |
+----------------------+------------+--------------+--------+
|          2           |      5     |      0.3     |   30   |
+----------------------+------------+--------------+--------+
|          3           |      7     |      0.4     |   40   |
+----------------------+------------+--------------+--------+
|          4           |      9     |      0.5     |   50   |
+----------------------+------------+--------------+--------+
|          5           |     11     |      0.6     |   60   |
+----------------------+------------+--------------+--------+

Rows 0-3 will be used as the training data, and 4-5 will be used as the test
data. We'll be asking for a prediction of the salary for the following.

+----------------------+------------+--------------+
| Years of Experience  |  Expertise | Trust Factor |
+======================+============+==============+
|          6           |     13     |      0.7     |
+----------------------+------------+--------------+
|          7           |     15     |      0.8     |
+----------------------+------------+--------------+

Let's create the ``training.csv``, ``test.csv``, and ``predict.csv`` files.

.. literalinclude:: /../examples/quickstart/train_data.sh

.. literalinclude:: /../examples/quickstart/test_data.sh

.. literalinclude:: /../examples/quickstart/predict_data.sh

Command Line
------------

For each command, we specify which model we want to use, and what our data
sources are. A detailed explanation of all the command line flags follows.

First we train the model. Our data source is the ``training.csv`` file.

.. literalinclude:: /../examples/quickstart/train.sh

We then assess the models accuracy using the test data from ``test.csv``.

.. literalinclude:: /../examples/quickstart/accuracy.sh

The test and training data are very simple, so the model should report 100%
accuracy.

.. code-block::

    1.0

Finally, we ask the model to make a prediction for each row in the
``predict.csv`` file.

.. literalinclude:: /../examples/quickstart/predict.sh

DFFML outputs in JSON format since it's very common and makes it easy to use the
DFFML command line from other scripts or languages.

.. code-block:: json

    [
        {
            "extra": {},
            "features": {
                "Expertise": 13,
                "Trust": 0.7,
                "Years": 6
            },
            "key": "0",
            "last_updated": "2020-02-07T14:17:08Z",
            "prediction": {
                "Salary": {
                    "confidence": 1.0,
                    "value": 70.13972055888223
                }
            }
        },
        {
            "extra": {},
            "features": {
                "Expertise": 15,
                "Trust": 0.8,
                "Years": 7
            },
            "key": "1",
            "last_updated": "2020-02-07T14:17:08Z",
            "prediction": {
                "Salary": {
                    "confidence": 1.0,
                    "value": 80.15968063872255
                }
            }
        }
    ]

The ``"confidence"`` value is determined by the underlying model implementation.
The scikit linear regression model just reports whatever the accuracy was on the
test dataset as the confidence.

.. _quickstart_command_line_flags_explained:

Command Line Flags Explained
++++++++++++++++++++++++++++

- ``-model scikitlr``

  - Use the linear regression model from the ``dffml-model-scikit`` package.
    More options for the model to use can be found on the
    :doc:`/plugins/dffml_model` plugin page.

- ``-model-features Years:int:1 Expertise:int:1 Trust:float:1``

  - The features the model should use to learn from. We specify the following
    attributes about each feature.

    - Name as it will appear in our data source (the column header in the
      ``training.csv`` file).

    - Data type. Years and Expertise are whole number (integer values), so we
      say ``int``. Trust is a percentage, measured from 0.0 being 0% to 1.0
      being 100%. For numbers with decimal places in them we say ``float``.

    - Dimensions of data.

        - All our features are a single value, so we say ``1``.

        - If we had a feature which was ten values, maybe some kind of time
          series data, we'd say ``10``. If we had a feature which was a
          flattened 28 by 28 image we'd say ``784``.

- ``-model-predict Salary:int:1``

  - The feature the model is trying to learn how to predict. We specify the same
    details as we did with the features to learn from.

- ``-scorer mse``

  - Report the modules accuracy use the Mead Squared Error accuracy scorer.
    See the :doc:`/plugins/dffml_accuracy` plugin page for all accuracy scorers.

- ``-sources f=csv``

  - The data sources to use as training data for the model.

  - We can specify multiple sources here in the following fashion.

    - ``-sources one=csv two=csv three=json``

  - Sources are ``tagged``, which just means that since there can be multiple
    you need to specify a tag to reference the source by when configuring it. On
    the left side of the ``=`` we put the tag, on the right we put the plugin
    name of the source. We're using the source that reads ``.csv`` files, so we
    specify ``csv``. The list of sources can be found on the
    :doc:`/plugins/dffml_source` plugin page.

    - We specify ``f`` as the tag, we could've used anything, but ``f`` will do
      fine (``f`` was chosen because it's a file).

- ``-source-filename $stage.csv``

  - The filename to be used for the source. On the :doc:`/plugins/dffml_source`
    plugin page you can see all of the source plugins and their possible
    arguments.

  - With regards to ``tagged`` sources, we could have also specified the
    filename using ``-source-f-filename $stage.csv``, since we tagged it as
    ``f``. If you have multiple sources you need to specify the arguments to
    each this way.

Python
------

If we wanted to do everything within Python our file might look like this

.. literalinclude:: /../examples/quickstart.py

The ouput should be as follows

.. code-block::

    Accuracy: 1.0
    {'Years': 6, 'Expertise': 13, 'Trust': 0.7, 'Salary': 70.0}
    {'Years': 7, 'Expertise': 15, 'Trust': 0.8, 'Salary': 80.0}

Check out the plugin docs for :doc:`/plugins/dffml_model` for usage of other
models. The :doc:`API </api/high_level>` docs may also be useful.

Data Sources
------------

DFFML makes it easy to pull data from various sources. All we have to do is
supply the filenames in place of the data.

.. literalinclude:: /../examples/quickstart_filenames.py

Async
-----

You may have noticed we're importing from ``dffml.noasync``. If you're using
``asyncio`` then you can just import from ``dffml``.

.. literalinclude:: /../examples/quickstart_async.py

HTTP
----

We can also deploy our trained model behind an HTTP server.

First we need to install the HTTP service, which is the HTTP server which will
serve our model. See the :doc:`/plugins/service/http/index` docs for more
information on the HTTP service.

.. code-block:: console

    $ pip install -U dffml-service-http

We start the HTTP service and tell it that we want to make our model accessible
via the HTTP :ref:`plugin_service_http_api_model` API.

.. warning::
    You should be sure to read the :doc:`/plugins/service/http/security` docs!
    This example of running the HTTP API is insecure and is only used to help
    you get up and running.

.. literalinclude:: /../examples/quickstart/model_start_http.sh

We can then ask the HTTP service to make predictions, or do training or accuracy
assessment.

.. literalinclude:: /../examples/quickstart/model_curl_http.sh

You should see the following prediction

.. code-block:: json

    {
        "iterkey": null,
        "records": {
            "0": {
                "key": "0",
                "features": {
                    "Expertise": 17,
                    "Trust": 0.9,
                    "Years": 8
                },
                "prediction": {
                    "Salary": {
                        "confidence": 1.0,
                        "value": 90.00000000000001
                    }
                },
                "last_updated": "2020-04-14T20:07:11Z",
                "extra": {}
            }
        }
    }
