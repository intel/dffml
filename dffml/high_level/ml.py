import contextlib
from typing import Union, Dict, Any

from ..model import Model
from ..record import Record
from ..feature import Feature, Features
from ..source.source import BaseSource
from ..accuracy.accuracy import AccuracyScorer, AccuracyContext
from ..util.internal import records_to_sources


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

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> model = SLRModel(
    ...     features=Features(
    ...         Feature("Years", int, 1),
    ...     ),
    ...     predict=Feature("Salary", int, 1),
    ...     location="tempdir",
    ... )
    >>>
    >>> async def main():
    ...     await train(
    ...         model,
    ...         {"Years": 0, "Salary": 10},
    ...         {"Years": 1, "Salary": 20},
    ...         {"Years": 2, "Salary": 30},
    ...         {"Years": 3, "Salary": 40},
    ...     )
    >>>
    >>> asyncio.run(main())
    """
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        # Run training
        return await mctx.train(sctx)


async def score(
    model,
    accuracy_scorer: Union[AccuracyScorer, AccuracyContext],
    features: Union[Feature, Features],
    *args: Union[BaseSource, Record, Dict[str, Any]],
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

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> model = SLRModel(
    ...     features=Features(
    ...         Feature("Years", int, 1),
    ...     ),
    ...     predict=Feature("Salary", int, 1),
    ...     location="tempdir",
    ... )
    >>>
    >>> async def main():
    ...     await train(
    ...         model,
    ...         {"Years": 0, "Salary": 10},
    ...         {"Years": 1, "Salary": 20},
    ...         {"Years": 2, "Salary": 30},
    ...         {"Years": 3, "Salary": 40},
    ...     )
    ...     print(
    ...         "Accuracy:",
    ...         await score(
    ...             model,
    ...             MeanSquaredErrorAccuracy(),
    ...             Feature("Salary", int, 1),
    ...             {"Years": 4, "Salary": 50},
    ...             {"Years": 5, "Salary": 60},
    ...         ),
    ...     )
    >>>
    >>> asyncio.run(main())
    Accuracy: 0.0
    """
    # TODO Use this to ensure that we're always passing features before records
    # We can remove it eventually once we know we've updated everywhere
    # appropriately
    if not isinstance(features, (Feature, Features)):
        raise TypeError(
            f"features was {type(features)}: {features!r}. Should have been Feature or Features"
        )
    if isinstance(features, Feature):
        features = Features(features)

    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        # Allow for keep models open
        if isinstance(accuracy_scorer, AccuracyScorer):
            accuracy_scorer = await astack.enter_async_context(accuracy_scorer)
            actx = await astack.enter_async_context(accuracy_scorer())
        else:
            # TODO Replace this with static type checking and maybe dynamic
            # through something like pydantic. See issue #36
            raise TypeError(f"{accuracy_scorer} is not an AccuracyScorer")

        return float(await actx.score(mctx, sctx, *features))


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

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> model = SLRModel(
    ...     features=Features(
    ...         Feature("Years", int, 1),
    ...     ),
    ...     predict=Feature("Salary", int, 1),
    ...     location="tempdir",
    ... )
    >>>
    >>> async def main():
    ...     await train(
    ...         model,
    ...         {"Years": 0, "Salary": 10},
    ...         {"Years": 1, "Salary": 20},
    ...         {"Years": 2, "Salary": 30},
    ...         {"Years": 3, "Salary": 40},
    ...     )
    ...     async for i, features, prediction in predict(
    ...         model,
    ...         {"Years": 6},
    ...         {"Years": 7},
    ...     ):
    ...         features["Salary"] = round(prediction["Salary"]["value"])
    ...         print(features)
    >>>
    >>> asyncio.run(main())
    {'Years': 6, 'Salary': 70}
    {'Years': 7, 'Salary': 80}
    """
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        # Run predictions
        async for record in mctx.predict(sctx):
            yield record if keep_record else (
                record.key,
                record.features(),
                record.predictions(),
            )
            if update:
                await sctx.update(record)
