# DFFML Models for Tensorflow Library

## About

DFFML models backed by Tensorflow.

## Demo

![Demo](https://github.com/intel/dffml/raw/master/docs/images/iris_demo.gif)

> This demo was taken before the below steps were updated, the actual accuracy
> may vary as this video shows accuracy being assessed against the training
> data. You should try it for yourself and see!

## Install

```console
virtualenv -p python3.7 .venv
. .venv/bin/activate
python3.7 -m pip install --user -U dffml[tensorflow]
```

## Usage

```console
wget http://download.tensorflow.org/data/iris_training.csv
wget http://download.tensorflow.org/data/iris_test.csv
head iris_training.csv
sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
head iris_training.csv
dffml train \
  -model tfdnnc \
  -model-epochs 3000 \
  -model-steps 20000 \
  -model-classification classification \
  -model-classifications 0 1 2 \
  -model-clstype int \
  -sources iris=csv \
  -source-filename iris_training.csv \
  -features \
    def:SepalLength:float:1 \
    def:SepalWidth:float:1 \
    def:PetalLength:float:1 \
    def:PetalWidth:float:1 \
  -log debug
dffml accuracy \
  -model tfdnnc \
  -model-classification classification \
  -model-classifications 0 1 2 \
  -model-clstype int \
  -sources iris=csv \
  -source-filename iris_test.csv \
  -features \
    def:SepalLength:float:1 \
    def:SepalWidth:float:1 \
    def:PetalLength:float:1 \
    def:PetalWidth:float:1 \
  -log critical
dffml predict all \
  -model tfdnnc \
  -model-classification classification \
  -model-classifications 0 1 2 \
  -model-clstype int \
  -sources iris=csv \
  -source-filename iris_test.csv \
  -features \
    def:SepalLength:float:1 \
    def:SepalWidth:float:1 \
    def:PetalLength:float:1 \
    def:PetalWidth:float:1 \
  -caching \
  -log critical \
  > results.json
head -n 33 results.json
```

## License

DFFML Tensorflow Models are distributed under the terms of the
[MIT License](LICENSE).
