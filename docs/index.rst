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

You can use DFFML from the :doc:`Command Line <cli>`, :doc:`Python
<api/high_level>`, or the :doc:`HTTP API <plugins/service/http/index>`, see the
:doc:`quickstart/model` to get started right away.

It makes training and using machine learning models as simple as

.. literalinclude:: /../examples/quickstart.py

Output:

.. code-block::

    Accuracy: 1.0
    {'Years': 6, 'Expertise': 13, 'Trust': 0.7, 'Salary': 70.0}
    {'Years': 7, 'Expertise': 15, 'Trust': 0.8, 'Salary': 80.0}

This is the documentation for the latest release, documentation for the master
branch can be found `here <master/index.html>`_.

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Introduction

    about
    installation
    concepts/index

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Usage

    quickstart/model
    tutorials/index
    examples/index

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Reference

    plugins/index
    cli
    plugins/service/http/index
    api/index
    troubleshooting
    arch/index

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Subprojects

    shouldi
    swportal

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Community

    GitHub <https://github.com/intel/dffml>
    Master Branch Docs <https://intel.github.io/dffml/master/>
    publications
    contact
    contributing/index
    news/index
    changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
