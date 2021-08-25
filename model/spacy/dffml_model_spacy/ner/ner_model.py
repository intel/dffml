import random
import pathlib
import warnings
from typing import AsyncIterator, Tuple, Any

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding


from dffml import (
    config,
    field,
    entrypoint,
    ModelNotTrained,
    SourcesContext,
    Record,
)
from dffml.model.model import Model
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelContext, ModelNotTrained


@config
class SpacyNERModelConfig:
    location: str = field("Output location.")
    model_name: str = field(
        "Name of one of the trained pipelines provided by spaCy.\
        You can find complete list at: https://spacy.io/models\
        Defaults to blank 'en' model.",
        default=None,
    )
    n_iter: int = field("Number of training iterations", default=10)
    dropout: float = field(
        "Dropout rate to be used during training", default=0.5
    )

    def __post_init__(self):
        self.location = pathlib.Path(self.location)


class SpacyNERModelContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        if "ner" not in self.parent.nlp.pipe_names:
            self.ner = self.parent.nlp.create_pipe("ner")
            self.parent.nlp.add_pipe("ner", last=True)
        else:
            # get it to add labels
            self.ner = self.parent.nlp.get_pipe("ner")

    async def _preprocess_data(self, sources: Sources):
        all_examples = []
        all_sources = sources.with_features(["sentence", "entities",])
        async for record in all_sources:
            all_examples.append(
                (
                    record.feature("sentence"),
                    {"entities": record.feature("entities")},
                )
            )
        return all_examples

    async def train(self, sources: Sources):
        train_examples = await self._preprocess_data(sources)
        for _, entities in train_examples:
            for ent in entities.get("entities"):
                self.ner.add_label(ent[2])

        # get names of other pipes to disable them during training
        pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
        other_pipes = [
            pipe
            for pipe in self.parent.nlp.pipe_names
            if pipe not in pipe_exceptions
        ]
        # only train NER
        with self.parent.nlp.disable_pipes(
            *other_pipes
        ), warnings.catch_warnings():
            # show warnings for misaligned entity spans once
            warnings.filterwarnings(
                "once", category=UserWarning, module="spacy"
            )
            if self.parent.config.model_name is None:
                self.parent.nlp.begin_training()
            for _ in range(self.parent.config.n_iter):
                random.shuffle(train_examples)
                losses = {}
                batches = minibatch(
                    train_examples, size=compounding(4.0, 32.0, 1.001)
                )
                for batch in batches:
                    examples = []
                    for doc, gold_dict in batch:
                        doc = self.parent.nlp.make_doc(doc)
                        examples.append(Example.from_dict(doc, gold_dict))
                    self.parent.nlp.update(
                        examples,
                        drop=self.parent.config.dropout,
                        losses=losses,
                    )
                self.logger.debug(f"Losses: {losses}")

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not self.parent.model_path.exists():
            raise ModelNotTrained("Train model before prediction.")

        async for record in sources.records():
            doc = self.parent.nlp(record.feature("sentence"))
            prediction = [(ent.text, ent.label_) for ent in doc.ents]
            record.predicted("Tag", prediction, "Nan")
            yield record


@entrypoint("spacyner")
class SpacyNERModel(Model):
    r"""
    Implemented using `Spacy statistical models <https://spacy.io/usage/training>`_ .

    .. note::

        You must download ``en_core_web_sm`` before using this model

        .. code-block:: console
            :test:

            $ python -m spacy download en_core_web_sm

    First we create the training and testing datasets.

    Training data:

    **train.json**

    .. code-block:: json
        :test:
        :filepath: train.json

        {
            "data": [
                {
                    "sentence": "I went to London and Berlin.",
                    "entities": [
                        {
                            "start":10,
                            "end": 16,
                            "tag": "LOC"
                        },
                        {
                            "start":21,
                            "end": 27,
                            "tag": "LOC"
                        }
                    ]
                },
                {
                    "sentence": "Who is Alex?",
                    "entities": [
                        {
                            "start":7,
                            "end": 11,
                            "tag": "PERSON"
                        }
                    ]
                }
            ]
        }

    Testing data:

    **test.json**

    .. code-block:: json
        :test:
        :filepath: test.json

        {
            "data": [
                {
                    "sentence": "Alex went to London?"
                }
            ]
        }

    Train the model

    .. code-block:: console
        :test:

        $ dffml train \
            -model spacyner \
            -sources s=op \
            -source-opimp dffml_model_spacy.ner.utils:parser \
            -source-args train.json False \
            -model-model_name en_core_web_sm \
            -model-location temp \
            -model-n_iter 5 \
            -log debug

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -model spacyner \
            -sources s=op \
            -source-opimp dffml_model_spacy.ner.utils:parser \
            -source-args train.json False \
            -model-model_name en_core_web_sm \
            -model-location temp \
            -model-n_iter 5 \
            -features tag:str:1 \
            -scorer sner \
            -log debug
        0.0

    Make a prediction

    .. code-block:: console
        :test:

        $ dffml predict all \
            -model spacyner \
            -sources s=op \
            -source-opimp dffml_model_spacy.ner.utils:parser \
            -source-args test.json True \
            -model-model_name en_core_web_sm \
            -model-location temp \
            -model-n_iter 5 \
            -log debug
        [
            {
                "extra": {},
                "features": {
                    "entities": [],
                    "sentence": "Alex went to London?"
                },
                "key": 0,
                "last_updated": "2020-07-27T16:26:18Z",
                "prediction": {
                    "Answer": {
                        "confidence": null,
                        "value": [
                            [
                                "Alex",
                                "PERSON"
                            ],
                            [
                                "London",
                                "GPE"
                            ]
                        ]
                    }
                }
            }
        ]

    The model can be trained on large datasets to get the expected
    output. The example shown above is to demonstrate the commandline usage
    of the model.

    In the above train, accuracy and predict commands, :ref:`plugin_source_dffml_op` source is used to
    read and parse data from json file before feeding it to the model. The function used by opsource to parse json data
    is:

    .. literalinclude:: /../model/spacy/dffml_model_spacy/ner/utils.py

    The location of the function is passed using:

    .. code-block:: console

            -source-opimp dffml_model_spacy.ner.utils:parser

    And the arguments to `parser` are passed by:

    .. code-block:: console

            -source-args train.json False

    where `train.json` is the name of file containing training data and the bool `False`
    is value of the flag `is_predicting`.
    """

    CONFIG = SpacyNERModelConfig
    CONTEXT = SpacyNERModelContext

    def __init__(self, config):
        super().__init__(config)
        self.nlp = None

    async def __aenter__(self):
        await super().__aenter__()
        self.path = (
            self.config.location
            if not hasattr(self, "temp_dir")
            else self.temp_dir
        )
        self.model_path = self.path / "ner"
        if self.model_path.exists():
            self.nlp = spacy.load(self.model_path)
            self.logger.debug("Loaded model from disk.")
        elif self.config.model_name:
            self.nlp = spacy.load(self.config.model_name)
            self.logger.debug(f"Loaded model {self.config.model_name}")
        else:
            self.nlp = spacy.blank("en")
            self.logger.debug("Created blank 'en' model")

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.nlp:
            self.nlp.to_disk(self.model_path)
            self.logger.debug(f"Saved model to {self.model_path}")
        return await super().__aexit__(exc_type, exc_value, traceback)
