dffml train \
  -model text_classifier \
  -model-epochs 30 \
  -model-predict sentiment:int:1 \
  -model-directory tempdir \
  -model-classifications 0 1 \
  -model-clstype int \
  -sources f=csv \
  -source-filename train.csv \
  -model-features \
    sentence:str:1 \
  -model-model_path "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1" \
  -model-add_layers \
  -model-layers "Dense(units=512, activation='relu')" "Dense(units=2, activation='softmax')" \
  -log debug