# Logging

## CLI

To enable logging when running `dffml` add the `-log <level>` flag to any
command.

Log levels correspond to the Python `logging` module, as DFFML uses that.

```console
dffml list repos -log debug -sources \
  csv=<(curl -sSL http://download.tensorflow.org/data/iris_test.csv \
        | sed 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g')
```

## Tests

To get logging output while testing, set the `LOGGING` environment variable.

```console
LOGGING=DEBUG python3.7 setup.py test
```
