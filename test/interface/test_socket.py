# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_socket.py
@time: 2021/9/24 11:37 上午
"""

from utils.client import TCPClient
import unittest
from utils.config import Config
from utils.extractor import JMESPathExtractor

je = JMESPathExtractor()


class TestAdd(unittest.TestCase):

    def setUp(self):
        socket=Config().get('socket')
        ip = socket.get('ip')
        port = socket.get('port')
        self.client = TCPClient(ip, port)

    def tearDown(self):
        self.client.close()

    def test_add(self):
        data = {
            'action': 'add',
            'params': {'a': 1, 'b': 2}
        }
        res = self.client.send(data, dtype='json')
        self.assertEqual(je.extract('result', res), 3)
        self.assertEqual(je.extract('action', res), 'add')

    def test_wrong_action(self):
        data = {
            'action': 'sub',
            'params': {'a': 1, 'b': 2}
        }
        res = self.client.send(data, dtype='json')
        self.assertEqual(je.extract('code', res), -2)
        self.assertEqual(je.extract('message', res), 'Wrong Action')

    def test_wrong_data(self):
        data = 'xxxxx'
        res = self.client.send(data)
        self.assertEqual(je.extract('code', res), -1)
        self.assertEqual(je.extract('message', res), 'Data Error')


if __name__ == '__main__':
    unittest.main(verbosity=2)
