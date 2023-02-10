import unittest

import argparse

from src import _hukamnama
from . import _util

class _BaseTest(_util.BaseTest):
    pass


# class DataTest(_BaseTest):
#     def test_mainline_shabad():
#         ctx = argparse.Namespace(function=_hukamnama.Function.DATAk)
#         _hukamnama.parse()

class FooTest(_BaseTest):
    def test_pass(self):
        self.assertTrue(True)

    # def test_fail(self):
    #     self.assertTrue(False)

    def test_foo(self):
        a = main.foo(1)
        print(a)
        self.assertTrue(a)

    def test_foo2(self):
        a = main.foo(2)
        print(a)
        self.assertFalse(a)
