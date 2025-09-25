# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: run1.py
@time: 2021/10/26 9:52 上午
"""
from telnetlib import EC
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from run import write_yaml
from test.common.get_token import get_element
driver_path = '/Users/leiyuxing/PycharmProjects/TestFramework/drivers/chromedriver'
driver = webdriver.Chrome(executable_path=driver_path)

driver.get('https://mail.qq.com/')

sleep(2)


driver.maximize_window()


# 定位login_frame

driver.switch_to.frame('ptlogin_iframe')

sleep(2)

driver.find_element_by_xpath('//*[@id="switcher_plogin"]').click()


# 定位账号、密码，并输入

sleep(2)

driver.find_element_by_xpath('//*[@id="u"]').send_keys("674116231@qq.com")

sleep(2)

driver.find_element_by_xpath('//*[@id="p"]').send_keys("lyx8659008")

sleep(2)

# 定位登录按钮

driver.find_element_by_xpath('//*[@id="login_button"]').click()
sleep(5)
data = driver.get_cookies()
cookie_data = [item["name"] + "=" + item["value"] for item in data]
cookie = ';'.join(item for item in cookie_data)
print(cookie)
# 写入cookie
write_yaml(cookie, "cookies")
path = "/Users/leiyuxing/PycharmProjects/TestFramework/test/common/token.yaml"
# 读取cookies
t = get_element(path)
value = t["cookies"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "Cookie": value
}
response = requests.get(
    "https://mail.qq.com/cgi-bin/frame_html?sid=rCv4KxnSPxFmRm4P&r=855a3be78c29fa34d7ff5aa994ce5648", headers=headers)
print(response)
