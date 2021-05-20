Ice Cream Sales
===============

In this tutorial we are going to predict ice-cream sales.

This example consist of the following steps

- Writing Operations to get population and temperature.
- Creating dataflow for the operations that we have written above.
- Using `merge` command for the data processing.
- Training a model from the preprocessed data.
- Getting the accuracy of the model
- Getting predictions from the model using test dataset.

Dataset
-------

In this we have two datasets for training and testing. We have
fields city, state, month, sales. This is a dummy dataset.

**dataset.csv**

.. literalinclude:: /../examples/dataflow/icecream_sales/dataset.csv
    :test:

**test_dataset.csv**

.. literalinclude:: /../examples/dataflow/icecream_sales/test_dataset.csv
    :test:

Operations
----------

We will be writing two operations:

1. An operation to get the temperature given the city, month.
2. An operation to get the population given the city, state

First we need to find some official sources from where we can get
the temperature and population for the cities that we have.

We will be using https://www.ncdc.noaa.gov/cdo-web/ to get the datasets for
the temperature and for the population we are using
https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/
for getting the population datasets.

Since the datasets are huge, hence we are using only specific files
from the dataset to get the values we need.

We will be using the `cached_download` method which caches the downloaded
files and speeds up the development time.

**operations.py**

.. literalinclude:: /../examples/dataflow/icecream_sales/operations.py
    :test:

In the `lookup_temperature` operation we would take the inputs
as city and month, we would go over the dataset links that we
have and download the file for that particular city and return
the temperature for that specific month.

In the `lookup_population` operation we would take the inputs
as city and state, we would go over all the state datasets
that we have and download the matching dataset for state and
returns the population for that particular city.

Dataflow
--------

Now we will be creating a dataflow using the operations that
we have written earlier. The main objective of the dataflow
would be to give output after running the operations over our
dummy dataset that we have.

**dataflow.sh**

.. code-block:: console
    :test:

    $ dffml dataflow create \
        -flow \
            '[{"seed": ["city"]}]'=operations:lookup_temperature.inputs.city \
            '[{"seed": ["month"]}]'=operations:lookup_temperature.inputs.month \
            '[{"seed": ["city"]}]'=operations:lookup_population.inputs.city \
            '[{"seed": ["state"]}]'=operations:lookup_population.inputs.state \
        -inputs \
            '["temperature", "population"]'=get_single_spec \
            -- \
            operations:lookup_population \
            operations:lookup_temperature \
            get_single | \
            tee preprocess_ops.json

The dataflow create command will create a dataflow for us
in the json format. Now we can use this dataflow within our
merge command.

Merge Command
-------------

We will be using the merge command. In the merge command we
would go over the dataset.csv file run it through the dataflow
that we have created earlier and dump the values of population
and temperature in a new file.

**processing.sh**

.. code-block:: console
    :test:

    $ dffml merge text=df temp=csv \
        -source-text-dataflow preprocess_ops.json \
        -source-text-features city:str:1 state:str:1 month:int:1 \
        -source-text-source csv \
        -source-text-source-filename dataset.csv \
        -source-temp-filename preprocessed.csv \
        -source-temp-allowempty \
        -source-temp-readwrite \
        -log debug
    $ cat preprocessed.csv

Model Training
--------------

Now we will be training our model, the model which
we will be using is `tfdnnr` model. You may also
use any other model for this purpose.

Our model will be trained on temperature and population
and the output being sales.

**train.sh**

.. code-block:: console
    :test:

    $ dffml train \
        -model tfdnnr \
        -model-epochs 300 \
        -model-steps 20 \
        -model-hidden 9 18 9 \
        -model-features population:int:1 temperature:float:1 \
        -model-predict sales:int:1 \
        -model-directory tempdir \
        -sources f=csv \
        -source-filename preprocessed.csv \
        -log debug

Model Accuracy
--------------

The accuracy of the trained model can be found out
using the accuracy method.

**accuracy.sh**

.. code-block:: console
    :test:

    $ dffml accuracy \
        -model tfdnnr \
        -model-hidden 9 18 9 \
        -model-features population:int:1 temperature:float:1 \
        -model-predict sales:int:1 \
        -model-directory tempdir \
        -sources f=csv \
        -source-filename preprocessed.csv \
        -log debug

Prediction
----------

For the prediction we will using the `test_dataset.csv` this data
was not present in the training dataset.

Here insted of creating and intermediary file we are directly
providing the output of the dataflow (temperature and population)
for the prediction of sales.

**predict.sh**

.. code-block:: console
    :test:

    $ dffml predict all \
        -model tfdnnr \
        -model-hidden 9 18 9 \
        -model-features population:int:1 temperature:float:1 \
        -model-predict sales:int:1 \
        -model-directory tempdir \
        -sources preprocess=df \
        -source-preprocess-dataflow preprocess_ops.json \
        -source-preprocess-features city:str:1 state:str:1 month:int:1 \
        -source-preprocess-source csv \
        -source-preprocess-source-filename test_dataset.csv \
        -log debug
