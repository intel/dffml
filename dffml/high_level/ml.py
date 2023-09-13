import contextlib
from typing import Union, Dict, Any, List


from ..record import Record
from ..source.source import BaseSource
from ..feature import Feature, Features
from ..model import Model, ModelContext
from ..util.internal import records_to_sources, list_records_to_dict, records_to_dict_check
from ..accuracy.accuracy import AccuracyScorer, AccuracyContext
from ..tuner import Tuner, TunerContext


async def train(model, *args: Union[BaseSource, Record, Dict[str, Any], List]):
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
    if (
        hasattr(model.config, "features")
        and any(isinstance(arg, list) for arg in args)
        and hasattr(model.config, "predict")
    ):
        if isinstance(model.config.predict, Features):
            predict_feature = [
                feature.name for feature in model.config.predict
            ]
        else:
            predict_feature = [model.config.predict.name]
        args = list_records_to_dict(
            [feature.name for feature in model.config.features]
            + predict_feature,
            *args,
            model=model,
        )
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        elif isinstance(model, ModelContext):
            mctx = model
        # Run training
        return await mctx.train(sctx)


async def score(
    model,
    accuracy_scorer: Union[AccuracyScorer, AccuracyContext],
    features: Union[Feature, Features],
    *args: Union[BaseSource, Record, Dict[str, Any], List],
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
    if any(isinstance(arg, list) for arg in args) and hasattr(
        model.config, "predict"
    ):
        if isinstance(model.config.predict, Features):
            predict_feature = [
                feature.name for feature in model.config.predict
            ]
        else:
            predict_feature = [model.config.predict.name]
        args = list_records_to_dict(
            [feature.name for feature in model.config.features]
            + predict_feature,
            *args,
            model=model,
        )

    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        elif isinstance(model, ModelContext):
            mctx = model
        # Allow for keep models open
        if isinstance(accuracy_scorer, AccuracyScorer):
            accuracy_scorer = await astack.enter_async_context(accuracy_scorer)
            actx = await astack.enter_async_context(accuracy_scorer())
        elif isinstance(accuracy_scorer, AccuracyContext):
            actx = accuracy_scorer
        else:
            # TODO Replace this with static type checking and maybe dynamic
            # through something like pydantic. See issue #36
            raise TypeError(f"{accuracy_scorer} is not an AccuracyScorer")

        return float(await actx.score(mctx, sctx, *features))


async def predict(
    model,
    *args: Union[BaseSource, Record, Dict[str, Any], List],
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
    if any(isinstance(arg, list) for arg in args) and hasattr(
        model.config, "predict"
    ):
        if isinstance(model.config.predict, Features):
            predict_feature = [
                feature.name for feature in model.config.predict
            ]
        else:
            predict_feature = [model.config.predict.name]
        args = list_records_to_dict(
            [feature.name for feature in model.config.features]
            + predict_feature,
            *args,
            model=model,
        )
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        elif isinstance(model, ModelContext):
            mctx = model
        # Run predictions
        async for record in mctx.predict(sctx):
            yield record if keep_record else (
                record.key,
                record.features(),
                record.predictions(),
            )
            if update:
                await sctx.update(record)

async def tune(
    model,
    tuner: Union[Tuner, TunerContext],
    accuracy_scorer: Union[AccuracyScorer, AccuracyContext],
    features: Union[Feature, Features],
    train_ds: Union[BaseSource, Record, Dict[str, Any], List],
    valid_ds: Union[BaseSource, Record, Dict[str, Any], List],
) -> float:

    """
    Tune the hyperparameters of a model with a given tuner.

    
    Parameters
    ----------
    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.
    tuner: Tuner
        Hyperparameter tuning method to use. See :doc:`/plugins/dffml_tuner` for
        tuner options.
    train_ds : list
        Input data for training. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.
    valid_ds : list
        Validation data for testing. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.


    Returns
    -------
    float
        A decimal value representing the result of the accuracy scorer on the given
        test set. For instance, ClassificationAccuracy represents the percentage of correct
        classifications made by the model.

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
    ...     score = await tune(
    ...         model,
    ...         ParameterGrid(objective="min"),
    ...         MeanSquaredErrorAccuracy(),
    ...         Features(
    ...             Feature("Years", float, 1),
    ...         ),
    ...         [
    ...             {"Years": 0, "Salary": 10},
    ...             {"Years": 1, "Salary": 20},
    ...             {"Years": 2, "Salary": 30},
    ...             {"Years": 3, "Salary": 40}
    ...         ],
    ...         [
    ...             {"Years": 6, "Salary": 70},
    ...             {"Years": 7, "Salary": 80}
    ...         ]
    ...
    ...     )
    ...     print(f"Tuner score: {score}") 
    ...    
    >>> asyncio.run(main())
    Tuner score: 0.0
    """

    if not isinstance(features, (Feature, Features)):
        raise TypeError(
            f"features was {type(features)}: {features!r}. Should have been Feature or Features"
        )
    if isinstance(features, Feature):
        features = Features(features)
    if hasattr(model.config, "predict"):
        if isinstance(model.config.predict, Features):
            predict_feature = [
                feature.name for feature in model.config.predict
            ]
        else:
            predict_feature = [model.config.predict.name]

    train_ds = records_to_dict_check(train_ds, model, predict_feature)
    valid_ds = records_to_dict_check(valid_ds, model, predict_feature)
    
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        train = await astack.enter_async_context(records_to_sources(*train_ds))
        test = await astack.enter_async_context(records_to_sources(*valid_ds))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        elif isinstance(model, ModelContext):
            mctx = model

        # Allow for scorers to be kept open
        if isinstance(accuracy_scorer, AccuracyScorer):
            accuracy_scorer = await astack.enter_async_context(accuracy_scorer)
            actx = await astack.enter_async_context(accuracy_scorer())
        elif isinstance(accuracy_scorer, AccuracyContext):
            actx = accuracy_scorer
        else:
            # TODO Replace this with static type checking and maybe dynamic
            # through something like pydantic. See issue #36
            raise TypeError(f"{accuracy_scorer} is not an AccuracyScorer")

        if isinstance(tuner, Tuner):
            tuner = await astack.enter_async_context(tuner)
            tctx = await astack.enter_async_context(tuner())
        elif isinstance(tuner, TunerContext):
            tctx = tuner
        else:
            raise TypeError(f"{tuner} is not an Tuner")

        return float(
            await tctx.optimize(mctx, features, actx, train, test)
        )

