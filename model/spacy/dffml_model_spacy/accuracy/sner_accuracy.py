from dffml.feature.feature import Features

import spacy
from spacy.scorer import Scorer
from spacy.training import Example


from dffml import (
    config,
    AccuracyContext,
    entrypoint,
    AccuracyScorer,
    ModelContext,
    ModelNotTrained,
    SourcesContext,
)


@config
class SpacyNerAccuracyConfig:
    pass


class SpacyNerAccuracyContext(AccuracyContext):
    """
    Accuracy Scorer for Spacy Ner Model
    """

    async def score(
        self, mctx: ModelContext, sources: SourcesContext, *features: Features
    ):
        if not mctx.is_trained:
            raise ModelNotTrained("Train model before assessing for accuracy.")

        test_examples = await mctx._preprocess_data(sources)
        mctx.nlp = spacy.load(mctx.parent.model_path)

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
