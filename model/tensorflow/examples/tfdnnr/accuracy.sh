dffml accuracy \
  -model tfdnnr \
  -model-predict TARGET:float:1 \
  -model-location tempdir \
  -model-hidden 8 16 8 \
  -features TARGET:float:1 \
  -sources s=csv \
  -source-filename test.csv \
  -model-features \
    Feature1:float:1 \
    Feature2:float:1 \
  -scorer mse \
  -log critical