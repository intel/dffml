dffml accuracy \
  -model daal4pylr \
  -model-features f1:float:1 \
  -model-predict ans:int:1 \
  -model-directory tempdir \
  -scorer mse \
  -sources f=csv \
  -source-filename test.csv
