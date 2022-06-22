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
a DFFML plugin which allows you to use TensorFlow via DFFML.
We'll also be using the `resize` operation from ``dffml-operations-image``, which is
a DFFML plugin which allows you to do image processing via DFFML.
We can install them with ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-tensorflow dffml-operations-image

Create a dataflow config file which will be used by the
:py:class:`DataFlowPreprocessSource <dffml.source.dfpreprocess.DataFlowPreprocessSource>` to normalize the
data just before feeding it to the model.

In the config file, using the ``dataflow create`` command we create a DataFlow
consisting of 2 operations: multiply and associate_definition. We
edit the DataFlow to have the multiplicand input of the multiply operation come
from a list in seed containing only one element that is the ``image`` feature
and the seed to have the input of the associate_definition operation come from the output
(product) of the multiply operation.

.. literalinclude:: /../examples/MNIST/create_dataflow.sh

.. TODO genereate this automaticlly
    graph TD
    0fbe41b549bb236aabadebd7924379fd[multiply]
    24e79f7035a289834b34967054b338f5(seed.image)
    style 24e79f7035a289834b34967054b338f5 fill:#f6dbf9,stroke:#a178ca
    24e79f7035a289834b34967054b338f5 --> 0fbe41b549bb236aabadebd7924379fd
    113e51b1af7d424eee96c632d74847f7(multiplier_def)
    style 113e51b1af7d424eee96c632d74847f7 fill:#f6dbf9,stroke:#a178ca
    113e51b1af7d424eee96c632d74847f7 --> 0fbe41b549bb236aabadebd7924379fd

.. image:: /images/mnist-normalize.svg
    :alt: Diagarm of MNIST normalization dataflow

Train the model.

.. literalinclude:: /../examples/MNIST/train.sh

Assess the model's accuracy.

.. literalinclude:: /../examples/MNIST/accuracy.sh

.. code-block:: console

    0.9591000080108643

Create an ``image.csv`` file which contains the names of the images (with their extension .png) to predict on.

.. literalinclude:: /../examples/MNIST/image_file.sh

In the config file, using the ``dataflow create`` command we create a DataFlow
consisting of 3 operations: resize, multiply and associate_definition. We
edit the DataFlow to have the data input of the resize operation come
from a list in seed containing ``image`` feature, have the multiplicand input of
multiply operation come from the output of flatten operation whose input
comes from the output (resized_array) of the resize operation
and to have the input of the associate_definition operation come from the output
(product) of the multiply operation.

.. literalinclude:: /../examples/MNIST/create_dataflow_1.sh

.. TODO genreate this automatically
    graph TD
    4b0696d0a16f6124e7f9edd38a1c1505[flatten]
    0fbe41b549bb236aabadebd7924379fd[multiply]
    dc3d3b1a336fbbd51585e31c95f45c83[resize]
    dc3d3b1a336fbbd51585e31c95f45c83 --> 4b0696d0a16f6124e7f9edd38a1c1505
    4b0696d0a16f6124e7f9edd38a1c1505 --> 0fbe41b549bb236aabadebd7924379fd
    113e51b1af7d424eee96c632d74847f7(multiplier_def)
    style 113e51b1af7d424eee96c632d74847f7 fill:#f6dbf9,stroke:#a178ca
    113e51b1af7d424eee96c632d74847f7 --> 0fbe41b549bb236aabadebd7924379fd
    acff930bdb76e6c260c827ef5c6bae75(resize.inputs.dsize)
    style acff930bdb76e6c260c827ef5c6bae75 fill:#f6dbf9,stroke:#a178ca
    acff930bdb76e6c260c827ef5c6bae75 --> dc3d3b1a336fbbd51585e31c95f45c83
    24e79f7035a289834b34967054b338f5(seed.image)
    style 24e79f7035a289834b34967054b338f5 fill:#f6dbf9,stroke:#a178ca
    24e79f7035a289834b34967054b338f5 --> dc3d3b1a336fbbd51585e31c95f45c83

.. image:: /images/mnist-resize.svg
    :alt: Diagarm of MNIST resizing and normalizing dataflow

In this example, the ``image.csv`` file contains the names of the following images

.. image:: /../examples/MNIST/image1.png
    :width: 140px
    :height: 140px

.. image:: /../examples/MNIST/image2.png
    :width: 140px
    :height: 140px

.. image:: /../examples/MNIST/image3.png
    :width: 140px
    :height: 140px

.. image:: /../examples/MNIST/image4.png
    :width: 140px
    :height: 140px

Predict with the trained model.

.. literalinclude:: /../examples/MNIST/predict.sh

Output

.. literalinclude:: /../examples/MNIST/output.json
