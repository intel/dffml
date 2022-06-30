dffml tune \
  -model pytorchnet \
  -model-features image:int:$((300*300*3)) \
  -model-clstype str \
  -model-classifications rock paper scissors \
  -model-predict label:int:1 \
  -model-network @model.yaml \
  -model-location rps_model \
  -model-loss crossentropyloss \
  -model-optimizer Adam \
  -model-validation_split 0.2 \
  -model-epochs 10 \
  -model-batch_size 32 \
  -model-imageSize 150 \
  -model-enableGPU \
  -model-patience 2 \
  -scorer pytorchscore \
  -tuner parameter_grid \
  -tuner-parameters @parameters.json \
  -log debug \
  -sources train=dir test=dir \
    -source-train-foldername rps/rps \
    -source-train-feature image \
    -source-train-labels rock paper scissors \
    -source-test-foldername rps-test-set/rps-test-set \
    -source-test-feature image \
    -source-test-labels rock paper scissors \

  
  
 