dffml predict all \
  -model autoclassifier \
  -model-directory tempdir \
  -model-predict classification:int:1 \
  -sources iris=csv \
  -model-features \
    SepalLength:float:1 \
    SepalWidth:float:1 \
    PetalLength:float:1 \
    PetalWidth:float:1 \
  -source-filename iris_predict.csv
