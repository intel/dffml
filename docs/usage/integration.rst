Automating Classification
=========================

This example will show you how to automate a manual classification process,
determining if a Git repo is maintained or abandoned. We'll be integrating
Machine Learning into an existing legacy application.

For this example assume you are a very curious open source software people (if
you're here you already are). Since you love looking at GitHub repos in your
free time, you long ago built a Python 2 based CGI web application where, every
time we came across a Git repo, you dug around, looked at the number of
committer, number of commits, etc. To come up with maintenance status. That
status being maintained, or unmaintained.

.. image:: /images/website-before.png

Instead of manually classifying each repo, we're going to put some machine
learning behind this little web app. The steps we're going to follow here are
generic, they do not apply specifically to this Python 2 CGI setup, this is just
an example that was chosen because hopefully it'll be an easy setup.

.. TODO Outline setups as a list here

Demo App Setup
--------------

We'll be using Python 2, 3.7, jq, and docker. So make sure you have all of those
installed. Python 2 is usually installed by default on most systems, your
package manager should have it if not.

Navigate to the ``maintained`` example, starting at the top directory of the
``dffml`` source.

.. code-block:: console

    $ cd examples/maintained/

Create a virtual environment for Python 3.7.

.. code-block:: console

    $ python3 -m venv .venv
    $ . .venv/bin/activate

Install DFFML.

.. code-block:: console

    $ pip install -U dffml

Download the Python 2 client libraries for MySQL.

.. code-block:: console

    $ python2 -m pip install -U --user \
        https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-8.0.16.tar.gz

Start MariaDB (functionally very similar to MySQL which its a fork of).

.. code-block:: console

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

    $ docker logs maintained_db 2>&1 | grep 'ready for'
    2020-01-13 21:31:09 0 [Note] mysqld: ready for connections.
    2020-01-13 21:32:16 0 [Note] mysqld: ready for connections.

Import the data. The data was pulled from a couple pages of GitHub search
results and randomly assigned a maintenance status. It is completely
meaningless.

If you want results that mean anything, you could discard all of this data and
use the web app to create a meaningful dataset by manually going through and
setting the status of repos.

.. code-block:: console

    $ docker run -i --rm --net=host mariadb:10 mysql \
        -h127.0.0.1 \
        -uuser \
        -ppass \
        --database db < db.sql

Fire up the CGI server. Yes, this is Python 3 now, but we're assuming there
was a legacy setup in place, the CGI server could just as well have been running
PHP. In fact a php app that does the same thing would follow these same
integration steps.

.. code-block:: console

    $ python -m http.server --cgi 8000

Gathering Data
--------------

We now have our dataset of git repos and their maintenance statuses in our web
app. If you go to http://127.0.0.1:8000/ you should see it.

Before we can train a model on this dataset, we need to transform it into
something that could be feed to a model. Right now all we have is URLs to git
repos.

Lets pull down that list of repos.

.. code-block:: console

    $ curl 'http://127.0.0.1:8000/cgi-bin/api.py?action=dump' \
        | jq -r 'keys[]' | tee /tmp/urls
    https://github.com/2bt/vmTetris.git
    https://github.com/AntoineMaillard06/Tetris.git
    https://github.com/Apolotary/My-tetris-on-python.git
    https://github.com/ArthanJans/TetrisPi.git
    https://github.com/CRAFT-THU/tetris.git

We're going to run these repos through DFFML's data flow orchestrator. We'll
tell the orchestrator to run certain ``Operations`` on each one of the URLs.
Those ``Operations`` will scrape data that is representative of the repo's
maintenance, we can then feed that data into a machine learning model.

.. note::

     This example is centered around machine learning. We'll be using DataFlows
     to collect a dataset for training, testing, and prediction. For a deeper
     understanding of Operations and DataFlows, see the
     :doc:`/tutorials/operations`.

The operations we're going to use are a part of ``dffml-feature-git``, which is
a separate Python package from DFFML (although maintained within the same repo)
which we can install via ``pip``. We'll also use the ``yaml`` config loader,
since that creates more user friendly configs than ``json``.

.. code-block:: console

    $ pip install -U dffml-feature-git dffml-config-yaml

The git operations / features rely on ``tokei``. We need to download and install
it first.

On Linux

.. code-block:: console

    $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' \
      | tar -xvz && \
      echo '22699e16e71f07ff805805d26ee86ecb9b1052d7879350f7eb9ed87beb0e6b84fbb512963d01b75cec8e80532e4ea29a tokei' | sha384sum -c - && \
      sudo mv tokei /usr/local/bin/

On OSX

.. code-block:: console

    $ curl -sSL 'https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz' \
      | tar -xvz && \
      echo '8c8a1d8d8dd4d8bef93dabf5d2f6e27023777f8553393e269765d7ece85e68837cba4374a2615d83f071dfae22ba40e2 tokei' | sha384sum -c - && \
      sudo mv tokei /usr/local/bin/

Operations are just Python functions, or classes. They define a routine which
will be run concurrently with other operations. Here's an example of the
``git_commits`` operation, which will find the number of commits within a date
range.

**feature/git/dffml_feature_git/feature/operations.py**

.. literalinclude:: /../feature/git/dffml_feature_git/feature/operations.py
    :linenos:
    :lineno-start: 363
    :lines: 363-394

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

We're going to use the operations provided in ``dffml-feature-git`` to gather
our dataset. The following command writes all the operations we're using to the
file ``/tmp/operations``.

.. code-block:: console

    $ cat > /tmp/operations <<EOF
    group_by
    quarters_back_to_date
    check_if_valid_git_repository_URL
    clone_git_repo
    git_repo_default_branch
    git_repo_checkout
    git_repo_commit_from_date
    git_repo_author_lines_for_dates
    work
    git_repo_release
    git_commits
    count_authors
    cleanup_git_repo
    EOF

We then create a ``DataFlow`` description of how they all link together.

.. code-block:: console

    $ dffml dataflow create -configloader yaml $(cat /tmp/operations) \
        > cgi-bin/dataflow.yaml

The inputs and outputs of operations within a running DataFlow are organized by
contexts. The context for our dataset generation will be the source URL to the
Git repo.

- We will be providing the source URL to the git repo on a per-repo basis.

- We provide the start date of the zeroith quarter, and 10 instances of quarter,
  since for each operation, every possible permutation of inputs will be run,
  ``quarters_back_to_date`` is going to take the start date, and the quarter,
  and produce a date range for that quarter.

- We'll also need to provide an input to the output operation ``group_by_spec``.
  Output operations decide what data generated should be used as feature data,
  and present it in a usable format.

  - Here we're telling the ``group_by`` operation to create feature data where
    the ``author_count``, ``work_spread`` and ``commit_count`` are grouped by
    the quarter they were generated for.

**cgi-bin/dataflow.yaml**

.. literalinclude:: /../examples/maintained/cgi-bin/dataflow.yaml
    :linenos:
    :lineno-start: 266
    :lines: 266-302

The speed of the following command depends on your internet connection, it may
take 2 minutes, it may take more. All the git repos in ``/tmp/urls`` will be
downloaded, this will also take up space in ``/tmp``, they will be cleaned up
automatically.

This command runs the dataflow on a set of repos, that set being the URLs in
``/tmp/urls``. The data generated on those repos is then being saved to
``/tmp/data.json`` (tagged as the ``gathered`` data source).

.. code-block:: console

    $ dffml dataflow run records set \
        -keys $(cat /tmp/urls) \
        -record-def URL \
        -dataflow cgi-bin/dataflow.yaml \
        -sources gathered=json \
        -source-filename /tmp/data.json \
        -no-strict
    [
        ... results ...
        {
            "extra": {},
            "features": {
                "authors": [
                    0,
                    2,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                "commits": [
                    0,
                    12,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                "work": [
                    0,
                    4,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ]
            },
            "last_updated": "2019-10-25T01:44:50Z",
            "key": "https://github.com/AntoineMaillard06/Tetris.git"
        }
    ]

Pulling from the Database
-------------------------

Now that we've gathered our data. We want to re-associate it with it's
classifications. To do this we need to access the database.

By copying the example source implementation
``examples/source/custom_source.py`` we can quickly modify it to use the
``aiomysql`` connector rather than sqlite.

.. note::

    The following source code is one of many examples of how you might write a
    source to interact with your existing database. If you don't have any
    existing logic and just want to store data in MySQL, you chould check out
    the MySQL :doc:`/plugins/dffml_source` plugin.

**demoapp/source.py**

.. literalinclude:: /../examples/maintained/demoapp/source.py

We then make sure to register our new source with Pythons ``entrypoint`` system,
to make it accessable to the command line interface.

**setup.py**

.. literalinclude:: /../examples/maintained/setup.py
    :lines: 32

Let's now install it so we can use it within the DFFML CLI.

.. code-block:: console

    $ pip install -e .

The source we've written uses a new table in the database. Lets create it.

**db_ml.sql**

.. literalinclude:: /../examples/maintained/db_ml.sql

You can pipe that query in with bash like we did the first time.

.. code-block:: console

    $ docker run -i --rm --net=host mariadb:10 mysql \
        -h127.0.0.1 \
        -uuser \
        -ppass \
        --database db < db_ml.sql

Now we'll take the data we stored in the json file and merge it back into the
database.

.. code-block:: console

    $ dffml merge db=demoapp gathered=json \
        -source-gathered-filename /tmp/data.json -log debug

List all the repos in the database to confirm all data and classifications show
up as expected.

.. code-block:: console

    $ dffml list records -sources db=demoapp

Training our Model
------------------

The model we'll be using is a part of ``dffml-model-tensorflow``, which is another
separate Python package from DFFML (although maintained within the same repo)
which we can install via ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-tensorflow

The model is a generic wrapper around Tensorflow's DNN estimator. We can use it
to train on our dataset.

.. code-block:: console

    $ dffml train all \
        -model tfdnnc \
        -model-epochs 400 \
        -model-steps 4000 \
        -model-predict maintained:str:1 \
        -model-classifications 0 1 \
        -sources db=demoapp \
        -model-features \
          authors:int:10 \
          commits:int:10 \
          work:int:10 \
        -log debug \
        -update

Now let's assess the accuracy, remember, this is bogus data so this number is
meaningless unless you threw out the dataset and put in real classifications.

.. code-block:: console

    $ dffml accuracy \
        -model tfdnnc \
        -model-predict maintained:str:1 \
        -model-classifications 0 1 \
        -sources db=demoapp \
        -model-features \
          authors:int:10 \
          commits:int:10 \
          work:int:10 \
        -log critical
    0.4722222089767456

The accuracy is 47.22%.

Making a Prediction
-------------------

Run the operations on the new repo: ``https://github.com/intel/dffml.git``

.. code-block:: console

    $ dffml dataflow run records set \
        -keys https://github.com/intel/dffml.git \
        -record-def URL \
        -dataflow cgi-bin/dataflow.yaml \
        -sources db=demoapp

Now that we have the data for the new repo, ask the model for a prediction.

.. code-block:: console

    $ dffml predict record \
        -keys https://github.com/intel/dffml.git \
        -model tfdnnc \
        -model-predict maintained:str:1 \
        -model-classifications 0 1 \
        -sources db=demoapp \
        -model-features \
          authors:int:10 \
          commits:int:10 \
          work:int:10 \
        -log critical \
        -update
    [
        {
            "extra": {},
            "features": {
                "authors": [
                    5,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                "commits": [
                    39,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                "work": [
                    4,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ]
            },
            "last_updated": "2019-05-23T10:33:03Z",
            "prediction": {
                "value": "0",
                "confidence": 1.0
            },
            "key": "https://github.com/intel/dffml.git"
        }
    ]

Modifying the Legacy App
------------------------

Now let's add a 'Predict' button to the app. The button will trigger the
operations to be run on the new URL, and then the prediction. The demo app will
then take the predicted classification and record that as the classification in
the database.

**index.html**

.. code-block:: html

    <div>
      <p>Submit or change the maintenance status of a repo.</p>
      <input id="URL" placeholder="git://server.git/repo"></input>
      <button id="maintained" class="good">Maintained</button>
      <button id="unmaintained" class="dangerous">Unmaintained</button>
      <button id="predict">Predict</button>
    </div>

The predict button will trigger an HTTP call to the CGI API. The CGI script will
run the same commands we just ran on the command line, and parse the output,
which is in JSON format, and set the resulting prediction classification in the
database.

**cgi-bin/api.py**

.. literalinclude:: /../examples/maintained/cgi-bin/api-ml.py
    :linenos:
    :lineno-start: 40
    :lines: 40-66

Hook up the predict button to call our new API.

**ml.js**

.. code-block:: javascript

    function predict(URL) {
      return fetch('cgi-bin/api.py?action=predict' +
        '&maintained=' + Number(maintained) +
        '&URL=' + URL)
      .then(function(response) {
        return response.json()
      }.bind(this));
    }

    window.addEventListener('DOMContentLoaded', function(event) {
      var tableDOM = document.getElementById('table');
      var URLDOM = document.getElementById('URL');
      var predictDOM = document.getElementById('predict');

      predictDOM.addEventListener('click', function(event) {
        predict(URLDOM.value)
        .then(function() {
          refreshTable(tableDOM);
        });
      });
    });

Finally, import the new script into the main page.

**index.html**

.. code-block:: html

    <head>
      <title>Git Repo Maintenance Tracker</title>
      <script type="text/javascript" src="main.js"></script>
      <script type="text/javascript" src="ml.js"></script>
      <link rel="stylesheet" type="text/css" href="theme.css">
    </head>

Visit the web app, and input a Git repo to evaluate into the input field. Then
click predict. The demo gif has had all the entries DROPed from the database.
But you can look through the table and you'll find that a prediction has been
run on the repo. Congratulations! You've automated a manual classification
process, and integrated machine learning into a legacy application.

.. image:: /images/integration_demo.gif
