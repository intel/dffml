dffml accuracy \
  -model alexnet \
  -model-clstype str \
  -model-classifications \
    crocus windflower fritillary tulip pansy dandelion tigerlily sunflower \
    bluebell cowslip coltsfoot snowdrop daffodil lilyvalley iris buttercup daisy \
  -model-directory alexnet_model \
  -model-batch_size 10 \
  -model-imageSize 224 \
  -model-enableGPU \
  -model-features image:int:$((500*500)) \
  -model-predict label:str:1 \
  -sources f=dir \
    -source-foldername ~/dataset/test \
    -source-feature image \
    -source-labels \
      crocus windflower fritillary tulip pansy dandelion tigerlily sunflower \
      bluebell cowslip coltsfoot snowdrop daffodil lilyvalley iris buttercup daisy