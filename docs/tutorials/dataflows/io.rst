Prediction Using IO Operations
==============================

This example will show you how to train a model using DFFML python API and use the
model for prediction by taking input from stdio.

DFFML offers several :ref:`plugin_models`. For this example
we will be using the Simple Linear Regression model
(:ref:`plugin_model_dffml_slr`) which is in the ``dffml`` package.

First we train the model and then create a DataFlow for making predictions
on user input.

**main.py**

.. literalinclude:: /../examples/io/io_usage.py
    :test:
    :filepath: main.py

On running the above code `AcceptUserInput` operation
waits for input from stdio.

.. code-block:: console
    :test:
    :stdin: 21

    $ python main.py
    Enter the value: 21

The feature value (which is the `str` "21") is then converted to `int` by
`literal_eval` operation. Before passing this value to `model_predict`
operation we need to create a mapping (`dict`) because `model_predict` takes a mapping for
feature name to feature value.
The mapping (`dict`) is created by `create_mapping` operation ( `{"Years": 21}` )
which is then passed to `model_predict` operation for making prediction.
The prediction is printed on stdout using `print_output` operation.

The output is:

.. code-block:: console

    {'Salary': {'confidence': 1.0, 'value': 220.0}}

The dataflow that we have created is

.. image:: /.. /examples/io/dataflow_diagram.svg

To re-generate the DataFlow diagram run.

.. code-block:: console
    :test:

    $ dffml service dev export examples.io.io_usage:dataflow | \
        dffml dataflow diagram -stages processing -configloader json /dev/stdin

Copy and pasting the output of the above code into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the graph.
