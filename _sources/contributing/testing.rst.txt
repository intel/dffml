Testing
=======

DFFML has a test suite with unit and integration tests. All plugins also have
unit tests, some have integration tests, eventually all will have integration
tests.

You can run the tests with

.. code-block:: console

    $ python3.7 setup.py test

To run a specific test, use the ``-s`` flag.

.. code-block:: console

    $ python3.7 setup.py test -s tests.test_cli.TestPredict.test_repo

Debug Logging
-------------

To get the debug output while testing set the ``LOGGING`` environment variable.

.. code-block:: console

    $ export LOGGING=debug

Test Coverage
-------------

Each pull request is expected to maintain or increase test coverage

.. code-block:: console

    $ python3.7 -m coverage run setup.py test
    $ python3.7 -m coverage report -m
    $ python3.7 -m coverage html


The last command generates a folder called ``htmlcov``, you can check the report
by opening the ``index.html`` in a web browser.

.. code-block:: console

    $ python3.7 -m http.server --directory htmlcov/ 8080


You can now view the coverage report at http://127.0.0.1:8080/

Test Datasets
-------------

In order to avoid potential legal issues, all datasets included within the
codebase of DFFML should be randomly generated.
