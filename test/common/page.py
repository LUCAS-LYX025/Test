# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: page.py
@time: 2021/9/10 5:13 下午
"""
from telnetlib import EC
from time import sleep

from numpy import sort
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from test.common.browser import Browser
from utils.log import logger


class Page(Browser):
    # 更多的封装请自己动手...
    def __init__(self, page=None, browser_type='firefox'):
        if page:
            self.driver = page.driver
        else:
            super(Page, self).__init__(browser_type=browser_type)

    @property
    def current_window(self):
        return self.driver.current_window_handle

    @property
    def title(self):
        return self.driver.title

    @property
    def current_url(self):
        return self.driver.current_url

    def get_driver(self):
        return self.driver

    def wait(self, seconds=3):
        sleep(seconds)

    def execute(self, js, *args):
        self.driver.execute_script(js, *args)

    def move_to(self, element):
        ActionChains(self.driver).move_to_element(element).perform()

    def find_element(self, *args):
        return self.driver.find_element(*args)

    def find_elements(self, *args):
        return self.driver.find_elements(*args)

    def switch_to_window(self, partial_url='', partial_title=''):
        """切换窗口
            如果窗口数<3,不需要传入参数，切换到当前窗口外的窗口；
            如果窗口数>=3，则需要传入参数来确定要跳转到哪个窗口
        """
        all_windows = self.driver.window_handles
        if len(all_windows) == 1:
            logger.warning('只有1个window!')
        elif len(all_windows) == 2:
            other_window = all_windows[1 - all_windows.index(self.current_window)]
            self.driver.switch_to.window(other_window)
        else:
            for window in all_windows:
                self.driver.switch_to.window(window)
                if partial_url in self.driver.current_url or partial_title in self.driver.title:
                    break
        logger.debug(self.driver.current_url, self.driver.title)

    def switch_to_frame(self, param):
        self.driver.switch_to.frame(param)

    def switch_to_alert(self):
        return self.driver.switch_to.alert

    def get_cookies(self):
        data = self.driver.get_cookies()
        sleep(3)
        cookie_data = [item["name"] + "=" + item["value"] for item in data]
        cookie = ';'.join(item for item in cookie_data)
        return cookie


if __name__ == '__main__':
    b = [7, 3, 10, 9, 9, 21, 35, 4, 6]
    a = list(set(b))
    for i in range(len(a) - 1):
        for j in range(len(a) - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    print(a)
    c = list(set(b))
    print(c)
    d= list(sort(c))
    print(d)