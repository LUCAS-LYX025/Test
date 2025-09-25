# -*- coding: utf-8 -*-

"""
@author: lucas
@Function: 连接数据库表并统计表属性
@file: connectSql.py
@time: 2021/10/3 4:17 下午
"""

from __future__ import division
import pymysql as MySQL


# 连接数据库
def connectSql(HOST, PORT, USER, PASSWD, DB, CHARSET):
    global conn
    print("开始连接ing")
    try:
        conn = MySQL.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB, charset=CHARSET)
        # charset解决字符乱码
    except:
        print("连接失败!")
    cur = conn.cursor()
    print("连接成功！！！")

    # 数据探查
    # tab=['xxxxxx','bbbbbb']  #指定探索的表名
    tab = []
    if len(tab) != 0:
        pass
    else:
        quary = """show tables; """
        cur.execute(quary)
        ret = cur.fetchall()  # 结果是二层tuple
        for i in ret:
            tab.append(i[0])
        print('表数量： %s' % len(tab))
        print('表list： %s' % tab)

    m = 1
    result = [['表名', '列名', '空值数量', '总数据量', '空值率', '字符类型', '字段长度', '备注', '主键', '权限']]
    for i in tab:
        if m == 100:
            break
            print(i)

        print("第" + str(m) + "个表")
        quary1 = "select count(*)  from  %s" % i
        cur.execute(quary1)
        retsc = cur.fetchall()

        quary2 = '''select  COLUMN_NAME from Information_schema.columns  where table_Name = '%s';''' % i
        cur.execute(quary2)
        ret1 = cur.fetchall()

        for col in ret1:
            ll = []
            quary3 = """select count(*)  from  %s  AS AAA where  AAA.%s  is null; """ % (i, col[0])
            print(quary3)
            cur.execute(quary3)
            ret2 = cur.fetchall()
            quary4 = """SELECT  DATA_TYPE,CHARACTER_MAXIMUM_LENGTH,COLUMN_COMMENT,COLUMN_KEY,PRIVILEGES  from information_schema.COLUMNS where  TABLE_NAME=\'%s\' and COLUMN_NAME=\'%s\';""" % (
                i, col[0])
            print(quary4)
            cur.execute(quary4)
            re4 = cur.fetchall()
            print(re4)
            ll.append(i)
            ll.append(col[0])
            ll.append(ret2[0][0])
            ll.append(retsc[0][0])
            try:
                ll.append(str(round(ret2[0][0] / retsc[0][0], 2)))
            except:
                ll.append(0)
            ll.append(re4[0][0])
            ll.append(re4[0][1])
            ll.append(re4[0][2])
            ll.append(re4[0][3])
            ll.append(re4[0][4])
            result.append(ll)
        m = m + 1
    print(result)
    cur.close()
    conn.close()
    return result


if __name__ == '__main__':
    connectSql("127.0.0.1", "3306", "root", "win8659008", " leiyuxing_project", "utf8")
    # connectSql("192.168.140.130", "3306", "root", "XMcs@2019", "ctp", "utf8")
