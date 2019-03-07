Data Flow Facilitator for Machine Learning (dffml)
==================================================

.. image:: https://travis-ci.org/intel/dffml.svg
    :target: https://travis-ci.org/intel/dffml
.. image:: https://bestpractices.coreinfrastructure.org/projects/2594/badge
    :target: https://bestpractices.coreinfrastructure.org/projects/2594

Is DFFML Right For Me?
----------------------

If you answer yes to any of these questions DFFML can make your life easier.

- Dataset Generation

  - Need to generate a dataset
  - Need to run asynchronous operations in order to gather dataset (http
    requests, interaction with command line utilities, etc.)

- Models

  - Want to quickly prototype how machine learning could be used on a dataset
    without writing a model
  - Need to write a finely tuned model by interacting with low level APIs of
    popular machine learning frameworks.

- Storage

  - Need a way to use datasets which could be stored in different locations or
    formats.

About
-----

DFFML facilitates data generation, model creation, and use of models via
services. See `Architecture`_ to learn how it works.

- Facilitates data collection, model creation, and use of models via services.
- Provides plumbing to facilitate the collection of feature data to create
  datasets.
- Allows developers to define their ML models via a standardized API.

  - This let's users try different libraries / models to compare performance.

- Plugin based

  - Features which gather feature data (Number of Git Authors, etc.)
  - Models which expose ML models via the standard API (Tensorflow, Scikit,
    etc.)
  - Sources which load and store feature data (CSV, JSON, MySQL, etc.)

The plumbing DFFML provides enables users to swap out models and features,
in order to quickly prototype.

Installation
------------

DFFML currently should work with Python 3.6. However, only Python 3.7 is
officially supported. This is because there are a lot of nice helper methods
Python 3.7 implemented that we intend to use instead of re-implementing.

.. code-block:: bash

    python3.7 -m pip install -U dffml

You can also install the Features for Git Version Control, and Models for
Tensorflow Library all at once.

- `DFFML Features for Git Version Control <feature/git/README.rst>`_
- `DFFML Models for Tensorflow Library <model/tensorflow/README.rst>`_

If you want a quick how to on the iris dataset head to the
`DFFML Models for Tensorflow Library <model/tensorflow/README.rst>`_ repo.

.. code-block:: bash

    python3.7 -m pip install -U dffml[git,tensorflow]

Docker Build
------------

This is a good option if you don't want to deal with installing Python 3.7.

.. code-block:: bash

    docker build -t dffml .

You can then alias dffml to run the docker container.

.. code-block:: bash

    alias dffml="docker run --rm -ti -v $HOME/.local:/home/$USER/.local/ -v $PWD:/workdir -w /workdir -e UID=$(id -u) -e USER=$USER dffml"

This creates an alias that takes your current working directory and mounts it
into ``/workdir`` as well as your ``$HOME/.local`` to the same in the container.

With the alias, you can run ``dffml`` commands as you would if installed via
``pip``.

.. code-block:: bash

    dffml list

Keep in mind that if you're working on files they can only be ones in your
current working directory, and if you want to access network resources and they
are on your host, you'll have to talk to ``172.17.0.1`` (docker0 inet address)
instead of ``localhost`` or ``127.0.0.1``.

The purpose of mounting ``$HOME/.local`` is so that if you want to
``pip install`` anything, you can, and it will persist between invocations due
to that being on the host.

If you wan to run ``pip`` you can put it after ``dffml``.

.. code-block:: bash

    dffml pip install example

Hacking
-------

Then install in development mode to the virtualenv and development dependencies.

.. code-block:: bash

    git clone git@github.com:intel/dffml
    cd dffml
    pip install --user -e .[git,tensorflow]

Usage
-----

See `DFFML Models for Tensorflow Library <model/tensorflow/README.rst>`_ repo
until documentation here is updated with a generic example.

Testing
-------

.. code-block:: bash

    python3.7 setup.py test

Architecture
------------

When applying Machine Learning to a new problem developers must first collect
data for models to train on. DFFML facilitates the collection of feature data
to create datasets for models to learn on.

.. image:: https://github.com/intel/dffml/raw/master/docs/arch.png

DFFML's architecture can be thought of similarly to a search engine. Each
**Feature** a developer defines searches for data associated with the unique key
its provided with. Once the data is found it is added to a **Repo** (repository)
associated with that unique key. A **Feature**'s search for data is dubbed
*evaluation*. A **Repo** holds the results of each **Feature**'s evaluation.
Results are stored under their respective **Feature** names.

To define machine learning a model within DFFML, users create a **Model**.
Models are responsible for training, assessing accuracy, and making
predictions. After evaluation a **Repo** can be used by a **Model** for any of
those tasks. Defining a machine learning model as a **Model** allows users to
quickly compare accuracy of various models on their gathered dataset.

Once the best most accurate model is known, users can easily integrate use of
the model into existing applications via the Python API, or a **Service**.
Services provide applications with ways to access the DFFML API over various
protocols and deployment scenarios.

Repo
----

A repo is a repository of information. It is instantiated with a source URL
which represents or points to where more information on it can be found.

Every repo has (or wants) a classification. Those which already have
classifications can be used to train Models. The classification of the repo is
what Education will ask it's models to make predictions on.

Feature
------

Features are given a repo, containing at the minimum a source URL for it,
and produce a list of results which represent the evaluation of that feature.

Not all methods are applicable to all repos. As such, all Features implement the
``applicable`` method.

Feature is the abstract base class for all features. New features must be
derived from this class and implement the fetch, parse, and calc methods. These
methods are always called in order by the evaluator. However, they are executed
in parallel with the same stages of other features.

A feature is provided with a repo
and is expected to fetch any data it needs to calculate itself when fetch
is called. All data fetched should be stored in tempdir() if it must reside
on disk.

Once the appropriate data is fetched the parse method is responsible for
storing the parts of that data which will be used to calculate in the
subclass

.. code-block:: python

    from dffml.feature import Feature

    class StringByFT(Feature):

        async def fetch(self):
            self.__value = '42'

        async def parse(self):
            self.__value = int(self.__value)

The calc method then uses variables set in parse to calculate the feature.

.. code-block:: python

    async def calc(self):
        return self.__value * 42

.. code-block:: python

    entry_points={
        'dffml.feature': [
            'string_by_42 = mypackage.string_by_42:StringByFT',
        ],
    },

Source
------

Repos come from a source. Sources may contain more information on a repo than
just it's source URL. Sources are responsible for providing the repos they
contain and updating those repos upon request.

Model
-------

Models are feed classified repos from which they learn from during their
training phase. After training they can be used to make a prediction about the
classification of a repo.

License
-------

dffml is distributed under the MIT License, see ``LICENSE``.

Legal
-----

..

    This software is subject to the U.S. Export Administration Regulations and
    other U.S. law, and may not be exported or re-exported to certain countries
    (Cuba, Iran, Crimea Region of Ukraine, North Korea, Sudan, and Syria) or to
    persons or entities prohibited from receiving U.S. exports (including
    Denied Parties, Specially Designated Nationals, and entities on the Bureau
    of Export Administration Entity List or involved with missile technology or
    nuclear, chemical or biological weapons).
