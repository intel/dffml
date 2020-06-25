dffml predict all \
  -model vwmodel \
  -model-features \
    A:str:1 \
  -model-predict B:int:1
  -sources f=csv \
  -model-noconvert \
  -source-filename test.csv