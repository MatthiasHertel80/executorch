# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import unittest

import torch
from executorch.backends.xnnpack.test.tester import Tester


class TestFloor(unittest.TestCase):
    def setUp(self):
        torch._dynamo.reset()

    class Floor(torch.nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x):
            z = torch.floor(x)
            return z

    def _test_floor(self, inputs):
        (
            Tester(self.Floor(), inputs)
            .export()
            .check_count({"torch.ops.aten.floor.default": 1})
            .to_edge_transform_and_lower()
            .check_count({"torch.ops.higher_order.executorch_call_delegate": 1})
            .check_not(["executorch_exir_dialects_edge__ops_aten_floor_default"])
            .to_executorch()
            .serialize()
            .run_method_and_compare_outputs()
        )

    def test_fp16_floor(self):
        inputs = (
            torch.Tensor(
                [
                    [0.0, 0.1, 0.5, 0.499],
                    [-0.6, -0.4, 100.1, -1000.1],
                ],
            ).to(torch.float16),
        )
        self._test_floor(inputs)

    def test_fp32_floor(self):
        inputs = (
            torch.Tensor(
                [
                    [0.0, 0.1, 0.5, 0.499],
                    [-0.6, -0.4, 100.1, -1000.1],
                ],
            ),
        )
        self._test_floor(inputs)
