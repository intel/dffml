dffml dataflow create get_single remove_stopwords collect_output extract_array_from_matrix tfidf_vectorizer  \
    -inputs '["extract_array_from_matrix.outputs.result"]'=get_single_spec 4=source_length \
    -flow \
      '[{"seed": ["sentence"]}]'=remove_stopwords.inputs.text \
      '[{"seed": ["source_length"]}]'=collect_output.inputs.length \
      '[{"remove_stopwords": "result"}]'=collect_output.inputs.sentence \
      '[{"collect_output": "all"}]'=tfidf_vectorizer.inputs.text \
      '[{"remove_stopwords": "result"}]'=extract_array_from_matrix.inputs.single_text_example \
      '[{"collect_output": "all"}]'=extract_array_from_matrix.inputs.collected_text \
      '[{"tfidf_vectorizer": "result"}]'=extract_array_from_matrix.inputs.input_matrix |
    tee nlp_ops_dataflow.json

