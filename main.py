# -*- coding: utf-8 -*-
from utils.client import METHODS
from utils.connectSql import connectSql
from utils.file_reader import ExcelReader
from utils.fileOperate import fileOperate

from utils.getHot import getHot
from utils.config import Config, DATA_PATH
from utils.writeHotToFile import writeToExcel, writeHotToFile

if __name__ == '__main__':
    http = Config().get('hot_top_http')
    headers = http.get('headers')
    url = http.get('url')
    hot_xpath = http.get('hot_xpath')
    # 微博热搜排行
    # data = getHot(METHODS[0], url, headers, hot_xpath[0])
    # writeHotToFile(data, 0)
    mysql = Config().get('mysql')
    HOST = mysql.get('host')
    PORT = mysql.get('port')
    USER = mysql.get('user')
    PASSWD = mysql.get('passwd')
    DB = mysql.get('db')
    CHARSET = Config().get('general_parameters').get('charset')
    result = connectSql(HOST, PORT, USER, PASSWD, DB, CHARSET[0])
    exportname = fileOperate(path=DATA_PATH).fileNaming()
    writeToExcel(result, '数据表', exportname)
    # e = DATA_PATH + '/' + exportname+'.xlsx'
    # reader = ExcelReader(e, title_line=True)
    # print(reader.data)
