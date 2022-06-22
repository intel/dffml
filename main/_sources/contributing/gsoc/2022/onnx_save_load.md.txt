# Save and Load Models to ONNX format

The goal of this project is to modify Models and use DataFlows to support saving
and loading to/from ONNX format.

Last year support was implemented for saving and loading to/from `.zip` and
`.tar` archives.

Currently all DFFML models have a `location` property, which is where they
store the contents of the model's state.

We want to enable people to easily save their models in the ONNX format. We want
to add support for saving to existing applicable models.

We want to enable people to easily loaded ONNX models and use them.

We want to document our changes so that people know how to use this new
functionality!

## Skills

- Python

## Difficulty

Beginner

## Estimated Time Required

175 hours

## Related Readings

- https://intel.github.io/dffml/main/contributing/gsoc/2022/
- https://github.com/onnx/tensorflow-onnx
- https://github.com/onnx/tutorials/blob/master/tutorials/TensorflowToOnnx-1.ipynb
- https://github.com/onnx/tutorials/blob/master/tutorials/OnnxTensorflowImport.ipynb
- The commit where archive support was implemented
  - [38390a45ea5a2aacd1dc2398ac2acbcf9b8c7a53](https://github.com/intel/dffml/commit/38390a45ea5a2aacd1dc2398ac2acbcf9b8c7a53)
- ``$ git log -p -- dffml/model/``

## Getting Started

- Read the contributing guidelines
  - https://intel.github.io/dffml/main/contributing/index.html
- Go through the quickstart
  - https://intel.github.io/dffml/main/quickstart/model.html
- Go trough the model tutorials
  - https://intel.github.io/dffml/main/tutorials/models/
- Go through the model plugins
  - https://intel.github.io/dffml/main/plugins/dffml_model.html
- Train a tensorflow model
  - https://intel.github.io/dffml/main/tutorials/models/iris.html
  - https://intel.github.io/dffml/main/examples/mnist.html
- Attempt exporting the tensorflow model
  - https://github.com/onnx/tensorflow-onnx
  - https://github.com/onnx/tutorials/blob/main/tutorials/TensorflowToOnnx-1.ipynb
- Attempt import of ONNX tensorflow model
  - https://github.com/onnx/tutorials/blob/main/tutorials/OnnxTensorflowImport.ipynb
- Start programming to understand better what will need to happen. The following
  is a rough guide meant to give you some activities that will help you better
  understand what needs to be done so you can write a more complete proposal.
  - On `__aenter__()` of `dffml.model.model.Model`, look at how `location` is
    inspected and `location_load` is used to load a model from an archive.
    - Think about how you would write a subclass of Model which would load an
      ONNX model.
  - Think about what model(s) you'll need to implement (A new ONNX based one?)
  - Think about what changes you'll need to make to the existing model loading.

## Potential Mentors

- [John Andersen](https://github.com/pdxjohnny)
- [Saahil Ali](https://github.com/programmer290399)

## Tracking and Discussion

This project is related to the following issues. Please discuss and ask
questions in the issue comments. Please also ping mentors on
[Gitter](https://gitter.im/dffml/community) when you post on the following
issues so that they are sure to see that you've commented.

- https://github.com/intel/dffml/issues/662
