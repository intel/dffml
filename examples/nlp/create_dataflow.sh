dffml dataflow create get_single remove_stopwords get_embedding -configloader yaml \
    -seed '["embedding"]'=get_single_spec "en_core_web_sm"=spacy_model_name_def "<PAD>"=pad_token_def 10=max_len_def \
    -flow \
      '[{"seed": ["sentence"]}]'=remove_stopwords.inputs.text \
      '[{"seed": ["spacy_model_name_def"]}]'=get_embedding.inputs.spacy_model \
      '[{"seed": ["pad_token_def"]}]'=get_embedding.inputs.pad_token \
      '[{"seed": ["max_len_def"]}]'=get_embedding.inputs.max_len \
      '[{"remove_stopwords": "result"}]'=get_embedding.inputs.text |
    tee nlp_ops_dataflow.yaml