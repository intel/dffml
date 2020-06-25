echo -e 'f1,ans\n0.8,0\n' | \
  dffml predict all \
  -model scratchlgrsag \
  -model-features f1:float:1 \
  -model-predict ans:int:1 \
  -model-directory tempdir \
  -sources f=csv \
  -source-filename /dev/stdin \
  -log debug