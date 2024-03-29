dffml accuracy \
  -model tfdnnc \
  -model-predict classification:int:1 \
  -model-location tempdir \
  -model-classifications 0 1 2 \
  -model-clstype int \
  -features classification:int:1 \
  -scorer clf \
  -sources iris=csv \
  -source-filename iris_test.csv \
  -model-features \
    SepalLength:float:1 \
    SepalWidth:float:1 \
    PetalLength:float:1 \
    PetalWidth:float:1 \
  -log critical