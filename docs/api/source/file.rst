File Based Sources
==================

`FileSource`: (Inherits Source class) FileSource class detects the type of source, opens it and calls abstract methods `load_fd` and `dump_fd` for parsing and dumping data in streams respectively.  

Supported Compressions:

1. `gzip`
2. `bz2`
3. `lzma`
4. `xz`
5. `zip`

# Data Sources

DFFML supports data sources in `CSV` and `JSON` formats with respective methods defined in the following classes:

1. `CSVSource`: (Inherits FileSource and MemorySource) Uses a CSV file as the source of the repo feature data. Abstract functions `load_fd` and `dump_fd` are defined.

2. `JSONSource`: (Inherits FileSource and MemorySource) Uses a JSON file as the source of the repo feature data. Abstract functions `load_fd` and `dump_fd` are defined.

JSON
----

.. automodule:: dffml.source.json
   :members:

CSV
---

.. automodule:: dffml.source.csv
   :members:

Generic File Based
------------------

.. automodule:: dffml.source.file
   :members:
