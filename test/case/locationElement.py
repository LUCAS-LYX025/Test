# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: locationElement.py
@time: 2021/10/17 4:50 下午
"""

import sys
from pathlib import Path



sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from selenium import webdriver
from PIL import Image
try:
    from PIL import Image
except ImportError:
    import Image

driver = webdriver.Chrome()
driver.get('http://www.baidu.com')
driver.save_screenshot('baidu.png')
element = driver.find_element_by_id("su")
print(element.location)  # 打印元素坐标
print(element.size)  # 打印元素大小
left = element.location['x']
top = element.location['y']
right = element.location['x'] + element.size['width']
bottom = element.location['y'] + element.size['height']
print(left,top ,right ,bottom )
im = Image.open('baidu.png')

im = im.crop((left, top, right, bottom))
print("2222")
im.save('baidu.png')



