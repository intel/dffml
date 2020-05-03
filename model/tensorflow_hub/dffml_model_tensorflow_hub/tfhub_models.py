# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import importlib

from .tfhub_utils import FullTokenizer


def bert_tokenizer(text, max_seq_length, vocab, do_lower_case=False):
    """
    Convert input text to bert format.
    """
    np = importlib.import_module("numpy")
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


class Embedder:
    def __init__(self, config):
        self.tf = importlib.import_module("tensorflow")
        self.hub = importlib.import_module("tensorflow_hub")
        self.config = config
        self.mainLayer = self._mainLayer()
        self.inputs, self.outputs = self._model()

    def _mainLayer(self):
        mainLayer = self.hub.KerasLayer(
            self.config.model_path, trainable=self.config.trainable
        )
        if self.config.embedType in ["bert"]:
            self.vocab_file = (
                mainLayer.resolved_object.vocab_file.asset_path.numpy()
            )
            self.do_lower_case = (
                mainLayer.resolved_object.do_lower_case.numpy()
            )
        return mainLayer

    def _model(self):
        if self.config.embedType in ["bert"]:
            input_word_ids = self.tf.keras.layers.Input(
                shape=(self.config.max_seq_length,),
                dtype=self.tf.int32,
                name="input_word_ids",
            )
            input_mask = self.tf.keras.layers.Input(
                shape=(self.config.max_seq_length,),
                dtype=self.tf.int32,
                name="input_mask",
            )
            segment_ids = self.tf.keras.layers.Input(
                shape=(self.config.max_seq_length,),
                dtype=self.tf.int32,
                name="segment_ids",
            )

            inputs = [input_word_ids, input_mask, segment_ids]
            outputs, _ = self.mainLayer(inputs)
        else:
            inputs = self.tf.keras.layers.Input(
                shape=[], name="input_text", dtype=self.tf.string
            )
            outputs = self.mainLayer(inputs)
        return inputs, outputs


class ClassificationModel(Embedder):
    def __init__(self, config):
        super().__init__(config)

    def load_model(self):
        outputs = self.outputs
        if self.config.add_layers:
            for layer in self.config.layers:
                outputs = layer(outputs)
        else:
            # default classifier
            outputs = self.tf.keras.layers.Dense(256, activation="relu")(
                outputs
            )
            outputs = self.tf.keras.layers.Dense(
                len(self.config.classifications), activation="softmax"
            )(outputs)

        model = self.tf.keras.models.Model(inputs=self.inputs, outputs=outputs)
        if self.config.embedType == "bert":
            # save vocab_file and `do_lower_case` variable
            model.vocab_file = self.tf.saved_model.Asset(self.vocab_file)
            model.do_lower_case = self.tf.Variable(
                self.do_lower_case, trainable=False
            )
        return model
