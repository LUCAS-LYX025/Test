# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: solution.py
@time: 2021/10/30 1:48 下午
"""
import collections


class Solution4(object):
    def findLucky(self, arr):
        """
        :type arr: List[int]
        :rtype: int
        """
        l = [key for key, val in collections.Counter(arr).items() if key == val]
        return max(l) if l else -1


class Solution1:
    def findLucky(self, arr):
        a = -1
        for k, v in collections.Counter(arr).items():
            if k == v:
                a = max(k, a)
        return a


class Solution2:
    def findLucky(self, arr):
        a = -1
        for i in set(arr):
            if arr.count(i) == i:
                a = max(a, i)
        return a


class Solution3:
    def findLucky(self, arr):
        a = -1
        info = {}
        for i in arr:
            info[i] = info.get(i, 0) + 1
        for k, v in info.items():
            if k == v:
                a = max((k, a))
        return a


if __name__ == '__main__':
    arr = [2, 2, 3, 4]
    l = Solution4().findLucky(arr)
    print(l)
    a = Solution1().findLucky(arr)
    print(a)
    b = Solution2().findLucky(arr)
    print(b)
    c = Solution3().findLucky(arr)
    print(c)
