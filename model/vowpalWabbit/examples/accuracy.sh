dffml accuracy  \
  -model vwmodel \
  -model-features \
    A:str:1 \
  -sources f=csv \
  -source-filename train.csv \
  -model-predict \
    B:int:1
