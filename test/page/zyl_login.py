# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: zyl_login.py
@time: 2021/11/10 9:24 上午
"""
from selenium.webdriver.common.by import By

from test.common.page import Page
from test.page.zyl_find_title import ZYLFindTitle

class ZYLLoginPage(Page):
    loc_username_input = (By.NAME, 'userName')
    loc_password_input = (By.NAME, 'password')
    loc_click_button = (By.XPATH, '//*[@id="app"]/div/form/button')

    def login(self, username, pwd):
        self.find_element(*self.loc_username_input).send_keys(username)
        self.find_element(*self.loc_password_input).send_keys(pwd)
        self.find_element(*self.loc_click_button).click()


if __name__ == '__main__':
    a = ZYLLoginPage(browser_type='firefox').get('https://zshqadminpre-jy.zuiyouliao.com/app-hq/LoginForDeveloper')
    a.login("admin", "*MWohI9%")
    a.wait(3)

    b = ZYLFindTitle(a).get("https://zshqadminpre-jy.zuiyouliao.com/app-hq/article/ArticleList")
    b.wait(3)
    b.findTitle()
    b.wait(3)
    a.quit()
