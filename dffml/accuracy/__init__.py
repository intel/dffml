# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Intel Corporation
"""
This the accuracy plugin
"""
from .accuracy import (
    AccuracyConfig,
    AccuracyContext,
    AccuracyScorer,
    InvalidNumberOfFeaturesError,
)
from .mse import MeanSquaredErrorAccuracy
from .clfacc import ClassificationAccuracy
