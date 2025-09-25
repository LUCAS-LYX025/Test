# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: mock_server.py
@time: 2021/10/15 3:26 下午
"""
from flask import Flask

app = Flask(__name__)


# 定义路由
@app.route('/api/test')
def get_xml():
    return 'hello world'


if __name__ == '__main__':
    # host：主机ip，配置为0.0.0.0或主机的ip，则其他同网络环境设备就可以访问该server
    # port：端口号，根据实际情况自定义设置，如5000
    app.run(debug=True, host='0.0.0.0', port='2000')