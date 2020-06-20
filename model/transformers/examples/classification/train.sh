dffml train \
  -model hfclassifier \
  -model-predict sentiment:int:1 \
  -model-label_list 0 1 \
  -model-clstype int \
  -sources f=csv \
  -source-filename train.csv \
  -model-epochs 2 \
  -model-model_name_or_path bert-base-cased \
  -model-output_dir hfclassification/checkpoints \
  -model-cache_dir hfclassification \
  -model-logging_dir hfclassification/logging \
  -model-no_cuda \
  -model-save_steps 1 \
  -model-features \
    sentence:str:1 \
  -log debug