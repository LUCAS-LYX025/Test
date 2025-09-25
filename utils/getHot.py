# -*- coding: utf-8 -*-

"""
@author: lucas
@Function: 获取热搜的方法
@file: getHot.py
@time: 2021/9/29 12:16 下午
"""

from lxml import etree

from utils.client import HTTPClient
from utils.voiceBroadcast import voiceBroadcast


def getHot(methods, url, headers, xpath):
    """
    methods: 请求方法
    url: 请求路径
    headers: 请求头
    xpath: 定位的列表路径
    n: 对应着文件格式，0-html,1-csv,2-json,3-xlsx......
    range_num: 排名数量
    """
    html = HTTPClient(url, methods, headers).send()
    html = html.content.decode('utf-8')
    html = etree.HTML(html)
    div = html.xpath(xpath)
    for a in div:
        titles = a.xpath(".//span[@class='t']/text()")
        numbers = a.xpath(".//span[@class='e']/text()")

    b = []
    for i in range(len(titles)):
        list = [f"排行榜第:{i + 1} 今日热搜:{titles[i]},热度为:{numbers[i][:-1]}"]
        #voiceBroadcast(200, '为您播报今天微博热搜:' + list[0])
        b.append([i + 1, titles[i], numbers[i][:-1]])
    return b
