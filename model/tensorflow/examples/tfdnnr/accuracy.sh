dffml accuracy \
  -model tfdnnr \
  -model-predict TARGET:float:1 \
  -model-hidden 8 16 8 \
  -sources s=csv \
  -source-filename test.csv \
  -model-features \
    Feature1:float:1 \
    Feature2:float:1 \
  -log critical