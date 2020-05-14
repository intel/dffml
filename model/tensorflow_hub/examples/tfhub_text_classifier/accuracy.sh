dffml accuracy \
  -model text_classifier \
  -model-predict sentiment:int:1 \
  -model-classifications 0 1 \
  -model-model_path "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1" \
  -model-clstype int \
  -sources f=csv \
  -source-filename test.csv \
  -model-features \
    sentence:str:1 \
  -log critical