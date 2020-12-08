import os

from transformers import (
    AutoTokenizer,
    TFAutoModelForSequenceClassification,
    TFTrainer,
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
class TransformerClassificationAccuracyConfig:
    pass


class TransformerClassificationAccuracyContext(AccuracyContext):
    """
    Accuracy Scorer for Transformers Classification Model
    """

    async def score(self, mctx: ModelContext, sources: SourcesContext):
        if not os.path.isfile(
            os.path.join(mctx.parent.config.output_dir, "tf_model.h5")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        config = mctx.parent.config._asdict()
        mctx.tokenizer = AutoTokenizer.from_pretrained(
            mctx.parent.config.output_dir
        )
        eval_features = await mctx._preprocess_data(sources)
        eval_dataset = await mctx.example_features_to_dataset(eval_features)

        def compute_metrics(p: EvalPrediction) -> Dict:
            preds = mctx.np.argmax(p.predictions, axis=1)
            return mctx.classification_compute_metrics(preds, p.label_ids)

        with mctx.parent.config.strategy.scope():
            mctx.model = TFAutoModelForSequenceClassification.from_pretrained(
                config["directory"]
            )
        trainer = TFTrainer(
            model=mctx.model,
            args=mctx.parent.config,
            eval_dataset=eval_dataset,
            compute_metrics=compute_metrics,
        )
        result = trainer.evaluate()
        return result["eval_acc"]


@entrypoint("tclf")
class TransformerClassificationAccuracy(AccuracyScorer):
    CONFIG = TransformerClassificationAccuracyConfig
    CONTEXT = TransformerClassificationAccuracyContext
