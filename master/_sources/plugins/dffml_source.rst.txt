.. _plugin_sources:

Sources
=======

Sources are implementations of :class:`dffml.source.source.BaseSource`, they
abstract the loading and storage of data / datasets.

If you want to get started creating your own source, check out the
:ref:`source_tutorial`.

dffml
-----

.. code-block:: console

    pip install dffml


csv
~~~

*Core*

Uses a CSV file as the source of repo feature data

**Args**

- filename: String

- readonly: Boolean

  - default: False

- label: String

  - default: unlabeled

- key: String

  - default: None

json
~~~~

*Core*

JSONSource reads and write from a JSON file on open / close. Otherwise
stored in memory.

**Args**

- filename: String

- readonly: Boolean

  - default: False

- label: String

  - default: unlabeled

memory
~~~~~~

*Core*

Stores repos in a dict in memory

**Args**

- keys: List of strings

  - default: []