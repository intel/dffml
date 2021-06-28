dffml accuracy \
  -model alexnet \
  -model-add_layers \
  -model-layers @layers.yaml \
  -model-clstype str \
  -model-classifications \
    crocus windflower fritillary tulip pansy dandelion tigerlily sunflower \
    bluebell cowslip coltsfoot snowdrop daffodil lilyvalley iris buttercup daisy \
  -model-directory alexnet_model \
  -model-imageSize 224 \
  -model-trainable \
  -model-enableGPU \
  -model-normalize_mean 0.485 0.456 0.406 \
  -model-normalize_std 0.229 0.224 0.225 \
  -model-features image:int:$((500*500)) \
  -model-predict label:str:1 \
  -sources f=dir \
    -source-foldername flower_dataset/test \
    -source-feature image \
    -source-labels \
      crocus windflower fritillary tulip pansy dandelion tigerlily sunflower \
      bluebell cowslip coltsfoot snowdrop daffodil lilyvalley iris buttercup daisy \
  -scorer pytorchscore