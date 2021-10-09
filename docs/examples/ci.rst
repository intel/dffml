Continuous Integration
======================

In this example we're going to build a continuous integration system.

Problem Statement
-----------------

GitHub Actions is great on a per repo basis. Sometimes you have the same CI job
that you'd like to run on multiple repos, only changing the config per repo.

One way you could do that is by adding the same workflow file to each repo.
However, this means you have to keep those workflow files in sync across repos
when the workflow is updated.

This example will cover building a CI system where workflows are centrally
managed. This eliminates variation between repo workflows and enables
organizational consistency.

Plan
----

Let's plan out how our CI process should work.

We know we're building a centralized CI service, so we want a main CI repo.
We'll call each other repo a Repo Under Test (RUT). We're assuming there are
``N`` RUTs, in the below description we describe one instance, since they are
all the same fundamentally.

- Central CI repo

  - Has access to compute to run each jobs for each RUT

    - In this example we'll assume compute is being provided by Kubernetes.
      You could host on different compute by writing an ``Orchestrator`` to
      interact with your platform / infrastructure as a service of choice.
      **TODO** Tutorial on writing an ``Orchestrator``
      https://github.com/intel/dffml/issues/1250

  - Has access to secrets

    - Secret management must allow for pre RUT secrets and globally applicable
      secrets to be accessed by the central CI repo.

  - Contains CI jobs to run

    - These will be in the form of DataFlows

  - Contains mappings of which CI jobs to run on which RUTs

    - These will be in the form of DataFlows

- Repos Under Test (RUTs)

  - Contain code

  - Contain jobs that are specific to just that repo
