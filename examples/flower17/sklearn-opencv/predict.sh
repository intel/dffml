dffml predict all \
  -model scikitrfc \
  -model-features \
    Histogram:int:$((8*8*8)) \
    HuMoments:int:7 \
    Haralick:int:13 \
  -model-predict label:str:1 \
  -model-location tempdir \
  -sources images=dfpreprocess \
    -source-images-source csv \
    -source-images-source-filename unknown_images.csv \
    -source-images-source-loadfiles image \
    -source-images-dataflow features.yaml \
    -source-images-features image:int:$((500*500)) \
  -log critical \
  -pretty