dffml dataflow create get_single remove_stopwords tfidf_vectorizer \
    -inputs '["tfidf_vectorizer.outputs.result"]'=get_single_spec  \
    -flow \
      '[{"seed": ["sentence"]}]'=remove_stopwords.inputs.text \
      '[{"remove_stopwords": "result"}]'=tfidf_vectorizer.inputs.text |
    tee nlp_ops_dataflow1.json