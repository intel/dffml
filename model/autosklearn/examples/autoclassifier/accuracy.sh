dffml accuracy \
  -model autoclassifier \
  -model-location tempdir \
  -model-predict classification:int:1 \
  -features classification:int:1 \
  -sources iris=csv \
  -source-filename iris_test.csv \
  -model-features \
    SepalLength:float:1 \
    SepalWidth:float:1 \
    PetalLength:float:1 \
    PetalWidth:float:1 \
  -scorer mse \
  -log critical
