dffml train \
  -model tfdnnr \
  -model-epochs 300 \
  -model-steps 2000 \
  -model-predict TARGET:float:1 \
  -model-directory tempdir \
  -model-hidden 8 16 8 \
  -sources s=csv \
  -source-filename train.csv \
  -model-features \
    Feature1:float:1 \
    Feature2:float:1 \
  -log debug