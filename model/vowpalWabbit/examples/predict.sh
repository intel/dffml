dffml predict all \
  -model vwmodel \
  -model-features \
    A:str:1 \
  -sources f=csv \
  -source-filename test.csv \
  -model-predict B:int:1