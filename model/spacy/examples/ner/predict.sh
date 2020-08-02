dffml predict all \
  -model spacyner \
  -sources s=op \
  -source-opimp model.spacy.dffml_model_spacy.ner.utils:parser \
  -source-args test.json True \
  -model-model_name_or_path en_core_web_sm \
  -model-output_dir temp \
  -model-n_iter 5 \
  -log debug 