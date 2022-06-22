Codebase Layout And Notes
=========================

.. contents::

Plugins
-------

DFFML is plugin based. This means that the source code for the main
package ``dffml``, is separate from the source code for many of the things you
might want to use in conjunction with it. For example, if you wanted to use the
machine learning models based on scikit, you'd install ``dffml-model-scikit``.
If you wanted to use machine learning models based on TensorFlow, you'd install
``dffml-model-tensorflow``. The source code for all *Official* plugins is within
the same Git repo (https://github.com/intel/dffml).

A *Official* plugin is any plugin maintained within the main Git repo.

This means users only have to install what they need. TensorFlow is several
hundred megabytes, not everyone wants that, or needs that to get machine
learning models that perform accurately on their problem.

All plugins have their base class that they derive from in the main package,
which is located in the ``dffml`` directory at the root of the git repo.

The plugin packages are located within their respective directories at the root
of the git repo. For example, source base classes are in ``dffml/source/`` and
source plugin packages are in ``source/``.

Adding A New Plugin
+++++++++++++++++++

To add a new *Official* plugin to DFFML. You need to first create the plugin in
the appropriate directory. Then add it to the lists of core plugins.

.. warning::

    The release process is automated. You should **NOT** upload the package to
    PyPi! Someone from Intel has to be the one to do that for *Official*
    plugins.

For *Official* plugins, the name given to create should be in the form of
``dffml-{PLUGIN_TYPE}-{NAME}``.

.. code-block:: console

    $ cd model/
    $ dffml service dev create model dffml-model-someframework
    $ mv dffml-model-someframework someframework

Now that we've created the plugin, we need to add it to a few lists

- Add the plugin to ``CORE_PLUGINS`` list in ``dffml/plugins.py``

- Update ``.github/workflows/testing.yml``

  - Add the path to the plugin to the ``jobs.test.strategy.matrix.plugin`` list.

  - Open an issue to have the ``PYPI_{PLUGIN_TYPE}_{NAME}`` token added under
    ``jobs.steps[-1].run``.

    - Sample issue format: ``pypi: Add token for dffml-{PLUGIN_TYPE}-{NAME} to
      testing.yml``

Double Context Entry Pattern
----------------------------

All classes in DFFML follow a double asynchronous context entry pattern. This is
ideal for usages such as creating a connection pool, then using a connection. Be
that with a database, client HTTP sessions, etc.

.. code-block:: python

    import asyncio
    from dffml.record import Record
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
                await sctx.update(Record("0", data={
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
      plugin: tfdnnc
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

Here, ``plugin`` is the ``...Arg`` class which signifies the plugin to load.
``config`` is the ``...Config`` class as a dict for that plugin.

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


setup.py
--------

There are various ``setup.py`` files throughout the codebase, one for the main
package, one for each plugin, and one in ``skel/``. There are also
``setup_common.py`` files.

Notes on Various Subsystems
---------------------------

DFFML is comprised of various subsystems. The following are some notes
that might be helpful when working on each of them.

Working on ``skel/``
++++++++++++++++++++

The packages in ``skel/`` are used to create new DFFML packages.

For example, to create a new package containing operations we run the following.

.. code-block:: console

    $ dffml service dev create operations dffml-operations-feedface

If you want to work on any of the packages in ``skel/``, you'll need to run the
``skel link`` command first fromt he ``dev`` service. This will symlink required
files in from ``common/`` so that testing will work.

.. code-block:: console

    $ dffml service dev skel link
