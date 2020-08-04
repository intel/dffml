dffml predict all \
    -model scikitgnb \
    -model-features tfidf_vectorizer.outputs.result:float:[1,1,2] \
    -model-predict sentiment:int:1 \
    -model-directory tempdir \
    -sources text=df \
    -source-text-dataflow nlp_ops_dataflow1.json \
    -source-text-features sentence:str:1 \
    -source-text-source csv \
    -source-text-source-filename test_data.csv \
    -pretty

