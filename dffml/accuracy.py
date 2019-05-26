# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
class Accuracy(float):
    def __str__(self):
        return "%.02f" % (float(self) * 100.0)
