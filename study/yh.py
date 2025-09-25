# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: yh.py
@time: 2024/12/21 10:29
"""

import os
import logging
from contextlib import closing
import pymssql
from dataphin import hivec
import decimal
from datetime import datetime

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库连接配置从环境变量读取
db_config = {
    'server': os.getenv('DB_SERVER'),  # 数据库实例的地址
    'database': os.getenv('DB_DATABASE'),  # 数据库名称
    'user': os.getenv('DB_USER'),  # 数据库用户名
    'password': os.getenv('DB_PASSWORD'),  # 数据库密码
}

# 存储过程名称
stored_procedure_name = os.getenv('STORED_PROCEDURE_NAME')

# CompanyCode组织编码参数变量
params = ['guijiao', 'bei_fang', 'hua_dong', 'wan_dong', 'hua_zhong']

# 输出字段
columns = os.getenv('COLUMNS')

# hive项目空间名称
v_project = os.getenv('V_PROJECT')

# 临时表名称
temp_table_name = os.getenv('TEMP_TABLE_NAME')


# 格式化函数,用于格式化输出参数
def format_value(val):
    if val is None:
        return "''"  # 将 None 转为空字符串 ''
    elif isinstance(val, str):
        return f"'{val}'"  # 对字符串加上单引号
    elif isinstance(val, datetime):
        return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"  # 日期格式化为字符串并加上单引号
    elif isinstance(val, decimal.Decimal):
        return f"'{val}'"  # 对 Decimal 类型加上单引号
    else:
        return str(val)  # 对其他类型直接转为字符串


# 调用存储过程并返回结果
def call_stored_procedure(param):
    try:
        with closing(pymssql.connect(**db_config)) as connection:
            with connection.cursor() as cursor:
                # 使用参数化查询避免 SQL 注入
                call_sql = f"exec {stored_procedure_name} @page=1,@limit=1,@CompanyCode=%s,@Fjprojguid='',@PartnerId='',@RoomInfo='',@Ywy='',@CstNameList='',@StartTime='',@EndTime='',@QyStartTime='',@QyEndTime='',@IsJY='',@UserID=99999,@UserAd='yxsc_xn_user',@DataType='',@IsTF='',@ContractName='' "
                cursor.execute(call_sql, (param,))

                # 获取第一个结果集（总行数）
                total_rows = cursor.fetchall()[0]
                logging.info(f"Total Count: {total_rows}")

                # 切换到下一个结果集（数据表）
                data = cursor.fetchall()
                return data

    except Exception as e:
        logging.error("连接失败: %s", e)
        return None


def insert_table(data_set):
    if not data_set:
        logging.warning("存储过程无数据返回.")
        return

    formatted_data_list = []
    for row in data_set:
        # 格式化结果集输出字段
        formatted_data = [format_value(val) for val in row[2:]]
        # 将格式化后的数据按逗号连接起来
        formatted_data_str = ', '.join(formatted_data)
        formatted_data_list.append(f"({formatted_data_str})")

    sql_statement_1 = f"INSERT INTO {v_project}.{temp_table_name}({columns}) VALUES " + ", ".join(formatted_data_list)

    try:
        hivec.execute(sql_statement_1)
    except Exception as e:
        logging.error(f"写入失败: {e}")


if __name__ == "__main__":
    for param in params:
        # 调用存储过程
        data_set = call_stored_procedure(param)
        if data_set:
            # 写入中间表
            insert_table(data_set)
