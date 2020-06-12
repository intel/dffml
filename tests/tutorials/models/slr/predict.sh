dffml predict all \
  -model myslr:MySLRModel \
  -model-feature Years:int:1 \
  -model-predict Salary:float:1 \
  -model-directory modeldir \
  -sources f=csv \
  -source-filename predict.csv
