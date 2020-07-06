Using Locks In DataFlow
=======================

All the operations in DFFML runs asynchrously. DFFML takes care of locking objects which
might be used by multiple operations so that you don't run in to any race conditions.
This example shows one such usage.

.. note::

    All the code for this example is located under the
    `examples/dataflow/locking <https://github.com/intel/dffml/blob/master/examples/dataflow/locking>`_
    directory of the DFFML source code.

**example.py**

.. literalinclude:: /../examples/dataflow/locking/example.py
    :linenos:
    :lineno-start: 1
    :lines: 1-9

First we define all the Definitions. Note that ``LOCKED_OBJ`` has ``lock=True``.

.. literalinclude:: /../examples/dataflow/locking/example.py
    :linenos:
    :lineno-start: 10
    :lines: 10-22

Our operation ``run_me`` takes an object(of defintion OBJ) sets the ``i`` aattribute of it, sleeps for given
time finally prints the value which was given as input and the current value of the object.
We'll run the dataflow with two values for i. If the operations run as expected when printing,
the value given as input and that of the object would be same.

.. literalinclude:: /../examples/dataflow/locking/example.py
    :linenos:
    :lineno-start: 25
    :lines: 25-40

But this codeblock gives an output

.. code-block:: json

    Running dataflow without locked object
    set i = 2, got i = 1
    set i = 1, got i = 1
    set i = 2, got i = 1
    set i = 1, got i = 1

We can see that the output is not what we expect. Since everything is running asynchrously,
when one operations sleeps the other operation might start running and it replaces the 
value. This is where locks come handy. We'll set ``run_me`` to take object of definition
``LOCKED_OBJ`` instead of ``OBJ`` and run the dataflow again.

.. literalinclude:: /../examples/dataflow/locking/example.py
    :linenos:
    :lineno-start: 42
    :lines: 42-63

This time the output is as expected

.. code-block:: json

    Running dataflow with locked object
    set i = 2, got i = 2
    set i = 1, got i = 1
    set i = 2, got i = 2
    set i = 1, got i = 1
