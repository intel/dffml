dffml accuracy \
  -model scikitlr \
  -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
  -model-predict Salary:float:1 \
  -model-location tempdir \
  -sources f=csv \
  -source-filename test.csv \
  -scorer mse
