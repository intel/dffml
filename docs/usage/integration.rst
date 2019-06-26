Example Integration
===================

This example will show you how to automate a manual classification process,
determining if a Git repo is maintained or abandoned.

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

.. code-block:: bash

    $ cd examples/maintained/

Create a virtual environment for Python 3.7.

.. code-block:: bash

    $ virtualenv -p python3.7 .venv
    $ . .venv/bin/activate

Install DFFML.

.. code-block:: bash

    $ pip install -U dffml

Download the Python 2 client libraries for MariaDB (same as MySQL).

.. code-block:: bash

    $ python2 -m pip install -U --user \
        https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-8.0.16.tar.gz

Start MariaDB

.. code-block:: bash

    $ docker run --rm -d --name maintained_db \
        -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
        -e MYSQL_USER=user \
        -e MYSQL_PASSWORD=pass \
        -e MYSQL_DATABASE=db \
        -p 3306:3306 \
        mariadb

Import the data. The data was pulled from a couple pages of GitHub search
results and randomly assigned a maintenance status. It is completely
meaningless.

You could discard all of this data and use the web app to create a meaningful
dataset by manually going through and setting the status of repos.

.. code-block:: bash

    $ docker run -i --rm --net=host mariadb mysql \
        -h127.0.0.1 \
        -uuser \
        -ppass \
        --database db < db.sql

Fire up the CGI server. Yes, this is Python 3 now, but we're assuming there
was a legacy setup in place, the CGI server could just as well have been running
PHP. In fact a php app that does the same thing would follow these same
integration steps.

.. code-block:: bash

    $ python -m http.server --cgi 8000

Gathering Data
--------------

We now have our dataset of git repos and their maintenance statuses in our web
app. If you go to http://127.0.0.1:8000/ you should see it.

Before we can train a model on this dataset, we need to transform it into
something that could be feed to a model. Right now all we have is URLs to git
repos.

Lets pull down that list of repos.

.. code-block:: bash

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

The operations we're going to use are a part of ``dffml-feature-git``, which is
a separate Python package from DFFML (although maintained within the same repo)
which we can install via ``pip``.

.. code-block:: bash

    $ pip install -U dffml-feature-git

Operations are just Python functions, or classes. They define a routine which
will be run concurrently with other operations. Here's an example of the
``git_commits`` operation, which will find the number of commits within a date
range.

.. code-block:: python

    @op(inputs={
            'repo': git_repository,
            'branch': git_branch,
            'start_end': date_pair
            },
        outputs={
            'commits': commit_count
            })
    async def git_commits(repo: Dict[str, str], branch: str, start_end: List[str]):
        start, end = start_end
        commit_count = 0
        proc = await create('git', 'log', '--oneline', '--before', start,
                '--after', end, branch, cwd=repo['directory'])
        while not proc.stdout.at_eof():
            line = await proc.stdout.readline()
            if line != b'':
                commit_count += 1
        await stop(proc)
        return {
                'commits': commit_count
                }

Since operations are run concurrently with each other, DFFML manages locking of
input data, such as git repositories. This is done via ``Definitions`` which are
the variables used as values in the ``input`` and ``output`` dictionaries.

We're going to use the operations provided in ``dffml-feature-git`` to gather
our dataset. First we'll define which operations we are going to use.

.. code-block:: bash

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

We then run the defined operations through the orchestrator. ``remap`` and
``group_by_spec`` are re-labeling the output's to the feature data names we
want.

The speed of the following command depends on your internet connection, it may
take 2 minutes, it may take more. All the git repos in ``/tmp/urls`` will be
downloaded, this will also take up space in ``/tmp``, they will be cleaned up
automatically.

.. code-block:: bash

    $ dffml operations repo \
        -log debug \
        -sources primary=json \
        -source-filename /tmp/data.json \
        -update \
        -keys $(cat /tmp/urls) \
        -repo-def URL \
        -remap \
          group_by.work=work \
          group_by.commits=commits \
          group_by.authors=authors \
        -dff-memory-operation-network-ops $(cat /tmp/operations) \
        -dff-memory-opimp-network-opimps $(cat /tmp/operations) \
        -inputs \
          {0,1,2,3,4,5,6,7,8,9}=quarter \
          "'2019-03-29 13:24'=quarter_start_date" \
          True=no_git_branch_given \
        -output-specs '{
            "authors": {
              "group": "quarter",
              "by": "author_count",
              "fill": 0
            },
            "work": {
              "group": "quarter",
              "by": "work_spread",
              "fill": 0
            },
            "commits": {
              "group": "quarter",
              "by": "commit_count",
              "fill": 0
            }
          }=group_by_spec'

We saved the gathered data to ``/tmp/data.json``.

Pulling from the Database
-------------------------

Now that we've gathered our data. We want to re-associate it with it's
classifications. To do this we need to access the database.

By copying the example source implementation
``examples/source/custom_source.py`` we can quickly modify it to use the
``aiomysql`` connector rather than sqlite.

.. TODO Add more explination here

Let's now install it so we can use it within the DFFML CLI.

.. code-block:: bash

    $ pip install -e .

The source we've written uses a new table in the database. Lets create it.

.. literalinclude:: /../examples/maintained/db_ml.sql

You can pipe that query in with bash like we did the first time.

.. code-block:: bash

    $ docker run -i --rm --net=host mariadb mysql \
        -h127.0.0.1 \
        -uuser \
        -ppass \
        --database db < db_ml.sql

Now we'll take the data we stored in the json file and merge it back into the
database.

.. code-block:: bash

    $ dffml merge db=demoapp gathered=json \
        -source-gathered-filename /tmp/data.json -log debug

List all the repos in the database to confirm all data and classifications show
up as expected.

.. code-block:: bash

    $ dffml list repos -sources db=demoapp

Training our Model
------------------

The model we'll be using is a part of ``dffml-model-tensorflow``, which is another
separate Python package from DFFML (although maintained within the same repo)
which we can install via ``pip``.

.. code-block:: bash

    $ pip install -U dffml-model-tensorflow

The model is a generic wrapper around Tensorflow's DNN estimator. We can use it
to train on our dataset.

.. code-block:: bash

    $ dffml train all \
        -model tfdnnc \
        -model-epochs 400 \
        -model-steps 4000 \
        -model-classification maintained \
        -model-classifications 0 1 \
        -sources db=demoapp \
        -features \
          def:authors:int:10 \
          def:commits:int:10 \
          def:work:int:10 \
        -log debug \
        -update

Now let's assess the accuracy, remember, this is bogus data so this number is
meaningless unless you threw out the dataset and put in real classifications.

.. code-block:: bash

    $ dffml accuracy \
        -model tfdnnc \
        -model-classification maintained \
        -model-classifications 0 1 \
        -sources db=demoapp \
        -features \
          def:authors:int:10 \
          def:commits:int:10 \
          def:work:int:10 \
        -log critical
    2019-05-23 10:23:40.056553: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 3491950000 Hz
    2019-05-23 10:23:40.057065: I tensorflow/compiler/xla/service/service.cc:150] XLA service 0x24fe3c0 executing computations on platform Host. Devices:
    2019-05-23 10:23:40.057087: I tensorflow/compiler/xla/service/service.cc:158]   StreamExecutor device (0): <undefined>, <undefined>
    0.4722222089767456

The accuracy is 47.22%.

Making a Prediction
-------------------

Run the operations on the new repo (https://github.com/intel/dffml.git).

.. code-block:: bash

    $ dffml operations repo \
        -log debug \
        -sources db=demoapp \
        -update \
        -keys https://github.com/intel/dffml.git \
        -repo-def URL \
        -remap \
          group_by.work=work \
          group_by.commits=commits \
          group_by.authors=authors \
        -dff-memory-operation-network-ops $(cat /tmp/operations) \
        -dff-memory-opimp-network-opimps $(cat /tmp/operations) \
        -inputs \
          {0,1,2,3,4,5,6,7,8,9}=quarter \
          "'2019-03-29 13:24'=quarter_start_date" \
          True=no_git_branch_given \
        -output-specs '{
            "authors": {
              "group": "quarter",
              "by": "author_count",
              "fill": 0
            },
            "work": {
              "group": "quarter",
              "by": "work_spread",
              "fill": 0
            },
            "commits": {
              "group": "quarter",
              "by": "commit_count",
              "fill": 0
            }
          }=group_by_spec'

Now that we have the data for the new repo, ask the model for a prediction.

.. code-block:: bash

    $ dffml predict repo \
        -keys https://github.com/intel/dffml.git \
        -model tfdnnc \
        -model-classification maintained \
        -model-classifications 0 1 \
        -sources db=demoapp \
        -features \
          def:authors:int:10 \
          def:commits:int:10 \
          def:work:int:10 \
        -log critical \
        -update
    2019-05-23 10:33:03.468591: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 3491950000 Hz
    2019-05-23 10:33:03.469217: I tensorflow/compiler/xla/service/service.cc:150] XLA service 0x4394920 executing computations on platform Host. Devices:
    2019-05-23 10:33:03.469235: I tensorflow/compiler/xla/service/service.cc:158]   StreamExecutor device (0): <undefined>, <undefined>
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
            "src_url": "https://github.com/intel/dffml.git"
        }
    ]

Modifying the Legacy App
------------------------

Now let's add a 'Predict' button to the app. The button will trigger the
operations to be run on the new URL, and then the prediction. The demo app will
then take the predicted classification and record that as the classification in
the database.

**examples/maintained/index.html**

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

**examples/maintained/cgi-bin/api.py**

.. code-block:: python

    # Add the imports we'll be using to the top of api.py
    import subprocess
    from datetime import datetime

    # ...

    elif action == 'predict':
        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        operations = [
            'group_by',
            'quarters_back_to_date',
            'check_if_valid_git_repository_URL',
            'clone_git_repo',
            'git_repo_default_branch',
            'git_repo_checkout',
            'git_repo_commit_from_date',
            'git_repo_author_lines_for_dates',
            'work',
            'git_repo_release',
            'git_commits',
            'count_authors',
            'cleanup_git_repo'
            ]
        subprocess.check_call(([
            'dffml', 'operations', 'repo',
            '-log', 'debug',
            '-sources', 'db=demoapp',
            '-update',
            '-keys', query['URL'],
            '-repo-def', 'URL',
            '-remap',
            'group_by.work=work',
            'group_by.commits=commits',
            'group_by.authors=authors',
            '-dff-memory-operation-network-ops'] + operations + [
            '-dff-memory-opimp-network-opimps'] + operations + [
            '-inputs'] + \
            ['%d=quarter' % (i,) for i in range(0, 10)] + [
            '\'%s\'=quarter_start_date' % (today,),
            'True=no_git_branch_given',
            '-output-specs', '''{
                "authors": {
                  "group": "quarter",
                  "by": "author_count",
                  "fill": 0
                },
                "work": {
                  "group": "quarter",
                  "by": "work_spread",
                  "fill": 0
                },
                "commits": {
                  "group": "quarter",
                  "by": "commit_count",
                  "fill": 0
                }
              }=group_by_spec''']))
        result = subprocess.check_output([
            'dffml', 'predict', 'repo',
            '-keys', query['URL'],
            '-model', 'tfdnnc',
            '-model-classification', 'maintained',
            '-model-classifications', '0', '1',
            '-sources', 'db=demoapp',
            '-features',
            'def:authors:int:10',
            'def:commits:int:10',
            'def:work:int:10',
            '-log', 'critical',
            '-update'])
        result = json.loads(result)
        cursor.execute("REPLACE INTO status (src_url, maintained) VALUES(%s, %s)",
                       (query['URL'], result[0]['prediction']['value'],))
        cnx.commit()
        print json.dumps(dict(success=True))

Hook up the predict button to call our new API.

**examples/maintained/ml.js**

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

**examples/maintained/index.html**

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
