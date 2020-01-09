Model Quickstart
================

In this example we have employee data telling us the employee's years of
experience, our level of trust in them, their level of expertise, and their
salary. Our goal will be to predict what the salary of a new hire should be,
given their years of experience, our level of trust in them, and their level of
expertise.

**training.csv**

.. literalinclude:: /../examples/training.csv

**test.csv**

.. literalinclude:: /../examples/test.csv

The model we'll be using is a part of ``dffml-model-tensorflow``, which is
another separate Python package from DFFML which we can install via ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-tensorflow

We will be using Tensorflow's deep neural network with a linear regressor as the
model. Other available models can be found on the plugin page.

**quickstart.py**

.. literalinclude:: /../examples/quickstart.py

Here's the two rows of new employee data we need predictions from

**predict.csv**

.. literalinclude:: /../examples/predict.csv

Let's run the ``quickstart.py`` file to get the predictions.

.. code-block:: console

    $ python quickstart.py
    Accuracy 0.8966069221496582
    70.49790954589844 (nan% confidence) 0
    Years                         6
    Expertise                     13
    Trust                         1.4
    80.61932373046875 (nan% confidence) 1
    Years                         7
    Expertise                     15
    Trust                         1.6
