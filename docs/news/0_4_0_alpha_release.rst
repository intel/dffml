0.4.0 Alpha Release
===================

Friends, Romans, countrymen, lend me ``pip install -U dffml`` commands.

It's been a long 10 months since our last release. A lot has changed in the
world of DFFML. Looking back it's clear how much progress we've made. The work
that was done to get us to 0.4.0 has really polished the project. There are no
doubt still kinks to work out, but we've come a long way.

If you're new to DFFML. See the :doc:`/installation` and
:doc:`/quickstart/model` documents to get started, then come back here to try
out the new features.

Highlights
----------

We have a ton of cool new features in this release. You can see the CHANGELOG
for the full details. We'll cover some highlights here.

- :doc:`Custom Neural Networks </tutorials/neuralnetwork>`

  - Saksham, one of our GSoC 2020 students, implemented PyTorch based models.
    The generic model allows users to use JSON or YAML files to define the
    layers they want in a neural network.

- :doc:`Image classification </examples/flower17/flower17>`

  - Saksham also exposed some PyTorch pre-trained models which are very useful
    for working with images. The full list can be found under
    :ref:`dffml-model-pytorch <plugin_model_dffml_model_pytorch>` on the model
    plugins page.

- :doc:`Natural Language Processing (NLP) Models and Operations </tutorials/dataflows/nlp>`

  - Himanshu, one of our GSoC 2020 students, implemented Natural Language
    Processing (NLP) models and operations. The Spacy based models can be found
    under :ref:`dffml-model-spacy <plugin_model_dffml_model_spacy>` on the model
    plugins page. The operations can be found under
    :ref:`dffml-operations-nlp <plugin_operation_dffml_operations_nlp>` on the
    operations plugins page. We had a slight hangup with the release of the
    Transformers based models, we hope to send all those out you all as soon as
    possible.

- :doc:`Continuous Deployment Examples </examples/webhook/index>`

  - Aghin, one of our GSoC 2020 students, wrote operations and tutorials which
    allow users to receive web hooks from GitHub and re-deploy their
    containerized models and operations whenever their code is updated.

- :doc:`New Models </plugins/dffml_model>`

  - In addition to the above mentioned models, we have many more that were
    added. We now have over 115 models! Check out the model plugins page to see
    them all.

- :doc:`Documentation Testing with Sphinx consoletest extention </contributing/consoletest>`

  - We developed a Sphinx extention which has allowed us to test the
    ``code-block:: console`` directives and others in our documentation. This
    serves as integration testing / documentation validation. The
    :doc:`/tutorials/models/docs` tutorial was written to explain how this can
    be used to write documentation for your models in the models' docstrings.

Road to Beta
------------

Things are looking up with regards to the path to our beta release.

We're going to start deciding what APIs are stable come the 0.5.0 beta release.

Up until then, including now, things have been subject to change at any time as
we have learned more about our problem space and how best to architecturally
approach it.

We have several major things on deck that we want to get before we declare beta.

- AutoML

  - We now have a lot of models to choose from and are at the stage where we
    need models to help us choose our models! We're going to have AutoML in the
    Beta release. This will pick the best model with the best hyper paramters
    for the job.

- Accuracy Scorers

  - Sudhanshu has been working on this since June 2020. He's done a major
    refactor of the codebase to take the accuracy methods out of all the models
    and move them into ``.score()`` methods in a new ``AccuracyScorer`` method.
    This will allow users to more easily compare accuracy of models against each
    other.

- Machine Learning support for videos

  - We still need to decide how we're going to support videos. DFFML's
    asynchronous approach will hopefully make it convenient to use with live
    video streams.

- Model directories auto stored into archives or remotely

  - We're going to implement automatic packing and unpacking of directories
    which models get saved and loaded from into/out of archives, such as Zip,
    Tar, etc. We'll also implement plugins to be able to push and pull them from
    remote storage. This will make models convenient to train in one location
    and deploy another.

- Remote execution

  - The :doc:`HTTP service </plugins/service/http/index>` already allows users
    to access all the DFFML command line and Python APIs over HTTP. We are going
    to integrate the :doc:`/api/high_level/index` API with the HTTP service. A remote
    execution plugin type will allow users to install only the base package,
    and whatever remote execution plugin they want on a machine. Users will then
    be able to run the HTTP service on a machine with all needed ML packages
    installed, and their Python API calls will run on the HTTP service. In cases
    where you have multiple architectures, one of which doesn't have ML
    packages compiled for it, this will be helpful (Edge).

- Config files in place of command line parameters

  - To stop users from having to copy paste so many command line parameters
    across command invocations, we'll be implementating support for config
    files. YAML, JSON, etc. will all be able to be used to store what could also
    be command line arguments.

- Command line to config file to Python API to HTTP API auto translation

  - Since DFFML offers consistent APIs across it's various interfaces, we will
    be able to implement an auto translator to convert one API to another. This
    means that if you have a DFFML command line invocation that you want to make
    into a Python API call, the translator will take your CLI command and output
    the DFFML Python API calls in Python.

- DataFlows with operation implementations in multiple languages

  - Our first target is to integrate wasmer to help us run web assembly
    binaries. We'll later expand this out to having multiple Operation
    Implementation networks that will allow users to create DataFlows that run
    code written in multiple languages. For example, Python, Rust, and Golang.
    This will allow users to leverage their favorite libraries to get the job
    done without worrying about them being in different languages.

- Premade data cleanup DataFlows

  - We'll have a set of out of the box data cleanup DataFlows that users can use
    before passing data to models. These will do common data cleanup tasks such
    as removing horrendous outliers.

- Continuous deployment tutorials

  - We will expand the tutorials released with 0.4.0 to include deployment
    behind reverse proxies for multiple projects, including how to setup
    encryption and authentication in a painless and maintainable way.

- Pandas DataFrame source

  - This is a small convenience that will probably improve usability. This
    change will allow us to pass DataFrame objects to the train/accuracy/predict
    functions.

Collaborations
--------------

- We're exploring participation with the OpenSSF Identifying Security Threats
  working group. Their effort is similar to :doc:`/shouldi` and we might be able
  to contribute some of what we've done there.

- We're exploring another use of DFFML internally at Intel. This time leveraging
  DataFlows more so than Machine Learning.


Thanks
------

Since 0.3.7 we've seen 35203/10423 insertions(+)/deletions(-) lines changed,
added, or removed, across 757 files.

You all have done amazing stuff!! Great job and keep up the good work!

- Aadarsh Singh
- Aghin Shah Alin
- Aitik Gupta
- Geetansh Saxena
- Hashim
- Himanshu Tripathi
- Ichisada Shioko
- Jan Keromnes
- Justin Moore
- Naeem Khoshnevis
- Nitesh Yadav
- Oliver O'Brien
- Saksham Arora
- Shaurya Puri
- Shivam Singh
- Sudeep Sidhu
- Sudhanshu kumar
- Sudharsana K J L
- Yash Lamba
- Yash Varshney
