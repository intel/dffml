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

- label: String

  - default: unlabeled

- readwrite: Boolean

  - default: False

- allowempty: Boolean

  - default: False

- key: String

  - default: src_url

- labelcol: String

  - default: label

json
~~~~

*Core*

JSONSource reads and write from a JSON file on open / close. Otherwise
stored in memory.

**Args**

- filename: String

- label: String

  - default: unlabeled

- readwrite: Boolean

  - default: False

- allowempty: Boolean

  - default: False

memory
~~~~~~

*Core*

Stores repos in a dict in memory

**Args**

- repos: List of repos

dffml_source_mysql
------------------

.. code-block:: console

    pip install dffml-source-mysql


mysql
~~~~~

*Core*

No description

**Args**

- host: String

  - default: 127.0.0.1

- port: Integer

  - default: 3306

- user: String

- password: String

- db: String

- repos-query: String

  - SELECT `key` as src_url, data_1 as feature_1, data_2 as feature_2 FROM repo_data

- repo-query: String

  - SELECT `key` as src_url, data_1 as feature_1, data_2 as feature_2 FROM repo_data WHERE `key`=%s

- update-query: String

  - INSERT INTO repo_data (`key`, data_1, data_2) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE data_1 = %s, data_2=%s

- model-columns: List of strings

  - Order of Columns in table

- ca: String

  - default: None
  - Path to server TLS certificate