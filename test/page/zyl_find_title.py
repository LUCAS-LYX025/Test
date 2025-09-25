# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: zyl_find_title.py
@time: 2021/11/10 4:37 下午
"""
from time import sleep

from selenium.webdriver.common.by import By

from test.common.page import Page


class ZYLFindTitle(Page):
    loc_palace_manage = (By.XPATH, '//*[@id="app"]/div/div[2]/section/div/div[2]/div[2]/input')
    loc_palace_audit = (By.XPATH, '//*[@id="app"]/div/div[2]/section/div/div[2]/button[1]')

    def findTitle(self):
        self.find_element(*self.loc_palace_manage).click()
        self.find_element(*self.loc_palace_manage).send_keys("涨到心慌")
        sleep(5)
        self.find_element(*self.loc_palace_audit).click()
