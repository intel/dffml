About
=====

Data Flow Facilitator for Machine Learning (DFFML) makes it easy to generate
datasets, train and use machine learning models, and integrate machine learning
into new or existing applications. It provides APIs for dataset generation,
storage, and model definition.

- Models handle implementations of machine learning algorithms.
  Likely wrapping code from a popular machine learning framework.

- Sources handle the storage of datasets, saving and loading them from files,
  databases, remote APIs, etc.

- DataFlows are directed graphs used to generate a dataset, as well as modify
  existing datasets. They can also be used to do non-machine learning tasks, you
  could use them to build a web app for instance.

You'll find the existing implementations of all of these on their respective
:ref:`plugins` pages. DFFML has a plugin based architecture, which allows us to
include some sources, models, and operations as a part of the main package,
``dffml``, and other functionality in more specific packages.

Mission Statement
-----------------

DFFML aims to be the easiest and most convenient way to use Machine Learning.

- Its a machine learning distribution. Providing you access to a set of popular
  machine learning libraries guaranteed to work together.

- Its a AI/ML Python library, command line application, and HTTP service.

- You give it your data and tell it what kind of model you want to train. It
  creates a model for you.

- If you want finer grained control over the model, you can easily do so by
  implementing your own model plugin.

- We make it easy to use and deploy your models.

- We provide a directed graph concurrent execution environment with managed
  locking which we call DataFlows.

- DataFlows make it easy to generate datasets or modify existing datasets for
  rapid iteration on feature engineering.

What is key objective of DataFlows
----------------------------------

- Our objective is to provide an environment where users can describe what they
  want done, without needing to know how it gets done.

- By separating the what from the how, each implementation of how a piece of
  work gets done doesn’t need to know anything about the implementations of how
  other pieces of work get done.

- This approach allows domain experts to implement the work within their
  domain, without needing to know anything about how the work of other domain
  experts is done.

- In such an environment, individual pieces of work implemented by respective
  domain experts can be knit together to accomplish arbitrary tasks.

- By taking this approach of separating the what from the how, we’ve created an
  environment where anyone can describe what they want to get done. How it gets
  done is handled by executing implementations provided by domain experts.

Why is this objective important?
--------------------------------

- Our existing software development model requires that experts in various
  domains maintain implementations of software which must be actively kept
  compatible with each other.

- By adopting this new model, we maximize workplace efficiency by compatibility
  between domain expert work being done at an orchestration level.

What industry challenges do DataFlows address / solve?
------------------------------------------------------

- We address and provide a solution for the challenge of how software written by
  experts in different domains can be used together without integration
  overhead.

Why DFFML
---------

- You want a "just bring your data" approach to machine learning.

  - No need to write code if you don't want to, use popular machine learning
    libraries via the command line, high level Python abstraction, or HTTP API.

- You want to do machine learning on a new problem that you don't have a dataset
  for, so you need to generate it.

  - Directed Graph Execution lets you write code that runs concurrently with
    managed locking. Making the feature engineering iteration process very fast.

Architecture
------------

This is a high level overview of how DFFML works.

.. TODO Autogenerate image during build

    graph TD

    subgraph DataFlow[Dataset Generation]
      df[Directed Graph Execution]
      generate_features[Generate Feature Data]
      single[Single Record]
      all[Whole DataSet]

      df --> generate_features
      generate_features --> single
      generate_features --> all
    end

    subgraph ml[Machine Learning]
      train[Model Training]
      accuracy[Model Accuracy Assessment]
      predict[Prediction Using Trained Model]
    end

    subgraph sources[Dataset Storage]
      source[Dataset Storage Abstraction]
      JSON
      CSV
      MySQL

      source --> JSON
      source --> CSV
      source --> MySQL
    end

    all --> train
    all --> accuracy
    single --> predict

    generate_features --> source
    predict --> source

.. image:: /images/arch.svg
    :alt: Architecture Diagram

Machine Learning
----------------

Python was chosen because of the machine learning community’s preference towards
it. In addition to the data flow side of DFFML, there is a machine learning
focused side. It provides a standardized way to defining, training, and using
models. It also allows for wrapping existing models so as to expose them via the
standardized API. Models can then be integrated into data flows as operations.
This enables trivial layering of models to create complex features. See
:ref:`plugin_models` for existing models and usage.

Data Flows - Directed Graph Execution
-------------------------------------

The idea behind this project is to provide a way to link together various new
or existing pieces of code and run them via an orchestration engine that
forwards the data between them all. Similar a microservice architecture but with
the orchestration being preformed according to a directed graph. This offers
greater flexibility in that interaction between services can easily be modified
without changing code, only the graph (known as the dataflow).

This is an example of the dataflow for a meta static analysis tool for Python,
``shouldi``. We take the package name (package) and feed it through operations,
which are just functions (but could be anything, some SaaS web API endpoint for
instance). All the data generated by running these operations is query-able,
allowing us to structure the output in whatever way is most fitting for our
application.

.. image:: /images/shouldi-dataflow.svg
    :alt: DataFlow for shouldi tool

Consistent API
--------------

DFFML decouples the interface through which the flow is accessed from the flow
itself. For instance, data flows can be run via the library, HTTP API, CLI, or
any communication channel (next targets are Slack and IRC). Data flows are also
asynchronous in nature, allowing them to be used to build any event driven
application (Chat, IoT data, etc.). The way in which operations are defined and
executed by the orchestrator will let us take existing API endpoints and code in
other languages and combine them into one cohesive workflow. The architecture
itself is programming language agnostic, the first implementation has been
written in Python.

Plugins
-------

We take a community driven approach to content. Architecture is plugin based,
which means anyone can swap out any piece by writing their own plugin and
publishing it to the Python Package Index. This means that developers can
publish operations and machine learning models that work out of the box with
everything else maintained as a part of the core repository and with other
developers models and operations. :doc:`tutorials/index` show how to create your
own plugins.

Users
-----

The following is a list of organizations and projects using DFFML. Please let us
know if you are using DFFML and we'll add you to the list. If you want help
using DFFML, see the :doc:`contact` page.

- Intel

  - Security analysis of Open Source Software dependencies.

Philosophy
----------

DFFML is an event driven directed graph execution architecture tightly coupled
with the typical machine learning workflow. The core concept is that all
software can be looked at as a set of operations that occur in response to
asynchronous events. Directed graphs are used to specify which operations should
be run in response to which events. Every event has data associated with it,
therefore we refer to the directed graph as a DataFlow.

The project as it exists now is a Python library which provides data set
generation via DataFlows, dataset storage, as well as model training, testing,
and inference. Users can leverage DataFlows to do feature engineering, to create
new datasets and modify or add to existing datasets. They then train models,
assess their accuracy and use them to make predictions via various deployment
methods.

DFFML has a plugin based architecture. Every model, data source, operation, etc.
is a plugin. We maintain a set of official plugins which wrap various machine
learning frameworks such as Daal4Py, TensorFlow, Scikit Learn, etc. By wrapping
frameworks in a standard API we simplify usage and make it easy for developers
to switch from one underlying framework to another.

Conceptually, DFFML is not just the Python implementation it is today. It’s a
programming language agnostic architecture centered around the concept of
DataFlows and the decoupling of definition from implementation. One goal of the
project closely associated with this is to have an orchestrator capable of
deploying and knitting together new or existing services without the need for
those services to know anything about each other. This could be thought of as a
level of abstraction beyond serverless architecture, which is where we're hoping
to take the project.

Team
----

We have an awesome team working on the project. We hold weekly meetings
and have a mailing list and chat! If you want to get involved, ask questions, or
get help getting started, see :doc:`contact`.

We participated in Google Summer of Code 2019 under the Python Software
Foundation. A big thanks to our students, Yash and Sudharsana!

- :doc:`GSoC 2019 Student Contributions <contributing/gsoc/2019>`

We are currently participating in Google Summer of Code 2020 under the Python
Software Foundation. Big thanks to Aghin, Himanshu, and Saksham!

- :doc:`GSoC 2020 Student Contributions <contributing/gsoc/2020>`

Thank you to everyone who's contributed to DFFML!!!

- Abdallah Bashir

- Aghin Shah Alin

- Arvindh Kumar Chandran

- Aryan Gupta

- Byambaa

- Constanza Heath

- Dentigg

- Dmitry Poliuha

- Govindarajan Panneerselvam

- Hashim

- Himanshu Tripathi

- iamandeepsandhu

- Jan Keromnes

- John Andersen

- Joseph Kato

- Justin Moore

- Naeem Khoshnevis

- NeerajBhadani

- NMNDV

- Pankaj Patil

- pradeepbhadani

- purnimapatel

- raghav-ys

- Saksham Arora

- Sanket Saurav

- shivam singh

- Sudhanshu kumar

- Sudharsana K J L

- Taksh Kamlesh

- Theo

- us

- Vaibhav Mehra

- Yash Lamba

- Yash Varshney

.. Generated with `git log --format=format:'%an' | sort | uniq`
   You'll want to filter out duplicates if you re-generate this
