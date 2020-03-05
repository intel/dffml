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
``dffml-model-tensorflow``. The source code for all *Official* plugins is within
the same Git repo (https://github.com/intel/dffml).

A *Official* plugin is any plugin maintained within the main Git repo.

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

setup.py
--------

There are various ``setup.py`` files throughout the codebase, one for the main
package, one for each plugin, and one in ``skel/``. There are also
``setup_common.py`` files.

Checking For Development Version
++++++++++++++++++++++++++++++++

You might have asked yourself, what is this thing?

.. code-block:: python

    INSTALL_REQUIRES = [] + (
        ["dffml>=0.3.4"]
        if not any(
            list(
                map(
                    os.path.isfile,
                    list(
                        map(
                            lambda syspath: os.path.join(
                                syspath, "dffml.egg-link"
                            ),
                            sys.path,
                        )
                    ),
                )
            )
        )
        else []
    )

This code is needed because ``python`` will use extracted versions of packages
over development versions if they are installed.

``pip`` will download and extract a package (thereby installing it) if it sees
it in the ``INSTALL_REQUIRES`` list. This wrecks havoc with our development
workflow.

For example, when we put the main package, ``dffml`` in the ``INSTALL_REQUIRES``
list of a plugin, ``pip`` will go off and download the appropriate version from
PyPi and extract it to a place Python searches for packages. Now when we run
anything we'll end up using the version ``pip`` just installed instead of the
version we're developing on locally.

The solution to this is to add the above code block to ``setup.py`` files. The
innermost list is ``sys.path``, which is all the places Python is going to look
for packages when there is an ``import`` statement. We use ``map`` to apply a
function to each directory in ``sys.path``. The map will take the directory name
and add ``dffml.egg-link`` to it. We add this because when you install something
in development mode (``dffml`` in this case) ``pip`` creates this ``.egg-link``
file. In the file is the path to the source code you're working on. Therefore,
if that file exists, then the package is installed in development mode. The next
``map`` then checks if any of the file paths generated by the previous ``map``
exist. If ``any`` of them exist, then there is a ``.egg-link`` file somewhere in
Python's search path, which means the package (``dffml`` in this case, hence the
``dffml.egg-link``) is installed in development mode.

If the package is installed in development mode, then we don't want ``pip`` to
install it from PyPi, since that would cause the development version not to be
used.

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
