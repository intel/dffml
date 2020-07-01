dffml predict all \
  -model autoregressor \
  -model-directory tempdir \
  -model-predict TARGET:float:1 \
  -sources iris=csv \
  -model-features \
    Feature1:float:1 \
    Feature2:float:1 \
  -source-filename predict.csv
