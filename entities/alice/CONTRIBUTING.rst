CONTRIBUTING
############

This document describes how to write Open Architecture overlays,
overlays for Alice, how to work within the codebase, and the
contribution process.

Debugging
*********

Run within the builtin Python debugger to be presented with a
Python interpreter breakpointed at the raised exception.

.. code-block:: console

    $ python -m pdb -m alice

Cloning the Repo
****************

We are currently on the ``alice`` feature branch of DFFML. See
https://github.com/intel/dffml/pull/1401 for more details.

.. code-block:: console

    $ git clone -b alice https://github.com/intel/dffml

Now open or change directory to the directory containing Alice's
source code within the project ``entities/alice``.

.. code-block:: console

    $ cd dffml/entities/alice

Data Flow Programming
*********************

Data Flow programming focueses on data types and data transformations.
Data Orented Design is also helpful in understanding Data Flow programming,
altough a distinct concept itself.

- https://en.wikipedia.org/wiki/Dataflow_programming
- https://www.gamedeveloper.com/programming/tips-on-writing-code-for-data-oriented-design
- https://www.youtube.com/watch?v=aPh4Z3SioB8

Finding Data Types to Work With
*******************************

**TODO** Finish this section

**TODO** CI job to export dataflow to schema to validate lists of
values for correctness as different definitions.

.. code-block:: console

    $ dffml service dev export alice.please.contribute:AlicePleaseContributeRecommendedCommunityStandards | tee alice.please.contribute.recommended-community-standards.json
    ...
    $schema: https://github.com/intel/dffml/raw/alice/entities/alice/schema/alice.please.contribute.recommended-community-standards.schema.json
    ...

Need to do something like the following, this section should source from
"She's Arriving When?" once completed or push to there for now.

.. code-block::

    def recursive(entrypoint):
        for line in subprocess.check_output("dffml service dev entrypoints list {entrypoint}", shell=True).split():
            dffml service dev export {entrypoint}.$0 | tee {entrypoint}.$.json
            recursive(entrypoint + "." + $0)

Making a Game Plan
******************

Since we're thinking about data, we need to make a game plan, we don't
want to get caught up writing unnessicary code. We don't want to deal with
production or development database configuration, we just want to figure
out how to get the data we need, then figure out where / how we can plug
that data extraction, that feature extraction, into the any applicable
collector flows (**TODO** link to Living Threat Model terminology).

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
an on it's own with mock data. Think of it as the library behind your
functionality.

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
    ) -> MyConfig:
        """
        >>> import json
        >>> import pathlib
        >>> import tempfile
        >>>
        >>> with tempfile.TemporaryDirectory() as tempdir:
        ...     pathlib.Path(tempdir, ".myconfig.json").write_text(json.dumps({"name": "Hello World"}))
        ...     print(read_my_config_from_directory_if_exists(tempdir))
        {'name': 'Hello World'}
        """
        path = patlib.Path(directory, ".myconfig.json")
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

**TODO** In maintainers cover unit testing infrastructure is slightly
different, see issue https://github.com/intel/dffml/issues/619

.. code-block:: console

    $ python -m doctest myconfig.py

Writing an Overlay
******************

Overlays can be as simple as a single function, or they can
be classes, files, dataflows, anything which you can generate
and Open Architecture description of (which should be everything
provided an ``OperationImplementationNetwork`` is/can be implemented)

**myconfig_overlay_alice_please_contribute_recommended_community_standards_overlay_git_myconfig.py**

.. code-block:: python

    from alice.please.contribute.recommended_community_standards.git import AliceGitRepo

    from .myconfig import MyConfigDirectory

    def repo_directory(
        repo: AliceGitRepo,
    ) -> MyConfigDirectory:
        """
        >>> from alice.please.contribute.recommended_community_standards.git import AliceGitRepo
        >>>
        >>> print(repo_directory(AliceGitRepo(directory="Wonderland", URL=None)))
        Wonderland
        """
        return repo.directory

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

    [dffml.overlays.alice.please.contribute.recommended-community-standards.git]
    myconfig = myconfig

    [dffml.overlays.alice.please.contribute.recommended-community-standards.git.myconfig]
    git = myconfig_overlay_alice_please_contribute_recommended_community_standards_overlay_git_myconfig

Creating a Plugin
*****************

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

    $ dffml service dev create blank alice-please-contribute-recommended-community-standards-overlay-git-myconfig
    $ cd alice-please-contribute-overlay-git-myconfig

Move the old files into position

.. code-block:: console

    $ mv ../dffml.git/entities/alice/myconfig* alice_please_contribute_overlay_git_myconfig/

Registering a Flow
******************

You can write a base flow as a class and then give the entrypoint
style path to the class or you can write a file with functions and
give the entrypoint style path as the entrypoint.

**TODO** Cover how overlay load infrastructure can be added too,
beyond these default only merge on apply `@overlays.present` (of
which `@overlay` is an alias).

TODO/Misc.
**********

**TODO** modify **dffml.git/entities/alice/entry_points.txt**
add the following, rename files first.

.. code-block::

    [dffml.overlays.alice.please]
    contribute = alice.please.contribute.git:AlicePleaseContribute

    [dffml.overlays.alice.please.contribute]
    recommended-community-standards = alice.please.contribute:AlicePleaseContributeRecommendedCommunityStandards

    [dffml.overlays.alice.please.contribute.recommended-community-standards]
    git = alice.please.contribute.git:AlicePleaseContributeRecommendedCommunityStandardsOverlayGit
