# -*- coding: utf-8 -*-

"""
@author: lucas
@Function: 一些支持方法，比如加密、排序
@file: support.py
@time: 2021/9/22 11:04 上午
"""
import hashlib
import os
import datetime
import time
import json

from utils.log import logger


class EncryptError(Exception):
    pass


def sign(sign_dict, private_key=None, encrypt_way='MD5'):
    """传入待签名的字典，返回签名后字符串
    1.字典排序
    2.拼接，用&连接，最后拼接上私钥
    3.MD5加密"""
    dict_keys = sign_dict.keys()
    dict_keys.sort()

    string = ''
    for key in dict_keys:
        if sign_dict[key] is None:
            pass
        else:
            string += '{0}={1}&'.format(key, sign_dict[key])
    string = string[0:len(string) - 1]
    string = string.replace(' ', '')

    return encrypt(string, salt=private_key, encrypt_way=encrypt_way)


def encrypt(string, salt='', encrypt_way='MD5'):
    u"""根据输入的string与加密盐，按照encrypt方式进行加密，并返回加密后的字符串"""
    string += salt
    if encrypt_way.upper() == 'MD5':
        hash_string = hashlib.md5()
    elif encrypt_way.upper() == 'SHA1':
        hash_string = hashlib.sha1()
    else:
        logger.exception(EncryptError('请输入正确的加密方式，目前仅支持 MD5 或 SHA1'))
        return False

    hash_string.update(string.encode())
    return hash_string.hexdigest()


def get_newest_file_of_path(path):
    """
    :param path: 文件夹路径
    :return path中创建日期最新的一个文件的文件名与创建时间
    """
    return sorted([(x, os.path.getctime(os.path.join(path, x))) for x in os.listdir(path)
                   if os.path.isfile(os.path.join(path, x))], key=lambda i: i[1])[-1]


def get_files_by_createtime(path):
    """ 按照创建时间由新到旧排列路径下所有文件 """
    return sorted([(x, os.path.getctime(os.path.join(path, x))) for x in os.listdir(path)
                   if os.path.isfile(os.path.join(path, x))], key=lambda i: i[1], reverse=True)


def save_time():
    """:return 可用于文件名的时间日期字符串"""
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


def save_date():
    """:return 可用于文件名的日期字符串"""
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def jprint(jstr, indent=2):
    """ 将符合json格式字符串以缩进的方式打印 """
    try:
        print(json.dumps(json.loads(jstr), sort_keys=True, ensure_ascii=False, indent=indent))
    except json.JSONDecodeError:
        print(jstr)


def timestamp_to_time(timestamp, ft='%Y-%m-%d %H:%M:%S'):
    """ 将时间戳转换成固定格式的日期时间字符串 """
    time_local = time.localtime(timestamp)
    return time.strftime(ft, time_local)


def time_to_timestamp(dtime, ft='%Y-%m-%d %H:%M:%S'):
    """ 将日期时间字符串转换成时间戳 """
    try:
        time_array = time.strptime(dtime, ft)
    except ValueError:
        time_array = time.strptime(dtime, '%Y-%m-%d')
    return int(time.mktime(time_array))


def days(d=3):
    """ 取 d 天前（负值）或 d 天后（正）的时间戳 """
    day_cal = datetime.datetime.now() + datetime.timedelta(days=d)
    # 转换为时间戳
    return int(time.mktime(day_cal.timetuple()))


if __name__ == '__main__':
    print(encrypt('100000307111111'))
    print(encrypt('100000307111111', encrypt_way='SHA1'))
    print(get_newest_file_of_path(os.path.join(os.path.dirname(os.path.abspath(".")), "report")))
    print(get_files_by_createtime(os.path.join(os.path.dirname(os.path.abspath(".")), "report")))
    t = '2017-12-09'
    tm = time_to_timestamp(t)
    print(tm)
    print(timestamp_to_time(tm))

    print(timestamp_to_time(days(3)))
    print(timestamp_to_time(days(-3)))
