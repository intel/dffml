FLOWER17 Species classification using Transfer Learning
=======================================================

The model we'll be using is :ref:`AlexNet CNN Model <plugin_model_dffml_model_pytorch_alexnet>`
which is a part of ``dffml-model-pytorch``, a DFFML plugin which allows you to use PyTorch
via DFFML. We can install it with ``pip``. We will also be using image loading from
``dffml-config-image`` and YAML file loading from ``dffml-config-yaml``.

.. code-block:: console

    $ pip install -U dffml-model-pytorch dffml-config-yaml dffml-config-image

There are 2 ways to perform Transfer Learning:

1. Fine-tuning the CNN
    Initializing the network with pre-trained weights(trained on ImageNet1000 dataset)
    and training the whole network on the dataset.

2. Using the CNN as fixed feature-extractor
    We freeze the parameters of the complete network except the final layer, so that the
    gradients for any other layer except the last layer are not computed in back-propagation.


In this example, we will be fine-tuning the AlexNet model. (We set `trainable=True`)

We first create a YAML file to define the last layer(s) to replace from the network architecture:

.. literalinclude:: /../examples/flower17/pytorch-alexnet/layers.yaml

Train the model.

.. literalinclude:: /../examples/flower17/pytorch-alexnet/train.sh

.. code-block:: console

    INFO:dffml.AlexNetModelContext:Training complete in 5m 41s
    INFO:dffml.AlexNetModelContext:Best Validation Accuracy: 0.927602

Assess the model's accuracy.

.. literalinclude:: /../examples/flower17/pytorch-alexnet/accuracy.sh

The output is:

.. code-block:: console

    0.8196078431372549

Create an ``unknown_images.csv`` file which contains the filenames of the images to predict on.

.. literalinclude:: /../examples/flower17/unknown_data.sh

In this example, the ``unknown_images.csv`` file contains the filenames of the following images

.. image:: /../examples/flower17/daisy.jpg
    :width: 140px
    :height: 140px

.. image:: /../examples/flower17/pansy.jpg
    :width: 140px
    :height: 140px

.. image:: /../examples/flower17/tigerlily.jpg
    :width: 140px
    :height: 140px

.. image:: /../examples/flower17/buttercup.jpg
    :width: 140px
    :height: 140px

Predict with the trained model.

.. literalinclude:: /../examples/flower17/pytorch-alexnet/predict.sh

Output

.. literalinclude:: /../examples/flower17/pytorch-alexnet/output.txt

The model predicts all the flower species correctly with 99% confidence!
