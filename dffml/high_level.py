"""
High level abstraction interfaces to DFFML. These are probably going to be used
in a lot of quick and dirty python files.
"""
import pathlib
from typing import Union, Dict, Any

from .repo import Repo
from .source.source import Sources, BaseSource
from .source.memory import MemorySource, MemorySourceConfig


def _repos_to_sources(*args):
    """
    Create a memory source out of any repos passed as a variable length list.
    Add all sources found in the variable length list to a list of sources, and
    the created source containing repos, and return that list of sources.
    """
    # If the first arg is an instance of sources, append the rest to that.
    if args and isinstance(args[0], Sources):
        sources = args[0]
    else:
        sources = Sources(
            *[arg for arg in args if isinstance(arg, BaseSource)]
        )
    # Repos to add to memory source
    repos = []
    # Make args mutable
    args = list(args)
    # Convert dicts to repos
    for i, arg in enumerate(args):
        if isinstance(arg, dict):
            arg = Repo(i, data={"features": arg})
        if isinstance(arg, Repo):
            repos.append(arg)
        if isinstance(arg, str) and "." in arg:
            filepath = pathlib.Path(arg)
            source = BaseSource.load(filepath.suffix.replace(".", ""))
            sources.append(source(filename=arg))
    # Create memory source if there are any repos
    if repos:
        sources.append(MemorySource(MemorySourceConfig(repos=repos)))
    return sources


async def train(model, *args: Union[BaseSource, Repo, Dict[str, Any]]):
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
        Input data for training. Could be a ``dict``, :py:class:`Repo`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.
    """
    sources = _repos_to_sources(*args)
    async with sources as sources, model as model:
        async with sources() as sctx, model() as mctx:
            return await mctx.train(sctx)


async def accuracy(
    model, *args: Union[BaseSource, Repo, Dict[str, Any]]
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
        Input data for training. Could be a ``dict``, :py:class:`Repo`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.

    Returns
    -------
    float
        A decimal value representing the percent of the time the model made the
        correct prediction. For some models this has another meaning. Please see
        the documentation for the model your using for further details.
    """
    sources = _repos_to_sources(*args)
    async with sources as sources, model as model:
        async with sources() as sctx, model() as mctx:
            return float(await mctx.accuracy(sctx))


async def predict(
    model,
    *args: Union[BaseSource, Repo, Dict[str, Any]],
    update: bool = False,
    keep_repo: bool = False,
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
        Input data for prediction. Could be a ``dict``, :py:class:`Repo`,
        filename, or one of the data :doc:`/plugins/dffml_source`.
    update : boolean, optional
        If ``True`` prediction data within records will be written back to all
        sources given. Defaults to ``False``.
    keep_repo : boolean, optional
        If ``True`` the results will be kept as their ``Repo`` objects instead
        of being converted to a ``(repo.key, features, predictions)`` tuple.
        Defaults to ``False``.

    Returns
    -------
    asynciterator
        ``Repo`` objects or ``(repo.key, features, predictions)`` tuple.
    """
    sources = _repos_to_sources(*args)
    async with sources as sources, model as model:
        async with sources() as sctx, model() as mctx:
            async for repo in mctx.predict(sctx.repos()):
                yield repo if keep_repo else (
                    repo.key,
                    repo.features(),
                    repo.predictions(),
                )
                if update:
                    await sctx.update(repo)
