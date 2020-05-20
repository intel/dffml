Testing
=======

DFFML has a test suite with unit and integration tests. All plugins also have
unit tests, some have integration tests, eventually all will have integration
tests.

You can run the tests with

.. code-block:: console

    $ python3 setup.py test

To run a specific test, use the ``-s`` flag.

.. code-block:: console

    $ python3 setup.py test -s tests.test_cli.TestPredict.test_record

.. _running_ci_tests_locally:

Running CI Tests Locally
------------------------

You can run any of the CI tests with the following docker / podman command.

.. code-block:: console

    $ sudo docker run --rm -ti -u $(id -u):$(id -g) \
        -e USER=$USER \
        -v $HOME/.cache/pip:/home/$USER/.cache/pip -w /usr/src/dffml \
        -v $PWD:/usr/src/dffml -w /usr/src/dffml \
        --entrypoint .ci/docker-entrypoint.sh python:3.7 .

The final argument tells the script which CI test to run. If you give a path,
such as ``.`` for the main package, or ``model/scikit`` for one of the plugins,
it will run the tests for the given package.

You can also change the docker image from ``python:3.7`` to ``python:3.8`` to
run the tests against another version of Python.

If you want to run any of the named CI tests, you can do that by giving the name
instead of a path. Make sure you run these with the ``python:3.7`` image (3.8
seems to have some weird issues, lack of ``pkg_resources`` to name one).

Options are as follows

- ``changelog``

- ``whitespace``

- ``style``

- ``docs``

- ``lines``

For example, to run the ``docs`` CI test, the final arguments to the above
command would be ``--entrypoint .ci/docker-entrypoint.sh python:3.7 docs``

Debug Logging
-------------

To get the debug output while testing set the ``LOGGING`` environment variable.

.. code-block:: console

    $ export LOGGING=debug

Test Coverage
-------------

Each pull request is expected to maintain or increase test coverage

.. code-block:: console

    $ python3 -m coverage run setup.py test
    $ python3 -m coverage report -m
    $ python3 -m coverage html


The last command generates a folder called ``htmlcov``, you can check the report
by opening the ``index.html`` in a web browser.

.. code-block:: console

    $ python3 -m http.server --directory htmlcov/ 8080


You can now view the coverage report at http://127.0.0.1:8080/

Test Datasets
-------------

In order to avoid potential legal issues, all datasets included within the
codebase of DFFML should be randomly generated.
