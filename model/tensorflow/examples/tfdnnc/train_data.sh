wget http://download.tensorflow.org/data/iris_training.csv
echo '376c8ea3b7f85caff195b4abe62f34e8f4e7aece8bd087bbd746518a9d1fd60ae3b4274479f88ab0aa5c839460d535ef iris_training.csv' | sha384sum -c -
sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
