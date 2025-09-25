# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: getWeiboHot.py
@time: 2021/9/29 11:25 上午
"""
import requests
from lxml import etree
import pandas as pd

url = 'https://s.weibo.com/top/summary?'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
}


def get_url(url):
    try:
        print("1111111111111111")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.ConnectionError as e:
        print(e.args)


def get_hot():
    hotlist = []  # 热搜内容列表，用来保存内容
    hot_url_list = []  # 热搜url列表
    index_list = []  # 索引号列表
    items = get_url(url)  # 调用函数，获取网页response.text
    # print(items)
    html = etree.HTML(items)  # 初始化
    hot_list = html.xpath('/html/body/div/section/ul/li')  # xpath定位，可在浏览器直接复制
    print("22222222222222")
    print(hot_list)
    # 获取热搜内容
    j = 1

    # 遍历所有li列表
    for i in hot_list:
        print("3333333")
        # 获取热搜内容
        hot = i.xpath('./a/span/text()')[0]  # 一直搞不懂[0]是什么意思
        hotlist.append(hot)
        # 获取内容的url
        hot_url = i.xpath('./a/@href')[0]
        hot_url = "https://s.weibo.com/" + str(hot_url)  # 需要组合正确的url，才能打开
        hot_url_list.append(hot_url)

        print(j, hot, hot_url)
        index_list.append(j)
        j = j + 1
        # 保存文件
        file = pd.DataFrame(data={'编号': index_list, '内容': hotlist, 'url': hot_url_list})
        file.to_csv('微博热搜.csv', encoding='utf_8_sig')


# 调用函数，完成爬取！
get_hot()
