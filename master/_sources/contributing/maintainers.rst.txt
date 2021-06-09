Maintainer Docs
===============

These docs are for the maintainers of DFFML, if you're not a maintainer, you
won't find anything useful here, unless your just curious.

Adding A New Plugin
-------------------

When a new plugin is added we need to go manually upload it for the first time.

.. code-block:: console

    $ cd model/new_model
    $ python3 setup.py test
    $ rm -rf dist
    $ git clean -xdf
    $ python3 setup.py sdist
    $ twine upload dist/*

Once it's be uploaded, we go to PyPi and create an API key which will be used to
upload it via the automatic release at the end of ``run_plugin`` within the CI
script.

.. image:: /images/pypi-token-to-github-secret.gif

Finally, update the ``PYPI_TOKENS`` file in ``.github/workflows/testing.yml``.
Add a line for the plugin along with it's sceret.

Doing a Release
---------------

- Create a major.minor bugfix branch if it does not exist. Switch to it if it
  does

- Increment the version number of each package

- Increment the version number of the main package in the dependency list of
  each package

- Increment the version number of the plugin packages in the dependency list of
  each package

- Modify ``CHANGELOG.md`` to replace the ``Unreleased`` section header with the
  new version and the date

- Commit the new version

- Pin all the dependencies

- Tag a release

- Push the new branch (if created) and the tag

- Switch to the master branch

- Cherry pick the release commit from the new branch, but not the pinning commit

- Push the master branch

.. code-block:: console

    $ git checkout -b N.N.x || git checkout N.N.x
    $ dffml service dev bump packages 0.0.1
    $ dffml service dev bump inter
    $ sed -i "s/Unreleased]/$(dffml service dev setuppy version dffml/version.py)] - $(date +%F)/" CHANGELOG.md
    $ git commit -sam "release: Version $(dffml service dev setuppy version dffml/version.py)"
    $ git tag $(dffml service dev setuppy version dffml/version.py)
    $ git push -u origin N.N.x
    $ git push --tags
    $ git checkout master
    $ git cherry-pick X.Y.Z~1
    $ git push
