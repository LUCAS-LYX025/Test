# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: SqlExcate.py
@time: 2021/10/17 1:09 下午
"""
import pymysql

from utils.config import Config

mysql = Config().get('mysql')
HOST = mysql.get('host')
USER = mysql.get('user')
PASSWD = mysql.get('passwd')
DB = mysql.get('db')

# 打开数据库连接
db = pymysql.connect(host=HOST, user=USER, password=PASSWD, db=DB)
# 使用 cursor()方法获取操作游标
cursor = db.cursor()
# SQL 查询语句
sql = "SELECT * FROM employee WHERE age > %s" % (18)

try:
    # 执行 SQL 语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        id = row[0]
        name = row[1]
        age = row[2]
        sex = row[3]
        grade = row[4]
        # 打印结果
        print("id=%s,name=%s,age=%s,sex=%s,income=%s" % (id, name, age, sex, grade))
except:
    print("Error: unable to fetch data")
# 关闭数据库连接
db.close()
