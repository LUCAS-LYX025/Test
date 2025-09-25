# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: pet_login.py
@time: 2021/10/26 4:01 下午
"""

from selenium.webdriver.common.by import By

from test.common.browser import Browser
from test.common.page import Page
from test.page.pet_find import PetFindPage
from utils.config import Config


class PetLoginPage(Page):
    loc_username_input = (By.NAME, 'username')
    loc_password_input = (By.NAME, 'password')
    loc_captcha_input = (By.NAME, 'captcha')
    loc_click_button = (By.XPATH, '//*[@id="app"]/div/form/button')

    def login(self, username, pwd, captcha):
        self.find_element(*self.loc_username_input).send_keys(username)
        self.find_element(*self.loc_password_input).send_keys(pwd)
        self.find_element(*self.loc_captcha_input).send_keys(captcha)
        self.find_element(*self.loc_click_button).click()


if __name__ == '__main__':
    screenshot = Config().get('screenshot')
    is_open_1 = screenshot.get('is_highlight_ele_screenshot')
    is_open_2 = screenshot.get('is_screenshot_ele')
    c = PetLoginPage.loc_username_input
    a = PetLoginPage(browser_type='firefox').get('https://petoperate.101el.com/login')
    #element = a.find_element(*c)
    #print(element)
    # print(is_open_1, is_open_2)
    # a.highlight(element, 'username', is_open_1, is_open_2)
    a.login("wangkai", "wk2021", "0000")
    cookie = a.get_cookies()
    print("登录用的", cookie)
    a.wait(2)
    #PetFindPage(a).get("https://petoperate.101el.com/dashboard")
    b=PetLoginPage(a).get("https://petoperate.101el.com/statistics/operationData")
    b.wait(3)
    PetLoginPage().quit()
    PetFindPage(a).quit()
