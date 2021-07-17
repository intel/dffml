.. _model_tutorial_slr:

Writing a Model
===============

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
    :test:
    :lines: 1-3

We'll also need a few things from DFFML.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :test:
    :lines: 5-16

Math
----

The first thing you'll want to do is add some functions which calculate the best
fit line and accuracy. These aren't important for understanding how DFFML works.
So we're going to skip over their logic in this tutorial. You can write your own
versions to find the best fit line for lists of X, and Y data if you want, or
you can copy these.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :test:
    :lines: 19-54

Config
------

DFFML makes it so that we can use our models from the command line, HTTP API,
and of course, Python. This all works because we define a config class for each
model.

Anything that a user might want to tweak about a models behavior should go in
the ``Config`` class for the model. The naming convention is ``TheName`` +
``Model`` + ``Config``.

Our model has three configurable properties.

- ``features``. A list of :py:class:`Feature <dffml.feature.Feature>` objects
  who's names will be present within each :py:class:`Record
  <dffml.record.Record>`. Our model only supports a single feature. It willl use
  the first feature in the features list as the X value for the regression line.

- ``predict``. The name of the feature we want to predict. Within each
  :py:class:`Record <dffml.record.Record>` this will be the data that our model
  should use as the Y value for the regression line.

- ``directory``. The location on disk where we'll save and load our model from

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :test:
    :lines: 57-63

Class
-----

The naming conventions for classes in DFFML is ``TheName`` + ``PluginType``.
We're making a ``Model`` plugin. So the name is ``MySLRModel``.

The plugin system needs us to do two things to ensure we can access our new
model from the DFFML command line and other interfaces.

We must use the ``entrypoint`` decorator passing it the name we want to
reference the model by. For anything that allows for specifying multiple
models, you can configure all models of the same type by using the string
provided here.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :test:
    :lines: 66-67

We must set the ``CONFIG`` attribute to the respective ``Config`` class.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :test:
    :lines: 180-181

We can override the ``__init__()`` method to do validation on the ``features``
config property. Simple linear regression only supports one input feature, so we
will raise a ``ValueError`` if the user supplys more than one feature.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :test:
    :lines: 183-187

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
    :test:
    :lines: 188-202

Predict
-------

To make a prediction, we access the ``regression_line`` within ``self.storage``,
we use the ``m`` and ``b`` indexes to calculate ``y = m * x + b``, we use the
``accuracy`` as our estimated confidence in the prediction.

We call :py:meth:`record.predicted <dffml.record.Record.predicted>`
passing it the name of the feature we predicted, the predicted value, and the
confidence in our prediction.

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/myslr.py
    :test:
    :lines: 205-224

Python Usage
------------

We can use our new model from Python code as follows. This example makes use of
``dffml.noasync`` which contains versions of ``train``, ``accuracy``, and
``predict`` which we don't have to be in an ``async`` function to call.

Let's first create our training, test, and prediction data CSV files.

**train.csv**

.. code-block::
    :test:
    :filepath: train.csv

    Years,Salary
    1,40
    2,50
    3,60
    4,70
    5,80

**test.csv**

.. code-block::
    :test:
    :filepath: test.csv

    Years,Salary
    6,90
    7,100

**predict.csv**

.. code-block::
    :test:
    :filepath: predict.csv

    Years
    8

Then we can write our Python file, **run.py**.

**run.py**

.. literalinclude:: /../examples/tutorials/models/slr/run.py
    :test:

We run it as we would any other Python file

.. code-block:: console
    :test:

    $ python3 run.py
    Accuracy: 1.0
    {'Years': 8, 'Salary': 110.0}

Command Line Usage
------------------

To use your new model on the command line we'll reference it by it's entrypoint
style path. This is in the format of ``file:ClassWithinFile``, so for this it'll
be ``myslr:MySLRModel``.

We do the same steps we did with Python, only using the command line interface.

.. code-block:: console
    :test:

    $ dffml train \
        -log debug \
        -model myslr:MySLRModel \
        -model-features Years:int:1 \
        -model-predict Salary:float:1 \
        -model-location modeldir \
        -sources f=csv \
        -source-filename train.csv

There's no output from the training command if everything went well

Now let's make predictions

.. code-block:: console
    :test:

    $ dffml predict all \
        -model myslr:MySLRModel \
        -model-features Years:int:1 \
        -model-predict Salary:float:1 \
        -model-location modeldir \
        -sources f=csv \
        -source-filename predict.csv
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
    :test:

    $ python -m pip install -U dffml-service-http

We start the HTTP service and tell it that we want to make our model accessable
via the HTTP :ref:`plugin_service_http_api_model` API.

.. warning::

    You should be sure to read the :doc:`/plugins/service/http/security` docs!
    This example of running the HTTP API is insecure and is only used to help
    you get up and running.

.. code-block:: console
    :test:
    :daemon: 8080

    $ dffml service http server -insecure -cors '*' -addr 0.0.0.0 -port 8080 \
        -models mymodel=myslr:MySLRModel \
        -model-features Years:int:1 \
        -model-predict Salary:float:1 \
        -model-location modeldir

We can then ask the HTTP service to make predictions, or do training or accuracy
assessment.

.. code-block:: console
    :test:
    :replace: cmds[0][2] = cmds[0][2].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))

    $ curl -f http://localhost:8080/model/mymodel/predict/0 \
        --header "Content-Type: application/json" \
        --data '{"0": {"features": {"Years": 8}}}'
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
