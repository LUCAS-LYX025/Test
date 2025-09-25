import pandas as pd
import re

# 读取TXT文件内容
with open('/Users/leiyuxing/PycharmProjects/TestFramework/test/test_cases.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# 使用正则表达式提取每个测试用例的信息
pattern = re.compile(
    r'### 用例编号：(.*?)\n'
    r'#### 功能：(.*?)\n'
    r'#### 测试目的：(.*?)\n'
    r'#### 前置条件：(.*?)\n'
    r'#### 优先级：(.*?)\n'
    r'#### 操作步骤：(.*?)\n'
    r'#### 输入数据：(.*?)\n'
    r'#### 预期结果：(.*?)\n'
    r'---', re.DOTALL
)

matches = pattern.findall(content)

# 将提取的数据转换为DataFrame
data = []
for match in matches:
    data.append({
        '用例编号': match[0].strip(),
        '功能': match[1].strip(),
        '测试目的': match[2].strip(),
        '前置条件': match[3].strip(),
        '优先级': match[4].strip(),
        '操作步骤': match[5].strip(),
        '输入数据': match[6].strip(),
        '预期结果': match[7].strip()
    })

df = pd.DataFrame(data)

# 将DataFrame写入Excel文件
df.to_excel('test_cases.xlsx', index=False, engine='openpyxl')

print("数据已成功提取并写入Excel文件：test_cases.xlsx")