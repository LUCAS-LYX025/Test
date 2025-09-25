# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: picture_toWEN.py
@time: 2023/12/19 09:29
"""
from PIL import Image
import pytesseract

# 加载图片
img = Image.open('J3.jpg')

# 将图片转为灰度图像
img = img.convert('L')

# 图片二值化
threshold = 100
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
img = img.point(table, '1')

# 识别图片中的文字
text = pytesseract.image_to_string(img, lang='chi_sim')
print(text)

