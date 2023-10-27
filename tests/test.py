"""
This module groups all the test cases and enables to execute
all of them. Just import the test into the namespace
"""
import os
import sys
import unittest

# Support for Python 2
try:
    from tests.modules.http_client import BaseTest
except ImportError:
    sys.path.append(os.path.join(sys.path[0], 'modules'))
    from http_client import BaseTest

if __name__ == "__main__":
    print("Python version: ", sys.version)
    print("\n")
    unittest.main(verbosity=2)