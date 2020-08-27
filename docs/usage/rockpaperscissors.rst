Rock Paper Scissors Classification using Custom Neural Network
==============================================================

This example will show you how to train and test a PyTorch based custom neural network model made using DFFML.
The dataset we will be using is the `rock-paper-scissors-dataset <http://www.laurencemoroney.com/rock-paper-scissors-dataset/>`_
which contains images of hands in Rock/Paper/Scissors poses, each image is a 300x300 RGB image.

The model we'll be using is :ref:`PyTorchNeuralNetwork <plugin_model_dffml_model_pytorch_pytorchnet>`
which is a part of ``dffml-model-pytorch``, a DFFML plugin which allows you to use PyTorch
via DFFML. We can install it with ``pip``. We will also be using image loading from
``dffml-config-image`` and YAML file loading from ``dffml-config-yaml`` for creating our neural network.

.. code-block:: console

    $ pip install -U dffml-model-pytorch dffml-config-image dffml-config-yaml


Download the dataset and verify with with ``sha384sum``.

.. literalinclude:: /../examples/rockpaperscissors/dataset.sh

.. code-block:: console

    rps.zip: OK
    rps-test-set.zip: OK
    rps-validation.zip: OK

Extract the datasets.

.. code-block:: console

    $ unzip rps.zip
    $ unzip rps-test-set.zip
    $ unzip rps-validation.zip -d rps-predict

The dataset for training the model will be in the `rps` directory.
The dataset for testing the model will be in the `rps-test-set` directory.
The images we will be using for prediction on the neural network will be in the `rps-predict` directory.

Now that we have our dataset ready, we can perform classification of the hand poses to predict whether
it is rock, paper or scissors!

We first create the neural network.

The neural network can be created in 2 ways using DFFML:
    1. By creating a dictionary of layers in YAML or JSON format passing the file via CLI (eg. @model.yaml).
    2. By using the torch module to create the model and passing an instance of the network to the model config.


Command Line
------------

We first create a YAML file to define the neural network with all the information about the layers along with
the forward method which is passed as list of layers under the model name key:

.. literalinclude:: /../examples/rockpaperscissors/model.yaml

.. seealso::
    Sequential layers can also be created by indenting the layers under a key!
    The layers definied inside the Sequential layer can be used again while defining the forward method in the
    following syntax: `- key1.layer2`

.. Note::
    If the forward method is not given in the YAML file, forward method is automatically creating by appending
    the top level layers sequentially.

Train the model.

.. literalinclude:: /../examples/rockpaperscissors/train.sh

.. code-block:: console

    INFO:dffml.PyTorchNeuralNetworkContext:Training complete in 1m 42s
    INFO:dffml.PyTorchNeuralNetworkContext:Best Validation Accuracy: 1.000000

Assess the model's accuracy.

.. literalinclude:: /../examples/rockpaperscissors/accuracy.sh

The output is:

.. code-block:: console

    0.8306451612903226

Predict with the trained model.

.. literalinclude:: /../examples/rockpaperscissors/predict.sh

Some of the Predictions:

.. literalinclude:: /../examples/rockpaperscissors/output.txt


Python API
----------

.. literalinclude:: /../examples/rockpaperscissors/python_example.py

The output will be as follows:

.. literalinclude:: /../examples/rockpaperscissors/python_output.txt

The model predicts the hand poses correctly with great confidence!
