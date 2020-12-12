dffml accuracy \
  -model spacyner \
  -sources s=op \
  -source-opimp model.spacy.dffml_model_spacy.ner.utils:parser \
  -source-args train.json False \
  -model-model_name_or_path en_core_web_sm \
  -model-directory temp \
  -model-n_iter 5 \
  -scorer sner \
  -log debug