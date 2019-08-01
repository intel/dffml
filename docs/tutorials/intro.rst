Introduction to DFFML
=====================

DFFML aims to streamline the training and use of various machine learning
models, dataset collection, and storage. As such there are three sides to the
DFFML triangle.

- :ref:`intro_sources` abstract the storage of datasets.

- :ref:`intro_models` abstract implementations of machine learning algorithms.

- The :ref:`intro_data_flow` side of things is used to generate a dataset, as well as
  modify existing datasets.

.. _intro_sources:

Sources
-------

A ``Source`` of data might be something like a CSV file, SQL database, or HDFS.

By providing a generic abstraction around where data is being saved and stored,
model implementations can access the data via the same API no matter where it is
stored.

Repos
~~~~~

A common construct within DFFML is the ``Repo``. A ``Repo`` object is a
repository of information associated with a unique key. The ``Repo`` holds all
the data associated with that key.

Say for instance you generated a dataset that had to do with cities. Your unique
key might be the name of the city, the state or province it's in, and the
country it's in. For example: ``Portland, OR, USA``.

The data associated with a ``Repo`` is called the feature data. Its stored
within a key value mapping within the ``Repo`` accessible via the
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

By wrapping various implementations of machine learning algorithms in DFFMLs
API, applications using DFFML via its Python library interface, command line
interface (, or coming soon its HTTP interface), can benefit from them being
wrapped in a similar design pattern. This means that switching from a model
implementing with one major framework to another is painless.

.. _intro_data_flow:

Data Flow
---------

One can think of the data flow side of DFFML as a event loop running at a high
level of abstraction. Event loop usually refers to waiting for ``read``,
``write``, and ``error`` events on network connections, files, or if you're in
JavaScript, a click on the page for instance.

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

The following are the key concepts relating to data flow.

Definition
~~~~~~~~~~

The name of the data type, and what it's primitive is. Primitive meaning is it a
string, integer, float, etc.

If a piece of data created or used of this data type needs to be locked. The
definition will also specify that (``lock=True``).

Operation
~~~~~~~~~

A name associated with some routine or function that will process some input
data and produce some output data.

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
parameters.

Lock Network
~~~~~~~~~~~~

Manges locking for Inputs.

Orchestrator
~~~~~~~~~~~~

All data flow objects are utilized via an Orchestrator
