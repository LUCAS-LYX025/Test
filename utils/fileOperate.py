# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:遍历查找出某个文件夹内所有的子文件,并且找出某个后缀的所有文件
@file: fileOperate.py
@time: 2021/10/8 5:23 下午
"""
import os

from utils.config import Config


class fileOperate():
    def __init__(self, path, rule=None, x=None):
        self.path = path
        self.rule = rule
        self.x = x

    # 遍历查找出某个文件夹内所有的子文件,并且找出某个后缀的所有文件
    def get_files(self):
        all = []
        for fpathe, dirs, fs in os.walk(self.path):  # os.walk 是获 取所有的目录
            for f in fs:
                filename = os.path.join(fpathe, f)
                if filename.endswith(self.rule):  # 判断是否是"xxx"结尾
                    all.append(filename)
        return all

    # 文件重命名
    def fileNaming(self):
        print("请输入文件名，如不输入，默认文件名export:  ")
        DEFAULT_FILE_NAME = Config().get('general_parameters').get('default_file_name')
        exportname = input()
        if exportname == '':
            exportname = DEFAULT_FILE_NAME
        if os.path.exists('%s\%s.xlsx' % (self.path, exportname)):
            os.remove('%s\%s.xlsx' % (self.path, exportname))
        print('导出文件路径： %s/%s.xlsx' % (self.path, exportname))
        return exportname


if __name__ == "__main__":
    path = "/Users/leiyuxing/PycharmProjects/TestFramework/data"
    b = fileOperate(path=path, rule=".xlsx").get_files()
    # b = get_files("/Users/leiyuxing/PycharmProjects/TestFramework/data", rule=".xlsx")
    for i in b:
        print(i)
    # exportname = fileOperate(path=path).fileNaming()
