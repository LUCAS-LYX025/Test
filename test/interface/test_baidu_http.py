# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_baidu_http.py
@time: 2021/9/17 2:25 下午
"""
import unittest
import warnings

from utils.assertion import assertHTTPCode
from utils.config import Config
from utils.client import HTTPClient
from utils.log import logger


class TestBaiDuHTTP(unittest.TestCase):
    URL = Config().get('URL')

    def setUp(self):
        self.client = HTTPClient(url=self.URL, method='GET')

    def test_baidu_http(self):
        res = self.client.send()
        # 加上这行，谨防报错
        warnings.simplefilter("ignore", ResourceWarning)
        logger.warning(res.text)
        assertHTTPCode(res, [400])
        self.assertIn('百度一下，你就知道', res.text)
