# Copyright (c) 2019 Adam Karpierz
# SPDX-License-Identifier: MIT

import unittest
import sys
from pathlib import Path

import pyc_wheel
from pyc_wheel import main

here = Path(__file__).resolve().parent
data_dir = here/"data"


class MainTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_main(self):
        # main(["--quiet", str(data_dir/"renumerate-1.3.4-py3-none-any.whl")])
        pass
