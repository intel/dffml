InnerSource Kubernetes
======================

**TODO** Initial description

Config Files
------------

As we've seen before, DataFlows can be serialized to config files. JSON
representations of DataFlows are not fun to hand edit. YAML looks a lot cleaner.

We're going to install the ``dffml-config-yaml`` package so that we don't have
to look at JSON.

.. code-block:: console
    :test:

    $ python -m pip install dffml-config-yaml

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

    $ dffml service dev export dataflow:dataflow | tee metrics.json

We can run the dataflow using the DFFML command line interface rather than
running the Python file.

If you want to run the dataflow on a single repo, you can do it as follows.

.. code-block:: console
    :test:

    $ dffml dataflow run records set \
        -dataflow metrics.json \
        -record-def "github.repo.url" \
        -keys \
          https://github.com/intel/dffml

kind
----

Kubernetes in docker if you don't already have a favorite way of making a
kubernetes cluster this is a good choice.

https://kind.sigs.k8s.io/docs/user/quick-start/

.. code-block:: console
    :test:

    $ curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.11.1/kind-linux-amd64
    $ chmod +x ./kind
    $ ./kind create cluster --wait 5m

Ideally we would use "Indexed Job for Parallel Processing with Static Work
Assignment"

- https://kubernetes.io/docs/tasks/job/indexed-parallel-processing-static/

- FEATURE STATE: Kubernetes v1.22 [beta]

Fallback is to use "Parallel Processing using Expansions"

- https://kubernetes.io/docs/tasks/job/parallel-processing-expansion/

Create jobs named uniquely based off of dataflow name and hash of dataflow (so
it's unique to what is executing, we can track which hash of the dataflow maps
to

- https://github.com/intel/dffml/issues/958

Map JOB_COMPLETION_INDEX to inputs for dataflow. Inputs contain repo URL, and
secrets associated with that run.

- https://kubernetes.io/docs/concepts/configuration/secret/

.. code-block:: yaml

    apiVersion: batch/v1
    kind: Job
    metadata:
      name: 'indexed-job'
    spec:
      completions: 5
      parallelism: 3
      completionMode: Indexed
      template:
        spec:
          restartPolicy: Never
          initContainers:
          - name: 'input'
            image: 'docker.io/library/bash'
            command:
            - "bash"
            - "-c"
            - |
              items=(foo bar baz qux xyz)
              echo ${items[$JOB_COMPLETION_INDEX]} > /input/data.txt
            volumeMounts:
            - mountPath: /input
              name: input
          containers:
          - name: 'worker'
            image: 'docker.io/library/busybox'
            command:
            - "rev"
            - "/input/data.txt"
            volumeMounts:
            - mountPath: /input
              name: input
          volumes:
          - name: input
            emptyDir: {}

.. code-block:: console
    :test:

    $ ./kind delete cluster
