MNIST Handwriten Digits
=======================

This example will show you how to train a model on the MNIST dataset and use the
model for prediction via the DFFML CLI and HTTP API.

Download the files and verify them with ``sha384sum``.

.. code-block:: console

    $ curl -sSLO "http://yann.lecun.com/exdb/mnist/{train-images-idx3,train-labels-idx1,t10k-images-idx3,t10k-labels-idx1}-ubyte.gz"
    $ sha384sum -c - << EOF
    1bf45877962fd391f7abb20534a30fd2203d0865309fec5f87d576dbdbefdcb16adb49220afc22a0f3478359d229449c  t10k-images-idx3-ubyte.gz
    ccc1ee70f798a04e6bfeca56a4d0f0de8d8eeeca9f74641c1e1bfb00cf7cc4aa4d023f6ea1b40e79bb4707107845479d  t10k-labels-idx1-ubyte.gz
    f40eb179f7c3d2637e789663bde56d444a23e4a0a14477a9e6ed88bc39c8ad6eaff68056c0cd9bb60daf0062b70dc8ee  train-images-idx3-ubyte.gz
    ba9c11bf9a7f7c2c04127b8b3e568cf70dd3429d9029ca59b7650977a4ac32f8ff5041fe42bc872097487b06a6794e00  train-labels-idx1-ubyte.gz
    EOF
    t10k-images-idx3-ubyte.gz: OK
    t10k-labels-idx1-ubyte.gz: OK
    train-images-idx3-ubyte.gz: OK
    train-labels-idx1-ubyte.gz: OK

The model we'll be using is a part of ``dffml-model-tensorflow``, which is
a DFFML plugin which allows you to use TensorFlow via DFFML. We can install it
with ``pip``.

.. code-block:: console

    $ pip install -U dffml-model-tensorflow

Train the model.

.. code-block:: console

    $ dffml train \
        -model tfdnnc \
        -model-batchsize 1000 \
        -model-hidden 30 50 25 \
        -model-clstype int \
        -model-predict label:int:1 \
        -model-classifications $(seq 0 9) \
        -model-features image:int:$((28 * 28)) \
        -sources images=idx3 label=idx1 \
        -source-images-filename train-images-idx3-ubyte.gz \
        -source-images-feature image \
        -source-label-filename train-labels-idx1-ubyte.gz \
        -source-label-feature label \
        -log debug
    ... log output ...

Assess the model's accuracy.

.. code-block:: console

    $ dffml accuracy \
        -model tfdnnc \
        -model-batchsize 1000 \
        -model-hidden 30 50 25 \
        -model-clstype int \
        -model-predict label:int:1 \
        -model-classifications $(seq 0 9) \
        -model-features image:int:$((28 * 28)) \
        -sources images=idx3 label=idx1 \
        -source-images-filename t10k-images-idx3-ubyte.gz \
        -source-images-feature image \
        -source-label-filename t10k-labels-idx1-ubyte.gz \
        -source-label-feature label \
        -log debug
    ... log output followed by accuracy as float ...
    0.8269000053405762

The accuracy likely won't be very good right now because we need to normalize
the data first.

.. note::

    Prediction and rest of this tutorial comming soon! We're currently working
    on getting the data normailzation working and reading image files from
    formats other than IDX.

