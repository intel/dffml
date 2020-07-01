dffml train \
  -model autoregressor \
  -model-predict TARGET:float:1 \
  -model-clstype int \
  -sources f=csv \
  -source-filename train.csv \
  -model-features \
    Feature1:float:1 \
    Feature2:float:1 \
  -model-time_left_for_this_task 120 \
  -model-per_run_time_limit 30 \
  -model-ensemble_size 50 \
  -model-delete_tmp_folder_after_terminate False \
  -model-directory tempdir \
  -log debug
