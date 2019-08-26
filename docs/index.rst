Welcome to DFFML!
=================

Data Flow Facilitator for Machine Learning (DFFML) provides APIs for dataset
generation, storage, and model definition.

DFFML abstracts three parts of the machine learning via an object oriented
approach involving three main classes.

- ``Source`` classes handle the storage of datasets, saving and loading them
  from files, databases, remote APIs, etc.

- ``Model`` classes handle implementations of machine learning algorithms.
  Likely wrapping code from a populary machine learning framework.

  - To get started using existing machine learning models right away, head over
    to :ref:`plugin_models`.

- ``OperationImplementation`` are used to generate a dataset, as well as modify
  existing datasets.

You'll find the existing implementations of all of these on their respective
plugins pages. DFFML has a plugin based architecture, which allows us to include
some sources, models, and operations as a part of the main package, ``dffml``,
and other functionality in more specific packages.

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Contents:

    installation
    tutorials/index
    usage/index
    plugins/index
    plugins/service/http/index
    api/index
    community

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
