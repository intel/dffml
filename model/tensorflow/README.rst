DFFML Models for Tensorflow Library
===================================

About
-----

DFFML models backed by Tensorflow.

Install
-------

.. code-block:: console

    virtualenv -p python3.7 .venv
    . .venv/bin/activate
    python3.7 -m pip install --user -U dffml[tensorflow]

Usage
-----

.. code-block:: console

     wget http://download.tensorflow.org/data/iris_training.csv
     wget http://download.tensorflow.org/data/iris_test.csv
     head iris_training.csv
     sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
     head iris_training.csv
     dffml train \
       -model dnn \
       -sources csv=iris_training.csv \
       -classifications 0 1 2 \
       -features \
         def:SepalLength:float:1 \
         def:SepalWidth:float:1 \
         def:PetalLength:float:1 \
         def:PetalWidth:float:1 \
       -num_epochs 3000 \
       -steps 20000
     dffml accuracy \
       -model dnn \
       -sources csv=iris_training.csv \
       -classifications 0 1 2 \
       -features \
         def:SepalLength:float:1 \
         def:SepalWidth:float:1 \
         def:PetalLength:float:1 \
         def:PetalWidth:float:1

License
-------

DFFML Tensorflow Models are distributed under the terms of the `MIT License
<https://choosealicense.com/licenses/mit>`_
