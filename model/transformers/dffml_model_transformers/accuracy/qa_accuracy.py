import os
import logging

from transformers import (
    AutoTokenizer,
    AutoModelForQuestionAnswering,
    squad_convert_examples_to_features,
)

from transformers.data.metrics.squad_metrics import squad_evaluate

from dffml import (
    config,
    ModelContext,
    ModelNotTrained,
    AccuracyContext,
    AccuracyScorer,
    SourcesContext,
    entrypoint,
)

logger = logging.getLogger(__name__)


@config
class TransformerQaAccuracyConfig:
    pass


class TransformerQaAccuracyContext(AccuracyContext):
    """
    Accuracy Scorer for Transformers QA Model
    """

    async def score(self, mctx: ModelContext, sources: SourcesContext):
        if not os.path.isfile(
            os.path.join(mctx.parent.config.output_dir, "pytorch_model.bin")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        mctx.tokenizer = AutoTokenizer.from_pretrained(
            mctx.parent.config.output_dir,
            do_lower_case=mctx.parent.config.do_lower_case,
        )
        eval_examples = await mctx._preprocess_data(sources)
        features, dataset = squad_convert_examples_to_features(
            examples=eval_examples,
            tokenizer=mctx.tokenizer,
            max_seq_length=mctx.parent.config.max_seq_length,
            doc_stride=mctx.parent.config.doc_stride,
            max_query_length=mctx.parent.config.max_query_length,
            is_training=False,
            return_dataset="pt",
        )

        results = {}
        if mctx.parent.config.local_rank in [-1, 0]:
            logger.info(
                "Loading checkpoints saved during training for evaluation"
            )
            mctx.model = AutoModelForQuestionAnswering.from_pretrained(
                mctx.parent.config.output_dir
            )
            mctx.model.to(mctx.parent.config.device)

            # Evaluate
            predictions = await mctx._custom_accuracy(
                eval_examples, features, dataset
            )
            results = squad_evaluate(eval_examples, predictions)

        logger.info("Results: {}".format(results))

        # return results
        return results["f1"]


@entrypoint("tqa")
class TransformerQaAccuracy(AccuracyScorer):
    CONFIG = TransformerQaAccuracyConfig
    CONTEXT = TransformerQaAccuracyContext
