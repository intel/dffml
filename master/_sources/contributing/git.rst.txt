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

File Formatting
---------------

We run the `black <https://github.com/psf/black>`_ formatter on all files. Try
to run it before every commit. This way, if you push up files for review, they
are easy to read, even if your pull request isn't yet ready to merge.

.. code-block:: console

    $ black .

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

