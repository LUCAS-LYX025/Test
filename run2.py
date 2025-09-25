# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: run2.py
@time: 2021/10/26 3:31 下午
"""
import json
from time import sleep
import requests
from selenium import webdriver

from run import write_yaml
from test.common.get_token import get_element

driver = webdriver.Firefox()
driver.get('https://petoperate.101el.com/login')

driver.find_element_by_name("username").send_keys("wangkai")
sleep(2)
driver.find_element_by_name("password").send_keys("wk2021")
sleep(2)
driver.find_element_by_name("captcha").send_keys("0000")
sleep(2)
driver.find_element_by_xpath('//*[@id="app"]/div/form/button').click()
data = driver.get_cookies()
print(data)
cookie_data = [item["name"] + "=" + item["value"] for item in data]
cookie = ';'.join(item for item in cookie_data)
print(cookie)

