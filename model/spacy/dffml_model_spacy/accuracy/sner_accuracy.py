import os

import spacy
from spacy.scorer import Scorer
from spacy.gold import GoldParse

from dffml import (
    config,
    AccuracyContext,
    entrypoint,
    AccuracyScorer,
    ModelContext,
    SourcesContext,
)


@config
class SpacyNerAccuracyConfig:
    pass


class SpacyNerAccuracyContext(AccuracyContext):
    """
    Accuracy Scorer for Spacy Ner Model
    """

    async def score(self, mctx: ModelContext, sources: SourcesContext):
        if not os.path.isdir(
            os.path.join(mctx.parent.config.directory, "ner")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        test_examples = await mctx._preprocess_data(sources)
        mctx.nlp = spacy.load(mctx.parent.config.directory)

        scorer = Scorer()
        for input_, annot in test_examples:
            doc_gold_text = mctx.nlp.make_doc(input_)
            gold = GoldParse(doc_gold_text, entities=annot["entities"])
            pred_value = mctx.nlp(input_)
            scorer.score(pred_value, gold)
        return scorer.scores["tags_acc"]


@entrypoint("sner")
class SpacyNerAccuracy(AccuracyScorer):
    CONFIG = SpacyNerAccuracyConfig
    CONTEXT = SpacyNerAccuracyContext
