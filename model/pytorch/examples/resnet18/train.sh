dffml train \
  -model resnet18 \
  -model-add_layers \
  -model-layers @layers.yaml \
  -model-clstype str \
  -model-classifications ants bees \
  -model-directory resnet18_model \
  -model-imageSize 224 \
  -model-epochs 5 \
  -model-batch_size 32 \
  -model-enableGPU \
  -model-features image:int:$((500*500)) \
  -model-predict label:str:1 \
  -sources f=dir \
    -source-foldername hymenoptera_data/train \
    -source-feature image \
    -source-labels ants bees \
  -log critical