CONTRIBUTING
############

This document describes how to write Open Architecture overlays,
overlays for Alice, how to work within the codebase, and the
contribution process.

Alice currently only supports **Python 3.9 on Linux**. ``pyenv``
https://github.com/pyenv/pyenv#installation is a good tool to use
to install another version of Python if your distro doen't have 3.9.

Alice is very much a work in progress. See
https://github.com/intel/dffml/pull/1401 for status.

Debugging
*********

Add ``-log debug`` to any ``alice`` CLI command to get verbose log output.

Run within the builtin Python debugger to be presented with a
Python interpreter breakpointed at the raised exception.

.. code-block:: console

    $ python -m pdb -m alice

Cloud Development Environment
*****************************

Using a cloud development environment gives you a place to work
that already has everything installed and configured. You can
start playing around and writing code immediatly.

**NOTE** Not sure what state gitpod is in, pretty sure there
was some sort of issue we need to move a file around or something.

https://gitpod.io/#github.com/intel/dffml/tree/alice

Cloning the Repo
****************

We are currently on the ``alice`` feature branch of DFFML. See
https://github.com/intel/dffml/pull/1401 for more details.

.. code-block:: console

    $ git clone -b alice https://github.com/intel/dffml

Now open or change directory to the directory containing Alice's
source code within the DFFML project: ``entities/alice``.
``dffml.git/entities/alice`` therefore means, the path
to ``entities/alice``, where the parent directory is wherever
you cloned the ``dffml`` git repo to above. If you were in a shell
at the root of the source tree this would be your current working
directory, the same as the output of ``pwd``. The directory itself
in the following example is just named ``dffml``, which is the default
for git to name based off the repo name on clone.

.. code-block:: console

    $ cd dffml/entities/alice

Dependencies
************

We require you have ``git`` and ``gh`` (https://cli.github.com/)
installed.

Installing in Development Mode
******************************

We recommened creating a virtual environment for Alice
if you haven't already.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console

            $ python -m venv .venv
            $ . .venv/bin/activate
            $ python -m pip install -U pip setuptools wheel

    .. group-tab:: Windows

        .. code-block:: console

            C:\Users\username> python -m venv .venv
            C:\Users\username> .venv\Scripts\activate
            (.venv) C:\Users\username> python -m pip install -U pip setuptools wheel

.. note::

    If you installed the package not in development mode
    off the README's instructions you'll need to uninstall
    all the packages you installed **by name**.

    .. code-block:: console

        $ python -m pip uninstall -y \
            alice \
            dffml \
            shouldi \
            dffml-feature-git \
            dffml-operations-innersource \
            dffml-config-yaml

Run ``pip`` with the ``-e`` flag to specify an editable install,
this must be done for each package.

We select the ``dev`` extra from ``extra_requires`` group to install.
This group is given in the ``setup.cfg`` file. It contains dependencies
which are referenced in the documentation and must be installed when
working on Alice.

We do not select the ``dev`` extra on the other packages unless we
intended to do development work on the as well.

.. code-block:: console

    $ python -m pip install \
        -e .[dev] \
        -e ../../ \
        -e ../../examples/shouldi/ \
        -e ../../feature/git/ \
        -e ../../operations/innersource/ \
        -e ../../configloader/yaml/

Tutorials
*********

These are tutorials on how to extend parts of Alice, they are backlinked from
her README.

- https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0002_our_open_source_guide.md

Data Flow Programming
*********************

Data Flow programming focueses on data types and data transformations.
Data Orented Design is also helpful in understanding Data Flow programming,
altough a distinct concept itself.

- Tutorials on DFFML Operations / DataFlows

  - https://intel.github.io/dffml/main/examples/shouldi.html
  - https://intel.github.io/dffml/main/examples/dataflows.html

- Talk snippit explaining above tutorial

  - https://youtu.be/D9puJiKKKS8?t=873
  
- Concuptual docs on data flow execution

  - https://intel.github.io/dffml/main/concepts/dataflow.html
  
- Misc. References

  - https://en.wikipedia.org/wiki/Dataflow_programming
  - https://www.gamedeveloper.com/programming/tips-on-writing-code-for-data-oriented-design
  - https://www.youtube.com/watch?v=aPh4Z3SioB8

Finding Data Types to Work With
*******************************

You can leverage
https://mermaid-js.github.io/mermaid-live-editor/
to visualize dataflows. Copy paste the output of the diagram code into
the webpage to edit and visualze the flow.

You can also install ``dffml-config-yaml`` via ``python -m pip install -e
configloader/yaml`` which gives you the ability to dump to YAML via addition of
the ``-configloader yaml`` option.

The JSON or YAML document's ``definitions`` field can be useful for finding new
data types available within the flow.

.. code-block:: console

    $ dffml service dev export alice.cli:AlicePleaseContributeCLIDataFlow | tee alice.please.contribute.recommended_community_standards.json
    $ dffml dataflow diagram -shortname alice.please.contribute.recommended_community_standards.json

.. image:: https://user-images.githubusercontent.com/5950433/176561571-cb866c83-4b4c-48f0-9dee-91c9ae7a12f5.svg

Making a Game Plan
******************

Since we're thinking about data, we need to make a game plan, we don't
want to get caught up writing unnessicary code. We don't want to deal with
production or development database configuration, we just want to figure
out how to get the data we need, then figure out where / how we can plug
that data extraction, that feature extraction, into the any applicable
collector flows (Living Threat Model terminology)

We want to enable collection of the ``name`` field within the JSON file
``.myconfig.json``. Here's our game plan

- Check if the ``.myconfig.json`` file exists within a directory.

  - If it doesn't exist, bail out, go no further
  - Read in the contexts
  - Parse the contents as JSON
  - Return the parsed contents

- Validate the contents conform to the expected format

  - Input validation using JSON schema
  - If schema validation fails, bail out, go no further

- Return the ``name`` property of the parsed contents

.. warning::

    **SECURITY** The if statements in the first list item where we check for
    file existance within this operation happens within and not as a
    distinct operation on purpose to avoid a TOCTOU issue if the lock on the
    directory were to be released between time of this operation and
    time of the next, so we contain dealing with the resource to this
    operation.

    References:

    - https://github.com/intel/dffml/blob/alice/docs/concepts/dataflow.rst
    - https://github.com/intel/dffml/issues/51

Writing Operations
******************

Your base flow is your core functionality, it should be modular enough run
with mock data or pre-configured connections. Think of it as the library behind
your functionality.

We implement off of our game plan, focusing on the functionality of bite sized
chunks. Leveraging doctests as our unittests.

References for writing operations, including examples with networking:

- https://intel.github.io/dffml/alice/examples/shouldi.html

**myconfig.py**

.. code-block:: python

    import json
    import pathlib
    from typing import NewType

    MyConfig = NewType("MyConfig", object)
    MyConfigUnvalidated = NewType("MyConfigUnvalidated", object)
    MyConfigProjectName = NewType("MyConfigProjectName", str)
    MyConfigDirectory = NewType("MyConfigDirectory", str)

    def read_my_config_from_directory_if_exists(
        directory: MyConfigDirectory,
    ) -> MyConfigUnvalidated:
        """
        >>> import json
        >>> import pathlib
        >>> import tempfile
        >>>
        >>> with tempfile.TemporaryDirectory() as tempdir:
        ...     _ = pathlib.Path(tempdir, ".myconfig.json").write_text(json.dumps({"name": "Hello World"}))
        ...     print(read_my_config_from_directory_if_exists(tempdir))
        {'name': 'Hello World'}
        """
        path = pathlib.Path(directory, ".myconfig.json")
        if not path.exists():
            return
        return json.loads(path.read_text())

    def validate_my_config(
        config: MyConfigUnvalidated,
    ) -> MyConfig:
        # TODO(security) json schema valiation of myconfig (or
        # make done automatically by operation manifest schema
        # validation on InputNetwork, maybe, just one option,
        # or maybe similar to how prioritizer gets applied,
        # or maybe this is an issue we already track: #1400)
        return config

    def my_config_project_name(
        config: MyConfig,
    ) -> MyConfigProjectName:
        """
        >>> print(my_config_project_name({"name": "Hello World"}))
        Hello World
        """
        return config["name"]

Run Doctests
************

We can run our doctests using Python's builtin helper.

.. code-block:: console

    $ python -m doctest myconfig.py

Writing an Overlay
******************

Overlays can be as simple as a single function, or they can
be classes, files, dataflows, anything which you can generate
an Open Architecture description of.

We use overlays to help keep our code modular. They focus on
the data types we need to connect. In this overlay, we will
be adding an operation which takes Alice's representation of
a Git repo, ``AliceGitRepo``, and returns the directory property
as the ``MyConfigDirectory`` definition.

**alice_please_contribute_recommended_community_standards_overlay_git_myconfig.py**

.. code-block:: python

    from alice.please.contribute.recommended_community_standards.recommended_community_standards import AliceGitRepo

    from myconfig import MyConfigDirectory

    def repo_directory(
        repo: AliceGitRepo,
    ) -> MyConfigDirectory:
        """
        >>> from alice.please.contribute.recommended_community_standards.recommended_community_standards import AliceGitRepo
        >>>
        >>> print(repo_directory(AliceGitRepo(directory="Wonderland", URL=None)))
        Wonderland
        """
        return repo.directory

Run our doctests for the new overlay.

.. code-block:: console

    $ python -m doctest alice_please_contribute_recommended_community_standards_overlay_git_myconfig.py

Registering an Overlay
**********************

The entry point system is an upstream Python option for plugin registration,
this is the method which we use to register overlays. The name is on the
left of the ``=``, the path to the overlay is on the right. The ``.ini``
section is the connonical form of the system context which our overlay
should be applied to.

.. note::

    If you are working within the exsiting alice codebase then the
    following ``entry_points.txt`` file and the
    rest of your files should be in the ``dffml.git/entities/alice``
    directory.

**entry_points.txt**

.. code-block::

    [dffml.overlays.alice.please.contribute.recommended_community_standards]
    MyConfigReader = myconfig
    AlicePleaseContributeRecommendedCommunityStandardsOverlayMyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig

Reinstall the package.

.. code-block:: console

    $ python -m pip install -e .

We can verify the plugins were installed by listing the items registered
to ``dffml.overlays.alice.please.contribute.recommended_community_standard``.

.. code-block:: console

    $ dffml service dev entrypoints list dffml.overlays.alice.please.contribute.recommended_community_standards | grep myconfig
    AlicePleaseContributeRecommendedCommunityStandardsOverlayMyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig -> alice 0.0.1 (/tmp/tmp.XrelIRGR0v/dffml/entities/alice)
    MyConfigReader = myconfig -> alice 0.0.1 (/tmp/tmp.XrelIRGR0v/dffml/entities/alice)

Contributing a Plugin to the 2nd or 3rd Party Ecosystem
*******************************************************

.. note::

    We recommened doing this after you have played around within the
    Alice codebase itself within ``dffml.git/entities/alice``, packaging
    can get tricky and get your environment stuck in weird states.
    You can add and modify the files you would within a plugin within
    the core Alice code directly. If you intend to submit your changes
    upstream into the ``alice`` branch as a pull request you should
    also skip this package creation step and work directly within
    this codebase.

If you want to make your operations, flows, overlays, and other work
available to others as a Python package, you can take the files you
created above and move them into your package.

Run the helper script provided by DFFML, or write the package files by hand.

References:

- https://github.com/intel/project-example-for-python

.. code-block:: console

    $ dffml service dev create blank alice-please-contribute-recommended_community_standards-overlay-git-myconfig

Move the old files into the new directory
``alice-please-contribute-recommended_community_standards-overlay-git-myconfig/alice_please_contribute_recommended_community_standards_overlay_git_myconfig``

.. code-block:: console

    $ mv *myconfig.py alice-please-contribute-recommended_community_standards-overlay-git-myconfig/alice_please_contribute_recommended_community_standards_overlay_git_myconfig/

Add a section to the ``entry_points.txt`` with the the new versions of the
Python ``import`` style paths.

**alice-please-contribute-recommended_community_standards-overlay-git-myconfig/entry_points.txt**

.. code-block::

    [dffml.overlays.alice.please.contribute.recommended_community_standards]
    MyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig.myconfig
    AlicePleaseContributeRecommendedCommunityStandardsOverlayMyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig.overlay

Enable the use of entrypoints registered in the ``entry_points.txt`` file.

.. code-block:: console

    $ sed -i 's/^# entry_points/entry_points/g' alice-please-contribute-recommended_community_standards-overlay-git-myconfig/setup.cfg

Install the new package.

.. code-block:: console

    $ python -m pip install -e alice-please-contribute-recommended_community_standards-overlay-git-myconfig

.. note::

    If you originally edited the ``entry_points.txt`` file in
    ``dffml.git/entities/alice`` then you need to remove the
    lines you added and reinstall the ``alice`` package in
    development mode.

    .. code-block:: console

        $ grep -v myconfig entry_points.txt | tee entry_points.txt.removed
        $ mv entry_points.txt.removed entry_points.txt
        $ python -m pip install -e .

Now re-run any commands which you might have run previously to validate you're
new overlays are being applied. The diagram or please contribute commands are
good targets.

We can verify the plugins were installed by listing the items registered
to ``dffml.overlays.alice.please.contribute.recommended_community_standard``.

.. code-block:: console

    $ dffml service dev entrypoints list dffml.overlays.alice.please.contribute.recommended_community_standards | grep myconfig
    AlicePleaseContributeRecommendedCommunityStandardsOverlayMyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig.overlay -> alice-please-contribute-recommended-community-standards-overlay-git-myconfig 0.1.dev1+gc4185e9.d20220630 (/tmp/tmp.XrelIRGR0v/dffml/entities/alice/alice-please-contribute-recommended_community_standards-overlay-git-myconfig)
    MyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig.myconfig -> alice-please-contribute-recommended-community-standards-overlay-git-myconfig 0.1.dev1+gc4185e9.d20220630 (/tmp/tmp.XrelIRGR0v/dffml/entities/alice/alice-please-contribute-recommended_community_standards-overlay-git-myconfig)

Registering a Flow
******************

You can write a base flow as a class and then give the entrypoint
style path to the class or you can write a file with functions and
give the entrypoint style path as the entrypoint.

**TODO** Currently there are only contribution docs for extending
Alice please contribute recommended community standards.

TODO/Misc.
**********

- Tell people not to write stuff in init files

- Fix the docs build

- Test this with the modified consoletest which doesn't
  just take blocks with ``:test:`` on them (so that they render
  on GitHub).

- Example of running static type checker (``mypy`` or something
  on ``myconfig.py``, ``dffml`` has incomplete type data, we
  have an open issue on this.

- Cover how overlay load infrastructure can be added too,
  beyond these default only merge on apply `@overlays.present` (of
  which `@overlay` is an alias).

- In "Contributing a Plugin to the 2nd or 3rd Party Ecosystem"
  link to 2nd Party ADR.

- CI job to export dataflow to schema to validate lists of
  values for correctness as different definitions.

- In "Installing in Development Mode" reference pip/setuptools
  docs on editable installs.

- Covered in DFFML maintainers docs that unit testing infrastructure is
  slightly different, we want to intergrate the output of
  https://github.com/intel/dffml/issues/619 once complete.

- Explain how to grab data to feed the Living Threat Model
  https://github.com/johnlwhiteman/living-threat-models

  - Overlay for insertion of all data in input network to database,
    or to file for caching.
