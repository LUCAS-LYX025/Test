# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: TestMathFunc.py
@time: 2021/9/6 1:39 下午
"""

import unittest

from utils.mathfunc import *



class TestMathFunc(unittest.TestCase):
    """Test mathfuc.py"""

    @classmethod
    def setUpClass(cls):
        print("This setUpClass() method only called once.")

    @classmethod
    def tearDownClass(cls):
        print("This tearDownClass() method only called once too.")

    # @unittest.skip("I don't want to run this case.")
    def test_add(self):
        """Test method add(a, b)"""
        self.skipTest('Do not run this.')
        print("add")
        self.assertEqual(3, add(1, 2))
        self.assertNotEqual(3, add(2, 2))

    def test_minus(self):
        """Test method minus(a, b)"""
        print("minus")
        self.assertEqual(1, minus(3, 2))

    def test_multi(self):
        """Test method multi(a, b)"""
        print("multi")
        self.assertEqual(6, multi(2, 3))

    def test_divide(self):
        """Test method divide(a, b)"""
        print("divide")
        self.assertEqual(2, divide(6, 3))
        self.assertEqual(2.5, divide(5, 2))

