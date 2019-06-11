# DFFML scratch Models

## About

scratch models.

## Demo

![Demo](https://github.com/intel/dffml/raw/master/docs/images/model_demo.gif)

## Usage

```console
wget http://download.tensorflow.org/data/iris_training.csv
wget http://download.tensorflow.org/data/iris_test.csv
head iris_training.csv
sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
head iris_training.csv
dffml train \
  -model scratch \
  -sources csv=iris_training.csv \
  -classifications 0 1 2 \
  -features \
    def:SepalLength:float:1 \
    def:SepalWidth:float:1 \
    def:PetalLength:float:1 \
    def:PetalWidth:float:1 \
  -epochs 3000 \
  -steps 20000 \
  -log debug
dffml accuracy \
  -model scratch \
  -sources csv=iris_training.csv \
  -classifications 0 1 2 \
  -features \
    def:SepalLength:float:1 \
    def:SepalWidth:float:1 \
    def:PetalLength:float:1 \
    def:PetalWidth:float:1 \
  -log critical
dffml predict all \
  -model scratch \
  -sources csv=iris_test.csv \
  -classifications 0 1 2 \
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

scratch Models are distributed under the terms of the
[MIT License](LICENSE).
