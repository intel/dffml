.. _model_tutorial_slr:

Simple Model
============

For this tutorial we'll be implementing our own machine learning algorithm from
scratch, which means that we're not using a machine learning focused library to
handle calculations for us, we'll do it all ourselves.

Our model will preform Simple Linear Regression (SLR). Which means it finds the
best fit line for a dataset.

You may know the best fit line as ``y = m * x + b``

We'll be working the in a new file named **myslr.py**, open / create it now

Imports
-------

We're going to need a few modules from the standard library, let's import them.

- ``pathlib`` will be used to define the directory were saved model state should
  be stored.

- ``statistics`` will be used to help us calculate the average (mean) of our
  data.

- ``typing`` is for Python's static type hinting. It lets use give hints to our
  editor or IDE so they can help us check our code before we run it.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 1-3

We'll also need a few things from DFFML.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 5-15

Math
----

The first thing you'll want to do is add some functions which calculate the best
fit line and accuracy. These aren't important for understanding how DFFML works.
So we're going to skip over their logic in this tutorial. You can write your own
versions to find the best fit line for lists of X, and Y data if you want, or
you can copy these.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 18-50

Config
------

DFFML makes it so that we can use our models from the command line, HTTP API,
and of course, Python. This all works because we define a config class for each
model.

Anything that a user might want to tweak about a models behavior should go in
the ``Config`` class for the model. The naming convention is ``TheName`` +
``Model`` + ``Config``.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 53-57

Our model has three configurable properties.

- ``feature``. The feature within each
  :py:class:`Record <dffml.record.Record>` that our model should use as the X
  value for the regression line

- ``predict``. The name of the feature we want to predict. Within each
  :py:class:`Record <dffml.record.Record>` this will be the data that our model
  should use as the Y value for the regression line

- ``directory``. The location on disk where we'll save and load our model from

Class
-----

The naming conventions for classes in DFFML is ``TheName`` + ``PluginType``.
We're making a ``Model`` plugin. So the name is ``MySLRModel``.

The plugin system needs us to do two things to ensure we can access our new
model from the DFFML command line and other interfaces.

- We must use the ``entrypoint`` decorator passing it the name we want to
  reference the model by. For anything that allows for specifying multiple
  models, you can configure all models of the same type by using the string
  provided here.

- We must set the ``CONFIG`` attribute to the respective ``Config`` class.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 60-63

Train
-----

The train method should train the model. First we ask the data ``sources`` for
any ``records`` containing the features our model was told to use.
``with_features`` takes a list of feature names each record should contain. This
let's us avoid records that are not applicable to our model.

Models should save their state to disk after training. Classes derived from
``SimpleModel`` can put anything they want saved into ``self.storage``, which
is saved and loaded from a JSON file on disk.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 65-79

Accuracy
--------

We give testing data ``sources`` to the accuracy method to determine the
accuracy of a model. For ``MySLRModel``, we'll load the saved ``m`` and ``b``
values computed during training, and use them to calculate the coefficient of
determination which we'll be treating as the accuracy for this model.

We're storing ``m``, ``b``, and the ``accuracy`` in the ``regression_line`` key
of the ``self.storage`` dict.

Models can define accuracy however they want, so long as ``1.0`` is the highest
accuracy it will ever output, and that ``1.0`` can be interpreted by the caller
to mean that the model predicted the correct value for every record given to the
accuracy method. Numbers approaching ``1.0`` should indicate that the model was
closer to making the correct prediction for each record.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 81-107

Predict
-------

To make a prediction, we access the ``regression_line`` within ``self.storage``,
we use the ``m`` and ``b`` indexes to calculate ``y = m * x + b``, we use the
``accuracy`` as our estimated confidence in the prediction.

We call :py:meth:`record.predicted <dffml.record.Record.predicted>`
passing it the name of the feature we predicted, the predicted value, and the
confidence in our prediction.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :lines: 109-128

Python Usage
------------

We can use our new model from Python code as follows. This example makes use of
``dffml.noasync`` which contains versions of ``train``, ``accuracy``, and
``predict`` which we don't have to be in an ``async`` function to call.

Let's first create our training, test, and prediction data CSV files.

.. literalinclude:: /../tests/tutorials/models/slr/train_data.sh

.. literalinclude:: /../tests/tutorials/models/slr/test_data.sh

.. literalinclude:: /../tests/tutorials/models/slr/predict_data.sh

Then we can write our Python file, **run.py**.

.. literalinclude:: /../tests/tutorials/models/slr/run.py

We run it as we would any other Python file

.. code-block:: console

    $ python3 run.py

The output should look like this

.. code-block::

   Accuracy: 1.0
   {'Years': 8, 'Salary': 110.0}

Command Line Usage
------------------

To use your new model on the command line we'll reference it by it's entrypoint
style path. This is in the format of ``file:ClassWithinFile``, so for this it'll
be ``myslr:MySLRModel``.

We do the same steps we did with Python, only using the command line interface.

.. literalinclude:: /../tests/tutorials/models/slr/train.sh

There's no output from the training command if everything went well

.. literalinclude:: /../tests/tutorials/models/slr/test.sh

The accuracy command outputs the percentage accuracy

.. code-block::

   1.0

Finally, let's make predictions

.. literalinclude:: /../tests/tutorials/models/slr/predict.sh

The output of prediction should like similar to this

.. code-block:: json

    [
        {
            "extra": {},
            "features": {
                "Years": 8
            },
            "key": "0",
            "last_updated": "2020-05-24T22:48:11Z",
            "prediction": {
                "Salary": {
                    "confidence": 1.0,
                    "value": 110.0
                }
            }
        }
    ]

HTTP Server Usage
-----------------

Your model will also be accessible via the HTTP API via a similar syntax.

First we need to install the HTTP service, which is the HTTP server which will
serve our model. See the :doc:`/plugins/service/http/index` docs for more
information on the HTTP service.

.. code-block:: console

    $ pip install -U dffml-service-http

We start the HTTP service and tell it that we want to make our model accessable
via the HTTP :ref:`plugin_service_http_api_model` API.

.. warning::

    You should be sure to read the :doc:`/plugins/service/http/security` docs!
    This example of running the HTTP API is insecure and is only used to help
    you get up and running.

.. literalinclude:: /../tests/tutorials/models/slr/start_http.sh

We can then ask the HTTP service to make predictions, or do training or accuracy
assessment.

.. literalinclude:: /../tests/tutorials/models/slr/curl_http.sh

You should see the following prediction

.. code-block:: json

    {
        "iterkey": null,
        "records": {
            "0": {
                "key": "0",
                "features": {
                    "Years": 8
                },
                "prediction": {
                    "Salary": {
                        "confidence": 1.0,
                        "value": 110.0
                    }
                },
                "last_updated": "2020-04-14T20:07:11Z",
                "extra": {}
            }
        }
    }
