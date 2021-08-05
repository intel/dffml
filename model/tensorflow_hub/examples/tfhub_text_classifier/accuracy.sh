dffml accuracy \
  -model text_classifier \
  -model-predict sentiment:int:1 \
  -model-location tempdir \
  -model-classifications 0 1 \
  -model-model_path "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1" \
  -model-clstype int \
  -features sentiment:int:1 \
  -sources f=csv \
  -source-filename test.csv \
  -model-features \
    sentence:str:1 \
  -scorer textclf \
  -log critical