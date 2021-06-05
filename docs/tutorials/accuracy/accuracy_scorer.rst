.. _accuracy_scorer_tutorial_mse:

Accuracy Scorer
===============

In this tutorial we will learn how to implement an accuracy
scorer. Our accuracy scorer will be a simple mean squared error
accuracy score, which is a common accuracy metric for regeression
models.

We will be working in a new file, **mse.py**

Imports
-------

First we need to import few modules from the standard library

- ``config``, this will help us creating config for the accuracy
  scorer that we will be implementing.

- ``AccuracyScorer`` and ``AccuracyContext`` provides the base
  scorer that we need to inherit and overide the ``score`` method.

Few other modules will also be required which needs to be imported.

.. literalinclude:: /../dffml/accuracy/mse.py
    :test:
    :lines: 1-11

Config
------

Here we will be implementing MeanSquaredErrorAccuracyConfig,
a config class for the scorer that we will be implementing.

.. literalinclude:: /../dffml/accuracy/mse.py
    :test:
    :lines: 14-16

Context
-------

Now we will be implementing MeanSquaredErrorAccuracyContext,
which inherits from AccuracyContext.

Here we will be implementing a score method which would
take the `ModelContext` and `Sources`, using this we would
have access the model's config and the sources records.

.. literalinclude:: /../dffml/accuracy/mse.py
    :test:
    :lines: 19-39

Scorer
------

Now we will be implementing our MeanSquaredErrorAccuracy
this would inherit from the AccuracyScorer. Here we will
also create an entrypoint for it, so we can also use this
scorer in the cli.

.. literalinclude:: /../dffml/accuracy/mse.py
    :test:
    :lines: 42-45
