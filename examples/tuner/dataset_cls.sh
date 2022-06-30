wget http://download.tensorflow.org/data/iris_training.csv 
wget http://download.tensorflow.org/data/iris_test.csv 
sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' iris_training.csv iris_test.csv