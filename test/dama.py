import pandas as pd
import random


# 判断地区词是否需要跳过
def is_preferential_word(word):
    preferential_words = ['福建', '福州']  # 可根据需要扩展更多地区词
    return word in preferential_words


# 函数：随机替换公司名称中的几个字符为'*'，并避免打码“有限公司”和地区词
def mask_company_name(company_name, num_to_mask):
    # 如果公司名称包含"有限公司"或地区词，先将这些部分标记出来
    if "有限公司" in company_name:
        part_before = company_name.split("有限公司")[0]  # "有限公司"前的部分
        part_after = "有限公司"  # "有限公司"本身
    else:
        part_before = company_name
        part_after = ""

    # 确定打码部分
    company_name_list = list(part_before)
    maskable_positions = [i for i in range(len(company_name_list)) if company_name_list[i] != '*']

    # 在不包括地区词的情况下进行打码
    for i, word in enumerate(company_name_list):
        if is_preferential_word(word):
            maskable_positions.remove(i)  # 跳过地区词位置

    # 随机选择要替换的位置
    num_to_mask = min(num_to_mask, len(maskable_positions))  # 避免打码的数量超过可替换的位置
    positions_to_mask = random.sample(maskable_positions, num_to_mask)

    # 用 '*' 替换选中的字符
    for pos in positions_to_mask:
        company_name_list[pos] = '*'

    # 返回修改后的公司名称
    masked_part_before = ''.join(company_name_list) + part_after
    return masked_part_before


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
input_file = '公司.xlsx'  # 输入的Excel文件
output_file = 'neww.xlsx'  # 输出的Excel文件
column_name = '公司名称'  # 公司名称所在的列名
num_to_mask = 1  # 随机替换1个字符为星号

# 执行处理
process_excel(input_file, output_file, column_name, num_to_mask)
