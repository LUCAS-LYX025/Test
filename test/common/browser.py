# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: browser.py
@time: 2021/9/10 4:53 下午
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import os
from selenium import webdriver
from utils.config import REPORT_PATH, Config, DRIVER_PATH
from PIL import Image

# 可根据需要自行扩展
# 火狐浏览器驱动路径
FIREFOX_PATH = DRIVER_PATH + '/geckodriver'
# 谷歌浏览器驱动路径
CHROMEDRIVER_PATH = DRIVER_PATH + '/chromedriver'

TYPES = {'firefox': webdriver.Firefox, 'chrome': webdriver.Chrome}
EXECUTABLE_PATH = {'firefox': FIREFOX_PATH, 'chrome': CHROMEDRIVER_PATH}
day = time.strftime('%Y%m%d', time.localtime(time.time()))
screenshot_path = REPORT_PATH + '/screenshot_%s' % day
tm = time.strftime('%H%M%S', time.localtime(time.time()))


class UnSupportBrowserTypeError(Exception):
    pass


class Browser(object):
    def __init__(self, browser_type='firefox'):
        self._type = browser_type.lower()
        if self._type in TYPES:
            self.browser = TYPES[self._type]
        else:
            raise UnSupportBrowserTypeError('仅支持%s!' % ', '.join(TYPES.keys()))
        self.driver = self.browser(executable_path=EXECUTABLE_PATH[self._type])

    def get(self, url, maximize_window=True, implicitly_wait=30):
        self.driver.get(url)
        if maximize_window:
            self.driver.maximize_window()
            #self.driver.page_source
        self.driver.implicitly_wait(implicitly_wait)
        return self

    def find(self, locator, timeout=30):
        '''定位元素，参数 locator 是元祖类型, 如("id", "yy")'''
        element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        return element

    # 是否存在元素
    def is_element_exsist2(self, locator):
        try:
            self.find(locator, timeout=30)
            return True
        except:
            return False

    # 截屏
    def screen_shot(self, screen_name):
        self.driver.maximize_window()

        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)
        filename = screenshot_path + '/%s_%s.png' % (screen_name, tm)
        self.driver.save_screenshot(filename)
        return filename

    # 截取元素
    def screenshot_element(self, element, element_name, file_name):
        print("22222222222")
        # 获取初始截屏的分辨率宽度
        width = self.driver.get_window_size().get("width")
        # 获取元素坐标
        left = element.location['x']
        top = element.location['y']
        right = (element.location['x'] + element.size['width'])
        bottom = (element.location['y'] + element.size['height'])
        im = Image.open(file_name)
        # 获取图片宽度
        p = im.size[0]
        # 计算被放大的分辨率倍数
        n = p / width
        print(n)
        # 截取元素坐标
        im = im.crop((left * n, top * n, right * n, bottom * n))
        # 保存截取元素的截图
        print(str(element))
        im.save(screenshot_path + "/" + str(element_name) + '元素.png')

    # 高亮元素
    def highlight(self, element, element_name=None, is_highlight_ele_screenshot=True, is_screenshot_ele=True):
        '''
        :param element: 定位到的元素
        :param element_name: 元素名
        :param is_highlight_ele_screenshot: 是否要带有高亮元素的截屏，默认True是要，Flase是不要
        :param is_screenshot_ele: 是否要截取元素的图，默认True是要，Flase是不要
        :return: 预期的截屏图
        '''

        # 高亮元素
        def apply_style():
            self.driver.execute_script("arguments[0].style.border='6px solid red'", element)

        # 截图
        if is_highlight_ele_screenshot:
            try:
                # 打开浏览器前的全屏截图
                self.screen_shot(element_name + '_before')
                apply_style()
                # 高亮元素后的全屏截图
                file_name = self.screen_shot(str(element_name) + '_after')
                print(str(element_name), file_name)
                if is_screenshot_ele:
                    print("1111111111")
                    # 截取的高亮元素图x
                    self.screenshot_element(str(element_name), file_name)
                    time.sleep(2)
            except Exception as e:
                return e

        apply_style()

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()


if __name__ == '__main__':
    # 读取配置文件控制截屏需求
    screenshot = Config().get('screenshot')
    is_open_1 = screenshot.get('is_highlight_ele_screenshot')
    is_open_2 = screenshot.get('is_screenshot_ele')
    b = Browser('chrome').get('http://www.baidu.com')
    locator = ('id', 'su')
    exsist = b.is_element_exsist2(locator)
    print("是否存在元素：", exsist)
    # 查找元素
    element = b.find(locator, timeout=10)
    b.highlight(element, 'su', is_open_1, is_open_2)
    b.quit()
