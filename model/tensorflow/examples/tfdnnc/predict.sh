echo -e 'SepalLength,SepalWidth,PetalLength,PetalWidth\n5.9,3.0,4.2,1.5\n' | \
dffml predict all \
  -model tfdnnc \
  -model-predict classification:int:1 \
  -model-classifications 0 1 2 \
  -model-clstype int \
  -sources iris=csv \
  -model-features \
    SepalLength:float:1 \
    SepalWidth:float:1 \
    PetalLength:float:1 \
    PetalWidth:float:1 \
  -source-filename /dev/stdin