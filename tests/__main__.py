# Copyright (c) 2019-2020 Adam Karpierz
# Licensed under the MIT License
# https://opensource.org/licenses/MIT

import unittest
import sys

from . import test_dir, top_dir


def main(argv=sys.argv):
    print("Running tests", "\n", file=sys.stderr)
    tests = unittest.defaultTestLoader.discover(start_dir=test_dir,
                                                top_level_dir=top_dir)
    result = unittest.TextTestRunner(verbosity=1).run(tests)
    return 0 if result.wasSuccessful() else 1


if __name__.rpartition(".")[-1] == "__main__":
    sys.exit(main())
