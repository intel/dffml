import unittest

from dffml.util.testing.docs import run_doctest


def bad_func():
    """
    >>> bad_func()
    True
    """
    return False


def good_func():
    """
    >>> good_func()
    True
    """
    return True


class TestDocs(unittest.TestCase):
    def test_run_doctest_bad(self):
        with self.assertRaisesRegex(Exception, "Failed example:"):
            run_doctest(bad_func, state={"globs": globals()})

    def test_run_doctest_good(self):
        run_doctest(good_func, state={"globs": globals()})
