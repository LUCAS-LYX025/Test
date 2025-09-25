# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: count_test.py
@time: 2021/10/8 2:02 下午
"""
# 一、统计
# 例1：统计在一个队列中的数字，有多少个正数，多少个负数，如[1, 3, 5, 7, 0, -1, -9, -4, -5, 8]
import json
from functools import reduce

a = [1, 3, 5, 7, 0, -1, -9, -4, -5, 8]
# 方法一
# 用列表生成式，生成新的列表
b = [i for i in a if i > 0]
print("大于 0 的个数:%s" % len(b))
c = [i for i in a if i < 0]
print("小于 0 的个数:%s" % len(c))

# 方法二
# 用传统的判断思维，累加
m = 0
n = 0
for i in a:
    if i > 0:
        m += 1
    elif i < 0:
        n += 1
    else:
        pass
print("大于 0 的个数:%s" % m)
print("小于 0 的个数:%s" % n)

# 二、字符串切片
# 例2：字符串 "axbyczdj"，如何得到结果“abcd”
a = "axbyczdj"
# 方法一
# 字符串切片
print(a[::2])

# 方法二
# 传统思维
c = []
for i in range(len(a)):
    if i % 2 == 0:
        c.append(a[i])
print("".join(c))

# 三、字符串切割
# 例3：已知一个字符串为“hello.world.yoyo”, 如何得到一个队列 ["hello","world","yoyo"]
a = "hello.world.yoyo"
b = a.split(".")
print(b)

# 四、格式化输出
# 例4：已知一个数字为 1，如何输出“0001”
a = 1
print("%04d" % a)

# 队列
# 例5：已知一个队列,如: [1, 3, 5, 7], 如何把第一个数字，放到第三个位置，得到: [3, 5, 1, 7]
a = [1, 3, 5, 7]
# insert 插入数据
a.insert(3, a[0])
print(a[1:])

# 交换
# 例6：已知 a = 9, b = 8,如何交换a和b的值，得到a的值为8,b的值为9
# 方法一
a = 9
b = 8
a, b = b, a
print(a)
print(b)

# 方法二
a = 9
b = 8

# 用中间变量 c
c = a
a = b
b = c
print(a)
print(b)

# 水仙花
'''
打印出 100-999 所有的"水仙花数"，
所谓"水仙花数"是指一个三位数，其各位数 字立方和等于该数本身。
例如:153 是一个"水仙花数"，因为 153=1 的三次方+ 5 的三次方+3 的三次方。
'''
sxh = []
for i in range(100, 1000):
    s = 0
    m = list(str(i))
    for j in m:
        s += int(j) ** len(m)
    if i == s:
        print(i)
        sxh.append(i)
print("100-999 的水仙花数:%s" % sxh)

# 完全数
'''
如果一个数恰好等于它的因子之和，则称该数为“完全数”，又称完美数或完备 数。 例如:第一个完全数是 6，它有约数 1、2、3、6，除去它本身 6 外，其余 3 个数相加，
1+2+3=6。第二个完全数是 28，它有约数 1、2、4、7、14、28，除去它本身 28 外，其余 5 个数相加，1+2+4+7+14=28。
那么问题来了，求 1000 以内的完全数有哪些?
'''
a = []
for i in range(1, 1000):
    s = 0
    for j in range(1, i):
        if i % j == 0 and j < i:
            s += j
    if s == i:
        print(i)
        a.append(i)
print("1000 以内完全数:%s" % a)

# 排序
# 冒泡排序
a = [7, 3, 10, 9, 21, 35, 4, 6]
s = range(1, len(a))[::-1]
print(list(s))

for i in s:
    for j in range(i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
    print("第 %s 轮交换后数据:%s" % (len(s) - i + 1, a))
print(a)
# sort 排序
# 已知一个队列[1, 3, 6, 9, 7, 3, 4, 6]
a = [1, 3, 6, 9, 7, 3, 4, 6]
# 从小到大排序，正序
a.sort()
print(a)
# 从大到小排序,倒叙
a.sort(reverse=True)
print(a)
# 去除重复数字
b = list(set(a))
print(b)

# a = 0  # 前两数的差值
# b = 1  # 从几开始
# while b < 100:
#     print(b, end=",")
#     a, b = b, a + b

s1 = [1, 3, 5, 7, 0, -1, -9, -4, -5, 8]
s2 = [1, 1, 1, 6, 8]
s3 = list(set(s1 + s2))
print("合并并去重数组结果：", s3)
s4 = set(s1 + s2)
print(s4)

# 字典
a = {"a": 1, "b": 2, "c": True}
# json
b = '{"a": 1, "b": 2, "c": true}'
print(type(a))
print(json.dumps(a))
