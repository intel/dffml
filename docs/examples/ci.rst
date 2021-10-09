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
