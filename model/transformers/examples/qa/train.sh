dffml train \
  -model qa_model \
  -model-model_type bert \
  -model-save_steps 3 \
  -model-model_name_or_path bert-base-cased \
  -model-output_dir qamodel/checkpoints \
  -model-cache_dir qamodel/cache \
  -sources s=op \
  -source-opimp dffml_model_transformers.qa.utils:parser \
  -source-args train.json True \
  -log debug