# Copyright (c) 2019-2021 Adam Karpierz
# Licensed under the MIT License
# https://opensource.org/licenses/MIT

__all__ = ('top_dir', 'test_dir')

import sys, pathlib
sys.dont_write_bytecode = True
test_dir = pathlib.Path(__file__).resolve().parent
top_dir = test_dir.parent
del sys, pathlib
