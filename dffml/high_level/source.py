from typing import AsyncIterator

from ..util.internal import records_to_sources
from ..source.source import BaseSource, Record


async def save(source: BaseSource, *args: Record) -> None:
    """
    Update a source's knowledge about given records.

    For each record given, call
    :py:func:`update <dffml.source.source.BaseSourceContext.update>` on the
    source. Effectively saving all the records to the source.

    Parameters
    ----------
    source : BaseSource
        Data source to use. See :doc:`/plugins/dffml_source` for sources and
        options.
    *args : list
        Records to be saved.

    Examples
    --------

    >>> import asyncio
    >>> import pathlib
    >>> from dffml import *
    >>>
    >>> source = CSVSource(filename="save.csv", allowempty=True, readwrite=True)
    >>>
    >>> async def main():
    ...     await save(
    ...         source,
    ...         Record(
    ...             "myrecord",
    ...             data={
    ...                 "features": {"Years": 0, "Expertise": 1, "Trust": 0.1},
    ...                 "prediction": {"Salary": {"value": 10, "confidence": 1.0}},
    ...             }
    ...         )
    ...     )
    ...     print(pathlib.Path("save.csv").read_text().strip())
    >>>
    >>> asyncio.run(main())
    key,tag,Expertise,Trust,Years,prediction_Salary,confidence_Salary
    myrecord,untagged,1,0.1,0,10,1.0
    """
    async with records_to_sources(source) as sctx:
        for record in args:
            await sctx.update(record)


async def load(source: BaseSource, *args: str) -> AsyncIterator[Record]:
    """
    Yields records from a source.

    Yields all the records from the source, if record keys are given then only
    those records are yielded.

    Parameters
    ----------
    source : BaseSource
        Data source to use. See :doc:`/plugins/dffml_source` for sources and
        options.
    *args : str
        Records to be returned. If empty, all the records in a source will be returned.

    Returns
    -------
    asynciterator
        :py:class:`Record <dffml.record.Record>` object

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> source = CSVSource(filename="load.csv", allowempty=True, readwrite=True)
    >>>
    >>> async def main():
    ...     await save(
    ...         source,
    ...         Record("1", data={"features": {"A": 0, "B": 1}}),
    ...         Record("2", data={"features": {"A": 3, "B": 4}}),
    ...     )
    ...
    ...     # All records in source
    ...     async for record in load(source):
    ...         print(record.export())
    ...
    ...     # For specific records in a source
    ...     async for record in load(source, "1"):
    ...         print(record.export())
    ...
    ...     # Lightweight source syntax
    ...     async for record in load("load.csv", "2"):
    ...         print(record.export())
    >>>
    >>> asyncio.run(main())
    {'key': '1', 'features': {'A': 0, 'B': 1}, 'extra': {}}
    {'key': '2', 'features': {'A': 3, 'B': 4}, 'extra': {}}
    {'key': '1', 'features': {'A': 0, 'B': 1}, 'extra': {}}
    {'key': '2', 'features': {'A': 3, 'B': 4}, 'extra': {}}
    """
    async with records_to_sources(source) as sctx:
        if args:
            # If specific records are to be loaded
            for record in args:
                yield await sctx.record(record)
        else:
            # All the records are loaded
            async for record in sctx.records():
                yield record
