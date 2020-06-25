dffml predict all \
  -model vwmodel \
  -model-features \
    A:str:1 \
  -model-predict \
    B:int:1 \
  -model-noconvert \
  -sources f=csv \
  -source-filename test.csv