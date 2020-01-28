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

A *Core* plugin is any plugin maintained within the main Git repo.

This means users only have to install what they need. TensorFlow is several
hundred megabytes, not everyone wants that, or needs that to get machine
learning models that preform accurately on their problem.

All plugins have their base class that they derive from in the main package,
which is located in the ``dffml`` directory at the root of the git repo.

The plugin packages are located within their respective directories at the root
of the git repo. For example, source base classes are in ``dffml/source/`` and
source plugin packages are in ``source/``.

Adding A New Plugin
+++++++++++++++++++

To add a new *Core* plugin to DFFML. You need to first create the plugin in the
appropriate directory. Then add it to the lists of core plugins.

.. warning::

    The release process is automated. You should **NOT** upload the package to
    PyPi! Someone from Intel has to be the one to do that for *Core* plugins.

For *Core* plugins, the name given to create should be in the form of
``dffml-{PLUGIN_TYPE}-{NAME}``.

.. code-block:: console

    $ cd model/
    $ dffml service dev create model dffml-model-someframework
    $ mv dffml-model-someframework someframework

Now that we've created the plugin, we need to add it to a few lists

- Add the plugin to ``CORE_PLUGINS`` list in ``dffml/service/dev.py``

- Update ``.github/workflows/testing.yml``

  - Add the path to the plugin to the ``jobs.test.strategy.matrix.plugin`` list.

  - Open an issue to have the ``PYPI_{PLUGIN_TYPE}_{NAME}`` token added under
    ``jobs.steps[-1].run``.

    - Sample issue format: ``pypi: Add token for dffml-{PLUGIN_TYPE}-{NAME} to
      testing.yml``

- Update ``scripts/docs/care`` to add your plugin name (with underscores instead
  of hyphens) on the line for the respective plugin type.

One-Two Punch
-------------

All classes in DFFML follow a double asynchronous context entry pattern. This is
ideal for usages such as creating a connection pool, then using a connection. Be
that with a database, client HTTP sessions, etc.

.. code-block:: python

    import asyncio
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

Config
------

Much of the DFFML codebase is dedicated to transforming configuration structures
between their incoming form to a ``dict`` which can be used to determine what
plugin needs to be loaded, and what the arguments for the configuration class of
that plugin are.

For example:

.. code-block:: yaml

    model:
      arg: tfdnnc
      config:
        epochs: 400
        steps: 4000
        classifications:
        - '0'
        - '1'
        predict:
          dtype: int
          length: 1
          name: maintained
        features:
        - dtype: int
          length: 10
          name: authors
        - dtype: int
          length: 10
          name: commits
        - dtype: int
          length: 10
          name: work

Currently, ``arg`` needs to be renamed to ``plugin``, it signifies the plugin to
load. ``config`` is the ``...Config`` class as a dict for that plugin.

The command line equivalent for the model is...

.. code-block:: console

    $ dffml ... \
        -model tfdnnc \
        -model-epochs 400 \
        -model-steps 4000 \
        -model-classifications 0 1 \
        -model-predict maintained:str:1 \
        -model-features \
          authors:int:10 \
          commits:int:10 \
          work:int:10 \

The reason it's called ``arg`` right now is because the parsing of the command
line came first and the argument is stored there when it's not nested.
