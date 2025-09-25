# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: testrd.py
@time: 2025/2/14 20:02
"""
import pandas as pd
import random

# 函数：随机替换公司名称中的几个字符为'*'
def mask_company_name(company_name, num_to_mask):
    # 如果num_to_mask大于公司名称的长度，调整为公司名称长度
    num_to_mask = min(num_to_mask, len(company_name))

    # 将公司名称转换为列表，方便修改
    company_name_list = list(company_name)

    # 随机选择要替换的位置
    positions_to_mask = random.sample(range(len(company_name)), num_to_mask)

    # 用 '*' 替换选中的字符
    for pos in positions_to_mask:
        company_name_list[pos] = '*'

    # 返回修改后的公司名称
    return ''.join(company_name_list)

# 读取Excel文件
def process_excel(input_file, output_file, column_name, num_to_mask):
    # 读取Excel文件
    df = pd.read_excel(input_file)

    # 检查公司名称列是否存在
    if column_name not in df.columns:
        print(f"错误: Excel文件中没有找到列名 '{column_name}'")
        return

    # 在公司名称列中进行打码
    df[column_name] = df[column_name].apply(lambda x: mask_company_name(str(x), num_to_mask))

    # 将修改后的数据保存到新文件
    df.to_excel(output_file, index=False)
    print(f"处理完成，结果已保存到 {output_file}")

# 使用示例
input_file = '公司-福州.xlsx'  # 输入的Excel文件
output_file = 'neww.xlsx'  # 输出的Excel文件
column_name = '公司名称'  # 公司名称所在的列名
num_to_mask = 1  # 随机替换3个字符为星号

# 执行处理
process_excel(input_file, output_file, column_name, num_to_mask)

