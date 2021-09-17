InnerSource Portal
==================

Example of using DFFML to create a web app to discover information about
software. The purpose of this example is to write an application using
dataflows. We'll show how a dataflow based architecture results in a
software development workflow that makes is easy for a large group of developers
to collaborate quickly and effectively.

All the code for this example project is located under the
`examples/innersource/swportal <https://github.com/intel/dffml/blob/master/examples/innersource/swportal/>`_
directory of the DFFML source code.

History
-------

DFFML was initially developed for use in an allowlist tool. The allowlist tool
was similar to the InnerSource portal in that it collected and displayed metrics
on software projects. It also ran those collected metrics through a machine
learning model to assign a classification to the projects.

The "Down the Dependency Rabbit Hole" talk from BSides PDX 2019 provides more
detail on this history and architecture. The following link will skip to the
metric gathering portion of the presentation which is the part of the talk most
relevant to this example.
https://www.youtube.com/watch?v=D9puJiKKKS8&t=328s

Frontend
--------

We'll be leveraging the InnerSource portal built by SAP
https://github.com/SAP/project-portal-for-innersource as our frontend.

You need to have nodejs installed (and ``yarn``, or can replace it with ``npm``)
before you can run the following commands.

.. image:: https://github.com/SAP/project-portal-for-innersource/raw/main/docs/overview.png
    :alt: Screenshot of SAP InnerSource portal showing grid of projects

We need to download the code first for the portal first. We'll be working from a
snapshot so you'll see a long string of hex which is the git commit. We download
the code and rename the downloaded directory to ``html-client``.

.. code-block:: console
    :test:

    $ curl -sfL 'https://github.com/SAP/project-portal-for-innersource/archive/8a328cf30f5626b3658577b223d990af6285c272.tar.gz' | tar -xvz
    $ mv project-portal-for-innersource-8a328cf30f5626b3658577b223d990af6285c272 html-client

Now we go into the html-client directory, install the depenedencies, and start
the server.

.. code-block:: console
    :test:
    :daemon: 8080

    $ cd html-client
    $ yarn install
    yarn install v1.22.5
    info No lockfile found.
    [1/4] Resolving packages...
    [2/4] Fetching packages...
    [3/4] Linking dependencies...
    [4/4] Building fresh packages...
    success Saved lockfile.
    Done in 2.38s.
    $ yarn start
    yarn run v1.22.5
    Starting up http-server, serving.
    Available on:
      http://127.0.0.1:8080
    Hit CTRL-C to stop the server

Now open a new terminal, make sure you're in the directory we started in, so
that ``html-client`` is a subdirectory. You may need to change directory to the
parent directory.

.. code-block:: console
    :test:

    $ cd ..
    $ ls -l

Crawler
-------

This tutorial focuses on building the "crawler", which is the code that grabs
metrics on each project in the portal.

The crawler is responsible for generating the metrics seen on each project modal
popup.

You can read more about what the expectations for the crawler are here:
https://github.com/SAP/project-portal-for-innersource/blob/main/docs/CRAWLING.md

.. image:: https://github.com/SAP/project-portal-for-innersource/raw/main/docs/details.png
    :alt: Screenshot of SAP InnerSource portal showing project details popup

Constraints
-----------

We have a number of constraints for this example.

- The repos we are interested in displaying are all hosted in GitHub. We can
  find the information we need stored on the file system. (See the
  `orgs <https://github.com/intel/dffml/blob/master/examples/innersource/swportal/orgs/>`_
  directory to see what this looks like).

 - The structure is such that GitHub orgs are directories. Each directory
   has a ``repos.yml`` file in it. There may be multiple YAML documents per
   file. Each YAML document gives the repo name and the repo owners.

- Different repo owners will want to collect and display different metrics in
  their project's detail page.

  - We want to make is easy for developers to reuse existing code and data when
    collecting new metrics.

  - We'll use DataFlows to collect metrics

- We must output in `repos.json
  <https://github.com/SAP/project-portal-for-innersource/blob/main/repos.json>`_
  format that the SAP portal frontend knows how to consume.

Architecture
------------

The following diagram shows the high level architecture of a crawler that
satisfies our constraints.

..
    flowchart TD
        repos_yml_source[read repo.yml files]
        repos_json_source[repos.json]
        dataflow[run dataflow]
        repos_yml_source -->|for each repo| dataflow
        dataflow -->|write| repos_json_source

.. image:: /images/swportal-high-level-architecture.svg
    :alt: Flow chart showing high level architechture where we read the repos.yml files run the dataflow on each repo, then save to the repos.json source.

Implementation Plan
-------------------

We'll be leveraging three major DFFML concepts as we implement our crawler.
These are Sources, and DataFlows & Operations.

- The input ``repo.yml`` files and the output ``repos.json`` file are ideal
  candidates for DFFML Sources.

  - A Source in DFFML is anything containing records which can be referenced by
    a unique identifier.

  - A GitHub repo can be uniquely identified by it's organization / user and
    it's name.

- Collecting a dataset, in this case metrics for a given repo, is a job for a
  DataFlow.

  - We can combine many different Operations together to collect metrics.

  - We're going to query GitHub for some metrics / data.

  - We're going to re-use metric gathers from the allowlist tool.

Input Data
----------

Let's create the ``orgs/`` directory, and two subdirectories. One for the
``intel`` GitHub organization, and one for the ``tpm2-software`` organization.
These directories will contain the ``repos.yml`` files.

.. code-block:: console
    :test:

    $ mkdir orgs/
    $ mkdir orgs/intel/
    $ mkdir orgs/tpm2-software/

Create the following files. For the sake of this example, the YAML file format
we're working with has multiple YAML documents per file, separated with ``---``.
Each document represents a GitHub repo. Each document gives the name of the repo
and the repo owners.

**orgs/intel/repos.yml**

.. literalinclude:: /../examples/innersource/swportal/orgs/intel/repos.yml
    :test:
    :filepath: orgs/intel/repos.yml

**orgs/tpm2-software/repos.yml**

.. literalinclude:: /../examples/innersource/swportal/orgs/tpm2-software/repos.yml
    :test:
    :filepath: orgs/tpm2-software/repos.yml

Reading Inputs
--------------

Create a directory where we'll store all of the sources (Python classes)
we'll use to read and write repo data / metrics.

.. code-block:: console
    :test:

    $ mkdir sources/

Install the PyYAML library, which we'll use to parse the YAML files.

.. code-block:: console
    :test:

    $ python -m pip install PyYAML

We'll implement a DFFML Source for the ``repos.yml`` files which live under
directories named after their respective GitHub orgs.

We'll back the repos in memory when we load them in, and don't need to support
writing them back out for this source.

**TOOD** See https://youtu.be/VogNhBMmsNk for more details on implemention until
this section gets further writing.

**sources/orgs_repos_yml.py**

.. literalinclude:: /../examples/innersource/swportal/sources/orgs_repos_yml.py
    :test:
    :filepath: sources/orgs_repos_yml.py

We list all the records for a source using the DFFML command line and the Python
entry point path to the class we just implemented
(``module.submodule:ClassName``). Each repo is a record.

.. code-block:: console
    :test:

    $ dffml list records \
        -sources orgs=sources.orgs_repos_yml:OrgsReposYAMLSource \
        -source-orgs-directory orgs/
    [
        {
            "extra": {},
            "features": {
                "name": "dffml",
                "owners": [
                    "johnandersenpdx@gmail.com"
                ]
            },
            "key": "https://github.com/intel/dffml"
        },
        {
            "extra": {},
            "features": {
                "name": "cve-bin-tool",
                "owners": [
                    "terri@toybox.ca"
                ]
            },
            "key": "https://github.com/intel/cve-bin-tool"
        },
        {
            "extra": {},
            "features": {
                "name": "tpm2-pkcs11",
                "owners": [
                    "william.c.roberts@intel.com"
                ]
            },
            "key": "https://github.com/tpm2-software/tpm2-pkcs11"
        },
        {
            "extra": {},
            "features": {
                "name": "tpm2-tools",
                "owners": [
                    "imran.desai@intel.com"
                ]
            },
            "key": "https://github.com/tpm2-software/tpm2-tools"
        }
    ]

Writing Outputs
---------------

We also need to implement DFFML Source for the ``repos.json`` file which is in
the format that the frontend knows how to display.

The builtin DFFML JSON format source outputs an object, whereas the frontend
expects an array. So we need to dump the Record feature data (which is where we
put the metrics and repo information), to and from the file.

We'll implement both reading and writing for this source, so that we can verify
it works easily via reading. Also because it's easy enough to implement since
we'll be subclassing from the ``FileSource`` and ``MemorySource`` which means we
only have to implement loading from the file descriptor (``fd``) and saving back
to it.

**TOOD** See https://youtu.be/VogNhBMmsNk for more details on implemention until
this section gets further writing.

**sources/sap_portal_repos_json.py**

.. literalinclude:: /../examples/innersource/swportal/sources/sap_portal_repos_json.py
    :test:
    :filepath: sources/sap_portal_repos_json.py

Try listing all the records in the new source to verify it works.

.. code-block:: console
    :test:

    $ dffml list records \
        -sources portal=sources.sap_portal_repos_json:SAPPortalReposJSONSource \
        -source-portal-filename html-client/repos.json
    [
        {
            "extra": {},
            "features": {
                "_InnerSourceMetadata": {
                    "logo": "./images/demo/Earth.png",
                    "participation": [
                        15,
                        3,
                        7,
                        2,
                        7,
                        6,
                        11,
                        4,
                        9,
                        11,
                        4,
                        0,
                        4,
                        6,
                        3,
                        2,
                        6,
                        4,
                        3,
                        5,
                        9,
                        1,
                        2,
                        2,
                        7,
                        6,
                        7,
                        25,
                        9,
                        7,
                        9,
                        10,
                        7,
                        3,
                        8,
                        10,
                        13,
                        6,
                        5,
                        4,
                        9,
                        6,
                        8,
                        8,
                        10,
                        3,
                        3,
                        6,
                        2,
                        8,
                        12,
                        8
                    ],
                    "score": 3900,
                    "topics": [
                        "earth",
                        "JavaScript",
                        "Sol"
                    ]
                },
                "created_at": "2017-01-31T09:39:12Z",
                "default_branch": "master",
                "description": "Earth is the third planet from the Sun and the home-world of humanity.",
                "forks_count": 331,
                "full_name": "Sol/earth",
                "html_url": "https://github.instance/Sol/earth",
                "id": 2342,
                "language": "JavaScript",
                "license": null,
                "name": "earth",
                "open_issues_count": 98,
                "owner": {
                    "avatar_url": "./images/demo/Sol.png",
                    "login": "Sol"
                },
                "pushed_at": "2020-10-08T12:18:22Z",
                "stargazers_count": 136,
                "updated_at": "2020-10-07T09:42:53Z",
                "watchers_count": 136
            },
            "key": "https://github.instance/Sol/earth"
        },
        <... output clipped ...>

Querying GitHub
---------------

Create a directory where we'll store all of the operations (Python functions)
we'll use to gather project data / metrics.

.. code-block:: console
    :test:

    $ mkdir operations/

Make it a Python module by creating a blank ``__init__.py`` file in it.

.. code-block:: console
    :test:

    $ touch operations/__init__.py

Install the PyGithub library, which we'll use to access the GitHub API.

.. code-block:: console
    :test:

    $ python -m pip install PyGithub

You'll need a Personal Access Token to be able to make calls to GitHub's API.
You can create one by following their documentation.

- https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token

When it presents you with a bunch of checkboxes for difference "scopes" you
don't have to check any of them, unless you want to access your own private
repos, then check the repos box.

.. code-block:: console

    $ export GITHUB_TOKEN=<paste your personal access token here>

You've just pasted your token into your terminal so it will likely show up in
your shell's history. You might want to either remove it from your history, or
just delete the token on GitHub's settings page after you're done with this
tutorial.

Write a Python function which returns an object representing a GitHub repo. For
simplicity of this tutorial, the function will take the token from the
environment variable we just set.

**operations/gh.py**

.. literalinclude:: /../examples/innersource/swportal/operations/gh.py
    :test:
    :filepath: operations/gh.py

You'll notice that we wrote a function, and then put an ``if`` statement. The
``if`` block let's us only run the code within the block when the script is run
directly (rather than when included via ``import``).

If we run Python on the script, and pass an org name followed by a repo name,
our ``if`` block will run the function and print the raw data of the repsonse
received from GitHub, containing a bunch of information about the repo.

You'll notice that the data being output here is a superset of the data we'd see
for the repo in the ``repos.json`` file. Meaning we have all the required data
and more.

.. code-block:: console
    :test:

    $ python operations/gh.py intel dffml
    {'allow_auto_merge': False,
     <... output clipped ...>
     'full_name': 'intel/dffml',
     <... output clipped ...>
     'html_url': 'https://github.com/intel/dffml',
     <... output clipped ...>
     'watchers_count': 135}

DataFlow
--------

Let's create a backup of the ``repos.json`` file, since we'll be overwriting it
with our own.

.. code-block:: console
    :test:

    $ cp html-client/repos.json repos.json.bak

We're going to create a Python script which will use all the operations we've
written, and the sources.

**dataflow.py**

.. literalinclude:: /../examples/innersource/swportal/dataflow.py
    :test:
    :filepath: dataflow.py

We can run the file the run the dataflow on all the input repos and save the
results to ``repos.json``.

.. code-block:: console
    :test:

    $ python dataflow.py

If you go to http://127.0.0.1:8080

.. image:: https://user-images.githubusercontent.com/5950433/128045522-54b3193c-826b-48aa-b82e-96306831d595.png
    :alt: Screenshot of SAP InnerSource portal showing new projects

We can also export the dataflow for use with the CLI, HTTP service, etc.

**TODO** Add link to webui when complete. It will be used for editing dataflows.
ETA Oct 2021.

.. code-block:: console
    :test:

    $ dffml service dev export dataflow:dataflow | tee dataflow.json

We can run the dataflow using the DFFML command line interface rather than
running the Python file.

The following command replicates loading from the ``orgs/`` source and updating
the ``repos.json`` source. Just as we did in Python, we add the record key to
each dataflow run as an input with the definition being ``github.repo.url``.
You can add ``-log debug`` to see verbose output.

.. code-block:: console
    :test:

    $ dffml dataflow run records all \
        -dataflow dataflow.json \
        -record-def "github.repo.url" \
        -sources \
          orgs=sources.orgs_repos_yml:OrgsReposYAMLSource \
          portal=sources.sap_portal_repos_json:SAPPortalReposJSONSource \
        -source-orgs-directory orgs/ \
        -source-portal-filename html-client/repos.json \
        -source-portal-readwrite \
        -update

If you want to run the dataflow on a single repo and add the data to the
repos.json file, you can do it as follows.

.. code-block:: console
    :test:

    $ dffml dataflow run records set \
        -dataflow dataflow.json \
        -record-def "github.repo.url" \
        -sources \
          portal=sources.sap_portal_repos_json:SAPPortalReposJSONSource \
        -source-portal-filename html-client/repos.json \
        -source-portal-readwrite \
        -update \
        -keys \
          https://github.com/intel/dffml

If you want to run the dataflow on a single repo, without updating the source,
you can do it as follows, by omiting the source related arguments.

.. code-block:: console
    :test:

    $ dffml dataflow run records set \
        -dataflow dataflow.json \
        -record-def "github.repo.url" \
        -keys \
          https://github.com/intel/dffml
