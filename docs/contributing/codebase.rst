Codebase Layout And Notes
=========================

.. contents::

Plugins
-------

DFFML is plugin based. This means that there the source code for the main
package ``dffml``, is separate from the source code for many of the things you
might want to use in conjunction with it. For example, if you wanted to use the
machine learning models based on scikit, you'd install ``dffml-model-scikit``.
If you wanted to use machine learning models based on TensorFlow, you'd install
``dffml-model-tensorflow``. The source code for all *Core* plugins is within the
same Git repo (https://github.com/intel/dffml).

This means users only have to install what they need. TensorFlow is several
hundred megabytes, not everyone wants that, or needs that to get machine
learning models that preform accurately on their problem.

All plugins have their base class that they derive from in the main package,
which is located in the ``dffml`` directory at the root of the git repo.

The plugin packages are located within their respective at the root of the git
repo. For example, source base classes are in ``dffml/source`` and source plugin
packages are in ``source/``.

One-Two Punch
-------------

All classes in DFFML follow a double asynchronous context entry pattern. This is
ideal for usages such as creating a connection pool, then using a connection. Be
that with a database, client HTTP sessions, etc.

.. code-block:: python

    from dffml.repo import Repo
    from dffml.source.csv import CSVSource, CSVSourceConfig

    async def main():
        # One
        async with CSVSource(
            CSVSourceConfig(
                filename="test.csv",
                allowempty=True,
                readwrite=True,
            )
        ) as source:
            # Two
            async with source() as sctx:
                # Punch
                await sctx.update(Repo("0", data={
                    "features": {
                        "first_column": 42,
                        "second_column": 1776,
                    }
                }))

    asyncio.run(main())

