# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: process_and_format_data.py.py
@time: 2024/12/20 19:56
"""
import decimal
from datetime import datetime

# 原始数据
data = (1, 1, 'a5124272-1991-ee11-b39a-b955f565009a', '安樾台', 'eb570940-f720-ee11-b399-af5b3b71130e', 'P0818-B0004-R0120',
        'a4124272-1991-ee11-b39a-b955f565009a', '安樾台-昌岗西地块-212地块2#-1001', '吴春燕', '兴业-林晓媛,兴业-周袁仪', 'linxiaoyuan,zhouyuanyi',
        datetime(2023, 12, 2, 0, 0), datetime(2024, 6, 5, 0, 0), datetime(2024, 7, 1, 0, 0), None, datetime(2024, 6, 5, 0, 0),
        decimal.Decimal('7920099.00000000'), 100, datetime(2024, 7, 4, 0, 0), '兴业_安樾台', decimal.Decimal('100.00000000'), '已结佣',
        decimal.Decimal('0.00500000'), decimal.Decimal('39600.50'), decimal.Decimal('0E-8'), decimal.Decimal('100.00000000'),
        decimal.Decimal('39600.50000000'), '工抵佣金标准1', decimal.Decimal('0.0000'), decimal.Decimal('0E-8'), decimal.Decimal('0.000000'),
        datetime(2023, 12, 28, 22, 5, 7), datetime(2024, 7, 9, 16, 24, 37, 67000), datetime(2024, 7, 11, 11, 26, 24, 557000),
        datetime(2024, 7, 11, 11, 31, 38, 487000), datetime(2024, 7, 16, 10, 56, 3, 140000), '正常', decimal.Decimal('0.000000'),
        '江湾和樾项目2023-2024年销售代理合同（兴业）', 'HT-2023-019868', decimal.Decimal('0E-8'), '', '否', '预售', None, decimal.Decimal('39600.50000000'),
        decimal.Decimal('39600.500000'))

# 格式化函数
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

# 使用列表推导式格式化数据
formatted_data = [format_value(val) for val in data]

# 将格式化后的数据按逗号连接起来
formatted_data_str = ', '.join(formatted_data)

# 输出结果
print(f"({formatted_data_str})")


