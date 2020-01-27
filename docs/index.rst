Welcome to DFFML!
=================

.. image:: https://github.com/intel/dffml/workflows/Tests/badge.svg?branch=master&event=push
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

The web UI cant be found `here <webui/>`_.

- Models handle implementations of machine learning algorithms.
  Likely wrapping code from a popular machine learning framework.

  - To use models from the command line see :ref:`plugin_models`

  - To use models from python see the :doc:`quickstart/model`

- Sources handle the storage of datasets, saving and loading them from files,
  databases, remote APIs, etc.

- DataFlows are directed graphs used to generate a dataset, as well as modify
  existing datasets. They can also be used to do non-machine learning tasks, you
  could use them to build a web app for instance.

You'll find the existing implementations of all of these on their respective
:ref:`plugins` pages. DFFML has a plugin based architecture, which allows us to
include some sources, models, and operations as a part of the main package,
``dffml``, and other functionality in more specific packages.

This is the documentation for the latest release, documentation for the master
branch can be found `here <master/index.html>`_.

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Contents:

    about
    quickstart/model
    installation
    tutorials/index
    usage/index
    plugins/index
    cli
    plugins/service/http/index
    api/index
    publications
    community
    contributing/index
    changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
