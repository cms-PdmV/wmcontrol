"""This module provides some utilities for unittest.TestCase"""

from functools import wraps


def parametrize(params):
    """Parametrize a TestCase using TestCase.subtest."""

    def decorator(f):
        @wraps(f)
        def wrapped(self):
            for param in params:
                self.setUp()
                with self.subTest(**param):
                    f(self, **param)
                self.tearDown()

        return wrapped

    return decorator