# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: get_it_execution.py
@time: 2021/10/16 10:45 上午
"""
import requests
from lxml import etree
import urllib3

urllib3.disable_warnings()

s = requests.session()


def get_it_execution():
    result = {}
    loginurl = "https://account.chsi.com.cn/passport/login"
    h1 = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }
    s.headers.update(h1)
    r = s.get(loginurl, verify=False)
    dom = etree.HTML(r.content.decode("utf-8"))

    try:
        result["lt"] = dom.xpath('//input[@name="lt"]')[0].get("value")
        result["execution"] = dom.xpath('//input[@name="execution"]')[0].get("value")
        print(result)
    except:
        print("lt、execution参数获取失败！")
    return result


def login_xuexin(result, user='13812348888', psw='123456'):
    loginurl = "https://account.chsi.com.cn/passport/login"
    h2 = {
        "Referer": loginurl,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Origin": "https://account.chsi.com.cn",
        "Content-Length": "4157",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "username": user,
        "password": psw,
        "rememberMe": "true",
        "lt": result["lt"],
        "execution": result["execution"],
        "_eventId": "submit"
    }
    s.headers.update(h2)
    r4 = s.post(loginurl, data=body, verify=False)
    print(r4.text)


if __name__ == "__main__":
    result = get_it_execution()
    login_xuexin(result, user='13950553595', psw='Win8659008')
