# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: checkFormat.py
@time: 2021/10/8 5:04 下午
"""
# 判断邮箱.com结尾
import re

'''
邮箱校验,格式为 username@companyname.com):
1. 校验输入内容是否符合规范(xx@yy.com), 如是进入下一步，如否则抛出提 示"incorrect email format"。
注意必须以.com 结尾674116231@qq.com
2. 可以循环“输入--输出判断结果”这整个过程 
3. 按字母 Q(不区分大小写)退出循环，结束程序
'''


def is_mail_style(x):
    a = re.match(r'^[0-9a-zA-Z\_\-]*@[0-9a-zA-Z]+(\.com)$', x)
    if a:
        yhm = re.findall("^(.+?)@", x)
        print("用户名:%s " % yhm[0])
        gc = re.findall("@(.+?)\.com", x)
        print("公司名:%s " % gc[0])
        return True
    else:
        print("incorrect email format")
        return False


a = input("请输入:")
while 1:
    if a == "q" or a == "Q":
        exit()
    else:
        if is_mail_style(a):
            break
    a = input("请输入:")
print("下一步!")

if __name__ == '__main__':
    is_mail_style("iii@dsdd.com")
