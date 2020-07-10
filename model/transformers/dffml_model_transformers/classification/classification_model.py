import os
import json
import importlib
from typing import Any, List, Tuple, AsyncIterator, Dict, Type

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from transformers import (
    AutoConfig,
    AutoTokenizer,
    EvalPrediction,
    TFAutoModelForSequenceClassification,
    TFTrainer,
    glue_convert_examples_to_features,
)

from dffml import export
from dffml.record import Record
from dffml.base import config, field
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelContext, Model, ModelNotTrained

from .utils import InputExample, classification_compute_metrics


@config
class HFClassificationModelConfig:
    features: Features = field("Feature to train on")
    predict: Feature = field("Feature holding target values")
    label_list: List[str] = field("List of target labels")
    cache_dir: str = field(
        "Directory to store the pre-trained models downloaded from s3"
    )
    model_name_or_path: str = field(
        "Path to pretrained model or model identifier from huggingface.co/models",
    )
    output_dir: str = field(
        "The output directory where the model predictions and checkpoints will be written.",
    )
    logging_dir: str = field("Tensorboard log dir.")
    from_pt: bool = field(
        "Whether to load model from pytorch checkpoint or .bin file",
        default=False,
    )
    clstype: Type = field("Data type of classifications values", default=str)
    max_seq_length: int = field(
        "The maximum total input sequence length after tokenization. Sequences longer than this will be truncated, sequences shorter will be padded.",
        default=128,
    )
    overwrite_cache: bool = field(
        "Overwrite the cached training and evaluation sets", default=False,
    )

    config_name: str = field(
        "Pretrained config name or path if not the same as model_name",
        default=None,
    )
    tokenizer_name: str = field(
        "Pretrained tokenizer name or path if not the same as model_name",
        default=None,
    )
    use_fast: bool = field(
        "Set this flag to use fast tokenization.", default=False
    )
    doc_stride: int = field(
        "When splitting up a long document into chunks, how much stride to take between chunks.",
        default=128,
    )
    optimizer_name: str = field(
        'Name of a Tensorflow optimizer among "adadelta, adagrad, adam, adamax, ftrl, nadam, rmsprop, sgd, adamw"',
        default="adam",
    )
    loss_name: str = field(
        "Name of a Tensorflow loss. For the list see: https://www.tensorflow.org/api_docs/python/tf/keras/losses",
        default="SparseCategoricalCrossentropy",
    )
    gpus: str = field(
        "List of gpu devices. If only one, switch to single gpu strategy, if None takes all availabel gpus",
        default="0",
    )
    no_cuda: bool = field("Avoid using CUDA when available", default=False)

    end_lr: float = field("End learning rate for optimizer", default=0)
    debug: bool = field(
        "Activate the trace to record computation graphs and profiling information",
        default=False,
    )
    overwrite_output_dir: bool = field(
        "Overwrite the content of the output directory.Use this to continue training if output_dir points to a checkpoint directory.",
        default=False,
    )

    evaluate_during_training: bool = field(
        "Run evaluation during training at each logging step.", default=False,
    )

    per_device_train_batch_size: int = field(
        "Batch size per GPU/TPU core/CPU for training.", default=8,
    )
    per_device_eval_batch_size: int = field(
        "Batch size per GPU/TPU core/CPU for evaluation.", default=8,
    )

    gradient_accumulation_steps: int = field(
        "Number of updates steps to accumulate before performing a backward/update pass.",
        default=1,
    )

    learning_rate: float = field(
        "The initial learning rate for Adam.", default=5e-5,
    )
    weight_decay: float = field(
        "Weight decay if we apply some.", default=0.0,
    )
    adam_epsilon: float = field(
        "Epsilon for Adam optimizer.", default=1e-8,
    )
    max_grad_norm: float = field(
        "Max gradient norm.", default=1.0,
    )

    num_train_epochs: float = field(
        "Total number of training epochs to perform.", default=1,
    )
    max_steps: int = field(
        "If > 0: set total number of training steps to perform. Override num_train_epochs.",
        default=-1,
    )
    warmup_steps: int = field(
        "Linear warmup over warmup_steps.", default=0,
    )

    logging_first_step: bool = field(
        "Log and eval the first global_step", default=False,
    )
    logging_steps: int = field(
        "Log every X updates steps.", default=500,
    )
    save_steps: int = field(
        "Save checkpoint every X updates steps.", default=500,
    )
    save_total_limit: int = field(
        "Limit the total amount of checkpoints.Deletes the older checkpoints in the output_dir. Default is unlimited checkpoints",
        default=None,
    )
    no_cuda: bool = field(
        "Do not use CUDA even when it is available", default=False,
    )
    seed: int = field(
        "random seed for initialization", default=42,
    )

    fp16: bool = field(
        "Whether to use 16-bit (mixed) precision (through NVIDIA apex) instead of 32-bit",
        default=False,
    )
    fp16_opt_level: str = field(
        "For fp16: Apex AMP optimization level selected in ['O0', 'O1', 'O2', and 'O3']."
        "See details at https://nvidia.github.io/apex/amp.html",
        default="O1",
    )

    local_rank: int = field(
        "For distributed training: local_rank", default=-1,
    )
    dataloader_drop_last: bool = field(
        "Drop the last incomplete batch if the length of the dataset is not divisible by the batch size",
        default=False,
    )
    past_index: int = field("Some models can make use of the past hidden states for their predictions. If this argument is set to a positive int, the `Trainer` will use the corresponding output (usually index 2) as the past state and feed it to the model at the next training step under the keyword argument `mems` ", default = -1)

    def to_json_string(self):
        config_dict = export(self)
        [config_dict.pop(key) for key in ["features", "predict", "clstype"]]
        return json.dumps(config_dict, indent=2)

    def __post_init__(self):
        self.tf = importlib.import_module("tensorflow")
        self.label_list = list(map(self.clstype, self.label_list))
        self.task_name = "sst-2"
        self.mode = "text-classification"
        if len(self.features) > 1:
            raise ValueError("Found more than one feature to train on")
        if self.fp16:
            self.tf.config.optimizer.set_experimental_options(
                {"auto_mixed_precision": True}
            )
        if len(self.gpus.split(",")) > 1:
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
        self.train_batch_size = self.per_device_train_batch_size * max(
            1, self.n_replicas
        )
        self.eval_batch_size = self.per_device_eval_batch_size * max(
            1, self.n_replicas
        )


class HFClassificationModelContext(ModelContext):
    def __init__(self, parent, **kwconfig):
        super().__init__(parent)
        self.pd = importlib.import_module("pandas")
        self.np = importlib.import_module("numpy")
        self.tf = importlib.import_module("tensorflow")
        self.features = self.parent.config.features.names()
        self.config = AutoConfig.from_pretrained(
            self.parent.config.config_name
            if self.parent.config.config_name
            else self.parent.config.model_name_or_path,
            num_labels=len(self.parent.config.label_list),
            finetuning_task=self.parent.config.task_name,
            cache_dir=self.parent.config.cache_dir,
        )

    async def _preprocess_data(self, sources: Sources):
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []
        all_records = []
        all_sources = sources.with_features(
            self.features + [self.parent.config.predict.name]
        )
        async for record in all_sources:
            all_records.append(record)
        for record in all_records:
            for feature, results in record.features(self.features).items():
                x_cols[feature].append(self.np.array(results))
            y_cols.append(record.feature(self.parent.config.predict.name))

        y_cols = self.np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = self.np.array(x_cols[feature])

        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        df = self.pd.DataFrame.from_dict(x_cols)
        df[self.parent.config.predict.name] = y_cols
        train_examples = [
            InputExample(i, text, None, label)
            for i, (text, label) in enumerate(
                zip(df[self.features[0]], df[self.parent.config.predict.name],)
            )
        ]
        return glue_convert_examples_to_features(
            train_examples,
            self.tokenizer,
            self.parent.config.max_seq_length,
            self.parent.config.task_name,
            self.parent.config.label_list,
        )

    async def example_features_to_dataset(self, example_features):
        def gen():
            for ex in example_features:
                yield (
                    {
                        "input_ids": ex.input_ids,
                        "attention_mask": ex.attention_mask,
                        "token_type_ids": ex.token_type_ids,
                    },
                    ex.label,
                )

        dataset = self.tf.data.Dataset.from_generator(
            gen,
            (
                {
                    "input_ids": self.tf.int32,
                    "attention_mask": self.tf.int32,
                    "token_type_ids": self.tf.int32,
                },
                self.tf.int64,
            ),
            (
                {
                    "input_ids": self.tf.TensorShape([None]),
                    "attention_mask": self.tf.TensorShape([None]),
                    "token_type_ids": self.tf.TensorShape([None]),
                },
                self.tf.TensorShape([]),
            ),
        )
        return dataset

    async def train(self, sources: Sources):
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.parent.config.tokenizer_name
            if self.parent.config.tokenizer_name
            else self.parent.config.model_name_or_path,
            cache_dir=self.parent.config.cache_dir,
        )
        with self.parent.config.strategy.scope():
            self.model = TFAutoModelForSequenceClassification.from_pretrained(
                self.parent.config.model_name_or_path,
                from_pt=self.parent.config.from_pt,
                config=self.config,
                cache_dir=self.parent.config.cache_dir,
            )
        train_features = await self._preprocess_data(sources)
        train_dataset = await self.example_features_to_dataset(train_features)
        trainer = TFTrainer(
            model=self.model,
            args=self.parent.config,
            train_dataset=train_dataset,
        )
        trainer.train()
        self.logger.info("Saving model to %s", self.parent.config.output_dir)
        trainer.save_model()
        self.tokenizer.save_pretrained(self.parent.config.output_dir)

    async def accuracy(self, sources: Sources):
        if not os.path.isfile(
            os.path.join(self.parent.config.output_dir, "tf_model.h5")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        config = self.parent.config._asdict()
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.parent.config.output_dir
        )
        eval_features = await self._preprocess_data(sources)
        eval_dataset = await self.example_features_to_dataset(eval_features)

        def compute_metrics(p: EvalPrediction) -> Dict:
            preds = self.np.argmax(p.predictions, axis=1)
            return classification_compute_metrics(preds, p.label_ids)

        with self.parent.config.strategy.scope():
            self.model = TFAutoModelForSequenceClassification.from_pretrained(
                config["output_dir"]
            )
        trainer = TFTrainer(
            model=self.model,
            args=self.parent.config,
            eval_dataset=eval_dataset,
            compute_metrics=compute_metrics,
        )
        result = trainer.evaluate()
        return Accuracy(result["eval_acc"])

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not os.path.isfile(
            os.path.join(self.parent.config.output_dir, "tf_model.h5")
        ):
            raise ModelNotTrained("Train model before prediction.")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.parent.config.output_dir
        )

        with self.parent.config.strategy.scope():
            self.model = TFAutoModelForSequenceClassification.from_pretrained(
                self.parent.config.output_dir
            )
        trainer = TFTrainer(model=self.model, args=self.parent.config,)
        async for record in sources.with_features(self.features):
            to_predict = record.features(self.features)
            eval_example = [
                InputExample(
                    0,
                    to_predict[self.features[0]],
                    None,
                    self.parent.config.label_list[0],
                )
            ]
            eval_features = glue_convert_examples_to_features(
                eval_example,
                self.tokenizer,
                self.parent.config.max_seq_length,
                self.parent.config.task_name,
                self.parent.config.label_list,
            )
            eval_dataset = await self.example_features_to_dataset(
                eval_features
            )

            all_prob = trainer.predict(eval_dataset).predictions
            max_prob_idx = all_prob.argmax(axis=-1)
            self.logger.debug(
                "Predicted probability of {} for {}: {}".format(
                    self.parent.config.predict.name, to_predict, all_prob[0],
                )
            )
            record.predicted(
                self.parent.config.predict.name,
                self.parent.config.label_list[max_prob_idx[0]],
                all_prob[0][max_prob_idx[0]],
            )
            yield record


@entrypoint("hfclassifier")
class HFClassificationModel(Model):
    """
    Implemented using `HuggingFace Transformers <https://huggingface.co/transformers/index.html>`_ Tensorflow based Models.
    Description about pretrianed models can be found `here <https://huggingface.co/transformers/pretrained_models.html>`_

    First we create the training and testing datasets

    .. literalinclude:: /../model/transformers/examples/classification/train_data.sh

    .. literalinclude:: /../model/transformers/examples/classification/test_data.sh

    Train the model

    .. literalinclude:: /../model/transformers/examples/classification/train.sh

    Assess the accuracy

    .. literalinclude:: /../model/transformers/examples/classification/accuracy.sh

    Output

    .. code-block::

        0.6666666666666666


    Make a prediction

    .. literalinclude:: /../model/transformers/examples/classification/predict.sh

    Output

    .. code-block:: json

        [
            {
                "extra": {},
                "features": {
                    "sentence": "Cats are stupid",
                    "sentiment": 0
                },
                "key": "0",
                "last_updated": "2020-06-12T08:31:45Z",
                "prediction": {
                    "sentiment": {
                        "confidence": 0.153812974691391,
                        "value": 1
                    }
                }
            },
            {
                "extra": {},
                "features": {
                    "sentence": "My office work is awesome",
                    "sentiment": 1
                },
                "key": "1",
                "last_updated": "2020-06-12T08:31:45Z",
                "prediction": {
                    "sentiment": {
                        "confidence": 0.13032104074954987,
                        "value": 1
                    }
                }
            }
        ]

    The model can be trained on large datasets to get the expected
    output. The example shown above is to demonstrate the commandline usage
    of the model.
    """

    CONTEXT = HFClassificationModelContext
    CONFIG = HFClassificationModelConfig
