FLOWER17 dataset classification using OpenCV and Scikit-Learn
=============================================================

This example will show you how to train and test a model on the `FLOWER17` dataset.
This dataset contains 17 classes of flower species, each having 80 images.

Download the dataset and verify with with ``sha384sum``.

.. literalinclude:: /../examples/flower17/dataset.sh

.. code-block:: console

    17flowers.tgz: OK

The model we'll be using is the `RandomForestClassifier` which is a part of
``dffml-model-scikit``, a DFFML plugin which allows you to use Scikit-Learn via DFFML.
We'll also be using the various operations from ``dffml-operations-image``, which is
a DFFML plugin which allows you to do image processing via DFFML and
``dffml-config-yaml`` and ``dffml-config-image`` for loading yaml and image files.
We can install them with ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-scikit dffml-operations-image dffml-config-yaml dffml-config-image

Extract the dataset.

.. code-block:: console

    $ tar -xzf 17flowers.tgz

All the images are now in a folder called `jpg`.
Let's split these images into flower_dataset/train and flower_dataset/test directories,
each directory containing sub-directories corresponding to the 17 flower classes using split.py.

.. literalinclude:: /../examples/flower17/split.py

We execute the split.py file. The train directory will contain 70 images for each class while
the test directory will contain 10 images for each class.

.. code-block:: console

    $ python split.py

Create a dataflow config file which will be used by the
:py:class:`DataFlowSource <dffml.source.df.DataFlowSource>` to preprocess
the data before feeding it to the model.

Our dataflow extracts features from the data which will then be used by the machine learning
model. Since the dataset contains flowers, we extract features that quantify the color, shape
and texture of each flower image.

We use the following set of operations from the :ref:`plugin_operation_dffml_operations_image`
plugin which use functions provided by OpenCV library, which the dataflow will run through to
extract features.

resize
~~~~~~
This operation resizes the images up or down to the specified size.

convert_color
~~~~~~~~~~~~~
This operation uses the OpenCV function `cv2.cvtColor` and converts the image from one
colorspace to another.

calcHist
~~~~~~~~
This operation extracts the histogram from the image array and is used in this tutorial
to quantify the colors present in a flower image.

normalize
~~~~~~~~~
This operation will be used to normalize the value range of the histogram here.

HuMoments
~~~~~~~~~
This operation calculates the seven Hu invariants which quantifies the information regarding
the orientation of the image. `Image Moments <https://en.wikipedia.org/wiki/Image_moment>`_

Haralick
~~~~~~~~
This operation extracts the texture features from the image.

flatten
~~~~~~~
This operation returns a copy of numpy array collapsed into 1 dimension.

The dataflow visualised:

.. image:: /.. /examples/flower17/dataflow_diagram.svg

We then create the dataflow config file, using the ``dataflow create`` command.

.. literalinclude:: /../examples/flower17/create_dataflow.sh

To re-create the visualization of the dataflow above, run:

.. literalinclude:: /../examples/flower17/dataflow_diagram.sh

Copy and pasting the output of the above code into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the graph.

Train the model.

.. literalinclude:: /../examples/flower17/train.sh

Assess the model's accuracy.

.. literalinclude:: /../examples/flower17/accuracy.sh

The output is:

.. code-block:: console

    0.27450980392156865

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

.. literalinclude:: /../examples/flower17/predict.sh

Output

.. literalinclude:: /../examples/flower17/output.txt

The model predicts 2 of the 4 images correctly!

The accuracy of the model can be increased by using various preprocessing techniques
for example scaling all the feature vectors within the range [0,1].
