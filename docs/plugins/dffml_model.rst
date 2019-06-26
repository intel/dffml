Models
======

Models are implementations of :class:`dffml.model.model.Model`, they
abstract the usage of machine learning models.

dffml_model_tensorflow
----------------------

tfdnnc
~~~~~~

*Core*

Implemented using Tensorflow's DNNClassifier. Models are saved under the
``directory`` in subdirectories named after the hash of their feature names.

**Args**

- directory: String

  - default: /home/user/.cache/dffml/tensorflow
  - Directory where state should be saved

- steps: Integer

  - default: 3000
  - Number of steps to train the model

- epochs: Integer

  - default: 30
  - Number of iterations to pass over all repos in a source

- hidden: List of integers

  - default: [12, 40, 15]
  - List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer
