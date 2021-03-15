# Implementing AutoML

AutoML or Automated Machine Learning as the name suggests automates the process
of solving problems with Machine Learning. AutoML is generally helpful for
people who aren't either familiar with Machine Learning or the involved
programming. AutoML aims to improve the efficiency of any task involving
Machine Learning.

The primary objective we are trying to achieve is to create a model that
takes as a property of its config a set of models to used for hyperparameter
tuning. Another property of its config is the set of models which we should
attempt to tune (via the first set). Default values for these results in using
all installed models to try to tune all installed model plugins.

- To start, we should define a reduced set of models (not all the ones we have).
  We'll implement AutoML supporting only this reduced set. The first phase of
  this project will be to make sure that one model can be used to tune
  hyperparameters of another model.

- The next phase will be to tune two models using the same tuning model. This
  followed by tuning two models, using two models which amounts to doing the
  previous task twice, with a different tuning model the second time.

- The following phase will be to go through each model in each model plugin we
  have and see which ones have issues being tuned using the approach taken in the
  previous phase. This phase will help us determine which properties or methods
  we may need to add to models to help them self identify and thereby indicate
  their requirements for hyperparameter tuning, or maybe their inherent lack of
  support for it.

- The final phase will be to implement hyperparameter tuning for N by N models,
  after implementing what we found to be gaps in the previous phase.<br>

Due to the shortened GSoC cycle, we may end up not doing all of these phases.
Which one we go to will be decided as we approach the selection process.

## Skills

- Python
- Intermediate Machine Learning
- Experience with various machine learning frameworks (AutoML frameworks would
  be a plus)

## Difficulty

Intermediate/Hard

## Related Readings

- https://github.com/intel/dffml/blob/master/docs/contributing/gsoc/2021.md
- https://scikit-learn.org/stable/model_selection.html#model-selection
- https://www.automl.org/automl/

## Getting Started

- Read the contributing guidelines
  - https://intel.github.io/dffml/master/contributing/index.html
- Go through the quickstart
  - https://intel.github.io/dffml/master/quickstart/model.html
- Go trough the model tutorials
  - https://intel.github.io/dffml/master/tutorials/models/
- Go through the model plugins
  - https://intel.github.io/dffml/master/plugins/dffml_model.html

## Potential Mentors

- [John Andersen](https://github.com/pdxjohnny)
- [Yash Lamba](https://github.com/yashlamba)
- [Saksham Arora](https://github.com/sakshamarora1)

## Tracking and Discussion

This project is related to the following issues. Please discuss and ask
questions in the issue comments. Please also ping mentors on
[Gitter](https://gitter.im/dffml/community) when you post on the following
issues so that they are sure to see that you've commented.

- https://github.com/intel/dffml/issues/968
