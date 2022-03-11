GSoC 2022
=========

DFFML is hoping to participate in Google Summer of Code under the Python
Software Foundation umbrella. You can read all about what GSoC is at
http://python-gsoc.org/ and
https://summerofcode.withgoogle.com/how-it-works/#timeline

NOTE:
=====
  
One of our community members is going to deliver a talk on GSoC. 
We'd recommend new contributors join and clear any GSoC related queries. 
Link for registration: https://lnkd.in/gAWiVrAE (Time mentioned in IST timezone)


About DFFML
-----------

DFFML is a plugin based library / framework for machine learning. It allows
users to wrap high or low level implementations of models that use various
machine learning libraries, so as to interact will lots of different model
implementations in the same way.

DFFML is also a tool for dataset generation. DFFML ues directed graphs to
generate and modify datasets.

Read more on the about page: https://intel.github.io/dffml/master/about.html

Project Ideas
-------------

We currently have the following project ideas:

- `Save and Load Models to ONNX format <https://github.com/intel/dffml/blob/master/docs/contributing/gsoc/2022/onnx_save_load.md>`_

  - Allow for DFFML to save trained models in the Open Neural Network Exchange
    format. This will help users easily deploy models.
  - Begineer
  - 175 hours

- `Time-Series Forecasting and Anomaly Detection <https://github.com/intel/dffml/blob/master/docs/contributing/gsoc/2022/forecasting.md>`_

  - Give users of DFFML forecasting capabilties. Allow them to predict the
    future! Work with time stamped data to train models and make predictions.
  - Begineer
  - 350 hours

- `Implementing AutoML <https://github.com/intel/dffml/blob/master/docs/contributing/gsoc/2022/automl.md>`_

  - Implement hyperparameter tuners, best model selection via grid search and
    or other means, automated feature engineering by modifying dataflows.
  - Intermediate to Difficult
  - 350 hours

- `Refactor of DataFlows to Include Event Type <https://github.com/intel/dffml/blob/master/docs/contributing/gsoc/2022/dataflow_event_types.md>`_

  - Refactor the :py:func:`dffml.high_level.run` API (and others) to make
    running Data Flows as dynamic as their event based content. This will let us
    use Data Flows "all the way down", paving the way for us to provide
    unprecedented levels of configurability to users.
  - Difficult
  - 350 hours

If you've got a idea you'd like to propose, please make a new issue with the
`gsoc: project:` prefix to discuss it! We're open to all sorts of ideas.
Students are also welcome to add "stretch goal" ideas to their application,
which don't have to be related to their main proposal (but still have to result
in contributions to DFFML). Stretch goals are for if you finish your proposed
project before the end of the summer, and have more that you want to do.

Getting Started
---------------

- Read the `Contributing <https://intel.github.io/dffml/master/contributing/index.html>`_ documentation.

- Get your development environment set up

- Go through the tutorials on the documentation site, make sure you're familiar
  with the command line interface.

  - Run the quickstart.

  - Run the examples for the various models found on the model plugins page

- `Run the tests <https://github.com/intel/dffml/tree/master/tests>`_. DFFML has
  unit tests and we track coverage (amount of lines of code tested).
  Make sure you know how to run them, and if you've never done Python unittests
  before you might want to
  `read up on python's unittest library <https://docs.python.org/3/library/unittest.html>`_.
  Figure out how to run a single test! Running one test instead of all of them
  will speed up your workflow when you are writing your tests! (hint, it's in
  the contributing docs!)

- Make your first contribution!

  - Don't be afraid to not get it right on the first try. If we all got
    everything right on the first try there would be no bugs in software. And
    there are LOTS of bugs in software.

  - Doesn't have to be related to your project. Just make sure we know that you
    understand how to interact with the community, codebase, and GitHub. If
    you're not familiar that's okay! We'll show you the ropes, but you have to
    jump in the pool if you want to learn how to swim.

  - You could start with some small and extra small issues (time wise).

  - You could help us increase the test coverage in any of the packages (check
    out the python package `coverage` to learn how to do this).

  - You could write a `new model <https://github.com/intel/dffml/issues/29>`_!
    Models are wrappers around any machine learning implementation or library,
    see the
    `new model tutorials
    <https://intel.github.io/dffml/master/tutorials/models/index.html>`_
    for more info. Make sure to include tests!

  - You could write a new operation to do something! Anything! Operations to
    grab weather and stock data have been suggested by people as good ideas.
    See the `Ice Cream Sales
    <https://intel.github.io/dffml/master/examples/icecream_sales.html>`_
    example.

Writing your GSoC application
-----------------------------

Instructions on `How to apply <http://python-gsoc.org/#apply>`_ can be found on
the Python GSoC website. Please don't forget to use our name (**DFFML**) in your
application title!

In your proposal, we're looking to see:

- What work you want to get done.

- How long you think it will take you.

- Why you think it will take you that long.

  - When estimating how long it will take you it helps to think about any
    contributions to DFFML you've done up until now and compare what you're
    proposing to what you've done.

Here's a template:
https://github.com/python-gsoc/python-gsoc.github.io/blob/464c41fc7b90d4e57a0a4582bf3531d8a742cc6b/2019/application2019.md

Deadlines
---------

See the milestones prefixed with "GSoC 2022"
https://github.com/intel/dffml/milestones?direction=desc&sort=due_date&state=open

Please see the :doc:`/contributing/gsoc/rubric` page for the project
proposal grading rubric.

Contacting the DFFML team
-------------------------

Most of our communication takes place on the
`Gitter channel <https://gitter.im/dffml/community>`_ you can also check out the
:doc:`/contact` page in the docs for more ways to get in touch.

We run a weekly meeting that we encourage everyone to join. We get people
started and do debugging.

If we're not responding, we may be busy and forgotten about your message. Ping
us again. In the meantime, try to think about approaching your problem from a
different angle. And when in doubt use the source! Reading the source of
something you're importing or using can be very helpful in figuring out your
problem.

Mentors
-------

This years mentors are as follows.

- Saahil Ali `@programmer290399 <https://github.com/programmer290399>`_
- John Andersen `@pdxjohnny <https://github.com/pdxjohnny>`_

Thanks
------

Big thanks to `Terri Oda <https://github.com/terriko>`_ her work organizing GSoC
and letting us copy her format she used for
`CVE Binary Tool <https://github.com/intel/cve-bin-tool>`_, another awesome
project with a security focus that has also been (and still is) a part of GSoC
as well. Check them out too!
