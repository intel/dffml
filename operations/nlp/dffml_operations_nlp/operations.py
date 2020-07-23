from typing import List, Dict, Tuple

import spacy
from spacy.attrs import ENT_IOB
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import (
    CountVectorizer,
    TfidfVectorizer,
    TfidfTransformer,
)

from dffml.df.base import op


def _load_model(spacy_model: str):
    try:
        nlp = spacy.load(spacy_model)
    except OSError:
        raise Exception(
            f"Can't find model {spacy_model}. Try running `python -m spacy download {spacy_model}"
        )
    return nlp


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
    nlp = _load_model(spacy_model)
    tokens = nlp(text)
    embedding = []
    for token in tokens:
        embedding.append(token.vector)
    return embedding


@op
async def pos_tagger(
    text: str, spacy_model: str, tag_type: str = "fine_grained"
) -> List[str]:
    """
    Assigns part-of-speech tags to text.

    Parameters
    ----------
    text : str
        Text to be tagged.

    spacy_model: str
        A spacy model with tagger and parser.

    Returns
    -------
    result: list
        A list containing tuples of word and their respective pos tag.
    """
    nlp = _load_model(spacy_model)
    doc = nlp(text)
    pos_tags = []
    if tag_type is "fine_grained":
        for token in doc:
            pos_tags.append((token.text, token.tag_))
    elif tag_type is "coarse_grained":
        for token in doc:
            pos_tags.append((token.text, token.pos_))
    return pos_tags


@op
async def lemmatizer(text: str, spacy_model: str) -> List[str]:
    """
    Reduce words in the text to their dictionary form (lemma)

    Parameters
    ----------
    text : str
        String to lemmatize.

    spacy_model: str
        Spacy model to be used for lemmatization.

    Returns
    -------
    result: list
        A list containing base form of the words.
    """
    nlp = _load_model(spacy_model)
    doc = nlp(text)
    lemma = []
    for word in doc:
        lemma.append(word.lemma_)
    return lemma


@op
async def get_similarity(text_1: str, text_2: str, spacy_model: str) -> float:
    """
    Calculates similarity between two text strings as a score between 0 and 1.

    Parameters
    ----------
    text_1 : str
        First string to compare.
    
    text_2 : str
        Second string to compare.

    spacy_model: str
        Spacy model to be used for extracting word vectors which are used for calculating similarity.

    Returns
    -------
    result: float
        A similarity score between 0 and 1.
    """
    nlp = _load_model(spacy_model)
    text_1_doc = nlp(text_1)
    text_2_doc = nlp(text_2)
    return text_1_doc.similarity(text_2_doc)


@op
async def get_noun_chunks(text: str, spacy_model: str) -> List[str]:
    """
    Extracts the noun chunks from text.

    Parameters
    ----------
    text : str
        String to extract noun chunks from.

    spacy_model: str
        A spacy model with the capability of parsing.

    Returns
    -------
    result: list
        A list containing noun chunks.
    """
    nlp = _load_model(spacy_model)
    text_doc = nlp(text)
    noun_chunks = list(text_doc.noun_chunks)
    return noun_chunks


@op
async def get_sentences(text: str, spacy_model: str) -> List[str]:
    """
    Extracts the sentences from text.

    Parameters
    ----------
    text : str
        String to extract sentences from.

    spacy_model: str
        A spacy model with the capability of parsing. Sentence 
        boundaries are calculated from the syntactic dependency parse.

    Returns
    -------
    result: list
        A list containing sentences.
    """
    nlp = _load_model(spacy_model)
    text_doc = nlp(text)
    sentences = list(text_doc.sents)
    return sentences


@op
async def count_vectorizer(
    text: List[str],
    encoding: str = "utf-8",
    decode_error: str = "strict",
    strip_accents: str = None,
    lowercase: bool = True,
    # preprocessor=None,
    # tokenizer=None,
    stop_words: str = None,
    token_pattern: str = "(?u)\\b\\w\\w+\\b",
    # ngram_range: tuple = (1, 1),
    analyzer: str = "word",
    max_df: float = 1.0,
    min_df: float = 1,
    max_features: int = None,
    vocabulary: dict = None,
    binary: bool = False,
    # dtype: str = <class 'numpy.int64'>
) -> List[int]:
    vectorizer = CountVectorizer(
        encoding=encoding,
        decode_error=decode_error,
        strip_accents=strip_accents,
        lowercase=lowercase,
        stop_words=stop_words,
        token_pattern=token_pattern,
        analyzer=analyzer,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features,
        vocabulary=vocabulary,
        binary=binary,
    )
    X = vectorizer.fit_transform(text)
    return X.toarray()


@op
async def tfidf_vectorizer(
    text: List[str],
    # input="content",
    encoding: str = "utf-8",
    decode_error: str = "strict",
    strip_accents: str = None,
    lowercase: bool = True,
    # preprocessor=None,
    # tokenizer=None,
    analyzer: str = "word",
    stop_words: str = None,
    token_pattern: str = "(?u)\\b\\w\\w+\\b",
    # ngram_range=(1, 1),
    max_df: str = 1.0,
    min_df: str = 1,
    max_features: str = None,
    vocabulary: str = None,
    binary: bool = False,
    # dtype="<class 'numpy.float64'>'",
    norm: str = "l2",
    use_idf: bool = True,
    smooth_idf: bool = True,
    sublinear_tf: bool = False,
) -> List[float]:
    vectorizer = TfidfVectorizer(
        encoding=encoding,
        decode_error=decode_error,
        strip_accents=strip_accents,
        lowercase=lowercase,
        analyzer=analyzer,
        stop_words=stop_words,
        token_pattern=token_pattern,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features,
        vocabulary=vocabulary,
        binary=binary,
        norm=norm,
        use_idf=use_idf,
        smooth_idf=smooth_idf,
        sublinear_tf=sublinear_tf,
    )

    X = vectorizer.fit_transform(text)
    return X.toarray()
