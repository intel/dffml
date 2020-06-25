dffml train \
  -model slr \
  -model-feature f1:float:1 \
  -model-predict ans:int:1 \
  -sources f=csv \
  -source-filename dataset.csv \
  -log debug
