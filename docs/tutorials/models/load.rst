Load Models Dynamically
=======================

The names of models you see on the :doc:`/plugins/dffml_model` page can be
passed to the :py:func:`Model.load() <dffml.model.model.Model.load>` class
method to dynamically import the model plugin and load the model.

**single.py**

.. literalinclude:: /../examples/tutorials/models/load/single.py
    :test:

.. code-block:: console
    :test:

    $ python single.py

You can also load all the models you have installed by not passing any
arguments to load. All models have a ``CONFIG`` property which is a
:py:mod:`dataclasses <dataclass>`. You can inspect the properties of the
dataclass using the :py:func:`dataclasses.fields` function.

**all.py**

.. literalinclude:: /../examples/tutorials/models/load/all.py
    :test:

.. code-block:: console
    :test:

    $ python all.py
    <class 'dffml.model.slr.SLRModel'>
        predict: Label or the value to be predicted
        features: Features to train on. For SLR only 1 allowed
        location: Location where state should be saved
