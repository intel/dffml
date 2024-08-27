dffml train \
    -model h2o \
    -model-predict TARGET:float:1 \
    -model-clstype int \
    -sources f=csv \
    -source-filename train.csv \
    -model-features \
        Feature1:float:1 \
        Feature2:float:1 \
    -model-location tempdir 