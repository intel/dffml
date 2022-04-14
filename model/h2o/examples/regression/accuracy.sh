dffml accuracy \
    -model h2o \
    -model-predict TARGET:float:1 \
    -model-location tempdir \
    -features TARGET:float:1 \
    -sources f=csv \
    -source-filename test.csv \
    -model-features \
        Feature1:float:1 \
        Feature2:float:1 \
    -scorer mse \
    -log critical