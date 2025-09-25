# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: find_ele.py
@time: 2021/10/28 9:11 上午
"""


# the file is base_page.py

# author=abao

# 定位元素方法

def find_element(self, type, position):
    if type == 'xpath':
        element = self.driver.find_element_by_xpath(position)

        return element

    elif type == 'id':

        element = self.driver.find_element_by_id(position)

        return element

    elif type == 'name':

        element = self.driver.find_element_by_name(position)

        return element

    elif type == 'link_text':

        element = self.driver.find_element_by_link_text(position)

        return element

    else:

        print("不支持的类型")

'''

try:

# 确保元素是可见的。

# 注意：以下入参为元组的元素，需要加*。Python存在这种特性，就是将入参放在元组里。

WebDriverWait(self.driver,10).until(lambda driver: element.is_displayed())

# 注意：以下入参本身是元组，不需要加*

#WebDriverWait( self.driver, 10 ).until( EC.visibility_of_element_located( loc ) )

return element

except:

print("元素没有出现，等待超时")

'''


# 定位元素方法

def find_elements(self, type, position):
    if type == 'xpath':

        element = self.driver.find_elements_by_xpath(position)

        # element_exist(element)

        return element

    elif type == 'id':

        element = self.driver.find_elements_by_id(position)

        # element_exist( element )

        return element

    elif type == 'name':

        element = self.driver.find_elements_by_name(position)

        # element_exist( element )

        return element

    elif type == 'link_text':

        element = self.driver.find_elements_by_link_text(position)

        # element_exist( element )

        return element

    else:

        print("不支持的类型")
