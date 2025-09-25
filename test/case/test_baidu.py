# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_baidu.py
@time: 2021/9/3 5:27 下午
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from time import sleep
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.HTMLTestRunner import HTMLTestRunner
from utils.config import Config, DATA_PATH, REPORT_PATH
from utils.file_reader import ExcelReader
from utils.log import logger

print(str(Path(__file__).parent.parent))


class TestBaiDu(unittest.TestCase):
    URL = Config().get('URL')
    excel = DATA_PATH + '/baidu.xlsx'
    locator_kw = (By.ID, 'kw')
    locator_su = (By.ID, 'su')

    locator_result = (By.XPATH, '//div[contains(@class, "result")]/h3/a')

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get(self.URL)

    def tearDown(self):
        self.driver.quit()

    def test_search(self):
        datas = ExcelReader(self.excel).data
        for d in datas:
            with self.subTest(data=d):
                self.setUp()
                self.driver.find_element(*self.locator_kw).send_keys(d['search'])
                self.driver.find_element(*self.locator_su).click()
                sleep(2)
                links = self.driver.find_elements(*self.locator_result)
                for link in links:
                    logger.info(link.text)
                self.tearDown()


if __name__ == '__main__':
    report = REPORT_PATH + '/Report.html'
    with open(report, 'w') as f:
        runner = HTMLTestRunner(f, verbosity=2, title='从0搭建测试框架 lucas', description='修改html报告')
        runner.run(TestBaiDu('test_search'))
    # e = Email(title='百度搜素测试报告',
    #           message='这是今天的测试报告，请查收！',
    #           receiver='674116231@qq.com',
    #           server='smtp.qq.com',
    #           sender='674116231@qq.com',
    #           password='nizzhlkocggfbfdc',
    #           path=report
    #           )
    # e.send()
