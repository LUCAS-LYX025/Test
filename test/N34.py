# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: N34.py
@time: 2025/2/14 20:39
"""
import pandas as pd
import random
import re


# 判断地区词是否需要跳过
def is_preferential_word(word):
    preferential_words = ['福建', '福州']  # 可根据需要扩展更多地区词
    return word in preferential_words


# 函数：随机替换公司名称中的几个字符为'*'，并避免打码“有限公司”和地区词
def mask_company_name(company_name, num_to_mask):
    # 先处理“有限公司”的部分
    company_name = re.sub(r"有限公司", "*有限公司", company_name)

    # 对其他部分进行打码，首先提取地区词并跳过它们
    words = re.split(r'([^\u4e00-\u9fa5])', company_name)  # 根据非中文字符拆分
    maskable_positions = []

    for idx, word in enumerate(words):
        if word and not is_preferential_word(word) and word != "*":  # 排除地区词和已打码的部分
            maskable_positions.append(idx)

    # 随机选择要替换的位置
    num_to_mask = min(num_to_mask, len(maskable_positions))  # 避免打码的数量超过可替换的位置
    positions_to_mask = random.sample(maskable_positions, num_to_mask)

    # 用 '*' 替换选中的字符
    for pos in positions_to_mask:
        words[pos] = '*' * len(words[pos])  # 替换该部分为星号

    # 返回修改后的公司名称
    return ''.join(words)


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
num_to_mask = 1  # 随机替换1个字符为星号

# 执行处理
process_excel(input_file, output_file, column_name, num_to_mask)

