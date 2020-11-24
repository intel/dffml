import os
import json
import pathlib
import importlib
from typing import Any, List, AsyncIterator, Tuple, Dict

import numpy as np
from seqeval.metrics import (
    f1_score,
    precision_score,
    recall_score,
)

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from transformers import (
    TFTrainer,
    AutoConfig,
    AutoTokenizer,
    TFAutoModelForTokenClassification,
    EvalPrediction,
)

from dffml import export
from dffml.record import Record
from dffml.base import config, field
from dffml.feature.feature import Feature
from dffml.model.accuracy import Accuracy
from dffml.accuracy import AccuracyContext
from dffml.util.entrypoint import entrypoint
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelContext, Model, ModelNotTrained

from .utils import (
    read_examples_from_df,
    TFNerDataset,
)


@config
class NERModelConfig:
    sid: Feature = field(
        "Unique Id to identify words of each sentence (Sentence ID)"
    )
    words: Feature = field("Tokens to train NER model")
    predict: Feature = field("NER Tags (B-MISC, I-PER, O etc.) for tokens")
    model_name_or_path: str = field(
        "Path to pre-trained model or shortcut name listed on https://huggingface.co/models"
    )
    output_dir: str = field(
        "The output directory where the model checkpoints will be written",
    )
    cache_dir: str = field(
        "Directory to store the pre-trained models downloaded from s3",
    )
    from_pt: bool = field(
        "Whether to load model from pytorch checkpoint or .bin file",
        default=False,
    )
    config_name: str = field(
        "Pretrained config name or path if not the same as model_name",
        default=None,
    )
    tokenizer_name: str = field(
        "Pretrained tokenizer name or path if not the same as model_name",
        default=None,
    )
    overwrite_output_dir: bool = field(
        "Overwrite the content of the output directory.Use this to continue training if output_dir points to a checkpoint directory.",
        default=False,
    )
    max_seq_length: int = field(
        "The maximum total input sentence length after tokenization.Sequences longer than this will be truncated, sequences shorter will be padded",
        default=128,
    )
    max_steps: int = field(
        "If greater than zero then sets total number of training steps to perform. Overrides `epochs`",
        default=0,
    )
    fp16: bool = field(
        "Whether to use 16-bit (mixed) precision instead of 32-bit",
        default=False,
    )
    use_fast: bool = field(
        "Set this flag to use fast tokenization.", default=False
    )
    ner_tags: List[str] = field(
        "List of all distinct NER Tags",
        default_factory=lambda: [
            "O",
            "B-MISC",
            "I-MISC",
            "B-PER",
            "I-PER",
            "B-ORG",
            "I-ORG",
            "B-LOC",
            "I-LOC",
        ],
    )
    do_lower_case: bool = field(
        "Set this flag if using uncased model.", default=False
    )
    gradient_accumulation_steps: int = field(
        "Number of updates steps to accumulate before performing a backward pass.",
        default=1,
    )
    learning_rate: float = field(
        "The initial learning rate for Adam", default=5e-5
    )
    weight_decay: float = field("Weight decay", default=0.0)
    adam_epsilon: float = field("Epsilon for Adam optimizer", default=1e-8)
    max_grad_norm: float = field("Max gradient norm.", default=1.0)
    epochs: int = field(
        "Total number of training epochs to perform.", default=1
    )
    warmup_steps: int = field("Linear warmup over warmup_steps.", default=0)
    save_steps: int = field(
        "Save checkpoint every X update steps.", default=10
    )
    seed: int = field("Random seed for initialization", default=2020)
    gpus: str = field(
        "List of gpu devices. If only one, switch to single gpu strategy, if None takes all availabel gpus",
        default="0",
    )
    tpu: str = field(
        "The Cloud TPU to use for training. This should be either the name used when creating the Cloud TPU, or a grpc://ip.address.of.tpu:8470 url",
        default=None,
    )
    num_tpu_cores: int = field("Total number of TPU cores to use.", default=8)
    per_device_train_batch_size: int = field(
        "Batch size per GPU/CPU/TPU for training", default=8
    )
    per_device_eval_batch_size: int = field(
        "Batch size per GPU/CPU/TPU for assessing accuracy", default=8
    )
    no_cuda: bool = field("Avoid using CUDA when available", default=False)

    optimizer_name: str = field(
        'Name of a Tensorflow optimizer among "adadelta, adagrad, adam, adamax, ftrl, nadam, rmsprop, sgd, adamw"',
        default="adam",
    )
    loss_name: str = field(
        "Name of a Tensorflow loss. For the list see: https://www.tensorflow.org/api_docs/python/tf/keras/losses",
        default="SparseCategoricalCrossentropy",
    )
    overwrite_cache: bool = field(
        "Overwrite the cached training and evaluation sets", default=False,
    )
    logging_dir: str = field(
        "Tensorboard log dir.",
        default=str(
            pathlib.Path("~", ".cache", "dffml", "transformers", "log")
        ),
    )
    logging_first_step: bool = field(
        "Log and eval the first global_step", default=False,
    )
    logging_steps: int = field(
        "Log every X updates steps.", default=500,
    )
    save_total_limit: int = field(
        "Limit the total amount of checkpoints.Deletes the older checkpoints in the output_dir. Default is unlimited checkpoints",
        default=None,
    )
    fp16_opt_level: str = field(
        "For fp16: Apex AMP optimization level selected in ['O0', 'O1', 'O2', and 'O3']."
        "See details at https://nvidia.github.io/apex/amp.html",
        default="O1",
    )

    local_rank: int = field(
        "For distributed training: local_rank", default=-1,
    )
    end_lr: float = field("End learning rate for optimizer", default=0)
    debug: bool = field(
        "Activate the trace to record computation graphs and profiling information",
        default=False,
    )
    num_train_epochs: float = field(
        "Total number of training epochs to perform.", default=1,
    )
    evaluate_during_training: bool = field(
        "Run evaluation during training at each logging step.", default=False,
    )
    dataloader_drop_last: bool = field(
        "Drop the last incomplete batch if the length of the dataset is not divisible by the batch size",
        default=False,
    )
    past_index: int = field(
        "Some models can make use of the past hidden states for their predictions. If this argument is set to a positive int, the `Trainer` will use the corresponding output (usually index 2) as the past state and feed it to the model at the next training step under the keyword argument `mems` ",
        default=-1,
    )

    def to_json_string(self):
        """
        Serializes this instance to a JSON string.
        """
        config_dict = export(self)
        [config_dict.pop(key) for key in ["sid", "words", "predict"]]
        return json.dumps(config_dict, indent=2)

    def __post_init__(self):
        self.tf = importlib.import_module("tensorflow")
        if self.fp16:
            self.tf.config.optimizer.set_experimental_options(
                {"auto_mixed_precision": True}
            )
        if self.tpu:
            resolver = self.tf.distribute.cluster_resolver.TPUClusterResolver(
                tpu=self.parent.config.tpu
            )
            self.tf.config.experimental_connect_to_cluster(resolver)
            self.tf.tpu.experimental.initialize_tpu_system(resolver)
            self.strategy = self.tf.distribute.experimental.TPUStrategy(
                resolver
            )
            self.n_replicas = self.num_tpu_cores
        elif len(self.gpus.split(",")) > 1:
            self.n_replicas = len(
                [f"/gpu:{gpu}" for gpu in self.gpus.split(",")]
            )
            self.strategy = self.tf.distribute.MirroredStrategy(
                devices=[f"/gpu:{gpu}" for gpu in self.gpus.split(",")]
            )
        elif self.no_cuda:
            self.n_replicas = 1
            self.strategy = self.tf.distribute.OneDeviceStrategy(
                device="/cpu:0"
            )
        else:
            self.n_replicas = len(self.gpus.split(","))
            self.strategy = self.tf.distribute.OneDeviceStrategy(
                device="/gpu:" + self.gpus.split(",")[0]
            )
        self.train_batch_size = (
            self.per_device_train_batch_size * self.n_replicas
        )
        self.eval_batch_size = (
            self.per_device_eval_batch_size * self.n_replicas
        )
        self.test_batch_size = (
            self.per_device_eval_batch_size * self.n_replicas
        )
        self.label_map: Dict[int, str] = {
            i: label for i, label in enumerate(self.ner_tags)
        }
        self.num_labels = len(self.ner_tags)
        self.mode = "token-classification"


class NERModelContext(ModelContext):
    def __init__(self, parent, **kwconfig):
        super().__init__(parent)
        self.pd = importlib.import_module("pandas")
        self.np = importlib.import_module("numpy")
        self.tf = importlib.import_module("tensorflow")

        self.config = AutoConfig.from_pretrained(
            self.parent.config.config_name
            if self.parent.config.config_name
            else self.parent.config.model_name_or_path,
            num_label=self.parent.config.num_labels,
            id2label=self.parent.config.label_map,
            label2id={
                label: i for i, label in enumerate(self.parent.config.ner_tags)
            },
            cache_dir=self.parent.config.cache_dir,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.parent.config.tokenizer_name
            if self.parent.config.tokenizer_name
            else self.parent.config.model_name_or_path,
            cache_dir=self.parent.config.cache_dir,
            use_fast=self.parent.config.use_fast,
        )

    def align_predictions(
        self, predictions: np.ndarray, label_ids: np.ndarray
    ) -> Tuple[List[int], List[int]]:
        preds = np.argmax(predictions, axis=2)
        batch_size, seq_len = preds.shape
        out_label_list = [[] for _ in range(batch_size)]
        preds_list = [[] for _ in range(batch_size)]

        for i in range(batch_size):
            for j in range(seq_len):
                if label_ids[i, j] != -1:
                    out_label_list[i].append(
                        self.parent.config.label_map[label_ids[i][j]]
                    )
                    preds_list[i].append(
                        self.parent.config.label_map[preds[i][j]]
                    )

        return preds_list, out_label_list

    def compute_metrics(self, p: EvalPrediction) -> Dict:
        preds_list, out_label_list = self.align_predictions(
            p.predictions, p.label_ids
        )

        return {
            "precision": precision_score(out_label_list, preds_list),
            "recall": recall_score(out_label_list, preds_list),
            "f1": f1_score(out_label_list, preds_list),
        }

    async def _preprocess_data(self, sources: Sources):
        x_cols: Dict[str, Any] = {
            feature: []
            for feature in (
                [self.parent.config.sid.name, self.parent.config.words.name]
            )
        }
        y_cols = []
        all_records = []
        all_sources = sources.with_features(
            [
                self.parent.config.sid.name,
                self.parent.config.words.name,
                self.parent.config.predict.name,
            ]
        )
        async for record in all_sources:
            if (
                record.feature(self.parent.config.predict.name)
                in self.parent.config.ner_tags
            ):
                all_records.append(record)
        for record in all_records:
            for feature, results in record.features(
                [self.parent.config.sid.name, self.parent.config.words.name]
            ).items():
                x_cols[feature].append(self.np.array(results))
            y_cols.append(record.feature(self.parent.config.predict.name))
        if not y_cols:
            raise ValueError("No records to train on")
        y_cols = self.np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = self.np.array(x_cols[feature])

        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        df = self.pd.DataFrame.from_dict(x_cols)
        df[self.parent.config.predict.name] = y_cols
        return df

    def get_dataset(self, data, tokenizer, mode):
        sid_col = self.parent.config.sid.name
        words_col = self.parent.config.words.name
        labels_col = self.parent.config.predict.name
        examples = read_examples_from_df(
            data, mode, sid_col, words_col, labels_col
        )
        return TFNerDataset(
            examples=examples,
            tokenizer=tokenizer,
            labels=self.parent.config.ner_tags,
            model_type=self.config.model_type,
            max_seq_length=self.parent.config.max_seq_length,
            overwrite_cache=self.parent.config.overwrite_cache,
            mode=mode,
        )

    async def train(self, sources: Sources):
        with self.parent.config.strategy.scope():
            self.model = TFAutoModelForTokenClassification.from_pretrained(
                self.parent.config.model_name_or_path,
                from_pt=self.parent.config.from_pt,
                config=self.config,
                cache_dir=self.parent.config.cache_dir,
            )

        data_df = await self._preprocess_data(sources)
        train_dataset = self.get_dataset(
            data_df, self.tokenizer, mode="train",
        )
        trainer = TFTrainer(
            model=self.model,
            args=self.parent.config,
            train_dataset=train_dataset.get_dataset(),
            eval_dataset=None,
            compute_metrics=self.compute_metrics,
        )
        trainer.train()
        trainer.save_model()
        self.tokenizer.save_pretrained(self.parent.config.output_dir)

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not os.path.isfile(
            os.path.join(self.parent.config.output_dir, "tf_model.h5")
        ):
            raise ModelNotTrained("Train model before prediction.")
        with self.parent.config.strategy.scope():
            self.model = TFAutoModelForTokenClassification.from_pretrained(
                self.parent.config.output_dir,
                config=self.config,
                cache_dir=self.parent.config.cache_dir,
            )

        async for record in sources.with_features(
            [self.parent.config.words.name]
        ):
            sentence = record.features([self.parent.config.words.name])
            df = self.pd.DataFrame(sentence, index=[0])
            test_dataset = self.get_dataset(df, self.tokenizer, mode="test",)
            trainer = TFTrainer(
                model=self.model,
                args=self.parent.config,
                train_dataset=None,
                eval_dataset=None,
                compute_metrics=self.compute_metrics,
            )
            predictions, label_ids, _ = trainer.predict(
                test_dataset.get_dataset()
            )
            preds_list, labels_list = self.align_predictions(
                predictions, label_ids
            )
            preds = [
                {word: preds_list[0][i]}
                for i, word in enumerate(
                    sentence[self.parent.config.words.name].split()
                )
            ]

            record.predicted(self.parent.config.predict.name, preds, "Nan")
            yield record


@entrypoint("ner_tagger")
class NERModel(Model):
    """
    Implemented using `HuggingFace Transformers <https://huggingface.co/transformers/index.html>`_ Tensorflow based Models.
    Description about pretrianed models can be found `here <https://huggingface.co/transformers/pretrained_models.html>`_

    First we create the training and testing datasets

    .. literalinclude:: /../model/transformers/examples/ner/train_data.sh

    .. literalinclude:: /../model/transformers/examples/ner/test_data.sh

    Train the model

    .. literalinclude:: /../model/transformers/examples/ner/train.sh

    Assess the accuracy

    .. literalinclude:: /../model/transformers/examples/ner/accuracy.sh

    Output

    .. code-block::

        0.888888888888889

    Make a prediction

    .. literalinclude:: /../model/transformers/examples/ner/predict.sh

    Output

    .. code-block:: json

        [
            {
                "extra": {},
                "features": {
                    "SentenceId": 1,
                    "Words": "DFFML models can do NER"
                },
                "key": "0",
                "last_updated": "2020-06-11T17:40:54Z",
                "prediction": {
                    "Tag": {
                        "confidence": NaN,
                        "value": [
                            {
                                "DFFML": "B-MISC"
                            },
                            {
                                "models": "I-MISC"
                            },
                            {
                                "can": "O"
                            },
                            {
                                "do": "B-MISC"
                            },
                            {
                                "NER": "B-MISC"
                            }
                        ]
                    }
                }
            },
            {
                "extra": {},
                "features": {
                    "SentenceId": 2,
                    "Words": "DFFML models can do regression"
                },
                "key": "1",
                "last_updated": "2020-06-11T17:40:57Z",
                "prediction": {
                    "Tag": {
                        "confidence": NaN,
                        "value": [
                            {
                                "DFFML": "B-MISC"
                            },
                            {
                                "models": "I-MISC"
                            },
                            {
                                "can": "O"
                            },
                            {
                                "do": "B-MISC"
                            },
                            {
                                "regression": "I-MISC"
                            }
                        ]
                    }
                }
            }
        ]

    The model can be trained on large datasets to get the expected
    output. The example shown above is to demonstrate the commandline usage
    of the model.

    Example usage of NER model using python API

    .. literalinclude:: /../model/transformers/examples/ner/ner_model.py
    """

    CONTEXT = NERModelContext
    CONFIG = NERModelConfig
