"""
Machine Learning models implemented with `PyTorch <https://pytorch.org/>`_.
Models are saved under the directory in `model.pt`.

**General Usage:**

Training:

.. code-block:: console

    $ dffml train \\
        -model PYTORCH_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-directory MODEL_DIRECTORY \\
        -model-CONFIGS CONFIG_VALUES \\
        -sources f=TRAINING_DATA_SOURCE_TYPE \\
        -source-CONFIGS TRAINING_DATA \\
        -log debug

Testing and Accuracy:

.. code-block:: console

    $ dffml accuracy \\
        -model PYTORCH_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-directory MODEL_DIRECTORY \\
        -model-CONFIGS CONFIG_VALUES \\
        -sources f=TESTING_DATA_SOURCE_TYPE \\
        -source-CONFIGS TESTING_DATA \\
        -log debug

Predicting with trained model:

.. code-block:: console

    $ dffml predict all \\
        -model PYTORCH_MODEL_ENTRYPOINT \\
        -model-features FEATURE_DEFINITION \\
        -model-predict TO_PREDICT \\
        -model-directory MODEL_DIRECTORY \\
        -model-CONFIGS CONFIG_VALUES \\
        -sources f=PREDICT_DATA_SOURCE_TYPE \\
        -source-CONFIGS PREDICTION_DATA \\
        -log debug


**Pre-Trained Models Available:**

+----------------+---------------------------------+--------------------+--------------------------------------------------------------------------------+
| Type           | Model                           | Entrypoint         | Architecture                                                                   |
+================+=================================+====================+================================================================================+
| Classification | AlexNet                         | alexnet            | `AlexNet architecture <https://arxiv.org/abs/1404.5997>`_                      |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | DenseNet-121                    | densenet121        | `DenseNet architecture <https://arxiv.org/pdf/1608.06993.pdf>`_                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | DenseNet-161                    | densenet161        |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | DenseNet-169                    | densenet169        |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | DenseNet-201                    | densenet201        |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | MnasNet 0.5                     | mnasnet0_5         | `MnasNet architecture <https://arxiv.org/pdf/1807.11626.pdf>`_                 |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | MnasNet 1.0                     | mnasnet1_0         |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | MobileNet V2                    | mobilenet_v2       | `MobileNet V2 architecture <https://arxiv.org/abs/1801.04381>`_                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-11                          | vgg11              | `VGG-11 architecture Configuration "A" <https://arxiv.org/pdf/1409.1556.pdf>`_ |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-11 with batch normalization | vgg11_bn           |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-13                          | vgg13              | `VGG-13 architecture Configuration "B" <https://arxiv.org/pdf/1409.1556.pdf>`_ |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-13 with batch normalization | vgg13_bn           |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-16                          | vgg16              | `VGG-16 architecture Configuration "D" <https://arxiv.org/pdf/1409.1556.pdf>`_ |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-16 with batch normalization | vgg16_bn           |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-19                          | vgg19              | `VGG-19 architecture Configuration "E" <https://arxiv.org/pdf/1409.1556.pdf>`_ |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | VGG-19 with batch normalization | vgg19_bn           |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | GoogleNet                       | googlenet          | `GoogleNet architecture <http://arxiv.org/abs/1409.4842>`_                     |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | Inception V3                    | inception_v3       | `Inception V3 architecture <http://arxiv.org/abs/1512.00567>`_                 |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ResNet-18                       | resnet18           | `ResNet architecture <https://arxiv.org/pdf/1512.03385.pdf>`_                  |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ResNet-34                       | resnet34           |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ResNet-50                       | resnet50           |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ResNet-101                      | resnet101          |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ResNet-152                      | resnet152          |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | Wide ResNet-101-2               | wide_resnet101_2   | `Wide Resnet architecture <https://arxiv.org/pdf/1605.07146.pdf>`_             |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | Wide ResNet-50-2                | wide_resnet50_2    |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ShuffleNet V2 0.5               | shufflenet_v2_x0_5 | `Shuffle Net V2 architecture <https://arxiv.org/abs/1807.11164>`_              |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ShuffleNet V2 1.0               | shufflenet_v2_x1_0 |                                                                                |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ResNext-101-32x8D               | resnext101_32x8d   | `ResNext architecture <https://arxiv.org/pdf/1611.05431.pdf>`_                 |
|                +---------------------------------+--------------------+--------------------------------------------------------------------------------+
|                | ResNext-50-32x4D                | resnext50_32x4d    |                                                                                |
+----------------+---------------------------------+--------------------+--------------------------------------------------------------------------------+


**Usage Example:**

Example below uses ResNet-18 Model using the command line.

Let us take a simple example: **Classifying Ants and Bees Images**

First, we download the dataset and verify with ``sha384sum``

.. code-block::

    curl -LO https://download.pytorch.org/tutorial/hymenoptera_data.zip
    sha384sum -c - << EOF
    491db45cfcab02d99843fbdcf0574ecf99aa4f056d52c660a39248b5524f9e6e8f896d9faabd27ffcfc2eaca0cec6f39  /home/tron/Desktop/Development/hymenoptera_data.zip
    EOF
    hymenoptera_data.zip: OK

Unzip the file

.. code-block::

    unzip hymenoptera_data.zip

We first create a YAML file to define the last layer(s) to replace from the network architecture

**layers.yaml**

.. literalinclude:: /../model/pytorch/examples/resnet18/layers.yaml

Train the model

.. literalinclude:: /../model/pytorch/examples/resnet18/train.sh

Assess accuracy

.. literalinclude:: /../model/pytorch/examples/resnet18/accuracy.sh

Output:

.. code-block::

    0.9215686274509803

Create a csv file with the names of the images to predict, whether they are ants or bees.

.. literalinclude:: /../model/pytorch/examples/resnet18/unknown_data.sh

Make the predictions

.. literalinclude:: /../model/pytorch/examples/resnet18/predict.sh

Output:

.. literalinclude:: /../model/pytorch/examples/resnet18/output.txt

"""
from .pytorch_pretrained import *
from .pytorch_net import PyTorchNeuralNetwork
from .utils.utils import *
