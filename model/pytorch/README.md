# DFFML pytorch Models

## About

A demo that implements IRIS classification model using pytorch and dffml.

## Usage

```console
mkdir data
cd data
wget http://download.tensorflow.org/data/iris_training.csv
wget http://download.tensorflow.org/data/iris_test.csv
head iris_training.csv
sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
head iris_training.csv
cd ..
dffml train \
  -model dfcn \
  -sources csv=data/iris_training.csv \
  -classifications 0 1 2 \
  -features \
    def:SepalLength:float:1 \
    def:SepalWidth:float:1 \
    def:PetalLength:float:1 \
    def:PetalWidth:float:1 \
  -num_epochs 3000 \
  -steps 20000 \
  -log debug
dffml accuracy \
  -model dfcn \
  -sources csv=data/iris_training.csv \
  -classifications 0 1 2 \
  -features \
    def:SepalLength:float:1 \
    def:SepalWidth:float:1 \
    def:PetalLength:float:1 \
    def:PetalWidth:float:1 \
  -log critical
```

## License

pytorch Models are distributed under the terms of the
[MIT License](LICENSE).
