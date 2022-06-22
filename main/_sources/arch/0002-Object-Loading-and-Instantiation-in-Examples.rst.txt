2. Object Loading and Instantiation in Examples
===============================================

Date: 2021-04-13

Status
------

Accepted

Context
-------

We have a plugin based system where we can load and instantiated loaded classes

We have two options, we allow for loading and installation at the same time, or
keep it separate.

Load and instantiate at same time

.. code-block:: python

    model = Model.load(model_entrypoint)(...)

Separate load and instantiate

.. code-block:: python

    ModelClass = Model.load(model_entrypoint)
    model = ModelClass(...)

Decision
--------

We decided that it's more straightforward to end users to keep it serrate.

Consequences
------------

Examples that do dynamic loading should load classes then instantiate, instead
of all at once.

.. code-block:: python

    # Load the model
    ModelClass = Model.load(model_entrypoint)

    # Configure the model
    model = ModelClass(
        features=Features(
            Feature("PetalWidth", float, 1),
            Feature("SepalWidth", float, 1),
            Feature("SepalLength", float, 1),
            Feature("PetalLength", float, 1),
        ),
        predict=Feature("classification", float, 1),
        directory="model",
    )
