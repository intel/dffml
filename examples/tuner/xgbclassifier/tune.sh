dffml tune \
-model xgbclassifier \
-model-features \
SepalLength:float:1 \
 SepalWidth:float:1 \
 PetalLength:float:1 \
 -model-predict classification \
-model-location tempDir \
-tuner parameter_grid \
-tuner-parameters @xgbtest.json \
-tuner-objective max \
 -scorer clf \
-sources train=csv test=csv \
 -source-train-filename iris_training.csv \
 -source-test-filename iris_test.csv