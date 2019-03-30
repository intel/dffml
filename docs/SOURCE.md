# Source

Repos come from a source. Sources may contain more information on a repo than
just it's source URL. Sources are responsible for providing the repos they
contain and updating those repos upon request.

# How sources work and supported formats

`Source`: Abstract base class for all sources. New sources are derived from this class. Abstract methods for sub-classes:

1. `update`: Updates a repo for a source
2. `repos`: Returns a list of repos retrieved
3. `repo`: Get a repo from the source or add it if it doesn't exist

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