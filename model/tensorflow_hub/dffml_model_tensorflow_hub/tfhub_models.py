# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""

import abc
import inspect
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple, Type
import os
from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.accuracy import Accuracy
from dffml.model.model import ModelConfig, ModelContext, Model
from dffml.util.entrypoint import entrypoint
from dffml.base import BaseConfig, config, field
from dffml.feature.feature import Feature, Features
from dffml_model_tensorflow.dnnc import TensorflowModelContext
import tensorflow as tf
import numpy as np
import tensorflow_hub as hub
import pandas as pd
from tensorflow.keras import backend as K
from dffml_model_tensorflow_hub.tfhub_utils import FullTokenizer


def bert_tokenizer(text, max_seq_length, vocab, do_lower_case=False):

    tokenizer = FullTokenizer(vocab, do_lower_case)
    input_ids = []
    input_masks = []
    segment_ids = []
    tokens = ["[CLS]"]
    for line in text:
        tokens = (["[CLS]"] + tokenizer.tokenize(str(line)))[
            : max_seq_length - 1
        ] + ["[SEP]"]
        zero_pad = [0] * (max_seq_length - len(tokens))

        input_id = tokenizer.convert_tokens_to_ids(tokens)
        input_mask = [1] * len(input_id) + zero_pad
        input_id = input_id + zero_pad
        segment_id = [0] * len(tokens) + zero_pad

        input_ids.append(input_id)
        input_masks.append(input_mask)
        segment_ids.append(segment_id)
    return [
        np.array(input_ids, dtype=np.int32),
        np.array(input_masks, dtype=np.int32),
        np.array(segment_ids, dtype=np.int32),
    ]


class BertModel(object):
    def __init__(self, config, **kwargs):
        # super().__init__(config)
        self.config = config
        self.model_path = config.model_path
        self.trainable = config.trainable
        self.mainLayer = hub.KerasLayer(
            self.model_path, trainable=self.trainable, **kwargs
        )
        self.vocab_file = (
            self.mainLayer.resolved_object.vocab_file.asset_path.numpy()
        )
        self.do_lower_case = (
            self.mainLayer.resolved_object.do_lower_case.numpy()
        )


class BertClassifier(BertModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        # self.bert = BertModel(config)

    def load_model(self):

        input_word_ids = tf.keras.layers.Input(
            shape=(self.config.max_seq_length,),
            dtype=tf.int32,
            name="input_word_ids",
        )
        input_mask = tf.keras.layers.Input(
            shape=(self.config.max_seq_length,),
            dtype=tf.int32,
            name="input_mask",
        )
        segment_ids = tf.keras.layers.Input(
            shape=(self.config.max_seq_length,),
            dtype=tf.int32,
            name="segment_ids",
        )

        bert_inputs = [input_word_ids, input_mask, segment_ids]
        bert_output, _ = self.mainLayer(bert_inputs)

        # Build classifier
        dense = tf.keras.layers.Dense(256, activation="relu")(bert_output)
        pred = tf.keras.layers.Dense(
            len(self.config.classifications), activation="softmax"
        )(dense)

        model = tf.keras.models.Model(inputs=bert_inputs, outputs=pred)
        return model


class EmbeddingModel(object):
    def __init__(self, config, **kwargs):
        self.config = config
        self.model_path = config.model_path
        self.trainable = config.trainable
        self.mainLayer = hub.KerasLayer(
            self.model_path,
            dtype=tf.string,
            trainable=self.trainable,
            input_shape=[],
            **kwargs,
        )


class NnlmClassifier(EmbeddingModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def load_model(self):

        embed_layer = self.mainLayer
        # Build classifier
        model = tf.keras.Sequential()
        model.add(embed_layer)
        model.add(tf.keras.layers.Dense(16, activation="relu"))
        model.add(
            tf.keras.layers.Dense(
                len(self.config.classifications), activation="softmax"
            )
        )
        return model
