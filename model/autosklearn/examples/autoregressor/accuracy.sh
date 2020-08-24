dffml accuracy \
  -model autoregressor \
  -model-predict TARGET:float:1 \
  -model-directory tempdir \
  -sources f=csv \
  -source-filename test.csv \
  -model-features \
    Feature1:float:1 \
    Feature2:float:1 \
  -accuracy-scorer=mse \
  -log critical
