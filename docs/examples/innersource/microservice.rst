InnerSource Microservice
========================

We created a crawler in the previous tutorial
:doc:`/examples/innersource/swportal`. Now we are going to deploy a micro
service which evaluates a single repo at a time using the same DataFlow we used
for the crawler.

Our end result will be a container which serves a JSON API endpoint. We can
send a request to the endpoint to evaluate metrics for an InnerSource repo.

Config Files
------------

As we've seen before, DataFlows can be serialized to config files. JSON
representations of DataFlows are not fun to hand edit. YAML looks a lot cleaner.

We're going to install the ``dffml-config-yaml`` package so that we don't have
to look at JSON.

.. code-block:: console
    :test:

    $ python -m pip install dffml-config-yaml

HTTP Service
------------

We're going to install the ``dffml-service-http`` package which will be the
server process of our microservice.

.. code-block:: console
    :test:

    $ python -m pip install dffml-service-http

To deploy our previous InnerSource crawler dataflow via the HTTP API, we need to
register a communication channel, which is the association of a URL path to the
dataflow.

We create a config file for the ``MultiComm`` we'll be using. ``MultiComm``
config files go under the ``mc`` directory of the directory being
used to deploy. Then config file itself then goes under the name of the
``MultiComm`` its associated with, ``http`` in this instance.

The HTTP service provides multiple channels of communication which we can attach
DataFlows to. These end up being URL paths in the case of the HTTP server.

We need to create a directory for the URL to DataFlow configuration mappings to
live in.

.. code-block:: console
    :test:

    $ mkdir -p mc/http

The file is populated with the URL path that should trigger the dataflow, how to
present the output data, and if the dataflow should return when all outputs
exist, or if it should continue waiting for more inputs (``asynchronous``, used
for websockets / http2).

**mc/http/metrics.yaml**

.. code-block:: yaml
    :test:
    :filepath: mc/http/metrics.yaml

    path: /metrics
    output_mode: json
    asynchronous: false

We also need to create a directory for the DataFlow to live in.

.. code-block:: console
    :test:

    $ mkdir df/

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

We're going to create a Python script which will use all the operations we've
written.

We need to download the ``repos.json`` file from the previous example so that we
know what fields our DataFlow should output.

.. code-block:: console
    :test:

    $ curl -fLo repos.json.bak https://github.com/SAP/project-portal-for-innersource/raw/main/repos.json

First we declare imports of other packages.

**dataflow.py**

.. literalinclude:: /../examples/innersource/swportal/dataflow.py
    :test:
    :filepath: dataflow.py
    :lines: 1-6

Then we import our operations.

**dataflow.py**

.. literalinclude:: /../examples/innersource/swportal/dataflow.py
    :test:
    :filepath: dataflow.py
    :lines: 12-13

Finally we define our dataflow.

**dataflow.py**

.. literalinclude:: /../examples/innersource/swportal/dataflow.py
    :test:
    :filepath: dataflow.py
    :lines: 15-81

We export the dataflow for use with the CLI, HTTP service, etc.

**TODO** Add link to webui when complete. It will be used for editing dataflows.
ETA Oct 2021.

.. code-block:: console
    :test:

    $ dffml service dev export dataflow:dataflow | tee df/metrics.json

We can run the dataflow using the DFFML command line interface rather than
running the Python file.

If you want to run the dataflow on a single repo, you can do it as follows.

.. code-block:: console
    :test:

    $ dffml dataflow run records set \
        -dataflow df/metrics.json \
        -record-def "github.repo.url" \
        -keys \
          https://github.com/intel/dffml

Serving the DataFlow
--------------------

.. warning::

    The ``-insecure`` flag is only being used here to speed up this
    tutorial. See documentation on HTTP API
    :doc:`/plugins/service/http/security` for more information.

We now start the http server and tell it that the ``MultiComm`` configuration
directory (``mc/``) can be found in the current directory, ``.``.

.. code-block:: console
    :test:
    :daemon: 8080

    $ dffml service http server -port 8080 -insecure -mc-config .

In another terminal, you can send a ``POST`` request containing the ``Input``
items that you want evaluated.

.. code-block:: console
    :test:
    :replace: cmds[0][-5] = cmds[0][-5].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))

    $ curl -sf \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"https://github.com/intel/dffml": [{"value":"https://github.com/intel/dffml","definition":"github.repo.url"}]}' \
      http://localhost:8080/metrics | python -m json.tool
		[
        {
            "extra": {},
            "features": {
                "created_at": "2018-09-19T21:06:34Z",
                "default_branch": "master",
                "description": "The easiest way to use Machine Learning. Mix and match underlying ML libraries and data set sources. Generate new datasets or modify existing ones with ease.",
                "forks_count": 118,
                "full_name": "intel/dffml",
                "html_url": "https://github.com/intel/dffml",
                "id": 149512216,
                "language": "Python",
                "license": {
                    "key": "mit",
                    "name": "MIT License",
                    "node_id": "MDc6TGljZW5zZTEz",
                    "spdx_id": "MIT",
                    "url": "https://api.github.com/licenses/mit"
                },
                "name": "dffml",
                "open_issues_count": 296,
                "owner": {
                    "avatar_url": "https://avatars.githubusercontent.com/u/17888862?v=4",
                    "events_url": "https://api.github.com/users/intel/events{/privacy}",
                    "followers_url": "https://api.github.com/users/intel/followers",
                    "following_url": "https://api.github.com/users/intel/following{/other_user}",
                    "gists_url": "https://api.github.com/users/intel/gists{/gist_id}",
                    "gravatar_id": "",
                    "html_url": "https://github.com/intel",
                    "id": 17888862,
                    "login": "intel",
                    "node_id": "MDEyOk9yZ2FuaXphdGlvbjE3ODg4ODYy",
                    "organizations_url": "https://api.github.com/users/intel/orgs",
                    "received_events_url": "https://api.github.com/users/intel/received_events",
                    "repos_url": "https://api.github.com/users/intel/repos",
                    "site_admin": false,
                    "starred_url": "https://api.github.com/users/intel/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/intel/subscriptions",
                    "type": "Organization",
                    "url": "https://api.github.com/users/intel"
                },
                "pushed_at": "2021-09-17T03:31:18Z",
                "stargazers_count": 143,
                "updated_at": "2021-08-31T16:20:16Z",
                "watchers_count": 143
            },
            "key": "https://github.com/intel/dffml",
            "last_updated": "2021-09-17T09:39:30Z"
        }
    ]

