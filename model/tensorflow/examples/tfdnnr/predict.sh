echo -e 'Feature1,Feature2,TARGET\n0.21,0.18,0.84\n' | \
  dffml predict all \
  -model tfdnnr \
  -model-predict TARGET:float:1 \
  -model-directory tempdir \
  -model-hidden 8 16 8 \
  -sources s=csv \
  -source-filename /dev/stdin \
  -model-features \
    Feature1:float:1 \
    Feature2:float:1 \
  -log critical