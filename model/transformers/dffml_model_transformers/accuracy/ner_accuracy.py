import os

from transformers import (
    TFTrainer,
    TFAutoModelForTokenClassification,
)

from dffml import (
    config,
    ModelContext,
    ModelNotTrained,
    AccuracyContext,
    AccuracyScorer,
    SourcesContext,
    entrypoint,
)


@config
class TransformerNerAccuracyConfig:
    pass


class TransformerNerAccuracyContext(AccuracyContext):
    """
    Accuracy Scorer for Transformers NER Model
    """

    async def score(self, mctx: ModelContext, sources: SourcesContext):
        if not os.path.isfile(
            os.path.join(mctx.parent.config.output_dir, "tf_model.h5")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        data_df = await mctx._preprocess_data(sources)
        eval_dataset = mctx.get_dataset(data_df, mctx.tokenizer, mode="eval",)
        with mctx.parent.config.strategy.scope():
            mctx.model = TFAutoModelForTokenClassification.from_pretrained(
                mctx.parent.config.output_dir,
                config=mctx.config,
                cache_dir=mctx.parent.config.cache_dir,
            )

        trainer = TFTrainer(
            model=mctx.model,
            args=mctx.parent.config,
            train_dataset=None,
            eval_dataset=eval_dataset.get_dataset(),
            compute_metrics=mctx.compute_metrics,
        )

        result = trainer.evaluate()
        return result["eval_f1"]


@entrypoint("tner")
class TransformerNerAccuracy(AccuracyScorer):
    CONFIG = TransformerNerAccuracyConfig
    CONTEXT = TransformerNerAccuracyContext
