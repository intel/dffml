DataFlows - shouldi
===================

This example will show you how to generate a dataset using operations. In the
process we'll create a meta static analysis tool, ``shouldi``.

Operations are the core of DFFML, they have inputs and outputs, are configurable
and are run by the Orchestrator in what amounts to a large event loop.
The events in the event loop are pieces of data entering the network. When a
piece of data which matches the data types of one of the operations inputs
enters the network, that operation is then run.

We're going to write a few operations which will run some Python static analysis
tools. With the goal being to create a command line utility called ``shouldi``
which will provide us with the information we need to make the decision, should
I install Python package X? When it's done it'll look like this

.. TODO Update example output

.. code-block:: console

    $ shouldi install dffml bandit
    dffml is okay to install
    Do not install insecure-package! {'safety_check_number_of_issues': 1}

Tools
-----

We'll write this meta static analysis tool by collecting and interpreting the
output of static analysis tools. The two tools we'll use are ``safety`` and
``bandit``.

``safety`` is a tool that checks for known vulnerabilities in packages published
on PyPi. This is how running safety on the command line works, we supply the
package name and version.

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

``bandit`` is a tool that does static analysis on the source code of Python
projects to check for things like SQL injections. This is how running ``bandit``
on the command line works, we supply the path to the source directory to scan.

.. code-block:: console

    $ bandit -r distributed-android-testing/
    [main]  INFO    profile include tests: None
    [main]  INFO    profile exclude tests: None
    [main]  INFO    cli include tests: None
    [main]  INFO    cli exclude tests: None
    [main]  INFO    running on Python 3.7.3
    67 [0.. 50.. ]
    Run started:2019-10-04 19:41:06.701058

    Test results:
    >> Issue: [B108:hardcoded_tmp_directory] Probable insecure usage of temp file/directory.
       Severity: Medium   Confidence: Medium
       Location: distributed-android-testing/docker/docker.py:20
       More Info: https://bandit.readthedocs.io/en/latest/plugins/b108_hardcoded_tmp_directory.html
    19              "chmod 700 /tmp/docker_install.sh",
    20              "/tmp/docker_install.sh",
    21              "usermod -aG docker ${USER}",
    22              "service docker restart"
    23          ]
    24          kwargs["sudo"] = True
    25          ssh.run_all(command, **kwargs)

    --------------------------------------------------
    >> Issue: [B104:hardcoded_bind_all_interfaces] Possible binding to all interfaces.
       Severity: Medium   Confidence: Medium
       Location: distributed-android-testing/docker/gitlab_webhooks/app.py:23
       More Info: https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html
    22      PORT = 9898
    23      ADDRESS = "0.0.0.0"
    24      STREAM = True

Plan
----

Our plan is to run these tools and make a decision as to if we should install
the package or not based on their reports.

The first step will be to write an ``Operation`` which wraps each tool.

An ``Operation`` is similar to a function signature, it consists of a name,
inputs, and outputs. The ``op`` decorator is a shorthand way of creating an
``Operation`` from a function. An ``Operation`` is analogous to a function
prototype in C.

Creating our Package
--------------------

Create a new package using the create script.

.. code-block:: console

    $ dffml service dev create operations shouldi
    $ cd shouldi

.. note::

    All the code for this example is located under the
    `examples/shouldi <https://github.com/intel/dffml/blob/master/examples/shouldi/>`_
    directory of the DFFML source code.

Installing Static Analysis Tools
--------------------------------

The tools we'll be using are ``bandit`` and ``safety``. We'll also need to make
http requests so let's install ``aiohttp`` too.

Some people are familiar with the ``requirements.txt`` file used to declare
dependences. For packages, we can declare our dependencies right in our
``setup.py`` file.

**setup.py**

.. code-block:: python

    SETUP_KWARGS["install_requires"] += [
        "aiohttp>=3.5.4",
        "bandit>=1.6.2",
        "safety>=1.8.5"
    ]

.. note::

    These versions will change over time, you should always check PyPi to find
    the latest version and use that version.

.. TODO Add link to pip oddities doc here once it exists

Now install the newly created package in development mode.

.. code-block:: console

    $ python3.7 -m pip install -e .

Safety Operation
----------------

To get parsable output, we'll run ``safety`` with the ``--json`` flag.

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

Bandit Operation
----------------

To get parsable output, we'll run with the ``-f json`` flag.

.. code-block:: console

    $ bandit -r -f json distributed-android-testing/
    {
      "metrics": {
        "_totals": {
          "CONFIDENCE.HIGH": 9.0,
          "CONFIDENCE.LOW": 0.0,
          "CONFIDENCE.MEDIUM": 3.0,
          "CONFIDENCE.UNDEFINED": 0.0,
          "SEVERITY.HIGH": 0.0,
          "SEVERITY.LOW": 10.0,
          "SEVERITY.MEDIUM": 2.0,
          "SEVERITY.UNDEFINED": 0.0,
          "loc": 5658,
          "nosec": 0
        }
      },
      "results": [
        {
          "code": "19         \"chmod 700 /tmp/docker_install.sh\",\n20         \"/tmp/docker_install.sh\",\n21         \"usermod -aG docker ${USER}\",\n22         \"service docker restart\"\n23     ]\n24     kwargs[\"sudo\"] = True\n25     ssh.run_all(command, **kwargs)\n",
          "filename": "distributed-android-testing/docker/docker.py",
          "issue_confidence": "MEDIUM",
          "issue_severity": "MEDIUM",
          "issue_text": "Probable insecure usage of temp file/directory.",
          "line_number": 20,
          "line_range": [
            18,
            19,
            20,
            21,
            22
          ],
          "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b108_hardcoded_tmp_directory.html",
          "test_id": "B108",
          "test_name": "hardcoded_tmp_directory"
        },
        {
          "code": "22 PORT = 9898\n23 ADDRESS = \"0.0.0.0\"\n24 STREAM = True\n",
          "filename": "distributed-android-testing/docker/gitlab_webhooks/app.py",
          "issue_confidence": "MEDIUM",
          "issue_severity": "MEDIUM",
          "issue_text": "Possible binding to all interfaces.",
          "line_number": 23,
          "line_range": [
            23
          ],
          "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html",
          "test_id": "B104",
          "test_name": "hardcoded_bind_all_interfaces"
        }
      ]
    }


Let's now write the operation to call ``safety`` via a subprocess.

.. literalinclude:: /../examples/shouldi/shouldi/bandit.py

Write a test for it

.. literalinclude:: /../examples/shouldi/tests/test_bandit.py

Run the tests

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_bandit

What's the Data Flow?
---------------------

So far ``shouldi`` uses two tools.

- ``bandit``

  - Which runs checks on the source code of a package to look for things like
    SQL injections

- ``safety``

  - Which checks if there are any open CVEs in a package

We're only planning on providing our tool with the package name though, and
we'll need the package version to run ``safety`` and the source code of the
package to run ``bandit``.

Let's outline what else needs to happen to get the package version and source
code of the package to those operations.

- In the processing stage we run all our data collection operations

  - Our input is the ``package`` name

    - This will be given to us on the command line

  - Access the PyPi API and get the JSON describing the package information

  - Concurrently

    - Extract the version from the package information

      -  Run ``safety`` using the version and the package name

    - Extract the URL of the latest release from the package information

      - Use the URL to download and extract the package source to a directory

        - Run ``bandit`` using the package source directory

- In the cleanup stage we release resources created in the processing stage

  - Remove the package source directory

- In the output stage we run operations which select data generated in the
  processing stage and use that selected data as the output of the dataflow.

  - Run the ``get_single`` operation which selects data matching the definitions
    we care about.

This is the directed graph that defines the dataflow of operations that make
up ``shouldi`` it shows us how all the operation we talked about above are
connected.

.. TODO Autogenerate this from the dataflow

.. image:: /images/shouldi-dataflow.png
    :alt: Diagram showing Dataflow

PyPi Operations
---------------

Let's write an operation to grab the version of a package.

.. literalinclude:: /../examples/shouldi/shouldi/pypi.py

Write a test for it

.. literalinclude:: /../examples/shouldi/tests/test_pypi.py

Run the tests

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_pypi

.. TODO Add they operations to setup.py entry_points

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
