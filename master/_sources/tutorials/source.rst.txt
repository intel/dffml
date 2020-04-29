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

This creates a Python package for you with a source that stores ``Record`` objects
in memory, called ``MiscSource``, and some tests.

Edit the Source
---------------

The implementation of a source consists mainly of creating a subclass of
:class:`dffml.source.source.BaseSourceContext`. Often there will be some initial
connection establishment in the :class:`dffml.source.source.BaseSource` as well
(as we will see in the sqlite example).

.. autoclass:: dffml.source.source.BaseSourceContext
    :members:
    :noindex:

We essentially just fill out the methods in the context class. And do any
context entry and exit we need to do in the context class and its parent.

Interact with the Database
--------------------------

.. TODO This section is way under-explained and should be improved

For this tutorial we'll be implementing a source which knows how to save and
load data from a ``sqlite`` database. We'll be using the ``aiosqlite`` package
to do this.

If we had a ``sqlite`` database will custom columns we could implement it like
so.

**examples/source/custom_sqlite.py**

.. literalinclude:: /../examples/source/custom_sqlite.py

Write the tests
---------------

**examples/source/test_custom_sqlite.py**

.. literalinclude:: /../examples/source/test_custom_sqlite.py

Run the tests
-------------

.. code-block:: console

    $ python3 setup.py test

Register your source
--------------------

Modify the **setup.py** file and change the ``dffml.source`` ``entrypoint``'s
to point to your new source class (not the one ending in ``Context``).

.. code-block:: python

    from setuptools import setup

    from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

    SETUP_KWARGS["entry_points"] = {
        "dffml.source": [f"customsqlite = {IMPORT_NAME}.custom_sqlite:CustomSQLiteSource"]
    }

    setup(**SETUP_KWARGS)

This allows you to use your source with the CLI and HTTP API (after you install
it).

Install your package
--------------------

The following command installs your new source.

.. code-block:: console

    $ python3 -m pip install --prefix=~/.local -e .
