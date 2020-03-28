Git and GitHub
==============

We encourage people to commit code and push it up to GitHub often. That way, if
you're having trouble with something you can send others a link to your code
where they can easily get an idea of what might be going wrong. Don't worry if
it's nowhere near complete! Asking each other for help just gets us to working
code faster!

Working On A Branch
-------------------

Be sure to checkout a new branch to do your work on.

.. code-block:: console

    $ git fetch origin
    $ git checkout -b my_new_thing origin/master

You'll need to fork the repo on GitHub too. Then add that as a remote.

.. note::

    ``$USER`` in this case would be your GitHub username

.. code-block:: console

    $ git remote add $USER git@github.com:$USER/dffml

Once you've committed a change on that branch you can push it to your fork.

.. code-block:: console

    $ git push -u $USER my_new_thing

Then you can keep committing on this branch and just use ``git push`` to send your
new commits to GitHub.

Issue and Pull Request title formatting
---------------------------------------

Please create issues and Pull Requests with titles in the format of

``sub_module: file: Short description``

Since DFFML is organized mostly in a two level fashion, this will help us track
where changes are needed or being made at a glance.

Where the filename is the same as the directory name, this is the case with
Abstract Base classes, then omit the filename.

Here are some examples:

- ``source: csv: Parse error due to seperator``
- ``feature: Add abstract method new_method``
- ``util: entrypoint: Change load_multiple``
- ``model: tensorflow: Add XYZ classifier``

If you've already made the commit, you can change the message by amending the
commit.

.. code-block:: console

    $ git commit --amend

Submitting A Pull Request
-------------------------

We try to keep changes in pull requests concise. This means you should title
your pull request so we know what it does and in the description tell us
anything else we need to know. Try to make bite sized changes. Generally, pull
requests should be under 1000 lines. If you find your pull request going over
that, it is probably time to clean up what you have and make sure it passes all
the CI and review so we can merge it, and you can start working on the rest of
your changes in a new pull request. This helps others working on the project and
users get access to your changes faster.

Once you have some work done on an issue or some feature you may be
implementing, you should submit a draft pull request, or prefix the title with
``WIP:`` to indicate that it's a Work In Progress.

Try to get as far as you can by running the tests locally, or looking at the
results of the CI. If you need help, ask in the Gitter channel if someone can
review your work or help you figure out what might be going wrong or how you
could solve an issue your stuck on.

Before you are get help, a review, or a final review, make sure to fetch the
latest changes from the master branch and ``merge`` or ``rebase`` them into your
branch.

When you are ready for final review, remove the ``WIP:`` prefix or draft status.
At this point, all the CI tests should be passing. It should be okay for a
maintainer to merge your pull request at this point. Pull requests with the
``WIP:`` prefix or draft status will not be merged.

How to Read the CI
------------------

We have continuous integration setup which can tell you a lot about if your pull
request is ready for review or not.

.. image:: /images/how-to-read-ci-tests.png
    :alt: Screenshot of CI with some tests passing and some failing

Look through all of the tests and identify which ones are failing. Click on the
test to view the logs, there is a drop down in the top right which will let you
view the "raw logs", which might be helpful.

All of the CI tests must pass for your pull request to be merged! Keep working
on it or ask for help if your not sure what's wrong.

If the lgtm bot comments and tells you that you're adding unused imports or
doing something it doesn't like, either fix it, or tell us why what you're doing
is okay.

+--------------+---------------------------------------------------------------+
| CI Test      | What's Probably Wrong                                         |
+--------------+---------------------------------------------------------------+
| CHANGELOG    | You need to say what your change is doing in CHANGELOG.md     |
+--------------+---------------------------------------------------------------+
| WHITESPACE   | https://softwareengineering.stackexchange.com/q/121555        |
+--------------+---------------------------------------------------------------+
| STYLE        | You need to run the ``black`` formater                        |
+--------------+---------------------------------------------------------------+
| DOCS         | There was an issue when running the ./scripts/docs.sh script  |
+--------------+---------------------------------------------------------------+

For the tests in the various plugins:

- You need to grab the latests changes from the master branch. Maybe you need to
  adapt to them, for example if something got renamed, check the changelog.

- You need to add any dependencies (``pip install ...``)  you need to the
  ``setup.py`` file of the plugin your working on.

- For ``model/tensorflow`` sometimes the neural networks get bad accuracy,
  causing the tests to fail. This is because they are initialized with random
  weights. Click on the failing test, then re-run it (as of writing this GitHub
  only allows re-running all of the tests).
