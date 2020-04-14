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
    async with source:
        async with source() as sctx:
            for record in args:
                await sctx.update(record)


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

    Examples
    --------

    >>> model = LinearRegressionModel(
    ...     features=Features(
    ...         DefFeature("Years", int, 1),
    ...         DefFeature("Expertise", int, 1),
    ...         DefFeature("Trust", float, 1),
    ...     ),
    ...     predict=DefFeature("Salary", int, 1),
    ... )
    >>>
    >>> async def main():
    ...     await train(
    ...         model,
    ...         {"Years": 0, "Expertise": 1, "Trust": 0.1, "Salary": 10},
    ...         {"Years": 1, "Expertise": 3, "Trust": 0.2, "Salary": 20},
    ...         {"Years": 2, "Expertise": 5, "Trust": 0.3, "Salary": 30},
    ...         {"Years": 3, "Expertise": 7, "Trust": 0.4, "Salary": 40},
    ...     )
    >>>
    >>> asyncio.run(main())
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

    Examples
    --------

    >>> model = LinearRegressionModel(
    ...     features=Features(
    ...         DefFeature("Years", int, 1),
    ...         DefFeature("Expertise", int, 1),
    ...         DefFeature("Trust", float, 1),
    ...     ),
    ...     predict=DefFeature("Salary", int, 1),
    ... )
    >>>
    >>> async def main():
    ...     print(
    ...         "Accuracy:",
    ...         await accuracy(
    ...             model,
    ...             {"Years": 4, "Expertise": 9, "Trust": 0.5, "Salary": 50},
    ...             {"Years": 5, "Expertise": 11, "Trust": 0.6, "Salary": 60},
    ...         ),
    ...     )
    >>>
    >>> asyncio.run(main())
    Accuracy: 1.0
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

    Examples
    --------

    >>> model = LinearRegressionModel(
    ...     features=Features(
    ...         DefFeature("Years", int, 1),
    ...         DefFeature("Expertise", int, 1),
    ...         DefFeature("Trust", float, 1),
    ...     ),
    ...     predict=DefFeature("Salary", int, 1),
    ... )
    >>>
    >>> async def main():
    ...     async for i, features, prediction in predict(
    ...         model,
    ...         {"Years": 6, "Expertise": 13, "Trust": 0.7},
    ...         {"Years": 7, "Expertise": 15, "Trust": 0.8},
    ...     ):
    ...         features["Salary"] = round(prediction["Salary"]["value"])
    ...         print(features)
    >>>
    >>> asyncio.run(main())
    {'Years': 6, 'Expertise': 13, 'Trust': 0.7, 'Salary': 70.0}
    {'Years': 7, 'Expertise': 15, 'Trust': 0.8, 'Salary': 80.0}
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
