.. _model_tutorial_package:

Packaging a Model
=================

In the pervious tutorial we created a DFFML style model, which we could use from
the command line, HTTP service, etc. We're now going to take that model and
package it so that it can be published to PyPi for others to download via
``pip`` and use as they do the rest of the :ref:`plugin_models` plugins.

Create the Package
------------------

To create a new model we first create a new Python package. DFFML has a helper
to create it for you.

The helper creates a model which does Simple Linear Regression (SLR). Which
means it finds the best fit line for a dataset. If you've done the
:ref:`model_tutorial_slr` tutorial then the same code from that tutorial in
**myslr.py** will be present in **dffml_model_myslr/myslr.py** (not your
modifications though if you made any).

You may know the best fit line as ``y = m * x + b``

.. code-block:: console
    :test:

    $ dffml service dev create model dffml-model-myslr

Then enter the directory of the package we just created

.. code-block:: console
    :test:

    $ cd dffml-model-myslr

Install the Package
-------------------

If you're planing on importing any third party packages, anything on
`PyPi <https://pypi.org>`_, you'll want to add it to the ``setup.cfg`` file
first, under the ``install_requires`` section.

**setup.cfg**

.. code-block:: python
    :test:
    :filepath: setup.cfg

        scikit-learn>=0.21.2

Any time you modify the dependencies of a package you should re-install it so
they get installed as well.

``pip``'s ``-e`` flag tells it we're installing our package in development mode,
which means anytime Python import's our package, it's going to use the version
that we're working on here. If you don't pass ``-e`` then anytime you make
changes in this directory, they won't take effect until you reinstall the
package.

.. code-block:: console
    :test:

    $ python -m pip install -e .

Testing
-------

Packages should have tests to make sure that when you change things they don't
break before you release your package to users.

Imports
~~~~~~~

Let's import everything we'll need. Since DFFML heavily leverages ``async``
code, we'll have our test cases derive from :py:class:`AsyncTestCase`, rather
than :py:class:`unittest.TestCase`.

**tests/test_model.py**

.. code-block:: python
    :filepath: tests/test_model.py

    import tempfile

    from dffml import train, accuracy, predict, Feature, Features, AsyncTestCase

    from dffml_model_myslr.myslr import MySLRModel

Test data
~~~~~~~~~

We usually try to randomly generate training and test data, but for this example
we're just going to hard code in some data.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :test:
    :filepath: tests/test_model.py
    :lines: 7-34

TestCase Class
~~~~~~~~~~~~~~

We create a temporary directory for our tests to use, and clean it up when
they're done.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :test:
    :filepath: tests/test_model.py
    :lines: 37-52

Testing Train
~~~~~~~~~~~~~

Similarly to the quickstart, all we need to to is pass the model and training
data to the :py:func:`train <dffml.train>` function.

The tests are prefixed with numbers to indicate what order they
should be run in, ensuring that accuracy and predict tests always have a trained
model to work with.

We're using the ``*`` operator here to expand the list of X, Y pair ``dict``'s.
See the offical Python documentation about
`Unpacking Argument Lists <https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists>`_
for more information on how the ``*``-operator works.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :test:
    :filepath: tests/test_model.py
    :lines: 54-56

Testing Accuracy
~~~~~~~~~~~~~~~~

Once again, all we need to to is pass the model and test data to the
:py:func:`accuracy <dffml.accuracy>` function. Then we check if it's in an
acceptable range. This test is helpful to make sure you never make any horribly
wrong changes to your model, since it will check that the accuracy is within an
acceptable range.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :test:
    :filepath: tests/test_model.py
    :lines: 58-64

Testing Prediction
~~~~~~~~~~~~~~~~~~

Finally, we use the test data and model with the
:py:func:`predict <dffml.predict>` function. Then we check if each predicted Y
value is within 10% of what it should be.

**tests/test_model.py**

.. literalinclude:: /../dffml/skel/model/tests/test_model.py
    :test:
    :filepath: tests/test_model.py
    :lines: 66-78

Run the tests
~~~~~~~~~~~~~

We can run the tests using the ``unittest`` module. The create command gave us
both unit tests and integration tests. We want to only run the unit tests right
now (``tests.test_model``).

.. code-block:: console
    :test:

    $ python -m unittest -v tests.test_model
    test_00_train (tests.test_model.TestMySLRModel) ... ok
    test_01_accuracy (tests.test_model.TestMySLRModel) ... ok
    test_02_predict (tests.test_model.TestMySLRModel) ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 0.003s

    OK

If you want to see the output of the call to ``self.logger.debug``, just set the
``LOGGING`` environment variable to ``debug``.

.. code-block:: console
    :test:

    $ LOGGING=debug python -m unittest -v tests.test_model

Entrypoint Registration
-----------------------

In the :ref:`model_tutorial_slr` tutorial we refrenced the new model on the
command line via it's entrypoint style path. This is in the format of
``file:ClassWithinFile``, so for that tutorial it was ``myslr:MySLRModel``.

That requires that the ``file`` be in a directory in current working directory,
or in a directory in the ``PYTHONPATH`` environment variable.

We can instead reference it by a shorter name, but we have to declare that name
within the ``dffml.model`` entrypoint in **entry_points.txt**. This tells the
Python packaging system that our package offers a plugin of the type
``dffml.model``, and we give the short name on the left side of the equals, and
the entrypoint path on the right side.

**entry_points.txt**

.. code-block:: ini
    :test:
    :overwrite:
    :filepath: entry_points.txt

    [dffml.model]
    myslr = dffml_model_myslr.myslr:MySLRModel

And remember that any time we modify the **setup.py**, we have to run the
setuptools ``egg_info`` hook to register the model with the ``entry_points``
system.

.. code-block:: console
    :test:

    $ python setup.py egg_info

Command Line Usage
------------------

Let's add some training data to a CSV file.

**train.csv**

.. code-block::
    :test:
    :filepath: train.csv

    Years,Salary
    1,40
    2,50
    3,60
    4,70
    5,80

Since we've registered our model as a ``dffml.model`` plugin, we can now
reference it by it's short name.

.. code-block:: console
    :test:

    $ dffml train \
        -log debug \
        -model myslr \
        -model-features Years:int:1 \
        -model-predict Salary:float:1 \
        -model-location modeldir \
        -sources f=csv \
        -source-filename train.csv

Uploading to PyPi
-----------------

You can now upload your package to PyPi, so that other's can install it using
``pip``, by running the following commands.

.. warning::

   Don't do this if you intened to contribute your model to the DFFML repo!
   Place the top level directory, **dffml-model-myslr**, into **model/slr**
   within the DFFML source tree, and submit a pull request.

.. code-block:: console

    $ python3 setup.py sdist && python3 -m twine upload dist/*
