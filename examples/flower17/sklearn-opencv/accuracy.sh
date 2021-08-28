dffml accuracy \
  -scorer skmodelscore \
  -model scikitrfc \
  -model-features \
    Histogram:int:$((8*8*8)) \
    HuMoments:int:7 \
    Haralick:int:13 \
  -model-predict label:str:1 \
  -model-location tempdir \
  -features label:str:1 \
  -sources images=dfpreprocess \
    -source-images-source dir \
    -source-images-source-foldername flower_dataset/test \
    -source-images-source-labels \
      crocus windflower fritillary tulip pansy dandelion tigerlily sunflower \
      bluebell cowslip coltsfoot snowdrop daffodil lilyvalley iris buttercup daisy \
    -source-images-source-feature image \
    -source-images-dataflow features.yaml \
    -source-images-features image:int:$((500*500)) \
  -log critical
