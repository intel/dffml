import os
import re
import glob
import math
import datetime
import collections
from typing import Any, List, Tuple, AsyncIterator

import numpy as np
import pandas as pd
from seqeval.metrics import f1_score, classification_report

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

try:
    from fastprogress import master_bar, progress_bar
except ImportError:
    from fastprogress.fastprogress import master_bar, progress_bar

from transformers import (
    TF2_WEIGHTS_NAME,
    BertConfig,
    BertTokenizer,
    DistilBertConfig,
    DistilBertTokenizer,
    GradientAccumulator,
    RobertaConfig,
    RobertaTokenizer,
    TFBertForTokenClassification,
    TFDistilBertForTokenClassification,
    TFRobertaForTokenClassification,
    create_optimizer,
)

from dffml.record import Record
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml.model.model import ModelContext, Model, ModelNotTrained

from .utils import read_examples_from_df, convert_examples_to_features

ALL_MODELS = sum(
    (
        tuple(conf.pretrained_config_archive_map.keys())
        for conf in (BertConfig, RobertaConfig, DistilBertConfig)
    ),
    (),
)
ORIGINAL_NER_MODELS = {
    "bert": (BertConfig, TFBertForTokenClassification, BertTokenizer),
    "distilbert": (
        DistilBertConfig,
        TFDistilBertForTokenClassification,
        DistilBertTokenizer,
    ),
    "roberta": (
        RobertaConfig,
        TFRobertaForTokenClassification,
        RobertaTokenizer,
    ),
}


@config
class NERModelConfig:
    sentence_id: Feature = field(
        "Unique Id to identify words of each sentence"
    )
    words: Feature = field("Tokens to train NER model")
    predict: Feature = field("NER Tags (B-MISC, I-PER, O etc.) for tokens")
    model_architecture_type: str = field(
        "Model architecture selected in the : "
        + ", ".join(ORIGINAL_NER_MODELS.keys())
    )
    model_name_or_path: str = field(
        "Path to pre-trained model or shortcut name selected in the list: "
        + ", ".join(ALL_MODELS)
    )
    output_dir: str = field(
        "The output directory where the model checkpoints will be written",
        default=os.path.join(
            os.path.expanduser("~"),
            ".cache",
            "dffml",
            "transformers",
            "checkpoints",
        ),
    )
    config_name: str = field(
        "Pretrained config name or path if not the same as model_name",
        default=None,
    )
    tokenizer_name: str = field(
        "Pretrained tokenizer name or path if not the same as model_name",
        default=None,
    )
    cache_dir: str = field(
        "Directory to store the pre-trained models downloaded from s3",
        default=os.path.join(
            os.path.expanduser("~"), ".cache", "dffml", "transformers"
        ),
    )
    max_seq_length: int = field(
        "The maximum total input sentence length after tokenization.Sequences longer than this will be truncated, sequences shorter will be padded",
        default=128,
    )
    max_steps: int = field(
        "If greater than zero then sets total number of training steps to perform. Overrides `epochs`",
        default=0,
    )
    use_fp16: bool = field(
        "Whether to use 16-bit (mixed) precision instead of 32-bit",
        default=False,
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
        "Total number of training epochs to perform.", default=2
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
    eval_all_checkpoints: bool = field(
        "Evaluate all checkpoints starting with the same prefix as model_name ending and ending with step number",
        default=False,
    )

    def __post_init__(self):
        if self.use_fp16:
            tf.config.optimizer.set_experimental_options(
                {"auto_mixed_precision": True}
            )
        if self.tpu:
            resolver = tf.distribute.cluster_resolver.TPUClusterResolver(
                tpu=self.parent.config.tpu
            )
            tf.config.experimental_connect_to_cluster(resolver)
            tf.tpu.experimental.initialize_tpu_system(resolver)
            self.strategy = tf.distribute.experimental.TPUStrategy(resolver)
            self.n_device = self.num_tpu_cores
        elif len(self.gpus.split(",")) > 1:
            self.n_device = len(
                [f"/gpu:{gpu}" for gpu in self.gpus.split(",")]
            )
            self.strategy = tf.distribute.MirroredStrategy(
                devices=[f"/gpu:{gpu}" for gpu in self.gpus.split(",")]
            )
        elif self.no_cuda:
            self.n_device = 1
            self.strategy = tf.distribute.OneDeviceStrategy(device="/cpu:0")
        else:
            self.n_device = len(self.gpus.split(","))
            self.strategy = tf.distribute.OneDeviceStrategy(
                device="/gpu:" + self.gpus.split(",")[0]
            )


class NERModelContext(ModelContext):
    def __init__(self, parent, **kwconfig):
        super().__init__(parent)
        self.pad_token_label_id = 0
        (
            self.ner_config_class,
            self.model_class,
            self.tokenizer_class,
        ) = ORIGINAL_NER_MODELS[self.parent.config.model_architecture_type]
        self.ner_config = self.ner_config_class.from_pretrained(
            self.parent.config.config_name
            if self.parent.config.config_name
            else self.parent.config.model_name_or_path,
            num_labels=len(self.parent.config.ner_tags) + 1,
            cache_dir=self.parent.config.cache_dir
            if self.parent.config.cache_dir
            else None,
        )

    async def _preprocess_data(self, sources: Sources):
        x_cols: Dict[str, Any] = {
            feature: []
            for feature in (
                [
                    self.parent.config.sentence_id.NAME,
                    self.parent.config.words.NAME,
                ]
            )
        }
        y_cols = []
        all_records = []
        all_sources = sources.with_features(
            [
                self.parent.config.sentence_id.NAME,
                self.parent.config.words.NAME,
                self.parent.config.predict.NAME,
            ]
        )
        async for record in all_sources:
            if (
                record.feature(self.parent.config.predict.NAME)
                in self.parent.config.ner_tags
            ):
                all_records.append(record)
        for record in all_records:
            for feature, results in record.features(
                [
                    self.parent.config.sentence_id.NAME,
                    self.parent.config.words.NAME,
                ]
            ).items():
                x_cols[feature].append(np.array(results))
            y_cols.append(record.feature(self.parent.config.predict.NAME))
        if not y_cols:
            raise ValueError("No records to train on")
        y_cols = np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])

        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        df = pd.DataFrame.from_dict(x_cols)
        df[self.parent.config.predict.NAME] = y_cols
        return df

    def serialized_features_to_dataset(
        self, serialized_features, max_seq_length
    ):
        name_to_features = {
            "input_ids": tf.io.FixedLenFeature([max_seq_length], tf.int64),
            "input_mask": tf.io.FixedLenFeature([max_seq_length], tf.int64),
            "segment_ids": tf.io.FixedLenFeature([max_seq_length], tf.int64),
            "label_ids": tf.io.FixedLenFeature([max_seq_length], tf.int64),
        }

        def _decode_record(record):
            example = tf.io.parse_single_example(record, name_to_features)
            features = {}
            features["input_ids"] = example["input_ids"]
            features["input_mask"] = example["input_mask"]
            features["segment_ids"] = example["segment_ids"]

            return features, example["label_ids"]

        d = tf.data.Dataset.from_tensor_slices(serialized_features)
        d = d.map(_decode_record, num_parallel_calls=4)
        count = d.reduce(0, lambda x, _: x + 1)
        return d, count.numpy()

    def serialize_features(self, features):
        all_examples = []

        for (ex_index, feature) in enumerate(features):
            if ex_index % 5000 == 0:
                self.logger.debug(
                    "Writing example %d of %d" % (ex_index, len(features))
                )

            def create_int_feature(values):
                f = tf.train.Feature(
                    int64_list=tf.train.Int64List(value=list(values))
                )
                return f

            record_feature = collections.OrderedDict()
            record_feature["input_ids"] = create_int_feature(feature.input_ids)
            record_feature["input_mask"] = create_int_feature(
                feature.input_mask
            )
            record_feature["segment_ids"] = create_int_feature(
                feature.segment_ids
            )
            record_feature["label_ids"] = create_int_feature(feature.label_ids)

            tf_example = tf.train.Example(
                features=tf.train.Features(feature=record_feature)
            )
            serialized_example = tf_example.SerializeToString()

            all_examples.append(serialized_example)
        return tf.convert_to_tensor(all_examples, tf.string)

    def get_dataset(
        self, data, tokenizer, pad_token_label_id, batch_size, mode
    ):
        config = self.parent.config._asdict()
        drop_remainder = True if config["tpu"] or mode == "train" else False
        labels = config["ner_tags"]
        sentence_id_col = self.parent.config.sentence_id.NAME
        words_col = self.parent.config.words.NAME
        labels_col = self.parent.config.predict.NAME
        examples = read_examples_from_df(
            data, mode, sentence_id_col, words_col, labels_col
        )
        features = convert_examples_to_features(
            examples,
            labels,
            config["max_seq_length"],
            tokenizer,
            cls_token_at_end=bool(
                config["model_architecture_type"] in ["xlnet"]
            ),
            # xlnet has a cls token at the end
            cls_token=tokenizer.cls_token,
            cls_token_segment_id=2
            if config["model_architecture_type"] in ["xlnet"]
            else 0,
            sep_token=tokenizer.sep_token,
            sep_token_extra=bool(
                config["model_architecture_type"] in ["roberta"]
            ),
            # roberta uses an extra separator b/w pairs of sentences, cf. github.com/pytorch/fairseq/commit/1684e166e3da03f5b600dbb7855cb98ddfcd0805
            pad_on_left=bool(config["model_architecture_type"] in ["xlnet"]),
            # pad on the left for xlnet
            pad_token=tokenizer.convert_tokens_to_ids([tokenizer.pad_token])[
                0
            ],
            pad_token_segment_id=4
            if config["model_architecture_type"] in ["xlnet"]
            else 0,
            pad_token_label_id=pad_token_label_id,
        )
        serialized_features = self.serialize_features(features)
        dataset, size = self.serialized_features_to_dataset(
            serialized_features, config["max_seq_length"]
        )

        if mode == "train":
            dataset = dataset.repeat()
            dataset = dataset.shuffle(buffer_size=8192, seed=config["seed"])

        dataset = dataset.batch(batch_size, drop_remainder)
        dataset = dataset.prefetch(buffer_size=batch_size)
        return dataset, size

    def _custom_train(
        self,
        train_dataset,
        tokenizer,
        model,
        num_train_examples,
        train_batch_size,
    ):
        config = self.parent.config._asdict()
        config["strategy"] = self.parent.config.strategy
        config["n_device"] = self.parent.config.n_device
        labels = config["ner_tags"]
        if config["max_steps"] > 0:
            num_train_steps = (
                config["max_steps"] * config["gradient_accumulation_steps"]
            )
            config["epochs"] = 1
        else:
            num_train_steps = (
                math.ceil(num_train_examples / train_batch_size)
                // config["gradient_accumulation_steps"]
                * config["epochs"]
            )

        with config["strategy"].scope():
            loss_fct = tf.keras.losses.SparseCategoricalCrossentropy(
                reduction=tf.keras.losses.Reduction.NONE
            )
            optimizer = create_optimizer(
                config["learning_rate"],
                num_train_steps,
                config["warmup_steps"],
            )

            if config["use_fp16"]:
                optimizer = tf.keras.mixed_precision.experimental.LossScaleOptimizer(
                    optimizer, "dynamic"
                )

            loss_metric = tf.keras.metrics.Mean(name="loss", dtype=tf.float32)
            gradient_accumulator = GradientAccumulator()

        self.logger.info("***** Running training *****")
        self.logger.info("  Num examples = %d", num_train_examples)
        self.logger.info("  Num Epochs = %d", config["epochs"])
        self.logger.info(
            "  Instantaneous batch size per device = %d",
            config["per_device_train_batch_size"],
        )
        self.logger.info(
            "  Total train batch size (w. parallel, distributed & accumulation) = %d",
            train_batch_size * config["gradient_accumulation_steps"],
        )
        self.logger.info(
            "  Gradient Accumulation steps = %d",
            config["gradient_accumulation_steps"],
        )
        self.logger.info("  Total training steps = %d", num_train_steps)

        model.summary()

        @tf.function
        def apply_gradients():
            grads_and_vars = []

            for gradient, variable in zip(
                gradient_accumulator.gradients, model.trainable_variables
            ):
                if gradient is not None:
                    scaled_gradient = gradient / (
                        config["n_device"]
                        * config["gradient_accumulation_steps"]
                    )
                    grads_and_vars.append((scaled_gradient, variable))
                else:
                    grads_and_vars.append((gradient, variable))

            optimizer.apply_gradients(grads_and_vars, config["max_grad_norm"])
            gradient_accumulator.reset()

        @tf.function
        def train_step(train_features, train_labels):
            def step_fn(train_features, train_labels):
                inputs = {
                    "attention_mask": train_features["input_mask"],
                    "training": True,
                }

                if config["model_architecture_type"] != "distilbert":
                    inputs["token_type_ids"] = (
                        train_features["segment_ids"]
                        if config["model_architecture_type"]
                        in ["bert", "xlnet"]
                        else None
                    )

                with tf.GradientTape() as tape:
                    logits = model(train_features["input_ids"], **inputs)[0]
                    logits = tf.reshape(logits, (-1, len(labels) + 1))
                    active_loss = tf.reshape(
                        train_features["input_mask"], (-1,)
                    )
                    active_logits = tf.boolean_mask(logits, active_loss)
                    train_labels = tf.reshape(train_labels, (-1,))
                    active_labels = tf.boolean_mask(train_labels, active_loss)
                    cross_entropy = loss_fct(active_labels, active_logits)
                    loss = tf.reduce_sum(cross_entropy) * (
                        1.0 / train_batch_size
                    )
                    grads = tape.gradient(loss, model.trainable_variables)

                    gradient_accumulator(grads)

                return cross_entropy

            per_example_losses = config["strategy"].experimental_run_v2(
                step_fn, args=(train_features, train_labels)
            )
            mean_loss = config["strategy"].reduce(
                tf.distribute.ReduceOp.MEAN, per_example_losses, axis=0
            )

            return mean_loss

        current_time = datetime.datetime.now()
        train_iterator = master_bar(range(config["epochs"]))
        global_step = 0
        self.logger_loss = 0.0

        for epoch in train_iterator:
            epoch_iterator = progress_bar(
                train_dataset,
                total=num_train_steps,
                parent=train_iterator,
                display=config["n_device"] > 1,
            )
            step = 1

            with config["strategy"].scope():
                for train_features, train_labels in epoch_iterator:
                    loss = train_step(train_features, train_labels)

                    if step % config["gradient_accumulation_steps"] == 0:
                        config["strategy"].experimental_run_v2(apply_gradients)
                        loss_metric(loss)
                        global_step += 1
                        if (
                            config["save_steps"] > 0
                            and global_step % config["save_steps"] == 0
                        ):
                            # Save model checkpoint
                            output_dir = os.path.join(
                                config["output_dir"],
                                "checkpoint-{}".format(global_step),
                            )

                            if not os.path.exists(output_dir):
                                os.makedirs(output_dir)

                            model.save_pretrained(output_dir)
                            self.logger.info(
                                "Saving model checkpoint to %s", output_dir
                            )

                    train_iterator.child.comment = (
                        f"loss : {loss_metric.result()}"
                    )
                    step += 1

            train_iterator.write(
                f"loss epoch {epoch + 1}: {loss_metric.result()}"
            )
            loss_metric.reset_states()
        self.logger.info(
            "  Training took time = {}".format(
                datetime.datetime.now() - current_time
            )
        )

    def _custom_accuracy(
        self,
        eval_dataset,
        tokenizer,
        model,
        num_eval_examples,
        eval_batch_size,
    ):
        config = self.parent.config._asdict()
        config["strategy"] = self.parent.config.strategy
        config["n_device"] = self.parent.config.n_device
        labels = config["ner_tags"]
        preds = None
        num_eval_steps = math.ceil(num_eval_examples / eval_batch_size)
        master = master_bar(range(1))
        master.main_bar.last_v = 0
        eval_iterator = progress_bar(
            eval_dataset,
            total=num_eval_steps,
            parent=master,
            display=config["n_device"] > 1,
        )
        loss_fct = tf.keras.losses.SparseCategoricalCrossentropy(
            reduction=tf.keras.losses.Reduction.NONE
        )
        loss = 0.0

        self.logger.info("***** Running evaluation *****")
        self.logger.info("  Num examples = %d", num_eval_examples)
        self.logger.info("  Batch size = %d", eval_batch_size)

        for eval_features, eval_labels in eval_iterator:
            inputs = {
                "attention_mask": eval_features["input_mask"],
                "training": False,
            }

            if config["model_architecture_type"] != "distilbert":
                inputs["token_type_ids"] = (
                    eval_features["segment_ids"]
                    if config["model_architecture_type"] in ["bert", "xlnet"]
                    else None
                )

            with config["strategy"].scope():
                logits = model(eval_features["input_ids"], **inputs)[0]
                tmp_logits = tf.reshape(logits, (-1, len(labels) + 1))
                active_loss = tf.reshape(eval_features["input_mask"], (-1,))
                active_logits = tf.boolean_mask(tmp_logits, active_loss)
                tmp_eval_labels = tf.reshape(eval_labels, (-1,))
                active_labels = tf.boolean_mask(tmp_eval_labels, active_loss)
                cross_entropy = loss_fct(active_labels, active_logits)
                loss += tf.reduce_sum(cross_entropy) * (1.0 / eval_batch_size)

            if preds is None:
                preds = logits.numpy()
                label_ids = eval_labels.numpy()
            else:
                preds = np.append(preds, logits.numpy(), axis=0)
                label_ids = np.append(label_ids, eval_labels.numpy(), axis=0)

        preds = np.argmax(preds, axis=2)
        y_pred = [[] for _ in range(label_ids.shape[0])]
        y_true = [[] for _ in range(label_ids.shape[0])]
        loss = loss / num_eval_steps
        for i in range(label_ids.shape[0]):
            for j in range(label_ids.shape[1]):
                if label_ids[i, j] != self.pad_token_label_id:
                    y_pred[i].append(labels[preds[i, j] - 1])
                    y_true[i].append(labels[label_ids[i, j] - 1])
        return y_true, y_pred, loss.numpy()

    def _custom_predict(
        self,
        test_dataset,
        tokenizer,
        model,
        num_test_examples,
        test_batch_size,
    ):
        config = self.parent.config._asdict()
        config["strategy"] = self.parent.config.strategy
        config["n_device"] = self.parent.config.n_device
        labels = config["ner_tags"]
        preds = None
        num_test_steps = math.ceil(num_test_examples / test_batch_size)
        master = master_bar(range(1))
        master.main_bar.last_v = 0

        test_iterator = progress_bar(
            test_dataset,
            total=num_test_steps,
            parent=master,
            display=config["n_device"] > 1,
        )
        loss_fct = tf.keras.losses.SparseCategoricalCrossentropy(
            reduction=tf.keras.losses.Reduction.NONE
        )
        loss = 0.0

        self.logger.info("***** Running evaluation *****")
        self.logger.info("  Num examples = %d", num_test_examples)
        self.logger.info("  Batch size = %d", test_batch_size)

        for test_features, test_labels in test_iterator:
            inputs = {
                "attention_mask": test_features["input_mask"],
                "training": False,
            }

            if config["model_architecture_type"] != "distilbert":
                inputs["token_type_ids"] = (
                    test_features["segment_ids"]
                    if config["model_architecture_type"] in ["bert", "xlnet"]
                    else None
                )

            with config["strategy"].scope():
                logits = model(test_features["input_ids"], **inputs)[0]
                tmp_logits = tf.reshape(logits, (-1, len(labels) + 1))
                active_loss = tf.reshape(test_features["input_mask"], (-1,))
                active_logits = tf.boolean_mask(tmp_logits, active_loss)
                tmp_test_labels = tf.reshape(test_labels, (-1,))
                active_labels = tf.boolean_mask(tmp_test_labels, active_loss)
                cross_entropy = loss_fct(active_labels, active_logits)
                loss += tf.reduce_sum(cross_entropy) * (1.0 / test_batch_size)

            if preds is None:
                preds = logits.numpy()
                label_ids = test_labels.numpy()
            else:
                preds = np.append(preds, logits.numpy(), axis=0)
                label_ids = np.append(label_ids, test_labels.numpy(), axis=0)

        preds = np.argmax(preds, axis=2)
        y_pred = [[] for _ in range(label_ids.shape[0])]

        for i in range(label_ids.shape[0]):
            for j in range(label_ids.shape[1]):
                if label_ids[i, j] != self.pad_token_label_id:
                    y_pred[i].append(labels[preds[i, j] - 1])
        return y_pred

    async def train(self, sources: Sources):

        self.tokenizer = self.tokenizer_class.from_pretrained(
            self.parent.config.tokenizer_name
            if self.parent.config.tokenizer_name
            else self.parent.config.model_name_or_path,
            do_lower_case=self.parent.config.do_lower_case,
            cache_dir=self.parent.config.cache_dir
            if self.parent.config.cache_dir
            else None,
        )

        with self.parent.config.strategy.scope():
            self.model = self.model_class.from_pretrained(
                self.parent.config.model_name_or_path,
                from_pt=bool(".bin" in self.parent.config.model_name_or_path),
                config=self.ner_config,
                cache_dir=self.parent.config.cache_dir
                if self.parent.config.cache_dir
                else None,
            )
            self.model.layers[-1].activation = tf.keras.activations.softmax

        train_batch_size = (
            self.parent.config.per_device_train_batch_size
            * self.parent.config.n_device
        )
        data_df = await self._preprocess_data(sources)
        train_dataset, num_train_examples = self.get_dataset(
            data_df,
            self.tokenizer,
            self.pad_token_label_id,
            train_batch_size,
            mode="train",
        )
        train_dataset = self.parent.config.strategy.experimental_distribute_dataset(
            train_dataset
        )
        self._custom_train(
            train_dataset,
            self.tokenizer,
            self.model,
            num_train_examples,
            train_batch_size,
        )

        if not os.path.exists(self.parent.config.output_dir):
            os.makedirs(self.parent.config.output_dir)

        self.logger.info("Saving model to %s", self.parent.config.output_dir)

        self.model.save_pretrained(self.parent.config.output_dir)
        self.tokenizer.save_pretrained(self.parent.config.output_dir)

    async def accuracy(self, sources: Sources):
        if not os.path.isfile(
            os.path.join(self.parent.config.output_dir, "tf_model.h5")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        config = self.parent.config._asdict()
        config["strategy"] = self.parent.config.strategy
        config["n_device"] = self.parent.config.n_device
        self.tokenizer = self.tokenizer_class.from_pretrained(
            config["output_dir"], do_lower_case=config["do_lower_case"]
        )
        eval_batch_size = (
            config["per_device_eval_batch_size"] * config["n_device"]
        )
        data_df = await self._preprocess_data(sources)
        eval_dataset, num_eval_examples = self.get_dataset(
            data_df,
            self.tokenizer,
            self.pad_token_label_id,
            eval_batch_size,
            mode="accuracy",
        )
        eval_dataset = self.parent.config.strategy.experimental_distribute_dataset(
            eval_dataset
        )

        checkpoints = []
        results = []

        if config["eval_all_checkpoints"]:
            checkpoints = list(
                os.path.dirname(c)
                for c in sorted(
                    glob.glob(
                        config["output_dir"] + "/**/" + TF2_WEIGHTS_NAME,
                        recursive=True,
                    ),
                    key=lambda f: int("".join(filter(str.isdigit, f)) or -1),
                )
            )

        if len(checkpoints) == 0:
            checkpoints.append(config["output_dir"])

        self.logger.info("Evaluate the following checkpoints: %s", checkpoints)

        for checkpoint in checkpoints:
            global_step = (
                checkpoint.split("-")[-1]
                if re.match(".*checkpoint-[0-9]", checkpoint)
                else "final"
            )

            with self.parent.config.strategy.scope():
                self.model = self.model_class.from_pretrained(checkpoint)

            y_true, y_pred, eval_loss = self._custom_accuracy(
                eval_dataset,
                self.tokenizer,
                self.model,
                num_eval_examples,
                eval_batch_size,
            )
            report = classification_report(y_true, y_pred, digits=4)

            if global_step:
                results.append(
                    {
                        global_step + "_report": report,
                        global_step + "_loss": eval_loss,
                    }
                )

        output_eval_file = os.path.join(
            config["output_dir"], "accuracy_results.txt"
        )
        with tf.io.gfile.GFile(output_eval_file, "w") as writer:
            for res in results:
                for key, val in res.items():
                    if "loss" in key:
                        self.logger.info(key + " = " + str(val))
                        writer.write(key + " = " + str(val))
                        writer.write("\n")
                    else:
                        self.logger.info(key)
                        self.logger.info("\n" + report)
                        writer.write(key + "\n")
                        writer.write(report)
                        writer.write("\n")
        # Return accuracy for the last checkpoint
        return Accuracy(f1_score(y_true, y_pred))

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not os.path.isfile(
            os.path.join(self.parent.config.output_dir, "tf_model.h5")
        ):
            raise ModelNotTrained("Train model before prediction.")
        config = self.parent.config._asdict()
        config["strategy"] = self.parent.config.strategy
        config["n_device"] = self.parent.config.n_device
        tokenizer = self.tokenizer_class.from_pretrained(
            config["output_dir"], do_lower_case=config["do_lower_case"]
        )
        model = self.model_class.from_pretrained(config["output_dir"])
        test_batch_size = (
            config["per_device_eval_batch_size"] * config["n_device"]
        )
        async for record in records:
            words = record.features([self.parent.config.words.NAME])
            df = pd.DataFrame(words, index=[0])
            test_dataset, num_test_examples = self.get_dataset(
                df,
                tokenizer,
                self.pad_token_label_id,
                test_batch_size,
                mode="test",
            )
            test_dataset = self.parent.config.strategy.experimental_distribute_dataset(
                test_dataset
            )
            y_pred = self._custom_predict(
                test_dataset,
                tokenizer,
                model,
                num_test_examples,
                test_batch_size,
            )
            preds = [
                [
                    {word: y_pred[i][j]}
                    for j, word in enumerate(
                        sentence.split()[: len(y_pred[i])]
                    )
                ]
                for i, sentence in enumerate(
                    df[self.parent.config.words.NAME].to_list()
                )
            ]
            record.predicted(self.parent.config.predict.NAME, preds, "Nan")
            yield record


@entrypoint("ner_tagger")
class NERModel(Model):
    CONTEXT = NERModelContext
    CONFIG = NERModelConfig
