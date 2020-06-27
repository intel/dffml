dffml train \
  -model autoclassifier \
  -model-predict classification:int:1 \
  -model-clstype int \
  -sources f=csv \
  -source-filename iris_training.csv \
  -model-features \
    SepalLength:float:1 \
    SepalWidth:float:1 \
    PetalLength:float:1 \
    PetalWidth:float:1 \
  -model-time_left_for_this_task 120 \
  -model-per_run_time_limit 30 \
  -model-ensemble_size 50 \
  -model-delete_tmp_folder_after_terminate False \
  -model-directory tempdir \
  -log debug
