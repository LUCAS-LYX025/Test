# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: run.py
@time: 2021/10/16 11:37 上午
"""
import unittest
import os
import yaml

from test.common.get_token import get_element
from utils.HTMLTestRunner import HTMLTestRunner

import requests, json

from utils.config import Config
from utils.mail import Email

curpath = os.path.dirname(os.path.realpath(__file__))


def login(user='lucas', psw='123456'):
    '''
    先执行登录，传账号和密码两个参数
    '''
    url = "http://localhost:3000/api/login"
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    request_param = {
        "user": user,
        "psw": psw
    }
    response = requests.post(url, data=json.dumps(request_param), headers=headers)
    # 返回JSON中data数据的token
    # token = "xxxxxxxxx"  # 登录后获取到的token值
    print("哈哈哈",response.json()['code'])
    return response.json()['entity']['token']


def write_yaml(value, key):
    '''
    把获取到的token值写入到yaml文件
    :param value:
    :return:
    '''
    ypath = os.path.join(curpath, "test", "common", "token.yaml")
    print("路径：", ypath)
    # 需写入的内容
    t = get_element(ypath)
    print(t)
    t[key] = value
    # 写入到yaml文件
    with open(ypath, 'w', encoding='utf-8', ) as f:
        # sort_keys=False只修改某个值，而不改变顺序
        yaml.dump(t, f, encoding='utf-8', allow_unicode=True, sort_keys=False)


def all_case(rule="test_zhifu_*.py"):
    '''加载所有的测试用例'''
    case_path = os.path.join(curpath, "test", "case")
    print(case_path)
    # 定义discover方法的参数
    discover = unittest.defaultTestLoader.discover(case_path,
                                                   pattern=rule,
                                                   top_level_dir=None)
    return discover


def run_case(all_case, reportName="report"):
    '''
    执行所有的用例, 并把结果写入HTML测试报告
    '''
    # /Users/leiyuxing/PycharmProjects/TestFramework/report
    report_path = os.path.join(curpath, reportName)  # 用例文件夹
    # 如果不存在这个report文件夹，就自动创建一个
    if not os.path.exists(report_path): os.mkdir(report_path)
    report_abspath = os.path.join(report_path, "result.html")
    print("report path:%s" % report_abspath)
    fp = open(report_abspath, "w")
    runner = HTMLTestRunner(stream=fp,
                            verbosity=2,
                            title=u'自动化测试报告,测试结果如下：',
                            description=u'用例执行情况：')

    # 调用add_case函数返回值
    runner.run(all_case)
    fp.close()
    return report_abspath


def send_report(report_abspath):
    mail = Config().get('mail')
    e = Email(title=mail.get('title'),
              message=mail.get('message'),
              receiver=mail.get('receiver'),
              server=mail.get('server'),
              sender=mail.get('sender'),
              password=mail.get('password'),
              path=report_abspath
              )
    e.send()


if __name__ == "__main__":
    # 登录获取token
    token = login(user='lucas', psw='123456')
    print(token)
    # 写入yaml文件
    write_yaml(token, "token")
    # 加载用例
    allcases = all_case()
    # 加载完用例后写入报告
    report_abspath = run_case(allcases)
    # 发送邮件
    # send_report(report_abspath)
