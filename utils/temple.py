# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: temple.py.py
@time: 2021/10/15 3:54 下午
"""


def zhifu():
    '''
    假设这里是一个支付的功能,未开发完 支付成功返回:{"result": "success", "reason":"null"}
    支付失败返回:{"result": "fail", "reason":"余额不足"} reason 返回失败原因
    '''
    pass


def zhifu_statues():
    '''根据支付的结果 success or fail，判断跳转到对应页面'''
    result = zhifu()
    print(result)
    try:
        if result["result"] == "success":
            return "支付成功"
        elif result["result"] == "fail":
            print("失败原因:%s" % result["reason"])
            return "支付失败"
        else:
            return "未知错误异常"
    except:
        return "Error, 服务端返回异常!"
