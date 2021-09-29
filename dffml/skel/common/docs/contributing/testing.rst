Testing
=======

You can run the tests with:

.. code-block:: console

    $ python3 -m unittest discover -v

You can run a single file by passing it's Python import path.

.. code-block:: console

    $ python3 -m unittest tests.test_mytestcase

You can also run all tests which have a given string in their name using ``-k``.

.. code-block:: console

    $ python3 -m unittest discover -v -k unpack_

Test Coverage
-------------

Each pull request is expected to maintain or increase test coverage

.. code-block:: console

    $ python3 -m coverage run -m unittest discover -v
    $ python3 -m coverage report -m
    $ python3 -m coverage html

The last command generates a folder called ``htmlcov``, you can check the report
by opening the ``index.html`` in a web browser.

.. code-block:: console

    $ python3 -m http.server --directory htmlcov/ 8080

You can now view the coverage report at http://127.0.0.1:8080/
