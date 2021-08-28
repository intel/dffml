FLOWER17 Species classification using OpenCV and Scikit-Learn
=============================================================

The model we'll be using is the `RandomForestClassifier` which is a part of
``dffml-model-scikit``, a DFFML plugin which allows you to use Scikit-Learn via DFFML.
We'll also be using the various operations from ``dffml-operations-image``, which is
a DFFML plugin which allows you to do image processing via DFFML and
``dffml-config-yaml`` and ``dffml-config-image`` for loading yaml and image files.
We can install them with ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-scikit dffml-operations-image dffml-config-yaml dffml-config-image

Create a dataflow config file which will be used by the
:py:class:`DataFlowPreprocessSource <dffml.source.dfpreprocess.DataFlowPreprocessSource>` to preprocess
the data before feeding it to the model.

Our dataflow extracts features from the data which will then be used by the machine learning
model. Since the dataset contains flowers, we extract features that quantify the color, shape
and texture of each flower image.

We use the following set of operations from the :ref:`plugin_operation_dffml_operations_image`
plugin which use functions provided by OpenCV library, which the dataflow will run through to
extract features.

+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  **resize**         |  This operation resizes the images up or down to the specified size.                                                                                                                      |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  **convert_color**  |  This operation uses the OpenCV function `cv2.cvtColor` and converts the image from one colorspace to another.                                                                            |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  **calcHist**       |  This operation extracts the histogram from the image array and is used in this tutorial to quantify the colors present in a flower image.                                                |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  **normalize**      |  This operation will be used to normalize the value range of the histogram here.                                                                                                          |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  **HuMoments**      |  This operation calculates the seven Hu invariants which quantifies the information regarding the orientation of the image. `Image Moments <https://en.wikipedia.org/wiki/Image_moment>`_ |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  **Haralick**       |  This operation extracts the texture features from the image.                                                                                                                             |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  **flatten**        |  This operation returns a copy of numpy array collapsed into 1 dimension.                                                                                                                 |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

The dataflow visualised:

.. image:: /../examples/flower17/sklearn-opencv/dataflow_diagram.svg

We then create the dataflow config file, using the ``dataflow create`` command.

.. literalinclude:: /../examples/flower17/sklearn-opencv/create_dataflow.sh

To re-create the visualization of the dataflow above, run:

.. code-block:: console

    dffml dataflow diagram features.yaml -simple -stages processing -configloader yaml

Copy and pasting the output of the above code into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the graph.

Train the model.

.. literalinclude:: /../examples/flower17/sklearn-opencv/train.sh

Assess the model's accuracy.

.. literalinclude:: /../examples/flower17/sklearn-opencv/accuracy.sh

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

.. literalinclude:: /../examples/flower17/sklearn-opencv/predict.sh

Output

.. literalinclude:: /../examples/flower17/sklearn-opencv/output.txt

The model predicts 2 of the 4 images correctly!

The accuracy of the model can be increased by using various preprocessing techniques
for example scaling all the feature vectors within the range [0,1].

Alternatively using Convolutional Neural Networks vastly improves the accuracy! -
`The Transfer Learning approach with Convolution Neural Networks <flower17_pytorch.html>`_
