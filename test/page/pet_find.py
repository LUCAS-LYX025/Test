# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: pet_find.py
@time: 2021/10/27 1:13 下午
"""
# //*[@id="app"]/div/div[2]/div[2]/div[1]/div/ul/div[2]/li/div
from selenium.webdriver.common.by import By

from test.common.page import Page


class PetFindPage(Page):
    loc_palace_manage = (By.CLASS_NAME, 'el-submenu__title')
    loc_palace_audit = (By.CLASS_NAME, 'el-menu-item')

    def findpet(self):
        self.find_element(*self.loc_palace_manage).click()
        self.find_element(*self.loc_palace_audit).click()
