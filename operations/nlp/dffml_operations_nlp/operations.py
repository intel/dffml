from typing import List

import spacy
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS

from dffml.df.base import op


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


@op
async def get_embedding(text: str, spacy_model: str) -> List[float]:
    try:
        nlp = spacy.load(spacy_model)
    except OSError:
        raise Exception(
            f"Can't find model {spacy_model}. Try running `python -m spacy download {spacy_model}"
        )

    tokens = nlp(text)
    embedding = []
    for token in tokens:
        embedding.append(token.vector)
    return embedding
