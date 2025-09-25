# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: baidu_main_page.py
@time: 2021/9/13 11:08 上午
"""
from selenium.webdriver.common.by import By
from test.common.page import Page


class BaiDuMainPage(Page):
    loc_search_input = (By.ID, 'kw')
    loc_search_button = (By.ID, 'su')

    def search(self, kw):
        """搜索功能"""
        self.find_element(*self.loc_search_input).send_keys(kw)
        self.find_element(*self.loc_search_button).click()


if __name__ == '__main__':
    loc_search_input = (By.ID, 'kw')
    print(loc_search_input)
