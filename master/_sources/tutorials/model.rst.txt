.. _model_tutorial:

New Model Tutorial
==================

If you have some data and want to do machine learning on it, you probably want
to head over to the :ref:`plugin_models` plugins. This tutorial is for
implementing a machine learning algorithm. Which is probably what you want if
there's not an existing plugin for your algorithm.

DFFML is not like PyTorch or TensorFlow. It's higher level than those. However,
that doesn't mean it *has* to be higher level. You can use the lower level APIs
of any library, or no library if you wanted.

For this tutorial we'll be implementing our own machine learning algorithm from
scratch, which means that we're not using a machine learning focused library to
handle calculations for us, just NumPy for to handle matrices.

Create the Package
------------------

To create a new model we first create a new Python package. DFFML has a helper
to create it for you.

The helper creates a model which does Simple Linear Regression (SLR). Which
means it finds the best fit line for a dataset.

You may know the best fit line as ``y = m * x + b``.

.. code-block:: console

    $ dffml service dev create model dffml-model-myslr
    $ cd dffml-model-myslr

Install the Package
-------------------

If you're planing on importing any third party packages, anything on
`PyPi <https://pypi.org>`_, you'll want to add it to the ``setup.py`` file
first.

**setup.py**

.. code-block:: python

    common.KWARGS["install_requires"] += ["scikit-learn>=0.21.2"]

Any time you modify the dependencies of a package you should re-install it so
they get installed as well. Anytime you change anything in ``"entry_points"``
you'll also want to re-install the package.

``pip``'s ``-e`` flag tells it we're installing our package in development mode,
which means anytime Python import's our package, it's going to use the version
that we're working on here.

.. code-block:: console

    $ pip install -e .

The Model
---------

First we'll cover the main aspects of writing a
:py:class:`Model <dffml.model.model.Model>`.

Imports
~~~~~~~

We're going to need a few modules from the standard library, let's import them.

- ``pathlib`` will be used to define the directory were saved model state should
  be stored.

- ``statistics`` will be used to help us calculate the average (mean) of our
  data.

- ``typing`` is for Python's static type hinting. It lets use give hints to our
  editor or IDE so they can help us check our code before we run it.

**dffml_model_myslr/misc.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/misc.py
    :lines: 1-3

We'll also need a few things from DFFML.

**dffml_model_myslr/misc.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/misc.py
    :lines: 5-16

Naming
~~~~~~

All the create scripts create class names that start with ``Misc``, since we'll
be creating a Simple Linear Regression model, you can change everywhere you see
``Misc`` to ``MySLR``.

The first thing you'll see is some functions which calculate the best fit line
and accuracy. These aren't important for understanding how DFFML works. So we're
going to skip over them in this tutorial.

Config
~~~~~~

Anything that a user might want to tweak about a models behavior should go in
the ``Config`` class for the model.

**dffml_model_myslr/misc.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/misc.py
    :lines: 54-61

Our model has three configurable properties.

- ``predict``. The name of the feature we want to predict for any
  :py:class:`Record <dffml.record.Record>`.

- ``features``. The features within each
  :py:class:`Record <dffml.record.Record>` that our model should use for
  training.

- ``directory``. The location on disk where we'll save and load our model from.

:py:class:`features <dffml.feature.feature.Features>` is a list. Our model is
Simple Linear Regression, which only supports one feature. Therefore, we'll only
use the 0th index in the features list within the rest of our model code.

Class
~~~~~

The plugin system needs us to do three things to ensure we can access our new
model from the DFFML command line and other interfaces.

- We must use the ``entrypoint`` decorator passing it the name we want to
  reference the model by. Instead of ``miscmodel``, use ``myslr``.

- We must set the ``CONFIG`` attribute to the respective ``Config`` class.

**dffml_model_myslr/misc.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/misc.py
    :lines: 64-67

- We must make sure ``setup.py``'s ``"entry_points"`` field correctly references
  the location of our model.

**setup.py**

.. literalinclude:: /../dffml/skel/model/setup.py
    :lines: 12-14

Remember, anytime you change anything in ``"entry_points"`` you'll also want to
re-install the package.

.. code-block:: console

    $ pip install -e .

Train
~~~~~

The train method should train the model. First we ask the data ``sources`` for
any ``records`` containing the features our model was told to use.
``with_features`` takes a list of feature names each record should contain.

Models should save their state to disk after training. Classes derived from
``SimpleModel`` can put anything they want saved into ``self.storage``, which
is saved and loaded from a JSON on disk.

**dffml_model_myslr/misc.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/misc.py
    :lines: 76-91

Accuracy
~~~~~~~~

We saved the accuracy as the 2nd index into the ``"regression_line"`` key in the
``self.storage`` dictionary. When we assess the accuracy we reload from there.

**dffml_model_myslr/misc.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/misc.py
    :lines: 93-101

Predict
~~~~~~~

To make a prediction, we access the ``regression_line`` within ``self.storage``,
we use the ``m`` and ``b`` indexes to calculate ``y = m * x + b``, we use the
``accuracy`` as our estimated confidence in the prediction.

We call :py:meth:`record.predicted <dffml.record.Record.predicted>`
passing it the name of the feature we predicted, the predicted value, and the
confidence in our prediction.

**dffml_model_myslr/misc.py**

.. literalinclude:: /../dffml/skel/model/REPLACE_IMPORT_PACKAGE_NAME/misc.py
    :lines: 103-122

The Tests
---------

Lets modify the test case to verify that we did this right.

Rename the imports
~~~~~~~~~~~~~~~~~~

We need to make sure our model is imported via it's new name, ``MySRL`` instead
of ``Misc``.

**tests/test_model.py**

.. code-block:: python

    import tempfile

    from dffml import train, accuracy, predict, Features, Feature, AsyncTestCase

    from dffml_model_myslr.misc import MySLRModel

Test data
~~~~~~~~~

We usually try to randomly generate training and test data, but for this example
we're just going to hard code in some data.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :lines: 7-34

Rename the test class
~~~~~~~~~~~~~~~~~~~~~

Change the test class's name, and make sure ``cls.model`` is instantiating a
``MySLR`` model instead of the ``Misc`` model.

We create a temporary directory for our tests to use, and clean it up when
they're done. The tests are prefixed with numbers to indicate what order they
should be run in, ensuring that accuracy and predict test always have a trained
model to work with.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :lines: 37-60

Testing Train
~~~~~~~~~~~~~

Similarly to the quickstart, all we need to to is pass the model and training
data to the :py:func:`train <dffml.train>` function.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :lines: 62-64

Testing Accuracy
~~~~~~~~~~~~~~~~

Once again, all we need to to is pass the model and test data to the
:py:func:`accuracy <dffml.accuracy>` function. Then we check if it's in an
acceptable range. This test is helpful to make sure you never make any horribly
wrong changes to your model, since it will check that the accuracy is within an
acceptable range.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :lines: 66-70

Testing Prediction
~~~~~~~~~~~~~~~~~~

Finally, we use the test data and model with the
:py:func:`predict <dffml.predict>` function. Then we check if each predicted Y
value is within 10% of what it should be.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :lines: 72-83

Run the tests
~~~~~~~~~~~~~

You can now start tweaking your new DFFML model to do something awesome!

.. code-block:: console

    $ python setup.py test
    running test
    WARNING: Testing via this command is deprecated and will be removed in a future version. Users looking for a generic test entry point independent of test runner are encouraged to use tox.
    running egg_info
    writing dffml_model_myslr.egg-info/PKG-INFO
    writing dependency_links to dffml_model_myslr.egg-info/dependency_links.txt
    writing entry points to dffml_model_myslr.egg-info/entry_points.txt
    writing top-level names to dffml_model_myslr.egg-info/top_level.txt
    reading manifest file 'dffml_model_myslr.egg-info/SOURCES.txt'
    reading manifest template 'MANIFEST.in'
    writing manifest file 'dffml_model_myslr.egg-info/SOURCES.txt'
    running build_ext
    test_00_train (tests.test_model.TestMySLRModel) ... ok
    test_01_accuracy (tests.test_model.TestMySLRModel) ... ok
    test_02_predict (tests.test_model.TestMySLRModel) ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 0.003s

    OK

If you want to see the output of the call to ``self.logger.debug``, just set the
``LOGGING`` environment variable to ``debug``.

.. code-block:: console

    $ LOGGING=debug python setup.py test

Command line usage
------------------

Use your new model from the command line just as you would any other model.

Your model will also be automatically accessible via the HTTP API and web UI
(coming soon).

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
        -model myslr \
        -model-features Years:int:1 \
        -model-predict Salary:float:1 \
        -sources f=csv \
        -source-filename dataset.csv \
        -log debug
    $ dffml accuracy \
        -model myslr \
        -model-features Years:int:1 \
        -model-predict Salary:float:1 \
        -sources f=csv \
        -source-filename dataset.csv \
        -log debug
    1.0
    $ echo -e 'Years,Salary\n6,0\n' | \
      dffml predict all \
        -model myslr \
        -model-features Years:int:1 \
        -model-predict Salary:float:1 \
        -sources f=csv \
        -source-filename /dev/stdin \
        -log debug
    [
        {
            "extra": {},
            "features": {
                "Salary": 0,
                "Years": 6
            },
            "last_updated": "2020-03-10T15:15:45Z",
            "prediction": {
                "Salary": {
                    "confidence": 1.0,
                    "value": 90.0
                }
            },
            "key": "0"
        }
    ]
