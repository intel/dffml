MNIST Handwriten Digits
=======================

This example will show you how to train a model on the MNIST dataset and use the
model for prediction via the DFFML CLI and HTTP API.

Download the files and verify them with ``sha384sum``.

.. literalinclude:: /../examples/MNIST/image_data.sh

.. code-block:: console

    t10k-images-idx3-ubyte.gz: OK
    t10k-labels-idx1-ubyte.gz: OK
    train-images-idx3-ubyte.gz: OK
    train-labels-idx1-ubyte.gz: OK

The model we'll be using is a part of ``dffml-model-tensorflow``, which is
a DFFML plugin which allows you to use TensorFlow via DFFML. We can install it
with ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-tensorflow

Create a dataflow config file which will be used by the
:py:class:`DataFlowSource <dffml.source.df.DataFlowSource>` to normalize the
data just before feeding it to the model.

In the config file, using the ``dataflow create`` command we create a DataFlow
consisting of 2 operations, multiply and associate_definition. We use ``sed`` to
edit the DataFlow to have the multiplicand input of the multiply operation come
from a list in seed containing only one element that is the ``image`` feature
and to have the input of the associate_definition operation come from the output
(product) of the multiply operation.

.. literalinclude:: /../examples/MNIST/create_dataflow.sh

.. literalinclude:: /../examples/MNIST/normalize.yaml

Train the model.

.. literalinclude:: /../examples/MNIST/train.sh

Assess the model's accuracy.

.. literalinclude:: /../examples/MNIST/accuracy.sh

.. code-block:: console

    0.8269000053405762

Create an ``image.csv`` file which contains the names of the images (with their extension .mnistpng) to predict on.

.. note::
    Make sure to download each image and save them with the `.mnistpng` extension.

.. literalinclude:: /../examples/MNIST/image_file.sh

In this example, the ``image.csv`` file contains the names of the following images

.. image:: /../examples/MNIST/image1.mnistpng
    :width: 140px
    :height: 140px

.. image:: /../examples/MNIST/image2.mnistpng
    :width: 140px
    :height: 140px

.. image:: /../examples/MNIST/image3.mnistpng
    :width: 140px
    :height: 140px

.. image:: /../examples/MNIST/image4.mnistpng
    :width: 140px
    :height: 140px

Predict with the trained model.

.. literalinclude:: /../examples/MNIST/predict.sh

Output

.. literalinclude:: /../examples/MNIST/output.json
