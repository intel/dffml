import asyncio
from typing import List, Dict, Any

import spacy
import numpy as np
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import (
    CountVectorizer,
    TfidfVectorizer,
)

from dffml.df.base import (
    op,
    Operation,
    OperationImplementation,
    OperationImplementationContext,
)
from dffml.df.types import Definition


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
    """
    Removes stopword from text data.

    Parameters
    ----------
    text : str
        String to be cleaned.

    custom_stop_words: List[str], default = None
        List of words to be considered as stop words.

    Returns
    -------
    result: A string without stop words.
    """
    all_text = []
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
    ngram_range: List[int] = None,
    analyzer: str = "word",
    max_df: float = 1.0,
    min_df: float = 1,
    max_features: int = None,
    vocabulary: dict = None,
    binary: bool = False,
    get_feature_names: bool = False,
) -> List[int]:
    """
    Converts a collection of text documents to a matrix of token counts using sklearn CountVectorizer's `fit_transform` method. 
    For details on parameters check https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
    Parameters specific to this operation are described below.

    Parameters
    ----------
    text : list
        A list of strings.

    get_feature_names: bool
        If `True` return feature names using get_feature_names method of CountVectorizer.

    Returns
    -------
    result: list
        A list containing token counts and feature names if `get_feature_names` is `True`.
    """
    if ngram_range is None:
        ngram_range = (1, 1)
    else:
        ngram_range = tuple(ngram_range)
    vectorizer = CountVectorizer(
        encoding=encoding,
        decode_error=decode_error,
        strip_accents=strip_accents,
        lowercase=lowercase,
        stop_words=stop_words,
        token_pattern=token_pattern,
        ngram_range=ngram_range,
        analyzer=analyzer,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features,
        vocabulary=vocabulary,
        binary=binary,
    )
    names = None
    X = vectorizer.fit_transform(text).toarray()
    if get_feature_names:
        names = vectorizer.get_feature_names()
    return [X, names]


collected_data = Definition(name="collected_data", primitive="List[str]")
data_received = Definition(name="data_received", primitive="bool")


@op(
    inputs={"data": collected_data}, outputs={"status": data_received},
)
def get_status_collected_data(data):
    return {"status": True}


data_example = Definition(name="data_example", primitive="str")


@op(
    inputs={"data": data_example}, outputs={"all_data": collected_data},
)
def collect_data(data_example):

    return {"status": True}


@op
async def tfidf_vectorizer(
    text: List[str],
    encoding: str = "utf-8",
    decode_error: str = "strict",
    strip_accents: str = None,
    lowercase: bool = True,
    # preprocessor=None,
    # tokenizer=None,
    analyzer: str = "word",
    stop_words: str = None,
    token_pattern: str = "(?u)\\b\\w\\w+\\b",
    ngram_range: List[int] = None,
    max_df: str = 1.0,
    min_df: str = 1,
    max_features: str = None,
    vocabulary: str = None,
    binary: bool = False,
    norm: str = "l2",
    use_idf: bool = True,
    smooth_idf: bool = True,
    sublinear_tf: bool = False,
    get_feature_names: bool = False,
) -> List[float]:
    """
    Convert a collection of raw documents to a matrix of TF-IDF features using sklearn TfidfVectorizer's `fit_transform` method.
    For details on parameters check https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
    Parameters specific to this operation are described below.

    Parameters
    ----------
    text : list
        A list of strings.

    get_feature_names: bool
        If `True` return feature names using get_feature_names method of TfidfVectorizer.

    Returns
    -------
    result: list
        A list containing token counts and feature names if `get_feature_names` is `True`.
    """
    if ngram_range is None:
        ngram_range = (1, 1)
    else:
        ngram_range = tuple(ngram_range)
    vectorizer = TfidfVectorizer(
        encoding=encoding,
        decode_error=decode_error,
        strip_accents=strip_accents,
        lowercase=lowercase,
        analyzer=analyzer,
        stop_words=stop_words,
        token_pattern=token_pattern,
        ngram_range=ngram_range,
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

    names = None
    text_list = []
    if type(text) != type(list()):
        text_list.append(text)
    else:
        text_list = text
    X = vectorizer.fit_transform(text_list).toarray()
    if X.shape[0] == 1:
        X = np.ravel(X)
    if get_feature_names:
        names = vectorizer.get_feature_names()
        return X, names
    return X


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
    """
    Maps words of text data to their corresponding word vectors.

    Parameters
    ----------
    text : str
        String to be converted to word vectors.

    max_len: int
        Maximum length of sentence.
        If the length of `text` > `max_len`, `text` is truncated
        to have length = `max_len`.
        If the length of `text` < `max_len`, `text` is padded with
        `pad_token` such that len(`text`) = `max_len`.

    pad_token: str
        Token to be used for padding `text` if len(`text`) < `max_len`

    spacy_model: str
        Spacy model to be used for assigning vectors to tokens.

    Returns
    -------
    result: A 2-d array of shape (max_len, embedding_size of vectors).
    """
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


collect_output = Operation(
    name="collect_output",
    inputs={
        "sentence": Definition("sentence", "string"),
        "length": Definition("source_length", "string"),
    },
    outputs={"all": Definition("all_sentences", "List[string]")},
    conditions=[],
)


class CollectOutputContext(OperationImplementationContext):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:

        async with self.parent.lock:
            if self.parent.length is None:
                self.parent.length = inputs["length"]
            self.parent.list.append(inputs["sentence"])

            if len(self.parent.list) == self.parent.length:
                self.parent.event.set()

        await self.parent.event.wait()

        return {"all": self.parent.list}


class CollectOutput(OperationImplementation):

    op = collect_output
    CONTEXT = CollectOutputContext

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = None
        self.length = None
        self.event = None
        self.list = []

    async def __aenter__(self) -> "OperationImplementationContext":
        self.lock = asyncio.Lock()
        self.event = asyncio.Event()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.lock = None


@op
async def extract_array_from_matrix(
    single_text_example: str,
    collected_text: List[str],
    input_matrix: List[float],
) -> List[float]:
    """
    Returns row from `input_matrix` based on index of `single_text_example` 
    in `collected_text`.

    Parameters
    ----------
    single_text_example : str
        String to be used for indexing into `collected_text`.

    collected_text: list
        List of strings.

    input_matrix: list
        A 2-D matrix where each row represents vector corresponding
        to `single_text_example`.

    Returns
    -------
    result: A 1-d array.
    """
    idx = collected_text.index(single_text_example)
    return input_matrix[idx, :]
