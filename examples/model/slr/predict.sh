echo -e 'f1,ans\n0.8,0\n' | \
  dffml predict all \
  -model slr \
  -model-features f1:float:1 \
  -model-predict ans:int:1 \
  -sources f=csv \
  -source-filename /dev/stdin \
  -log debug
