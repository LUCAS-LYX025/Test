# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: panson.py
@time: 2024/7/29 17:17
"""
import requests

# 请求的URL
url = 'http://data.zz.baidu.com/urls'

# 请求参数
params = {
    'site': 'https://www.zhuansushijie.com',
    'token': 'WEYvbWSNuqn2txhh'
}

# 请求头部，指定Content-Type为text/plain
headers = {
    'Content-Type': 'text/plain'
}

# POST请求的数据，这里可以为空，因为text/plain的请求通常不需要请求体内容
data = 'https://www.zhuansushijie.com/newsDetail-393ef7662899410585925be564713d16.html'

# 发送POST请求
response = requests.post(url, params=params, headers=headers, data=data)


# 打印响应内容
print(response.text)

