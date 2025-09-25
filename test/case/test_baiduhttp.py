# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_baiduhttp.py
@time: 2021/9/17 3:46 下午
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.interface.test_baidu_http import TestBaiDuHTTP
from utils.HTMLTestRunner import HTMLTestRunner

from utils.config import REPORT_PATH

if __name__ == '__main__':
    report = REPORT_PATH + '/report.html'
    with open(report, 'w') as f:
        runner = HTMLTestRunner(f, verbosity=2, title='百度', description='接口html报告')
        runner.run(TestBaiDuHTTP('test_baidu_http'))
