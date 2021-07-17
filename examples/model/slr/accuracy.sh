dffml accuracy \
  -model slr \
  -model-features f1:float:1 \
  -model-predict ans:int:1 \
  -model-location tempdir \
  -sources f=csv \
  -source-filename dataset.csv \
  -scorer mse \
  -log debug
