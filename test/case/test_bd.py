# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_bd.py
@time: 2025/1/10 14:21
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time



def selenium_search():
    # 创建 WebDriver 实例
    driver = webdriver.Chrome('/Users/leiyuxing/PycharmProjects/TestFramework/drivers/chromedriver')  # 确保已安装 Chrome 驱动程序

    # 打开百度首页
    driver.get('https://www.baidu.com/')

    # 找到搜索框并输入搜索内容
    input_box = driver.find_element(By.ID, 'kw')  # 获取输入框 (ID: kw)
    # 打印输入框的值
    input_box.send_keys('SpiderFlow')  # 输入要搜索的内容
    # 找到搜索按钮并点击
    search_button = driver.find_element(By.ID, 'su')  # 获取搜索按钮 (ID: su)
    search_button.click()  # 点击搜索按钮

    # 等待页面加载
    time.sleep(3)  # 等待 3 秒

    # 打印当前页面标题
    print(driver.title)

    # 关闭浏览器
    driver.quit()

# 调用函数进行搜索操作
selenium_search()

