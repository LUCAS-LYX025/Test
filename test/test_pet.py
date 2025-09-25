# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_pet.py
@time: 2021/11/3 11:33 上午
"""
from test.page.pet_find import PetFindPage
from test.page.pet_login import PetLoginPage

c = PetLoginPage.loc_username_input
a = PetLoginPage(browser_type='firefox').get('https://petoperate.101el.com/login')
a.login("wangkai", "wk2021", "0000")
a.wait(2)
PetFindPage(a).get("https://petoperate.101el.com/dashboard").findpet()
PetLoginPage().quit()
PetFindPage(a).quit()
