from typing import List

import spacy
from spacy.symbols import ORTH
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS

from dffml.df.base import op
from dffml.df.types import Definition


@op
async def remove_stopwords(
    text: str, custom_stop_words: List[str] = None
) -> str:
    all_tokens = []
    clean_tokens = []

    nlp = English()

    #  "nlp" Object is used to create documents with linguistic annotations.
    doc = nlp(text)

    # Create list of word tokens in text and remove custom stop words
    for token in doc:
        if custom_stop_words:
            if token.text not in custom_stop_words:
                all_tokens.append(token.text)
        else:
            all_tokens.append(token.text)

    # Create list of word tokens after removing stopwords
    for word in all_tokens:
        lexeme = nlp.vocab[word]
        if lexeme.is_stop == False:
            clean_tokens.append(word)
    return " ".join(clean_tokens)


# Definitions
text_def = Definition(name="text_def", primitive="str")
max_len_def = Definition(name="max_len_def", primitive="int")
pad_token_def = Definition(name="pad_token_def", primitive="str")
spacy_model_name_def = Definition(name="spacy_model_name_def", primitive="str")
embedding_def = Definition(name="embedding", primitive="generic")


@op(
    name="get_embedding",
    inputs={
        "text": text_def,
        "spacy_model": spacy_model_name_def,
        "max_len": max_len_def,
        "pad_token": pad_token_def,
    },
    outputs={"embedding": embedding_def},
)
async def get_embedding(
    text: str, max_len: int, pad_token: str, spacy_model: str
) -> List[float]:
    try:
        nlp = spacy.load(spacy_model)
    except OSError:
        raise Exception(
            f"Can't find model {spacy_model}. Try running `python -m spacy download {spacy_model}"
        )
    raw_tokens = text.split(" ")
    num_extra_tokens = max_len - len(raw_tokens)
    if num_extra_tokens >= 0:
        raw_tokens.extend([pad_token] * num_extra_tokens)
    else:
        raw_tokens = raw_tokens[:max_len]
    padded_text = " ".join(raw_tokens)

    nlp.tokenizer.add_special_case(pad_token, [{"ORTH": pad_token}])
    tokens = nlp(padded_text)
    embedding = []
    for token in tokens:
        embedding.append(token.vector)
    return {"embedding": embedding}
