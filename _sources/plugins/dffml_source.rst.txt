Sources
=======

Sources are implementations of :class:`dffml.source.source.BaseSource`, they
abstract the loading and storage of data / datasets.

dffml
-----

csv
~~~

*Core*

Uses a CSV file as the source of repo feature data

**Args**

- filename: String

- readonly: Boolean

  - default: False

json
~~~~

*Core*

JSONSource reads and write from a JSON file on open / close. Otherwise
stored in memory.

**Args**

- filename: String

- readonly: Boolean

  - default: False

memory
~~~~~~

*Core*

Stores repos in a dict in memory

**Args**

- keys: List of strings

  - default: []