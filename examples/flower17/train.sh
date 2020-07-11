dffml train \
  -model scikitrfc \
  -model-features \
    flatten.outputs.result:int:$((8*8*8)) \
    HuMoments.outputs.result:int:7 \
    Haralick.outputs.result:int:13 \
  -model-predict label:str:1 \
  -model-directory tempdir \
  images=df \
    -sources images=df \
    -source-images-source dir \
    -source-images-source-foldername flower_dataset/train \
    -source-images-source-labels \
      crocus windflower fritillary tulip pansy dandelion tigerlily sunflower \
      bluebell cowslip coltsfoot snowdrop daffodil lilyvalley iris buttercup daisy \
    -source-images-source-feature image \
    -source-images-dataflow features.yaml \
    -source-images-features image:int:$(( 500*500 )) \
  -log critical