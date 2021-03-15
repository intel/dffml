# Dataset Cleanup Operations and DataFlows

The goal here is to provide data flows that would work "out of the box" for most
users dataset cleanup needs.

This might mean data flows that drop outliers, convert dates, etc.

We need to take an evidence based approach. Using several real world popular
datasets (which have no legal or ethical questions whatsoever, we try to stay
out of trouble here!) we'll want to see what cleanup is required for each of
them. We'll then make sure that we have pre-made data flows which work for all
of that set of example datasets.

We probably want to come up with an easier way to chain data flows together as a
part of this (rather than the merge command). This means taking the cleaned up
data from one data flow and cleaning that further using another data flow.

## Skills

- Python
- Experience with feature engineering

## Difficulty

Intermediate

## Related Readings

- https://intel.github.io/dffml/master/contributing/gsoc/2021/index.html
- We have some preprocessing operations for images and NLP already. Some of them leverage scikit
  - https://intel.github.io/dffml/master/plugins/dffml_operation.html#dffml-operations-nlp
  - https://intel.github.io/dffml/master/plugins/dffml_operation.html#dffml-operations-image
  - https://scikit-learn.org/stable/modules/preprocessing.html#preprocessing

## Getting Started

- Read the contributing guidelines
  - https://intel.github.io/dffml/master/contributing/index.html
- Go through the quickstart
  - https://intel.github.io/dffml/master/quickstart/model.html
- Go trough the model tutorials
  - https://intel.github.io/dffml/master/tutorials/models/
- Go through the model plugins
  - https://intel.github.io/dffml/master/plugins/dffml_model.html
- Go through the data flow related docs and tutorials
  - https://intel.github.io/dffml/master/tutorials/dataflows/index.html
  - https://intel.github.io/dffml/master/examples/integration.html
  - https://intel.github.io/dffml/master/examples/shouldi.html
  - https://intel.github.io/dffml/master/examples/dataflows.html
  - https://intel.github.io/dffml/master/examples/mnist.html
  - https://intel.github.io/dffml/master/examples/flower17/flower17.html
  - https://intel.github.io/dffml/master/examples/webhook/index.html
- Find a few public datasets that are in need of cleanup
  - Make sure there are a mix of data types, floats, ints, boolean values.
  - Make sure that across all the examples you find, there are at least 4
    categorical columns of a string data type. For example, city names, animal
    names, etc.
- Prototype what steps you need to take to cleanup the data
  - A step might be, remove outliers, encode categorical data to numeric,
    normalize, etc.
- Implement any cleanup steps for those datasets
- Run the datasets through a few models, with and without cleanup steps applied.
  Record the difference in accuracy. Make sure that you choose datasets which
  result in good accuracy after cleanup. We want to use simple examples.

## Potential Mentors

- [John Andersen](https://github.com/pdxjohnny)
- [Saksham Arora](https://github.com/sakshamarora1)

## Tracking and Discussion

This project is related to the following issues. Please discuss and ask
questions in the issue comments. Please also ping mentors on
[Gitter](https://gitter.im/dffml/community) when you post on the following
issues so that they are sure to see that you've commented.

- https://github.com/intel/dffml/issues/969 (main issue to track this project)
- https://github.com/intel/dffml/issues/819
- https://github.com/intel/dffml/issues/652
