dffml train \
  -model scratchlgrsag \
  -model-features f1:float:1 \
  -model-predict ans:int:1 \
  -model-directory tempdir \
  -sources f=csv \
  -source-filename dataset.csv \
  -log debug