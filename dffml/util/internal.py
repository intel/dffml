"""
Helper functions for dealing with internal data types
"""
import pathlib
import contextlib
from typing import Optional

from ..record import Record
from ..source.source import (
    Sources,
    SourcesContext,
    BaseSource,
    BaseSourceContext,
)
from ..df.types import DataFlow
from ..configloader.configloader import BaseConfigLoader
from ..source.memory import MemorySource, MemorySourceConfig


class CannotConvertToRecord(Exception):
    """
    Raised when a list is provided to convert to records but the model doesn't
    exist.
    """


@contextlib.asynccontextmanager
async def records_to_sources(*args):
    """
    Create a memory source out of any records passed as a variable length list.
    Add all sources found in the variable length list to a list of sources, and
    the created source containing records, and return that list of sources.
    """
    sources = Sources()
    sctxs = []
    # Records to add to memory source
    records = []
    # Convert dicts to records
    for i, arg in enumerate(args):
        if isinstance(arg, dict):
            arg = Record(i, data={"features": arg})
        if isinstance(arg, Record):
            records.append(arg)
        elif isinstance(arg, pathlib.Path) or (
            isinstance(arg, str) and "." in arg
        ):
            filepath = pathlib.Path(arg)
            source = BaseSource.load(filepath.suffixes[0].replace(".", ""))
            sources.append(source(filename=arg))
        elif isinstance(arg, (Sources, BaseSource)):
            sources.append(arg)
        elif isinstance(arg, (SourcesContext, BaseSourceContext)):
            sctxs.append(arg)
        else:
            raise ValueError(
                f"Don't know what to do with non-source type: {arg!r}"
            )
    # Create memory source if there are any records
    if records:
        sources.append(MemorySource(MemorySourceConfig(records=records)))
    # Open the sources
    async with sources as sources:
        async with sources() as sctx:
            # Add any already open source contexts
            for already_open_sctx in sctxs:
                sctx.append(already_open_sctx)
            yield sctx


def list_records_to_dict(features, *args, model=None):
    if model:
        args = list(args)
        for i in range(len(args)):
            if isinstance(args[i], list):
                args[i] = dict(zip(features, args[i]))
        return args
    raise CannotConvertToRecord("Model does not exist!")


async def load_dataflow_from_configloader(
    dataflow, configloader_cls: Optional[BaseConfigLoader] = None
):
    """
    Load a dataflow from a configloader if it is not an instance of a dataflow
    already. Optionally takes an explicitly given subclass of
    :py:class:`BaseConfigLoader`. Otherwise currently attempts to guess based on
    dataflow being a filepath, loads configloader registered to entrypoint of
    the file extension.

    **TODO** This just guesses based on filetype, we should also support
    protocol's from URLs for example: ``protocol://``
    """
    if isinstance(dataflow, DataFlow):
        return dataflow
    dataflow_path = pathlib.Path(dataflow)
    if configloader_cls is None:
        config_type = dataflow_path.suffix.replace(".", "")
        configloader_cls = BaseConfigLoader.load(config_type)
    async with configloader_cls() as configloader:
        async with configloader() as loader:
            exported = await loader.loadb(dataflow_path.read_bytes())
            return DataFlow._fromdict(**exported)
