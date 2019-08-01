Data Set Generation
===================

This example will show you how to generate a dataset using operations.

Operations are the core of DFFML, they have inputs and outputs, are configurable
and are run by the Data Flow Facilitator in what amounts to a large event loop.
The events in the event loop are pieces of data entering the network. When a
piece of data which matches the data types of one of the operations inputs
enters the network, that operation is then run.

We're going to write a few operations which will run some Python static analysis
tools. With the goal being to create a command line utility called ``shouldi``
which will provide us with the information we need to make the decision, should
I install Python package X? When it's done it'll look like this

.. code-block:: console

    $ shouldi install insecure-package bandit
    bandit is okay to install
    Do not install insecure-package! {'safety_check_number_of_issues': 1}

Creating our Package
--------------------

Clone a copy of DFFML and navigate the top of the source directory.

Create a new package using the create script.

.. code-block:: console

    $ ./scripts/create.sh operations shouldi

You can now move this to another directory if you wish (the copy for this
example is located under ``examples/shouldi``.

.. code-block:: console

    $ mv operations/shouldi ../shouldi
    $ cd ../shouldi

We're going to change the name of the package to ``shouldi`` instead of the
default, ``dffml_operations_shouldi``.

**setup.py**

.. code-block:: python

    NAME = "shouldi"

We need to rename the directory as well.

.. code-block:: console

    $ mv dffml_operations_shouldi shouldi

And the directory within the coveragerc file

**.coveragerc**

.. code-block:: python

    source =
        shouldi
        tests

Now install your freshly renamed module!

.. code-block:: console

    $ python3.7 -m pip install -e .

Installing Static Analysis Tools
--------------------------------

For simplicities sake the beginning of this example will use subprocesses to
interact with command line Python static analysis tools. Let's install them all
via ``pip``.

.. code-block:: console

    $ python3.7 -m pip install -U safety pylint bandit

We need to make http requests so let's install ``aiohttp``.

**setup.py**

.. code-block:: python

    INSTALL_REQUIRES = [
        "aiohttp>=3.5.4"
        ]

Our Zeroth Operation
--------------------

We'll write an operation to check for CVEs in a package by using ``safety``.

Safety uses the package name and version to tell us if there are any security
issues in the package for that version.

To use safety, we have to have the version of the package we want to check.

Let's write an operation to grab the version of a package.

.. literalinclude:: /../examples/shouldi/shouldi/pypi.py

Write a test for it

.. literalinclude:: /../examples/shouldi/tests/test_pypi.py

Run the tests

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_pypi

Safety Operation
----------------

The output of the last operation will automatically be combined with the package
name to create a call you our new operation, ``SafetyCheck``.

This is how running safety on the command line works.

.. code-block:: console

    $ echo insecure-package==0.1.0 | safety check --stdin
    ╒══════════════════════════════════════════════════════════════════════════════╕
    │                                                                              │
    │                               /$$$$$$            /$$                         │
    │                              /$$__  $$          | $$                         │
    │           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           │
    │          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           │
    │         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           │
    │          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           │
    │          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           │
    │         |_______/  \_______/|__/     \_______/   \___/   \____  $$           │
    │                                                          /$$  | $$           │
    │                                                         |  $$$$$$/           │
    │  by pyup.io                                              \______/            │
    │                                                                              │
    ╞══════════════════════════════════════════════════════════════════════════════╡
    │ REPORT                                                                       │
    │ checked 1 packages, using default DB                                         │
    ╞════════════════════════════╤═══════════╤══════════════════════════╤══════════╡
    │ package                    │ installed │ affected                 │ ID       │
    ╞════════════════════════════╧═══════════╧══════════════════════════╧══════════╡
    │ insecure-package           │ 0.1.0     │ <0.2.0                   │ 25853    │
    ╘══════════════════════════════════════════════════════════════════════════════╛

We want parsable output, so let's try it with the ``--json`` flag.

.. code-block:: console

    $ echo insecure-package==0.1.0 | safety check --stdin --json
    [
        [
            "insecure-package",
            "<0.2.0",
            "0.1.0",
            "This is an insecure package with lots of exploitable security vulnerabilities.",
            "25853"
        ]
    ]

Let's now write the operation to call ``safety`` via a subprocess.

.. literalinclude:: /../examples/shouldi/shouldi/safety.py

Write a test for it

.. literalinclude:: /../examples/shouldi/tests/test_safety.py

Run the tests

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_safety

.. TODO Add they operations to setup.py entry_points

.. TODO Add bandit

.. TODO Add pylint

CLI
---

Writing the CLI is as simple as importing our operations and having the memory
orchestrator run them. DFFML also provides a quick and dirty CLI abstraction
based on :py:mod:`argparse` which will speed things up.

.. TODO explain more about writing the CLI and the orchestrator

**shouldi/cli.py**

.. literalinclude:: /../examples/shouldi/shouldi/cli.py

Let's test out the code in ``shouldi.cli`` before making it accessible via the
command line.

.. literalinclude:: /../examples/shouldi/tests/test_cli.py

Run the all the tests this time

.. code-block:: console

    $ python3.7 setup.py test

If you have coverage installed (``pip install coverage``) you can also check the
code coverage.

.. code-block:: console

    $ python3.7 -m coverage run setup.py test
    running test
    running egg_info
    writing shouldi.egg-info/PKG-INFO
    writing dependency_links to shouldi.egg-info/dependency_links.txt
    writing entry points to shouldi.egg-info/entry_points.txt
    writing requirements to shouldi.egg-info/requires.txt
    writing top-level names to shouldi.egg-info/top_level.txt
    reading manifest file 'shouldi.egg-info/SOURCES.txt'
    reading manifest template 'MANIFEST.in'
    writing manifest file 'shouldi.egg-info/SOURCES.txt'
    running build_ext
    test_run (tests.test_safety.TestSafetyCheck) ... ok
    test_install (tests.test_cli.TestCLI) ... ok
    test_run (tests.test_pypi.TestPyPiLatestPackageVersion) ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 1.282s

    OK
    $ python3.7 -m coverage report -m
    Name                     Stmts   Miss Branch BrPart  Cover   Missing
    --------------------------------------------------------------------
    shouldi/__init__.py          0      0      0      0   100%
    shouldi/cli.py              27      0      6      0   100%
    shouldi/definitions.py       5      0      2      0   100%
    shouldi/pypi.py             12      0      2      0   100%
    shouldi/safety.py           18      0      0      0   100%
    shouldi/version.py           1      0      0      0   100%
    tests/__init__.py            0      0      0      0   100%
    tests/test_cli.py           11      0      0      0   100%
    tests/test_pypi.py           9      0      0      0   100%
    tests/test_safety.py         9      0      0      0   100%
    --------------------------------------------------------------------
    TOTAL                       92      0     10      0   100%

We want this to be usable as a command line utility, Python's
:py:mod:`setuptools` allows us to define console ``entry_points``. All we have
to do is tell :py:mod:`setuptools` what Python function we want it to call when
a user runs a given command line application. The name of our CLI is ``shouldi``
and the function we want to run is ``main`` in the ``ShouldI`` class which is in
the ``shouldi.cli`` module.

**setup.py**

.. code-block:: python

    entry_points={"console_scripts": ["shouldi = shouldi.cli:ShouldI.main"]},

Re-install the package via pip

.. code-block:: console

    $ python3.7 -m pip install -e .

Now we should be able to run our new tool via the CLI! (Provided your ``$PATH``
is set up correctly.

.. code-block:: console

    $ shouldi install insecure-package bandit
    bandit is okay to install
    Do not install insecure-package! {'safety_check_number_of_issues': 1}
