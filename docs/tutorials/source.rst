.. _source_tutorial:

New Source Tutorial
===================

This tutorial is for implementing a data source. Which is probably what you want
if the way you store your data doesn't have an existing :ref:`plugin_sources`
plugin. Or even more likely, you have a very specific way an existing
application you're trying to integrate with stores data you want in it's
database.

Create the Package
------------------

To create a new source we first create a new python package. DFFML has a script
to create it for you.

.. code-block:: console

    $ dffml service dev create source my-source
    $ cd my-source

This creates a Python package for you with a source that stores ``Repo`` objects
in memory, called ``MiscSource``, and some tests.

Edit the Source
---------------

For this tutorial we'll be implementing a source which knows how to save and
load data from a ``sqlite`` database. We'll be using the ``aiosqlite`` package
to do this.

Imports
~~~~~~~

We're going to need a few modules from the standard library, let's import them.

.. code-block:: python

    import aiosqlite

Interact with the Database
~~~~~~~~~~~~~~~~~~~~~~~~~~

*This section is way under-explained and should be improved*

The implementation of a source consists mainly of creating a subclass of
:class:`dffml.source.source.BaseSourceContext`. Often there will be some initial
connection establishment in the :class:`dffml.source.source.BaseSource` as well
(as we will see in the sqlite example).

.. autoclass:: dffml.source.source.BaseSourceContext
    :members:
    :noindex:

If we had a ``sqlite`` database will custom columns we could implement it like
so.

.. literalinclude:: /../examples/source/custom_sqlite.py

Run the tests
~~~~~~~~~~~~~

.. code-block:: console

    $ python3.7 setup.py test
