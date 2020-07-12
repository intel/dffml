dffml predict all \
  -model scikitrfc \
  -model-features \
    flatten.outputs.result:int:$((8*8*8)) \
    HuMoments.outputs.result:int:7 \
    Haralick.outputs.result:int:13 \
  -model-predict label:str:1 \
  -model-directory tempdir \
  images=df \
    -sources images=df \
    -source-images-source csv \
    -source-images-source-filename unknown_images.csv \
    -source-images-source-loadfiles image \
    -source-images-dataflow features.yaml \
    -source-images-features image:int:1 \
  -log critical \
  -pretty > output.txt