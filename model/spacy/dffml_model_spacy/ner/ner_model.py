import os
import random
import pathlib
import warnings
from typing import AsyncIterator, Tuple, Any

import spacy
from spacy.scorer import Scorer
from spacy.gold import GoldParse
from spacy.util import minibatch, compounding


from dffml import (
    config,
    field,
    entrypoint,
    ModelNotTrained,
    Accuracy,
    SourcesContext,
    Record,
)
from dffml.model.model import Model
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelContext, ModelNotTrained


@config
class SpacyNERModelConfig:
    output_dir: str = field("Output directory")
    model_name_or_path: str = field(
        "Model name or path to saved model. Defaults to blank 'en' model.",
        default=None,
    )
    n_iter: int = field("Number of training iterations", default=10)
    dropout: float = field(
        "Dropout rate to be used during training", default=0.5
    )

    def __post_init__(self):
        self.output_dir = pathlib.Path(self.output_dir)


class SpacyNERModelContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        if self.parent.config.model_name_or_path is not None:
            # load existing model
            self.nlp = spacy.load(self.parent.config.model_name_or_path)
            self.logger.debug(
                "Loaded model '%s'" % self.parent.config.model_name_or_path
            )
        else:
            # create blank Language class
            self.nlp = spacy.blank("en")
            self.logger.debug("Created blank 'en' model")

        if "ner" not in self.nlp.pipe_names:
            self.ner = self.nlp.create_pipe("ner")
            self.nlp.add_pipe(self.ner, last=True)
        else:
            # get it to add labels
            self.ner = self.nlp.get_pipe("ner")

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
            pipe for pipe in self.nlp.pipe_names if pipe not in pipe_exceptions
        ]
        # only train NER
        with self.nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
            # show warnings for misaligned entity spans once
            warnings.filterwarnings(
                "once", category=UserWarning, module="spacy"
            )
            if self.parent.config.model_name_or_path is None:
                self.nlp.begin_training()
            for itn in range(self.parent.config.n_iter):
                random.shuffle(train_examples)
                losses = {}
                batches = minibatch(
                    train_examples, size=compounding(4.0, 32.0, 1.001)
                )
                for batch in batches:
                    texts, annotations = zip(*batch)
                    self.nlp.update(
                        texts,  # batch of texts
                        annotations,  # batch of annotations
                        drop=self.parent.config.dropout,
                        losses=losses,
                    )
                self.logger.debug("Losses", losses)

        if self.parent.config.output_dir is not None:
            if not self.parent.config.output_dir.exists():
                self.parent.config.output_dir.mkdir()
            self.nlp.to_disk(self.parent.config.output_dir)
            self.logger.debug("Saved model to", self.parent.config.output_dir)

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        if not os.path.isdir(
            os.path.join(self.parent.config.output_dir, "ner")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        test_examples = await self._preprocess_data(sources)
        self.nlp = spacy.load(self.parent.config.output_dir)

        scorer = Scorer()
        for input_, annot in test_examples:
            doc_gold_text = self.nlp.make_doc(input_)
            gold = GoldParse(doc_gold_text, entities=annot["entities"])
            pred_value = self.nlp(input_)
            scorer.score(pred_value, gold)
        return Accuracy(scorer.scores["tags_acc"])

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not os.path.isdir(
            os.path.join(self.parent.config.output_dir, "ner")
        ):
            raise ModelNotTrained("Train model before prediction.")
        self.nlp = spacy.load(self.parent.config.output_dir)

        async for record in sources.records():
            doc = self.nlp(record.feature("sentence"))
            prediction = [(ent.text, ent.label_) for ent in doc.ents]
            record.predicted("Answer", prediction, "Nan")
            yield record


@entrypoint("spacyner")
class SpacyNERModel(Model):
    CONFIG = SpacyNERModelConfig
    CONTEXT = SpacyNERModelContext
