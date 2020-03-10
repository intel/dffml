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

*Official*

Uses a CSV file as the source of record feature data

**Args**

- filename: String

- tag: String

  - default: untagged

- readwrite: Boolean

  - default: False

- allowempty: Boolean

  - default: False

- key: String

  - default: key

- tagcol: String

  - default: tag

idx1
~~~~

*Official*

Source to read files in IDX1 format (such as MNIST digit label dataset).

**Args**

- filename: String

- feature: String

  - Name of the feature the data will be referenced as

- readwrite: Boolean

  - default: False

- allowempty: Boolean

  - default: False

idx3
~~~~

*Official*

Source to read files in IDX3 format (such as MNIST digit image dataset).

**Args**

- filename: String

- feature: String

  - Name of the feature the data will be referenced as

- readwrite: Boolean

  - default: False

- allowempty: Boolean

  - default: False

json
~~~~

*Official*

JSONSource reads and write from a JSON file on open / close. Otherwise
stored in memory.

**Args**

- filename: String

- tag: String

  - default: untagged

- readwrite: Boolean

  - default: False

- allowempty: Boolean

  - default: False

memory
~~~~~~

*Official*

Stores records in a dict in memory

**Args**

- records: List of records

dffml_source_mysql
------------------

.. code-block:: console

    pip install dffml-source-mysql


mysql
~~~~~

*Official*

No description

**Args**

- host: String

  - default: 127.0.0.1

- port: Integer

  - default: 3306

- user: String

- password: String

- db: String

- records-query: String

  - SELECT `key` as key, data_1 as feature_1, data_2 as feature_2 FROM record_data

- record-query: String

  - SELECT `key` as key, data_1 as feature_1, data_2 as feature_2 FROM record_data WHERE `key`=%s

- update-query: String

  - INSERT INTO record_data (`key`, data_1, data_2) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE data_1 = %s, data_2=%s

- model-columns: List of strings

  - Order of Columns in table

- ca: String

  - default: None
  - Path to server TLS certificate