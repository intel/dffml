dffml accuracy  \
  -model vwmodel \
  -model-features \
    A:str:1 \
  -model-predict \
    B:int:1 \
  -model-noconvert \
  -scorer mse \
  -sources f=csv \
  -source-filename train.csv

