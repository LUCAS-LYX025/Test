# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_zhifu_statues.py
@time: 2021/10/15 4:16 下午
"""
import unittest
from unittest import mock

from utils import temple


class Test_zhifu_statues(unittest.TestCase):
    '''单元测试用例'''

    def test_01(self):
        '''测试支付成功场景'''
        # mock 一个支付成功的数据
        temple.zhifu = mock.Mock(return_value={"result": "success",
                                               "reason": "null"})
        # 根据支付结果测试页面跳转
        statues = temple.zhifu_statues()
        print(statues)
        self.assertEqual(statues, "支付成功")

    def test_02(self):
        '''测试支付失败场景'''

        # mock 一个支付成功的数据
        temple.zhifu = mock.Mock(return_value={"result": "fail",
                                               "reason": "余额不足"})
        # 根据支付结果测试页面跳转
        statues = temple.zhifu_statues()
        self.assertEqual(statues, "支付失败")

    def test_03(self):
        '''测试支付失败场景--未知错误异常'''
        temple.zhifu = mock.Mock(return_value={"result": "xxx",
                                               "reason": "未知错误异常"})
        statues = temple.zhifu_statues()
        self.assertEqual(statues, "未知错误异常")

    def test_04(self):
        '''测试支付错误场景--服务端返回异常'''
        temple.zhifu = mock.Mock(return_value={"result": "fail"})
        statues = temple.zhifu_statues()
        self.assertEqual(statues, "Error, 服务端返回异常!")


if __name__ == "__main__":
    unittest.main()
