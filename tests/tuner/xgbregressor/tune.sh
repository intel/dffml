dffml tune \
-model xgbregressor \
-model-features f1:float:1 \
  -model-predict ans:int:1 \
-model-location tempDir \
-tuner parameter_grid \
-tuner-parameters @xgbtest.json \
-tuner-objective min \
 -scorer mse \
 -features ans:int:1 \
-sources train=csv test=csv \
-source-train-tag train \
-source-test-tag test \
 -source-train-filename dataset.csv \
 -source-test-filename dataset2.csv \

