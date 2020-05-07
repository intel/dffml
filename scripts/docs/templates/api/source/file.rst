File Based Sources
==================

``FileSource``: (Inherits Source class) FileSource class detects the type of
source, opens it and calls abstract methods ``load_fd`` and ``dump_fd`` for
parsing and dumping data in streams respectively.

Supported Compressions:

1. ``gzip``
2. ``bz2``
3. ``lzma``
4. ``xz``
5. ``zip``

DFFML supports data sources in ``CSV`` and ``JSON`` formats with respective
methods defined in the following classes:

2. :doc:`CSVSource <csv>`: (Inherits FileSource and MemorySource) Uses a CSV
   file as the source of the record feature data. Abstract functions ``load_fd``
   and ``dump_fd`` are defined.

2. :doc:`JSONSource <json>`: (Inherits FileSource and MemorySource) Uses a JSON
   file as the source of the record feature data. Abstract functions ``load_fd``
   and ``dump_fd`` are defined.

Generic File Based
------------------

.. automodule:: dffml.source.file
   :members:
