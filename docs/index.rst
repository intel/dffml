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

Training and using machine learning models as simple as

.. literalinclude:: /../examples/quickstart.py

Output:

.. code-block::

    Accuracy: 1.0
    {'Years': 6, 'Expertise': 13, 'Trust': 0.7, 'Salary': 70.0}
    {'Years': 7, 'Expertise': 15, 'Trust': 0.8, 'Salary': 80.0}

You can use DFFML from the command line, Python, or the HTTP API, see the
:doc:`quickstart/model` to get started right away.

The web UI (under heavy development) can be found `here <webui/>`_.

This is the documentation for the latest release, documentation for the master
branch can be found `here <master/index.html>`_.

DFFML's source code can be found on `GitHub <https://github.com/intel/dffml>`_.

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Introduction

    about
    installation

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Examples

    quickstart/model
    tutorials/index
    usage/index

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Reference

    plugins/index
    cli
    plugins/service/http/index
    api/index

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Community

    publications
    contact
    contributing/index
    changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
