# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: get_token.py
@time: 2021/10/16 11:20 上午
"""
import os

import yaml

cur = os.path.dirname(os.path.realpath(__file__))
print(cur)


def get_token(yamlName="token.yaml"):
    '''
    从token.yaml读取token值
    :param yamlName: 配置文件名称
    :return: token值
    '''
    p = os.path.join(cur, yamlName)
    print("当前路径：", p)
    f = open(p)
    a = f.read()
    t = yaml.safe_load(a)
    f.close()
    return t["token"]


def get_element(path):
    f = open(path)
    a = f.read()
    t = yaml.safe_load(a)
    f.close()
    return t


if __name__ == "__main__":
    print(get_token())
    path="/Users/leiyuxing/PycharmProjects/TestFramework/test/common/token.yaml"
    t=get_element(path)
    value=t["test"]
