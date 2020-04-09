Prediction Using IO Operations
==============================

This example will show you how to train a model using DFFML python API and use the
model for prediction by taking input from stdio.

The model we'll be using is ``slr`` which is a part of ``dffml`` models.
We can install it
with ``pip``.

.. code-block:: console

    $ pip install -U dffml

First we train the model and then create a DataFlow for making predictions
on user input.


.. literalinclude:: /../examples/io/io_usage.py

On running the above code `AcceptUserInput` operation
waits for input from stdio.

.. code-block:: console

    Enter the value:
    21

The value (here "21") is then converted to `int` by
`literal_eval` operation.
A mapping is created by `create_mapping` operation ({"Years": 21})
which is then passed to `model_predict` operation for making prediction.
The prediction is printed on stdout using `print_output` operation.

The output is:

.. code-block:: console

    {'Salary': {'confidence': 1.0, 'value': 220.0}}