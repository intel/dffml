Sources
=======

Sources are how DFFML abstracts storage of feature data. This allows users to
swap out their data sources as they progress from testing through integration.

Most DFFML CLI commands work with the :class:`dffml.source.source.Sources` class
which merges the feature data of Repos with the same ``src_url``. This means
when multiple sources are given to those CLI commands, feature data stored in
those various sources/databases under the same unique key will automatically
accessible within one :class:`dffml.repo.Repo`.

DFFML has several built in sources which can be used programmatically or via the
CLI and other services.

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: Contents:

    base
    memory
    file

Developers can of course define their own sources. For example if you have an
existing SQL database you want to pull feature data from, you would implement a
source that queries that database and SELECTs data from the applicable columns.

The implementation of a source consists mainly of creating a subclass of
:class:`dffml.source.source.BaseSourceContext`. Often there will be some initial
connection establishment in the :class:`dffml.source.source.BaseSource` as well
(as we will see in the sqlite example).

.. autoclass:: dffml.source.source.BaseSourceContext
    :members:
    :noindex:

Here's how a source to query custom columns might be implemented.

.. literalinclude:: /../examples/source/custom_sqlite.py
