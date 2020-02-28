Welcome to DFFML!
=================

.. image:: https://github.com/intel/dffml/workflows/Tests/badge.svg
    :target: https://github.com/intel/dffml/actions
    :alt: Test Status
.. image:: https://codecov.io/gh/intel/dffml/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/intel/dffml
    :alt: codecov
.. image:: https://bestpractices.coreinfrastructure.org/projects/2594/badge
    :target: https://bestpractices.coreinfrastructure.org/projects/2594
    :alt: CII
.. image:: https://badges.gitter.im/gitterHQ/gitter.svg
    :target: https://gitter.im/dffml/community
    :alt: Gitter chat
.. image:: https://img.shields.io/pypi/v/dffml.svg
    :target: https://pypi.org/project/dffml
    :alt: PyPI version

Data Flow Facilitator for Machine Learning (DFFML) makes it easy to generate
datasets, train and use machine learning models, and integrate machine learning
into new or existing applications. It provides APIs for dataset generation,
storage, and model definition.

- :ref:`plugin_models` handle implementations of machine learning algorithms.
  Likely wrapping code from a popular machine learning framework.

- Sources handle the storage of datasets, saving and loading them from files,
  databases, remote APIs, etc.

- DataFlows are directed graphs used to generate a dataset, as well as modify
  existing datasets. They can also be used to do non-machine learning tasks, you
  could use them to build a web app for instance.

You'll find the existing implementations of all of these on their respective
:ref:`plugins` pages. DFFML has a plugin based architecture, which allows us to
include some sources, models, and operations as a part of the main package,
``dffml``, and other functionality in more specific packages.

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Contents:

    about
    community
    installation
    tutorials/index
    usage/index
    plugins/index
    cli
    plugins/service/http/index
    api/index
    publications

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
