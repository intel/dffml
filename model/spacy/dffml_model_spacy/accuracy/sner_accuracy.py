import os

import spacy
from spacy.scorer import Scorer
from spacy.training import Example

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
        if not os.path.isdir(os.path.join(mctx.parent.config.location, "ner")):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        test_examples = await mctx._preprocess_data(sources)
        mctx.nlp = spacy.load(mctx.parent.config.location)

        scorer = Scorer()
        examples = []
        for input_, annot in test_examples:
            pred_value = mctx.nlp(input_)
            example = Example.from_dict(
                pred_value, {"entities": annot["entities"]}
            )
            example.reference = mctx.nlp.make_doc(input_)
            examples.append(example)
        scores = scorer.score(examples)
        return scores["token_acc"]


@entrypoint("sner")
class SpacyNerAccuracy(AccuracyScorer):
    CONFIG = SpacyNerAccuracyConfig
    CONTEXT = SpacyNerAccuracyContext
