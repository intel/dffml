"""
High level abstraction interfaces to DFFML. These are probably going to be used
in a lot of quick and dirty python files.
"""
import pathlib
from typing import Union, Dict, Any

from .record import Record
from .source.source import Sources, BaseSource
from .source.memory import MemorySource, MemorySourceConfig


def _records_to_sources(*args):
    """
    Create a memory source out of any records passed as a variable length list.
    Add all sources found in the variable length list to a list of sources, and
    the created source containing records, and return that list of sources.
    """
    # If the first arg is an instance of sources, append the rest to that.
    if args and isinstance(args[0], Sources):
        sources = args[0]
    else:
        sources = Sources(
            *[arg for arg in args if isinstance(arg, BaseSource)]
        )
    # Records to add to memory source
    records = []
    # Make args mutable
    args = list(args)
    # Convert dicts to records
    for i, arg in enumerate(args):
        if isinstance(arg, dict):
            arg = Record(i, data={"features": arg})
        if isinstance(arg, Record):
            records.append(arg)
        if isinstance(arg, str) and "." in arg:
            filepath = pathlib.Path(arg)
            source = BaseSource.load(filepath.suffix.replace(".", ""))
            sources.append(source(filename=arg))
    # Create memory source if there are any records
    if records:
        sources.append(MemorySource(MemorySourceConfig(records=records)))
    return sources


async def train(model, *args: Union[BaseSource, Record, Dict[str, Any]]):
    """
    Train a machine learning model.

    Provide records to the model to train it. The model should be already
    instantiated.

    Parameters
    ----------
    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.
    *args : list
        Input data for training. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.
    """
    sources = _records_to_sources(*args)
    async with sources as sources, model as model:
        async with sources() as sctx, model() as mctx:
            return await mctx.train(sctx)


async def accuracy(
    model, *args: Union[BaseSource, Record, Dict[str, Any]]
) -> float:
    """
    Assess the accuracy of a machine learning model.

    Provide records to the model to assess the percent accuracy of its
    prediction abilities. The model should be already instantiated and trained.

    Parameters
    ----------
    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.
    *args : list
        Input data for training. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.

    Returns
    -------
    float
        A decimal value representing the percent of the time the model made the
        correct prediction. For some models this has another meaning. Please see
        the documentation for the model your using for further details.
    """
    sources = _records_to_sources(*args)
    async with sources as sources, model as model:
        async with sources() as sctx, model() as mctx:
            return float(await mctx.accuracy(sctx))


async def predict(
    model,
    *args: Union[BaseSource, Record, Dict[str, Any]],
    update: bool = False,
    keep_record: bool = False,
):
    """
    Make a prediction using a machine learning model.

    The model must be trained before using it to make a prediction.

    Parameters
    ----------
    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.
    *args : list
        Input data for prediction. Could be a ``dict``, :py:class:`Record`,
        filename, or one of the data :doc:`/plugins/dffml_source`.
    update : boolean, optional
        If ``True`` prediction data within records will be written back to all
        sources given. Defaults to ``False``.
    keep_record : boolean, optional
        If ``True`` the results will be kept as their ``Record`` objects instead
        of being converted to a ``(record.key, features, predictions)`` tuple.
        Defaults to ``False``.

    Returns
    -------
    asynciterator
        ``Record`` objects or ``(record.key, features, predictions)`` tuple.
    """
    sources = _records_to_sources(*args)
    async with sources as sources, model as model:
        async with sources() as sctx, model() as mctx:
            async for record in mctx.predict(sctx.records()):
                yield record if keep_record else (
                    record.key,
                    record.features(),
                    record.predictions(),
                )
                if update:
                    await sctx.update(record)
