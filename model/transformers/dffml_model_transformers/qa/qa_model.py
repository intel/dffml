import os
import json
import random
import timeit
import logging
import importlib
from typing import Any, List, Tuple, AsyncIterator

import torch
import numpy as np
from tqdm import tqdm, trange
from torch.utils.data.distributed import DistributedSampler
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler


from dffml.record import Record
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.model.model import ModelContext, Model, ModelNotTrained

from transformers.data.processors.squad import SquadExample, SquadResult
from transformers.data.metrics.squad_metrics import (
    compute_predictions_log_probs,
    compute_predictions_logits,
    squad_evaluate,
)
from transformers import (
    MODEL_FOR_QUESTION_ANSWERING_MAPPING,
    WEIGHTS_NAME,
    AdamW,
    AutoConfig,
    AutoModelForQuestionAnswering,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
    squad_convert_examples_to_features,
)

logger = logging.getLogger(__name__)

MODEL_CONFIG_CLASSES = list(MODEL_FOR_QUESTION_ANSWERING_MAPPING.keys())
MODEL_TYPES = tuple(conf.model_type for conf in MODEL_CONFIG_CLASSES)

@config
class QAModelConfig:
    model_type: str = field(
        "Model type in the list: " + ", ".join(MODEL_TYPES)
    )
    model_name_or_path: str = field(
        "Path to pretrained model or model identifier from huggingface.co/models",
    )
    output_dir: str = field(
        "The output directory where the model checkpoints and predictions will be written.",
    )
    cache_dir: str = field(
        "Where do you want to store the pre-trained models downloaded from s3",
    )
    tokenizer_name: str = field(
        "Pretrained tokenizer name or path if not the same as model_name",
        default=None,
    )
    config_name: str = field(
        "Pretrained config name or path if not the same as model_name",
        default=None,
    )
    null_score_diff_threshold: str = field(
        "If null_score - best_non_null is greater than the threshold predict null.",
        default=0.0,
    )
    max_seq_length: int = field(
        "The maximum total input sequence length after WordPiece tokenization. Sequences longer than this will be truncated, and sequences shorter than this will be padded.",
        default=384,
    )
    doc_stride: int = field(
        "When splitting up a long document into chunks, how much stride to take between chunks.",
        default=128,
    )
    max_query_length: int = field(
        "The maximum number of tokens for the question. Questions longer than this will be truncated to this length",
        default=64,
    )
    do_lower_case: bool = field(
        "Set this flag while using uncased model", default=False
    )
    per_gpu_train_batch_size: int = field(
        "Batch size per GPU/CPU for training", default=8
    )
    per_gpu_eval_batch_size: int = field(
        "Batch size per GPU/CPU for evaluation", default=8
    )
    learning_rate: float = field(
        "The initial learning rate for Adam", default=5e-5
    )
    gradient_accumulation_steps: int = field(
        "Number of updates steps to accumulate before performing a backward/update pass",
        default=1,
    )
    weight_decay: float = field("Weight decay if we apply some.", default=0.0)
    adam_epsilon: float = field("Epsilon for Adam optimizer", default=1e-8)
    max_grad_norm: float = field("Max gradient norm.", default=1.0)
    num_train_epochs: float = field(
        "Total number of training epoches to perform", default=1.0
    )
    max_steps: int = field(
        "If > 0: set total number of training steps to perform. Override num_train_epochs.",
        default=-1,
    )
    warmup_steps: int = field("Linear warmup over warmup_steps.", default=0)
    n_best_size: int = field(
        "The total number of n-best predictions to generate", default=20
    )
    max_answer_length: int = field(
        "The maximum length of an answer that can be generated. This is needed because the start and end predictions are not conditioned on one another.",
        default=30,
    )
    lang_id: int = field(
        "language id of input for language-specific xlm models (see tokenization_xlm.PRETRAINED_INIT_CONFIGURATION)",
        default=0,
    )
    logging_steps: int = field("Log every X updates steps.", default=500)
    save_steps: int = field(
        "Save checkpoint every X update steps", default=500
    )
    no_cuda: bool = field(
        "Whether not to use CUDA when available", default=False
    )
    overwrite_output_dir: bool = field(
        "Overwrite the content of the output directory", default=False
    )
    seed: int = field("random seed for initialization", default=2020)
    local_rank: int = field(
        "local_rank for distributed training on gpus", default=-1
    )
    fp16: int = field(
        "Whether to use 16-bit (mixed) precision (through NVIDIA apex) insted of 32-bit",
        default=False,
    )
    fp16_opt_level: str = field(
        "For fp16: Apex AMP optimization level selected in ['O0', 'O1', 'O2', and 'O3']. See details at https://nvidia.github.io/apex/amp.html",
        default="O1",
    )
    threads: int = field(
        "Multiple threads for converting example to features", default=1
    )

    def __post_init__(self):
        if self.doc_stride >= self.max_seq_length - self.max_query_length:
            logger.warning(
                "WARNING - You've set a doc stride which may be superior to the document length in some "
                "examples. This could result in errors when building features from the examples. Please reduce the doc "
                "stride or increase the maximum length to ensure the features are correctly built."
            )
        if self.local_rank == -1 or self.no_cuda:
            device = torch.device(
                "cuda"
                if torch.cuda.is_available() and not self.no_cuda
                else "cpu"
            )
            self.n_gpu = 0 if self.no_cuda else torch.cuda.device_count()
        else:
            torch.cuda.set_device(self.local_rank)
            device = torch.device("cuda", self.local_rank)
            torch.distributed.init_process_group(backend="nccl")
            self.n_gpu = 1
        self.device = device
        set_seed(self.seed, self.n_gpu)

        if self.local_rank not in [-1, 0]:
            torch.distributed.barrier()

        self.model_type = self.model_type.lower()

