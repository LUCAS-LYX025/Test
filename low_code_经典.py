# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: run3.py
@time: 2023/12/11 14:35
"""

from time import sleep

from selenium import webdriver

driver_path = '/Users/leiyuxing/PycharmProjects/TestFramework/drivers/chromedriver'
driver = webdriver.Chrome(executable_path=driver_path)
# 请求路径
driver.get('https://lcptest4.zuiyouliao.com/login')
sleep(2)
# 放大窗口
driver.maximize_window()
# 输入账号
driver.find_element_by_css_selector('#pane-account input[type="text"]').send_keys("13950553595")
sleep(2)
# 输入密码
driver.find_element_by_css_selector('input[type="password"]').send_keys("a123456")
sleep(2)
# 点击登录按钮
driver.find_element_by_xpath('//*[@id="popContainer"]/div/div/div/div[2]/div/div[2]/button').click()
sleep(2)
# 进入test12应用
driver.find_element_by_xpath('//*[@id="popContainer"]/div/div/div/div[2]/div[2]/div[4]/div[2]').click()
sleep(2)
# 进入表单
driver.find_element_by_xpath(
    '//*[@id="popContainer"]/div/section/section/section/aside/div[3]/div[1]/div/ul/div[2]/div[1]/div[2]/span').click()
sleep(2)
data = ['a']
for item in data:
    # 点击新建数据
    driver.find_element_by_xpath(
        '//*[@id="popContainer"]/div/section/section/section/section/div/div[1]/div[2]/div[1]/div[2]/button').click()
    sleep(2)
    # 单行文本输入值
    driver.find_element_by_xpath('//*[@id="fd_p1jwww9knq8"]').send_keys(item)
    sleep(2)

    # 点击提交按钮
    driver.find_element_by_xpath(
        '/html/body/div[3]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/button[3]').click()
    sleep(2)

# 关闭浏览器
driver.quit()
