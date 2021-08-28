Automating Classification
=========================

This example will show you how to automate a manual classification process,
determining if a Git repo is maintained or abandoned. We'll be integrating
Machine Learning into an existing application.

For this example assume you are a very curious open source software person.
You love looking at git repos in your free time. Every time you come
across a Git repo, you dig around, look at the number of committers, number of
commits, etc. and come up with maintenance status for the repo (maintained, or
unmaintained).

To help you track your assigned statues you built a Python 3 CGI web app.

.. image:: /images/website-before.png
    :alt: Screenshot of the very basic web app with a table showing repo URLs and their mantainance status

When you assign a maintenance status to a repo you are *classifying* it.
Instead of manually classifying each repo, we're going to put some machine
learning behind this little web app. The steps we're going to follow here are
generic, they do not apply specifically to this Python CGI setup, this is just
an example that was chosen because hopefully it'll be an easy setup.

CGI Application
---------------

The CGI application we'll be integrating with is comprised of five files. You
should create these files and populate them with the code your about to see.

- The webpage **index.html**

- The webpage's JavaScript **main.js**

- The webpage's CSS **theme.css**

- The backend api **cgi-bin/api.py**

First create the webpage

**index.html**

.. literalinclude:: /../examples/maintained/index.html
    :test:
    :language: html

Then the JavaScript, which will interact with the CGI API.

**main.js**

.. literalinclude:: /../examples/maintained/main.js
    :test:
    :language: javascript

The style sheet which gives the page colors and styling

**theme.css**

.. literalinclude:: /../examples/maintained/theme.css
    :test:
    :language: css

Now create the **cgi-bin** directory which is where our server side Python
script will run.

.. code-block:: console
    :test:

    $ mkdir cgi-bin

Then create the backend API script. This script connects to the database and
provides two actions.

- Classify a repo by setting its status to maintained or unmaintained

- Dump all repos along with their maintenance status which we've classified

**cgi-bin/api.py**

.. literalinclude:: /../examples/maintained/cgi-bin/api.py
    :test:
    :filepath: cgi-bin/api.py

We have to make the cgi-bin directory and API file executable so that the CGI
server can run it.

.. code-block:: console
    :test:

    $ chmod 755 cgi-bin cgi-bin/api.py

Setup
-----

We'll be using Python, and docker or podman. If you don't have docker installed,
but you do have podman installed, you can replace "docker" with "podman" in all
of the following commands.

Create a virtual environment where we'll install all our Python packages to.
Make sure to update ``pip`` in case it's old, and install ``setuptools`` and
``wheel`` so that we can install the MySQL package.

.. code-block:: console
    :test:

    $ python -m venv .venv
    $ . .venv/bin/activate
    $ python -m pip install -U pip setuptools wheel

Download the Python client libraries for MySQL.

.. code-block:: console
    :test:

    $ python -m pip install -U \
        https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-8.0.21.tar.gz

Start MariaDB (functionally very similar to MySQL which its a fork of).

.. code-block:: console
    :test:

    $ docker run --rm -d --name maintained_db \
        -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
        -e MYSQL_USER=user \
        -e MYSQL_PASSWORD=pass \
        -e MYSQL_DATABASE=db \
        -p 3306:3306 \
        mariadb:10

Wait for the database to start. Run the following command until you see ``ready
for connections`` twice in the output.

.. code-block:: console
    :test:
    :poll-until:
    :ignore-errors:
    :compare-output: bool(stdout.count(b"ready for") == 2)

    $ docker logs maintained_db 2>&1 | grep 'ready for'
    2020-01-13 21:31:09 0 [Note] mysqld: ready for connections.
    2020-01-13 21:32:16 0 [Note] mysqld: ready for connections.

Instead of having you go classify a bunch of repos manually, we're going to
assign a bunch of repos a random maintenance status. This will of course produce
a meaningless model. If you want a model that's accurate you should go classify
repos for real.

The randomly assigned maintenance status and URL for the repo will be stored in
the database. We need to install the ``dffml-source-mysql`` plugin to use
MariaDB/MySQL with DFFML.

.. code-block:: console
    :test:
    :replace: cmds[0].append("dffml")

    $ python -m pip install -U dffml-source-mysql

To get our dummy data, we'll be using the GitHub v4 API to search for "todo".
The search should return repos implementing a TODO app.

You'll need a Personal Access Token to be able to make calls to GitHub's API.
You can create one by following their documentation.

- https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token

When it presents you with a bunch of checkboxes for difference "scopes" you
don't have to check any of them.

.. code-block:: console

    $ export GITHUB_TOKEN=<paste your personal access token here>

You've just pasted your token into your terminal so it will likely show up in
your shell's history. You might want to either remove it from your history, or
just delete the token on GitHub's settings page after you're done with this
tutorial.

Now we'll write a function to pull the first 10 repo URLs that result from our
"TODO" search. The type annotations are important here, make sure you copy them
exactly. 0 means unmaintained, 1 means maintained.

**github_search.py**

.. literalinclude:: /../examples/maintained/github_search.py
    :test:

We'll use this function as a Source. In DFFML a source is somewhere a dataset is
stored. In this case the source is dynamic, it's pulling from an API and
randomly assigning a classification. You could even modify it to ask the user
for their manual classification instead of randomly assigning one.

We use the merge command to take data from one source and merge it with data in
another source. In our case we'll be taking records from the ``get_repos``
function within **github_search.py** and moving them into our database.

The ``op`` source allows us to use any ``OperatationImplementation`` (a Python
function) as a source of records.

We'll be using the ``dffml merge`` command to take the search results from the
GitHub API and putting them with their randomly assigned status into our
database.

.. code-block::
    :test:

    $ dffml merge github=op db=mysql \
        -source-github-opimp github_search:get_repos \
        -source-github-args todo $GITHUB_TOKEN \
        -source-db-insecure \
        -source-db-user user \
        -source-db-password pass \
        -source-db-db db \
        -source-db-key key \
        -source-db-init \
          'CREATE TABLE IF NOT EXISTS `status` (
             `key` varchar(767) NOT NULL,
             `maintained` TINYINT,
             PRIMARY KEY (`key`)
           ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;' \
        -source-db-records \
          'SELECT `key`, `maintained` FROM `status`' \
        -source-db-record \
          'SELECT `key`, `maintained` FROM `status` WHERE `key`=%s' \
        -source-db-update \
          'INSERT INTO `status` (`key`, `maintained`) VALUES(%s, %s) ON DUPLICATE KEY UPDATE `maintained`=%s' \
        -source-db-features '{"maintained": "maintained"}' \
        -source-db-predictions '{}'

Now that we have a database running and have our data in the database, we're
ready to start the CGI server. You'll want to do this in another terminal.
The last argument is the port to serve on, change that number if you already
have something running on that port.

.. code-block:: console
    :test:
    :daemon: 8000

    $ . .venv/bin/activate
    $ python3 -m http.server --cgi 8000

You can see all the records and their statuses that we imported into the
database by calling the API.

.. code-block:: console
    :test:
    :poll-until:
    :ignore-errors:
    :compare-output: bool(stdout.count(b"github.com") >= 1)
    :replace: cmds[0][2] = cmds[0][2].replace("8000", str(ctx["HTTP_SERVER"]["8000"]))

    $ curl -v 'http://127.0.0.1:8000/cgi-bin/api.py?action=dump' | \
        python3 -m json.tool

Gathering Data
--------------

We now have our dataset of git repos and their maintenance statuses in our web
app. If you go to http://127.0.0.1:8000/ you should see it.

Before we can train a model on this dataset, we need to transform it into
something that could be feed to a model. Right now all we have is URLs to git
repos.

We're going to run these repos through DFFML's data flow orchestrator. We'll
tell the orchestrator to run certain ``Operations`` on each one of the URLs.
Those ``Operations`` will scrape data that is representative of the repo's
maintenance, we can then feed that data into a machine learning model.

.. note::

     This example is centered around machine learning. We'll be using DataFlows
     to collect a dataset for training, testing, and prediction. For a deeper
     understanding of Operations and DataFlows, see the
     :doc:`/examples/shouldi`.

The operations we're going to use are a part of ``dffml-feature-git``, which is
a separate Python package from DFFML which we can install via ``pip``. We'll
also use the ``yaml`` configloader, since that creates more user friendly
configs than ``json``.

.. code-block:: console
    :test:

    $ python -m pip install -U dffml-feature-git dffml-config-yaml

The git operations / features rely on ``tokei``. We need to download and install
it first.

.. TODO sha validation

.. tabs::

    .. group-tab:: Linux

        .. code-block:: console
            :test:

            $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-unknown-linux-gnu.tar.gz' \
                | tar -xvz -C .venv/bin/

    .. group-tab:: MacOS

        .. code-block:: console

            $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' \
                | tar -xvz -C .venv/bin/

Operations are just Python functions, or classes. They define a routine which
will be run concurrently with other operations. Here's an example of the
``git_commits`` operation, which will find the number of commits within a date
range. This function / operation was installed when you installed the
``dffml-feature-git`` package via ``pip``.

.. literalinclude:: /../feature/git/dffml_feature_git/feature/operations.py
    :linenos:
    :lines: 372-399

We're going to use the operations provided in ``dffml-feature-git`` to gather
our dataset. The following command creates a ``DataFlow`` description of how
all the operations within ``dffml-feature-git`` link together. The ``DataFlow``
is stored in the YAML file **dataflow.yaml**.

.. code-block::
    :test:

    $ dffml dataflow create \
        -configloader yaml \
        -inputs \
          10=quarters \
          true=no_git_branch_given \
          '{"authors": {"group": "author_count", "by": "quarter"},
            "commits": {"group": "commit_count", "by": "quarter"},
            "work": {"group": "work_spread", "by": "quarter"}}'=group_by_spec \
        -- \
          group_by \
          make_quarters \
          quarters_back_to_date \
          check_if_valid_git_repository_URL \
          clone_git_repo \
          git_repo_default_branch \
          git_repo_commit_from_date \
          git_repo_author_lines_for_dates \
          work \
          git_commits \
          count_authors \
          cleanup_git_repo \
        | tee dataflow.yaml \
        | tail -n 15
    seed:
    - definition: quarters
      value: 10
    - definition: group_by_spec
      value:
        authors:
          by: quarter
          group: author_count
        commits:
          by: quarter
          group: commit_count
        work:
          by: quarter
          group: work_spread

Since operations are run concurrently with each other, DFFML manages locking of
input data, such as git repositories. This is done via ``Definitions`` which are
the variables used as values in the ``input`` and ``output`` dictionaries. We
link together all of the operations in a ``DataFlow``. The pink boxes in the
diagram below are the inputs to the network. The purple are the different
operations. Arrows show how data moves between operations.

.. TODO Autogenerate this from the dataflow

.. image:: /images/integration_dataflow.svg
    :alt: Diagram showing Dataflow

We can also visualize how the individual inputs and outputs are linked together.
Inputs and outputs of the same ``Definition`` can be linked together
automatically.

.. TODO Autogenerate this from the dataflow

.. image:: /images/integration_dataflow_complex.svg
    :alt: Diagram showing detailed version of Dataflow

The inputs and outputs of operations within a running DataFlow are organized by
contexts. The context for our dataset generation will be the source URL to the
Git repo.

- We will be providing the source URL to the git repo on a per-repo basis.

- We provide the start date of the zeroith quarter, and 10 instances of quarter,
  since for each operation, every possible permutation of inputs will be run,
  ``quarters_back_to_date`` is going to take the start date, and the quarter,
  and produce a date range for that quarter. We use ``make_quarters`` and pass
  ``10=quarters`` to make ten instances of ``quarter``.

- We'll also need to provide an input to the output operation ``group_by_spec``.
  Output operations decide what data generated should be used as feature data,
  and present it in a usable format.

  - Here we're telling the ``group_by`` operation to create feature data where
    the ``author_count``, ``work_spread`` and ``commit_count`` are grouped by
    the quarter they were generated for.

Training our Model
------------------

The model we'll be using is a part of ``dffml-model-tensorflow``, which is
another separate Python package from DFFML which we can install via ``pip``.

.. code-block:: console
    :test:

    $ python -m pip install -U dffml-model-tensorflow

The model is a generic wrapper around Tensorflow's DNN estimator. We can use it
to train on our dataset.

We're going to put the training command in it's own file, since it's very long

We use the :py:class:`DataFlowPreprocessSource <dffml.source.dfpreprocess.DataFlowPreprocessSource>` to run
the DataFlow we created using the above ``dffml dataflow create`` command on
each repo. When we run the DataFlow we pass it the current date and tell it to
use the record's key as the repo URL (since that's what the key is).

**train.sh**

.. literalinclude:: /../examples/maintained/train.sh
    :test:

Run **train.sh** to train the model

The speed of the following command depends on your internet connection, it may
take 2 minutes, it may take more. All the git repos in the database will be
downloaded, this will also take up space in ``/tmp``, they will be cleaned up
automatically.

.. code-block:: console
    :test:

    $ bash train.sh

Making a Prediction
-------------------

Run the operations on the new repo: ``https://github.com/intel/dffml`` and
have the model make a prediction

We're going to put the prediction command in it's own file, since it's very long

**predict.sh**

.. literalinclude:: /../examples/maintained/predict.sh
    :test:

Run **predict.sh** to make a prediction using the model. We're asking the model
to make a prediction on the DFFML repo.

.. code-block:: console
    :test:

    $ bash predict.sh https://github.com/intel/dffml
    [
        {
            "extra": {},
            "features": {
                "authors": [
                    9,
                    16,
                    20,
                    14,
                    10,
                    4,
                    5,
                    0,
                    0,
                    0
                ],
                "commits": [
                    110,
                    273,
                    252,
                    105,
                    65,
                    64,
                    51,
                    0,
                    0,
                    0
                ],
                "work": [
                    75,
                    82,
                    73,
                    34,
                    56,
                    3,
                    5,
                    0,
                    0,
                    0
                ]
            },
            "key": "https://github.com/intel/dffml",
            "last_updated": "2020-10-12T21:15:13Z",
            "prediction": {
                "maintained": {
                    "confidence": 0.9999271631240845,
                    "value": "1"
                }
            }
        }
    ]

Modifying the Legacy App
------------------------

Now let's add a 'Predict' button to the app. The button will trigger the
operations to be run on the new URL, and then the prediction. The demo app will
then take the predicted classification and record that as the classification in
the database.

The predict button will trigger an HTTP call to the CGI API. The CGI script will
run the same commands we just ran on the command line, and parse the output,
which is in JSON format, and set the resulting prediction classification in the
database.

We modify the backend CGI Python API to have it call our **predict.sh** script.

**cgi-bin/api.py**

.. literalinclude:: /../examples/maintained/cgi-bin/api-ml.py
    :test:
    :diff: /../examples/maintained/cgi-bin/api.py
    :filepath: cgi-bin/api.py

Test the new prediction capabilities from the command line with ``curl``

.. code-block:: console
    :test:
    :replace: cmds[0][2] = cmds[0][2].replace("8000", str(ctx["HTTP_SERVER"]["8000"]))

    $ curl -v 'http://127.0.0.1:8000/cgi-bin/api.py?action=predict&URL=https://github.com/intel/dffml' | \
        python -m json.tool

Hook up the predict button to call our new API by adding an event listener when
the Predict button is clicked.

**ml.js**

.. literalinclude:: /../examples/maintained/ml.js
    :test:
    :language: javascript

We need to import the new script into the main page and add the HTML for the
predict button.

**index.html**

.. literalinclude:: /../examples/maintained/ml.html
    :test:
    :diff: /../examples/maintained/index.html
    :filepath: index.html

Visit the web app, and input a Git repo to evaluate into the input field. Then
click predict. The demo gif has had all the entries DROPed from the database.
But you can look through the table and you'll find that a prediction has been
run on the repo. Congratulations! You've automated a manual classification
process, and integrated machine learning into a legacy application.

.. image:: /images/integration_demo.gif
