# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: mathfunc.py
@time: 2021/9/6 1:50 下午
"""
from functools import reduce


# 加法
def add(a, b):
    return a + b


# 减法
def minus(a, b):
    return a - b


# 乘法
def multi(a, b):
    return a * b


# 除法
def divide(a, b):
    return a / b


# 阶乘
def reduces(a):
    return reduce(multi, range(1, a + 1))


# 幂的递归
def mi(a, b):
    if b == 0:
        return 1
    else:
        return a * mi(a, b - 1)


if __name__ == '__main__':
    b = reduces(10)
    print(b)
    a = mi(3, 4)
    print(a)
