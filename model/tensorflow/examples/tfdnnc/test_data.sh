wget http://download.tensorflow.org/data/iris_test.csv
echo '8c2cda42ce5ce6f977d17d668b1c98a45bfe320175f33e97293c62ab543b3439eab934d8e11b1208de1e4a9eb1957714 iris_test.csv' | sha384sum -c -
sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' *.csv
