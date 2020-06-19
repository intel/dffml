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


def set_seed(seed, n_gpu):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(seed)


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


class QAModelContext(ModelContext):
    def __init__(self, parent, **kwconfig):
        super().__init__(parent)
        self.config = AutoConfig.from_pretrained(
            self.parent.config.config_name
            if self.parent.config.config_name
            else self.parent.config.model_name_or_path,
            cache_dir=self.parent.config.cache_dir
            if self.parent.config.cache_dir
            else None,
        )

    def to_list(self, tensor):
        return tensor.detach().cpu().tolist()

    async def _preprocess_data(self, sources: Sources):
        all_examples = []
        all_sources = sources.with_features(
            [
                "question",
                "context",
                "answer_text",
                "start_pos_char",
                "title",
                "is_impossible",
                "answers",
            ]
        )
        async for record in all_sources:
            example = SquadExample(
                qas_id=record.key,
                question_text=record.feature("question"),
                context_text=record.feature("context"),
                answer_text=record.feature("answer_text"),
                start_position_character=record.feature("start_pos_char"),
                title=record.feature("title"),
                is_impossible=record.feature("is_impossible"),
                answers=record.feature("answers"),
            )
            all_examples.append(example)
        return all_examples

    async def _custom_train(self, train_dataset):
        """ Train the model """
        if self.parent.config.local_rank in [-1, 0]:
            tb_writer = SummaryWriter()

        self.parent.config.train_batch_size = (
            self.parent.config.per_gpu_train_batch_size
            * max(1, self.parent.config.n_gpu)
        )
        train_sampler = (
            RandomSampler(train_dataset)
            if self.parent.config.local_rank == -1
            else DistributedSampler(train_dataset)
        )
        train_dataloader = DataLoader(
            train_dataset,
            sampler=train_sampler,
            batch_size=self.parent.config.train_batch_size,
        )

        if self.parent.config.max_steps > 0:
            t_total = self.parent.config.max_steps
            self.parent.config.num_train_epochs = (
                self.parent.config.max_steps
                // (
                    len(train_dataloader)
                    // self.parent.config.gradient_accumulation_steps
                )
                + 1
            )
        else:
            t_total = (
                len(train_dataloader)
                // self.parent.config.gradient_accumulation_steps
                * self.parent.config.num_train_epochs
            )

        # Prepare optimizer and schedule (linear warmup and decay)
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p
                    for n, p in self.model.named_parameters()
                    if all(nd not in n for nd in no_decay)
                ],
                "weight_decay": self.parent.config.weight_decay,
            },
            {
                "params": [
                    p
                    for n, p in self.model.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]

        optimizer = AdamW(
            optimizer_grouped_parameters,
            lr=self.parent.config.learning_rate,
            eps=self.parent.config.adam_epsilon,
        )
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.parent.config.warmup_steps,
            num_training_steps=t_total,
        )

        # Check if saved optimizer or scheduler states exist
        if os.path.isfile(
            os.path.join(self.parent.config.model_name_or_path, "optimizer.pt")
        ) and os.path.isfile(
            os.path.join(self.parent.config.model_name_or_path, "scheduler.pt")
        ):
            # Load in optimizer and scheduler states
            optimizer.load_state_dict(
                torch.load(
                    os.path.join(
                        self.parent.config.model_name_or_path, "optimizer.pt"
                    )
                )
            )
            scheduler.load_state_dict(
                torch.load(
                    os.path.join(
                        self.parent.config.model_name_or_path, "scheduler.pt"
                    )
                )
            )

        if self.parent.config.fp16:
            try:
                from apex import amp
            except ImportError:
                raise ImportError(
                    "Please install apex from https://www.github.com/nvidia/apex to use fp16 training."
                )

            self.model, optimizer = amp.initialize(
                self.model,
                optimizer,
                opt_level=self.parent.config.fp16_opt_level,
            )

        # multi-gpu training
        if self.parent.config.n_gpu > 1:
            self.model = torch.nn.DataParallel(self.model)

        # Distributed training
        if self.parent.config.local_rank != -1:
            self.model = torch.nn.parallel.DistributedDataParallel(
                self.model,
                device_ids=[self.parent.config.local_rank],
                output_device=self.parent.config.local_rank,
                find_unused_parameters=True,
            )

        # Train
        logger.info("***** Running training *****")
        logger.info("  Num examples = %d", len(train_dataset))
        logger.info("  Num Epochs = %d", self.parent.config.num_train_epochs)
        logger.info(
            "  Instantaneous batch size per GPU = %d",
            self.parent.config.per_gpu_train_batch_size,
        )
        logger.info(
            "  Total train batch size (w. parallel, distributed & accumulation) = %d",
            self.parent.config.train_batch_size
            * self.parent.config.gradient_accumulation_steps
            * (
                torch.distributed.get_world_size()
                if self.parent.config.local_rank != -1
                else 1
            ),
        )
        logger.info(
            "  Gradient Accumulation steps = %d",
            self.parent.config.gradient_accumulation_steps,
        )
        logger.info("  Total optimization steps = %d", t_total)

        global_step = 1
        epochs_trained = 0
        steps_trained_in_current_epoch = 0
        # Check if continuing training from a checkpoint
        if os.path.exists(self.parent.config.model_name_or_path):
            try:
                # set global_step to gobal_step of last saved checkpoint from model path
                checkpoint_suffix = self.parent.config.model_name_or_path.split(
                    "-"
                )[
                    -1
                ].split(
                    "/"
                )[
                    0
                ]
                global_step = int(checkpoint_suffix)
                epochs_trained = global_step // (
                    len(train_dataloader)
                    // self.parent.config.gradient_accumulation_steps
                )
                steps_trained_in_current_epoch = global_step % (
                    len(train_dataloader)
                    // self.parent.config.gradient_accumulation_steps
                )

                logger.info(
                    "  Continuing training from checkpoint, will skip to saved global_step"
                )
                logger.info(
                    "  Continuing training from epoch %d", epochs_trained
                )
                logger.info(
                    "  Continuing training from global step %d", global_step
                )
                logger.info(
                    "  Will skip the first %d steps in the first epoch",
                    steps_trained_in_current_epoch,
                )
            except ValueError:
                logger.info("  Starting fine-tuning.")

        tr_loss, logging_loss = 0.0, 0.0
        self.model.zero_grad()
        train_iterator = trange(
            epochs_trained,
            int(self.parent.config.num_train_epochs),
            desc="Epoch",
            disable=self.parent.config.local_rank not in [-1, 0],
        )
        set_seed(self.parent.config.seed, self.parent.config.n_gpu)

        for _ in train_iterator:
            epoch_iterator = tqdm(
                train_dataloader,
                desc="Iteration",
                disable=self.parent.config.local_rank not in [-1, 0],
            )
            for step, batch in enumerate(epoch_iterator):

                # Skip past any already trained steps if resuming training
                if steps_trained_in_current_epoch > 0:
                    steps_trained_in_current_epoch -= 1
                    continue

                self.model.train()
                batch = tuple(t.to(self.parent.config.device) for t in batch)

                inputs = {
                    "input_ids": batch[0],
                    "attention_mask": batch[1],
                    "token_type_ids": batch[2],
                    "start_positions": batch[3],
                    "end_positions": batch[4],
                }

                if self.parent.config.model_type in [
                    "xlm",
                    "roberta",
                    "distilbert",
                    "camembert",
                ]:
                    del inputs["token_type_ids"]

                if self.parent.config.model_type in ["xlnet", "xlm"]:
                    inputs.update({"cls_index": batch[5], "p_mask": batch[6]})
                    if hasattr(self.model, "config") and hasattr(
                        self.model.config, "lang2id"
                    ):
                        inputs.update(
                            {
                                "langs": (
                                    torch.ones(
                                        batch[0].shape, dtype=torch.int64
                                    )
                                    * self.parent.config.lang_id
                                ).to(self.parent.config.device)
                            }
                        )

                outputs = self.model(**inputs)
                # model outputs are tuples
                loss = outputs[0]

                if self.parent.config.n_gpu > 1:
                    loss = (
                        loss.mean()
                    )  # average on multi-gpu parallel (not distributed) training
                if self.parent.config.gradient_accumulation_steps > 1:
                    loss = (
                        loss / self.parent.config.gradient_accumulation_steps
                    )

                if self.parent.config.fp16:
                    with amp.scale_loss(loss, optimizer) as scaled_loss:
                        scaled_loss.backward()
                else:
                    loss.backward()

                tr_loss += loss.item()
                if (
                    step + 1
                ) % self.parent.config.gradient_accumulation_steps == 0:
                    if self.parent.config.fp16:
                        torch.nn.utils.clip_grad_norm_(
                            amp.master_params(optimizer),
                            self.parent.config.max_grad_norm,
                        )
                    else:
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(),
                            self.parent.config.max_grad_norm,
                        )

                    optimizer.step()
                    scheduler.step()
                    self.model.zero_grad()
                    global_step += 1

                    # Log metrics
                    if (
                        self.parent.config.local_rank in [-1, 0]
                        and self.parent.config.logging_steps > 0
                        and global_step % self.parent.config.logging_steps == 0
                    ):
                        # Only evaluate when single GPU otherwise metrics may not average well
                        if (
                            self.parent.config.local_rank == -1
                            and self.parent.config.evaluate_during_training
                        ):
                            results = evaluate(
                                self.parent.config, self.model, tokenizer
                            )
                            for key, value in results.items():
                                tb_writer.add_scalar(
                                    "eval_{}".format(key), value, global_step
                                )
                        tb_writer.add_scalar(
                            "lr", scheduler.get_lr()[0], global_step
                        )
                        tb_writer.add_scalar(
                            "loss",
                            (tr_loss - logging_loss)
                            / self.parent.config.logging_steps,
                            global_step,
                        )
                        logging_loss = tr_loss

                    # Save model checkpoint
                    if (
                        self.parent.config.local_rank in [-1, 0]
                        and self.parent.config.save_steps > 0
                        and global_step % self.parent.config.save_steps == 0
                    ):
                        output_dir = os.path.join(
                            self.parent.config.output_dir,
                            "checkpoint-{}".format(global_step),
                        )
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        # Take care of distributed/parallel training
                        model_to_save = (
                            self.model.module
                            if hasattr(self.model, "module")
                            else self.model
                        )
                        model_to_save.save_pretrained(output_dir)
                        self.tokenizer.save_pretrained(output_dir)

                        torch.save(
                            self.parent.config,
                            os.path.join(output_dir, "training_args.bin"),
                        )
                        logger.info(
                            "Saving model checkpoint to %s", output_dir
                        )

                        torch.save(
                            optimizer.state_dict(),
                            os.path.join(output_dir, "optimizer.pt"),
                        )
                        torch.save(
                            scheduler.state_dict(),
                            os.path.join(output_dir, "scheduler.pt"),
                        )
                        logger.info(
                            "Saving optimizer and scheduler states to %s",
                            output_dir,
                        )

                if (
                    self.parent.config.max_steps > 0
                    and global_step > self.parent.config.max_steps
                ):
                    epoch_iterator.close()
                    break
            if (
                self.parent.config.max_steps > 0
                and global_step > self.parent.config.max_steps
            ):
                train_iterator.close()
                break

        if self.parent.config.local_rank in [-1, 0]:
            tb_writer.close()

        return global_step, tr_loss / global_step

    async def train(self, sources: Sources):
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.parent.config.tokenizer_name
            if self.parent.config.tokenizer_name
            else self.parent.config.model_name_or_path,
            do_lower_case=self.parent.config.do_lower_case,
            cache_dir=self.parent.config.cache_dir
            if self.parent.config.cache_dir
            else None,
        )
        self.model = AutoModelForQuestionAnswering.from_pretrained(
            self.parent.config.model_name_or_path,
            from_tf=bool(".ckpt" in self.parent.config.model_name_or_path),
            config=config,
            cache_dir=self.parent.config.cache_dir
            if self.parent.config.cache_dir
            else None,
        )

        if self.parent.config.local_rank == 0:
            # Make sure only the first process in distributed training will download model & vocab
            torch.distributed.barrier()

        self.model.to(self.parent.config.device)

        if self.parent.config.fp16:
            try:
                import apex

                apex.amp.register_half_function(torch, "einsum")
            except ImportError:
                raise ImportError(
                    "Please install apex from https://www.github.com/nvidia/apex to use fp16 training."
                )

        # Training
        train_examples = await self._preprocess_data(sources)
        _, train_dataset = squad_convert_examples_to_features(
            examples=train_examples,
            tokenizer=self.tokenizer,
            max_seq_length=self.parent.config.max_seq_length,
            doc_stride=self.parent.config.doc_stride,
            max_query_length=self.parent.config.max_query_length,
            is_training=True,
            return_dataset="pt",
        )
        global_step, tr_loss = await self._custom_train(train_dataset)
        logger.info(
            " global_step = %s, average loss = %s", global_step, tr_loss
        )

        # Save the trained model and the tokenizer
        if (
            self.parent.config.local_rank == -1
            or torch.distributed.get_rank() == 0
        ):
            # Create output directory if needed
            if not os.path.exists(
                self.parent.config.output_dir
            ) and self.parent.config.local_rank in [-1, 0]:
                os.makedirs(self.parent.config.output_dir)

            logger.info(
                "Saving model checkpoint to %s", self.parent.config.output_dir
            )
            # Save a trained model, configuration and tokenizer using `save_pretrained()`.
            # Take care of distributed/parallel training
            model_to_save = (
                self.model.module
                if hasattr(self.model, "module")
                else self.model
            )
            model_to_save.save_pretrained(self.parent.config.output_dir)
            self.tokenizer.save_pretrained(self.parent.config.output_dir)

            # save training arguments together with the trained model
            torch.save(
                self.parent.config,
                os.path.join(
                    self.parent.config.output_dir, "training_args.bin"
                ),
            )

    async def _custom_accuracy(self, examples, features, dataset, prefix=""):

        if not os.path.exists(
            self.parent.config.output_dir
        ) and self.parent.config.local_rank in [-1, 0]:
            os.makedirs(self.parent.config.output_dir)

        self.parent.config.eval_batch_size = (
            self.parent.config.per_gpu_eval_batch_size
            * max(1, self.parent.config.n_gpu)
        )

        eval_sampler = SequentialSampler(dataset)
        eval_dataloader = DataLoader(
            dataset,
            sampler=eval_sampler,
            batch_size=self.parent.config.eval_batch_size,
        )

        # multi-gpu evaluate
        if self.parent.config.n_gpu > 1 and not isinstance(
            self.model, torch.nn.DataParallel
        ):
            self.model = torch.nn.DataParallel(self.model)

        # Eval
        logger.info("***** Running evaluation {} *****".format(prefix))
        logger.info("  Num examples = %d", len(dataset))
        logger.info("  Batch size = %d", self.parent.config.eval_batch_size)

        all_results = []
        start_time = timeit.default_timer()

        for batch in tqdm(eval_dataloader, desc="Evaluating"):
            self.model.eval()
            batch = tuple(t.to(self.parent.config.device) for t in batch)

            with torch.no_grad():
                inputs = {
                    "input_ids": batch[0],
                    "attention_mask": batch[1],
                    "token_type_ids": batch[2],
                }

                if self.parent.config.model_type in [
                    "xlm",
                    "roberta",
                    "distilbert",
                    "camembert",
                ]:
                    del inputs["token_type_ids"]

                feature_indices = batch[3]

                # XLNet and XLM use more arguments for their predictions
                if self.parent.config.model_type in ["xlnet", "xlm"]:
                    inputs.update({"cls_index": batch[4], "p_mask": batch[5]})
                    # for lang_id-sensitive xlm models
                    if hasattr(self.model, "config") and hasattr(
                        self.model.config, "lang2id"
                    ):
                        inputs.update(
                            {
                                "langs": (
                                    torch.ones(
                                        batch[0].shape, dtype=torch.int64
                                    )
                                    * self.parent.config.lang_id
                                ).to(self.parent.config.device)
                            }
                        )

                outputs = self.model(**inputs)

            for i, feature_index in enumerate(feature_indices):
                eval_feature = features[feature_index.item()]
                unique_id = int(eval_feature.unique_id)

                output = [self.to_list(output[i]) for output in outputs]

                if len(output) >= 5:
                    start_logits = output[0]
                    start_top_index = output[1]
                    end_logits = output[2]
                    end_top_index = output[3]
                    cls_logits = output[4]

                    result = SquadResult(
                        unique_id,
                        start_logits,
                        end_logits,
                        start_top_index=start_top_index,
                        end_top_index=end_top_index,
                        cls_logits=cls_logits,
                    )
                else:
                    start_logits, end_logits = output
                    result = SquadResult(unique_id, start_logits, end_logits)

                all_results.append(result)

        evalTime = timeit.default_timer() - start_time
        logger.info(
            "  Evaluation done in total %f secs (%f sec per example)",
            evalTime,
            evalTime / len(dataset),
        )

        # Compute predictions
        output_prediction_file = os.path.join(
            self.parent.config.output_dir, "predictions_{}.json".format(prefix)
        )
        output_nbest_file = os.path.join(
            self.parent.config.output_dir,
            "nbest_predictions_{}.json".format(prefix),
        )

        # XLNet and XLM use a more complex post-processing procedure
        if self.parent.config.model_type in ["xlnet", "xlm"]:
            start_n_top = (
                self.model.config.start_n_top
                if hasattr(self.model, "config")
                else self.model.module.config.start_n_top
            )
            end_n_top = (
                self.model.config.end_n_top
                if hasattr(self.model, "config")
                else self.model.module.config.end_n_top
            )

            predictions = compute_predictions_log_probs(
                examples,
                features,
                all_results,
                self.parent.config.n_best_size,
                self.parent.config.max_answer_length,
                output_prediction_file,
                output_nbest_file,
                None,
                start_n_top,
                end_n_top,
                False,
                self.tokenizer,
                True,
            )
        else:
            predictions = compute_predictions_logits(
                examples,
                features,
                all_results,
                self.parent.config.n_best_size,
                self.parent.config.max_answer_length,
                self.parent.config.do_lower_case,
                output_prediction_file,
                output_nbest_file,
                None,
                True,
                False,
                self.parent.config.null_score_diff_threshold,
                self.tokenizer,
            )

        return predictions

    async def accuracy(self, sources: Sources):
        if not os.path.isfile(
            os.path.join(self.parent.config.output_dir, "pytorch_model.bin")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.parent.config.output_dir,
            do_lower_case=self.parent.config.do_lower_case,
        )
        eval_examples = await self._preprocess_data(sources)
        features, dataset = squad_convert_examples_to_features(
            examples=eval_examples,
            tokenizer=self.tokenizer,
            max_seq_length=self.parent.config.max_seq_length,
            doc_stride=self.parent.config.doc_stride,
            max_query_length=self.parent.config.max_query_length,
            is_training=False,
            return_dataset="pt",
        )

        results = {}
        if self.parent.config.local_rank in [-1, 0]:
            logger.info(
                "Loading checkpoints saved during training for evaluation"
            )
            self.model = AutoModelForQuestionAnswering.from_pretrained(
                self.parent.config.output_dir
            )
            self.model.to(self.parent.config.device)

            # Evaluate
            predictions = await self._custom_accuracy(
                eval_examples, features, dataset
            )
            results = squad_evaluate(eval_examples, predictions)

        logger.info("Results: {}".format(results))

        # return results
        return Accuracy(results["f1"])
