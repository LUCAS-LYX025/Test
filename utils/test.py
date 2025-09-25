# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test.py
@time: 2021/10/15 1:52 下午
"""
from utils.client import HTTPClient, METHODS

token = 'jinjideleishen1123344'
name = 'lucas'
id = '27'

url = 'http://localhost:3002/api/mockman'
headers = {'token': token}
data = {'name': name, 'id': id}
result = HTTPClient(url, METHODS[1], headers=headers).send(data=data)
print(type(result.json()))
r = result.json()['data']['job']
print(r)
print(result)
