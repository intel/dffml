Concepts
========

Here we explain the main concepts of DFFML. How things work, and the
philosophies behind why they work the way they do. If anything here is unclear,
or you think there's a more user friendly way to do something, please let us
know. See the :doc:`/contact` page for how to reach us.

DFFML aims to streamline the training and use of various machine learning
models, dataset collection, and storage. As such there are three sides to the
DFFML triangle.

- :ref:`intro_sources` abstract the storage of datasets.

- :ref:`intro_models` abstract implementations of machine learning algorithms.

- :ref:`intro_data_flow` are used to generate a datasets, as well as
  modify existing datasets.

Every part of DFFML is a plugin, which means that you can replace it with your
own implementation without needing to modifying DFFML itself. It also means
everyone can use each others plugins by publishing them to PyPi, or just
creating a public Git repo.

If you don't see the plugin you need already implemented under
:doc:`/plugins/index`, you can :ref:`cli_service_dev_create` it yourself.

.. _intro_sources:

Sources
-------

A ``Source`` of data might be something like a CSV file, SQL database, or HDFS.

By providing a generic abstraction around where data is being saved and stored,
model implementations can access the data via the same API no matter where it
is.

Records
~~~~~~~

A common construct within DFFML is the ``Record``. A ``Record`` object is a
repository of information associated with a unique key. The ``Record`` holds all
the data associated with that key.

Say for instance you generated a dataset that had to do with cities. Your unique
key might be the name of the city, the state or province it's in, and the
country it's in. For example: ``Portland, OR, USA``.

The data associated with a ``Record`` is called the feature data. Its stored
within a key value mapping within the ``Record`` accessible via the
``features()`` method. Our city example might have the following feature data.

.. code-block:: json

    {
      "climate": "rainy",
      "population": "too many",
      "traffic": "heavy"
    }

.. _intro_models:

Models
------

A ``Model`` could be any implementation of a machine learning algorithm.

By wrapping various implementations of machine learning algorithms in DFFML's
API, applications using DFFML via its Python library interface, command line
interface, or HTTP interface, can benefit from them being wrapped in a similar
design pattern. This means that switching from a model implemented with one
major framework to another is painless.

.. _intro_data_flow:

DataFlows
---------

One can think of the data flow side of DFFML as a event loop running at a high
level of abstraction. Event loop usually refers to waiting for ``read``,
``write``, and ``error`` events on network connections, files, or if you're in
JavaScript, it might be a click.

The idea behind event loops is that when a new event comes in, it triggers some
processing of the data associated with that event.

For DFFML we define data types that we care about, and then define operations
(essentially functions) that get run when new data of our defined data types
shows up.

One benefit of using the data flow programming abstraction provided by DFFML is
it runs everything concurrently and manages locking of data used by the routines
running concurrently. In addition to running concurrently, ``asyncio``, which
DFFML makes heavy use of, makes it easy to run things in parallel, so as to
fully utilize a CPUs cores and threads.

The following are the key concepts relating to DataFlows.

Definition
~~~~~~~~~~

The name of the data type, and what it's primitive is. Primitive meaning is it a
string, integer, float, etc.

If a piece of data created or used of this data type needs to be locked, the
definition will also specify that (``lock=True``).

Operation
~~~~~~~~~

The definition of some routine or function that will process some input
data and produce some output data. It contains the names of the inputs and
outputs, what stage the operation runs in, and the name of the operation.

Stage
~~~~~

Operations can be run at various different stages.

- Processing

  - Operations with this stage will be run until no new permutations of their
    input parameters exist.

- Cleanup

  - After there are no operations to be run in the processing stage, cleanup
    operations are run to free any resources created during processing.

- Output

  - Used to get data out of the network. Operations running in the output Stage
    will produce the data used as the result of running all the operations.

Operation Implementation
~~~~~~~~~~~~~~~~~~~~~~~~

The routine or function responsible for preforming an Operation.

We separate the concept of an operation from its implementation because the goal
is to allow for transparent execution of operations written in other languages,
deployed as micro services, or parts of SaaS APIs. Transparent from the view of
the DataFlow which defines the interconnections between operations.

Input Network
~~~~~~~~~~~~~

All data, inputs and outputs live within the Input Network, since outputs of one
operation are usually inputs to another, we refer to them all as inputs.
Therefore, they all reside within the Input Network.

Operation Network
~~~~~~~~~~~~~~~~~

All the definitions of Operations reside in the Operation Network.

Operation Implementation Network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the references to implementations of Operations reside in the Operation
Implementation Network.

This network is responsible for the execution of any given Operation within it.

Redundancy Checker
~~~~~~~~~~~~~~~~~~

Checks if an operation has been called before with a given set of input
parameters. This is used because a DataFlow runs by executing all possible
permutations of inputs for any given operation, and completes when no new
permutations of inputs exist for every operation.

Lock Network
~~~~~~~~~~~~

Manages locking of input data so that operations can run concurrently without
managing their own resource locking.

Orchestrator
~~~~~~~~~~~~

The orchestrator uses the various networks to execute dataflows.

.. toctree::
    :glob:
    :maxdepth: 2

    dataflow
