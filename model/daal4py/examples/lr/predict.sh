echo -e 'f1,ans\n0.8,1\n' | \
  dffml predict all \
  -model daal4pylr \
  -model-features f1:float:1 \
  -model-predict ans:int:1 \
  -model-directory tempdir \
  -sources f=csv \
  -source-filename /dev/stdin
