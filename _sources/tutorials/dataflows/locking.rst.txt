Using Locks In DataFlow
=======================

All the operations in DFFML runs asynchronously. DFFML takes care of locking objects which
might be used by multiple operations so that you don't run in to any race conditions.
This example shows one such usage.

.. note::

    All the code for this example is located under the
    `examples/dataflow/locking <https://github.com/intel/dffml/blob/master/examples/dataflow/locking>`_
    directory of the DFFML source code.

First we import required packages and objects, and create Definitions for each
data type our operation will use. Note that ``LOCKED_OBJ`` has ``lock=True``.

**example.py**

.. literalinclude:: /../examples/dataflow/locking/example.py
    :lines: 1-8

Our operation ``run_me`` takes an object(of definition OBJ) sets the ``i``
attribute of it, sleeps for given time finally prints the value which was given
as input and the current value of the object.

**example.py**

.. literalinclude:: /../examples/dataflow/locking/example.py
    :lines: 11-15

We'll run the dataflow with two values for i. If the operations run as expected when printing,
the value given as input and that of the object would be same.

**example.py**

.. literalinclude:: /../examples/dataflow/locking/example.py
    :lines: 18-29

But this codeblock gives an output

.. code-block::

    Running dataflow without locked object
    set i = 2, got i = 1
    set i = 1, got i = 1
    set i = 2, got i = 1
    set i = 1, got i = 1

We can see that the output is not what we expect. Since everything is running asynchronously,
when one operations sleeps the other operation might start running and it replaces the
value. This is where locks come handy. We'll set ``run_me`` to take object of definition
``LOCKED_OBJ`` instead of ``OBJ`` and run the dataflow again.

**example.py**

.. literalinclude:: /../examples/dataflow/locking/example.py
    :lines: 31-45

This time the output is as expected

.. code-block::

    Running dataflow with locked object
    set i = 2, got i = 2
    set i = 1, got i = 1
    set i = 2, got i = 2
    set i = 1, got i = 1
