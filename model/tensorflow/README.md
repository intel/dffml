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
### Classifier
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
### Regressor
* Generating data,this creates files `train_data.csv` and `test_data.csv`,
  make sure to take a BACKUP of files with same name in the directory
  from where this command is run as it overwrites any existing files
#### Train_data
```
  $ awk -v n=1000 -v seed="$RANDOM" 'BEGIN { 
        srand(seed); 
        for (i=0; i<n; ++i) 
        {
            x=rand();y=rand();z=(2*x+3*y);
            printf("%.2f,%.2f,%.2f\n", x,y,z)
        }

        }' > train_data.csv
  $ sed -i '1s/^/Feature1,Feature2,TARGET\n/' train_data.csv
  $ head train_data.csv
```
#### Test_data
```
  $ awk -v n=50 -v seed="$RANDOM" 'BEGIN { 
      srand(seed+1); 
      for (i=0; i<n; ++i) 
      {
          x=rand();y=rand();
          printf("%.2f,%.2f\n", x,y)
      }

      }' > test_data.csv
  $ sed -i '1s/^/Feature1,Feature2\n/' test_data.csv

  $ head test_data.csv 
```
#### Using the model
```
  $ dffml train \
        -model tfdnnr \
        -model-epochs 300 \
        -model-steps 2000 \
        -model-predict TARGET \
        -model-hidden 8 16 8 \
        -sources s=csv \
        -source-readonly \
        -source-filename train_data.csv \
        -features \
          def:Feature1:float:1 \
          def:Feature2:float:1 \
        -log debug
    >> OUTPUTS LOG AND LOSSESS <<
    
    $ dffml accuracy \
          -model tfdnnr \
          -model-predict TARGET \
          -model-hidden 8 16 8 \
          -sources s=csv \
          -source-readonly \
          -source-filename train_data.csv \
          -features \
            def:Feature1:float:1 \
            def:Feature2:float:1 \
          -log critical
     
      >> 0.9998210011 << 
      >> Output accuracy may slightly vary due to random initialisation of train and test set <<

    $ dffml predict all \
          -model tfdnnr \
          -model-predict TARGET \
          -model-hidden 8 16 8 \
          -sources s=csv \
          -source-readonly \
          -source-filename test_data.csv \
          -features \
            def:Feature1:float:1 \
            def:Feature2:float:1 \
          -log critical > results.json
    
    $ head -n 40 results.json
     
```
   Dont mind the `NaN` in `confidence` thats the expected behaviour

## License

DFFML Tensorflow Models are distributed under the terms of the
[MIT License](LICENSE).
