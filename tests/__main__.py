# Copyright (c) 2019-2019 Adam Karpierz
# Licensed under the MIT License
# https://opensource.org/licenses/MIT

import unittest, sys
from . import test_dir, top_dir
tests = unittest.defaultTestLoader.discover(start_dir=test_dir,
                                            top_level_dir=top_dir)
result = unittest.TextTestRunner(verbosity=1).run(tests)
sys.exit(0 if result.wasSuccessful() else 1)
