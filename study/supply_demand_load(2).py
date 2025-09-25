# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 11:23:52 2021

@author: huangshizhi
"""
import re
import os
import pandas as pd
import requests
import time
import json
from requests.adapters import HTTPAdapter
from datetime import datetime, timedelta

def get_request_headers():
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries=3))
    init_headers = {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Host': 'upas.zuiyouliao.com', 'Origin': 'https://portal.zuiyouliao.com',
                    'Referer': 'https://portal.zuiyouliao.com/',
                    'sec-ch-ua': '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
                    'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}  # 设置请求的信息头
    url = "https://upas.zuiyouliao.com/api/upas/auth/login"  # 设置生产环境请求的URL
    # url = "https://upascrmtest.zuiyouliao.com/api/upas/auth/login"  # 设置测试环境请求的URL
    # 1.通过登录账户获取cookie
    Data = {"account": "18150355901", "password": "a0%hNcuS"}
    # Data = {"account": "18850105016", "password": "%^c6JE3x"}#生产环境
    # Data = {"account": "admin", "password": "admin123"}#测试环境账号
    login = s.post(url, json=Data, headers=init_headers)  # 向服务器发出POST请求
    token = login.json()['message']
    request_headers = {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br',
                       'Accept-Language': 'zh-CN,zh;q=0.9',
                       'Content-Type': 'application/json;charset=UTF-8',
                       'Host': 'upas.zuiyouliao.com', 'Origin': 'https://portal.zuiyouliao.com',
                       'Referer': 'https://portal.zuiyouliao.com/',
                       'sec-ch-ua': '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
                       'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'empty',
                       'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                       'ZYL-UPAS-TOKEN': token}  # 设置请求的信息头

    return request_headers


def underline2hump(underline_str):
    '''
    下划线形式字符串转成驼峰形式
    :param underline_str: 下划线形式字符串
    :return: 驼峰形式字符串
    '''
    # 这里re.sub()函数第二个替换参数用到了一个匿名回调函数，回调函数的参数x为一个匹配对象，返回值为一个处理后的字符串
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


def get_id(name, get_id_url_prefix, request_headers):
    # 根据请求地址前缀get_id_url_prefix，名称name，返回名称对应ID
    id_url_test = get_id_url_prefix + str(name)
    print(id_url_test)
    id_value = ''
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    try:
        response = s.get(url=id_url_test, headers={'Content-Type': 'application/json',
                                                   # 'ZYL-UPAS-TOKEN':'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJJZCI6IjI4YzE0ZTYzZTdjZDRkMWFhZTYwODVhNmE0OWUzMzlmIiwibmFtZSI6Iui2hee6p-euoeeQhuWRmCIsImV4cCI6MTY0OTg0MDIwM30.DeJlDAvs80bhheq018OpV4K6jigUu-mHx8C-gZPTzO6pfpWV9RXAQFTzBlHkSYyCm6DyckGF2Le6PiHsXJ7z4btkpIuw_ccXu4vqumeBzpe5vI48cj9c-IFoOSsBvZKjPxl33g6l1FkamC1Q7nPwa5LM6q6RA36Np8gc8K0AIlk',
                                                   'ZYL-UPAS-TOKEN': request_headers['ZYL-UPAS-TOKEN'],
                                                   "encoding": "utf-8"})
        entity = json.loads(response.text)['entity']
        id_value = list(entity.values())[0]['id']
        print("返回的状态码:%s" % json.loads(response.text)['code'])
        print(json.loads(response.text)['message'] + "!")
    except:
        print("Connection refused by the server...")
    return id_value




def transfer_postSupDemDTO(supply_demand_info3):
    # supply_demand_info3=supply_demand_info4
    # postSupDemDTO字段转换为json,json格式嵌套
    # supply_demand_info3['prodCategory'] = supply_demand_info3['prodCategory'].apply(lambda x :prodCategory_dict[x])
    columns_list = list(supply_demand_info3.columns)
    supply_demand_info3.columns = [underline2hump(x) for x in columns_list]
    intersection_list = list(set(columns_list).intersection(set(postSupDemDTOList)))
    s2 = supply_demand_info3.groupby(['customerId', 'releaseTime'], as_index=False).apply(lambda x: x.to_dict('records'))

    s2.columns = ['customerId', 'releaseTime', 'postSupDemDTO']
    s3 = pd.merge(left=supply_demand_info3, right=s2, how='left', on=['customerId', 'releaseTime'])
    s4 = s3.drop(intersection_list, axis=1)
    return s4


def get_city_data(area_tree_url):
    # 根据区域请求url地址,返回城市数据框
    s = requests.session()
    response = s.get(url=area_tree_url, headers={'Content-Type': 'application/json', "encoding": "utf-8"})
    data = json.loads(response.text)['entity']
    response_code = json.loads(response.text)['code']
    print("返回的状态码:%s" % response_code)
    data_list = []
    if response_code == '200':
        for d in data:
            province_list = d['provinces']
            for p in province_list:
                # p = province_list[1]
                city_list = p['cityDTOS']
                for c in city_list:
                    data_dict = {}
                    data_dict['areaName'] = d['areaName']
                    data_dict['areaId'] = d['areaId']
                    data_dict['provinceId'] = p['code']
                    data_dict['province_name'] = p['name']
                    data_dict['cityId'] = c['code']
                    data_dict['cityName'] = c['name']
                    data_list.append(data_dict)

    city_df = pd.DataFrame(data_list)
    city_df['code']=city_df['provinceId']
    city_df['cityId']=None
    city_df['level']=2
    city_df['name']=city_df['province_name']
    city_list = ['provinceId', 'cityId', 'areaId', 'code', 'level', 'name']
    city_df=city_df[city_list].drop_duplicates()
    city_df.index = range(len(city_df))
    city_df.index = city_df['name']

    c2 = city_df[city_list].to_dict(orient='index')

    tmp_list = []
    for key, value in c2.items():
        city_data = {}
        city_data['deliveryAddressList'] = key
        city_data['deliveryAddressList2'] = (value)
        tmp_list.append(city_data)

    tmp_df = pd.DataFrame(tmp_list)
    tmp_df['deliveryAddressList2'] = tmp_df['deliveryAddressList2'].apply(
        lambda x: json.loads('[' + json.dumps(x, ensure_ascii=False) + ']'))

    return tmp_df


def data_to_json(test_df, url, request_headers):
    '''
    将数据转成Json格式通过接口返回到业务系统
    request_data_length:每次请求数量
    url:接口URL地址
    test_df = post_data2[14:15]
    url = add_author_url
    '''
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    start_time = time.time()
    if len(test_df) > 0:
        columns_list = list(test_df.columns)
        # 接口字段为驼峰形式(字段类型转换)
        test_df.columns = [underline2hump(x) for x in columns_list]
        data_str = test_df.to_json(orient='records')
        data = json.loads(data_str)
        # 每次同步一条数据
        for i in range(len(data)):
            print("正在传输第" + str(i) + "条记录")
            json_dict = data[i]
            try:
                # print(request_headers['ZYL-UPAS-TOKEN'])
                response = s.post(url=url, headers={'Content-Type': 'application/json',
                                                    'ZYL-UPAS-TOKEN': request_headers['ZYL-UPAS-TOKEN'],
                                                    "encoding": "utf-8"}, json=json_dict)
            except:
                print("Connection refused by the server...")

            # print("返回的状态码:%s" % json.loads(response.text)['code'])
            # print(json.loads(response.text)['message'] + "!")
            print(response.json())

    print("通过接口返回的数据量为:%d条" % len(test_df))
    print("通过接口导入到数据库耗时%.2fs" % (time.time() - start_time))

def get_tag_data(api_url):
    # 根据区域请求url地址,返回城市数据框
    s = requests.session()
    response = s.get(url=api_url, headers={'Content-Type': 'application/json', "encoding": "utf-8"})
    data = json.loads(response.text)['entity']
    response_code = json.loads(response.text)['code']
    print("返回的状态码:%s" % response_code)
    all_tag=pd.DataFrame()
    if response_code == '200':
        for i in data:
            re_df=pd.DataFrame(i['children'])
            all_tag=pd.concat([all_tag,re_df])
    return all_tag[['id', 'tagName']]

def deal_tag(df):
    '''
    处理标签数据方法
    '''
    tag_list=[]
    for i in df["tagName"]:
        if i in tag_data.keys():
            tag_list.append(tag_data[i])
    return tag_list

def get_user_id(api_url,customer_list):
    # api_url=get_id_url_prefix
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries=3))
    init_headers = {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Host': 'zshqadmin.zuiyouliao.com', 'Origin': 'https://zshqadmin.zuiyouliao.com',
                    'Referer': 'https://zshqadmin.zuiyouliao.com/api/customer/swagger-ui.html',
                    'sec-ch-ua': '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
                    'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}  # 设置请求的信息头
    # 1.通过登录账户获取cookie
    Data= {
        "externalUserIds": customer_list,
        "token": "0fb6cece7b6f4cad9ed15a57d71c1e7a"
    }
    login = s.post(api_url, json=Data, headers=init_headers)  # 向服务器发出POST请求
    token = login.json()['entity']
    token_data=[[i,j] for i,j in token.items()]
    customer_df=pd.DataFrame(token_data,columns=['user_id','customerId'])
    customer_df['user_id']=customer_df['user_id'].astype(str)
    return customer_df

if __name__ == '__main__':
    supply_file_path = os.getcwd() + "/供求帖子.xlsx"
    # 返回对应请求头
    request_headers = get_request_headers()

    # 环境地址前缀(测试环境接口hqadmintest;预生产环境接口zshqadmin;生产环境zshqadmin;)
    # 地址转换接口
    area_tree_url = "https://zshqadmin.zuiyouliao.com/api/upas/area/area/tree"
    # 获取用户id接口
    get_id_url_prefix = "https://zshqadmin.zuiyouliao.com/customer/user/batch/externalUserIds"
    # 添加评论
    post_add_byadmin = "https://zshqadmin.zuiyouliao.com/api/information/post/addByAdmin"
    # 获取标签接口
    tag_id_url='https://zshqadmin.zuiyouliao.com/api/information/tag-group/admin/tree?keywordType=1'

    # 4.供求帖子接口
    supply_demand_info = pd.read_excel(rf"{supply_file_path}",
                                       header=1, sheet_name="新标准"
                                       ,dtype={'materialName':str,'categoryName':str,'prodFactory':str,'user_id':str,'phone':str})
    del supply_demand_info['Unnamed: 20'],supply_demand_info['Unnamed: 14']
    # 去重
    supply_demand_info = supply_demand_info.drop_duplicates()
    supply_demand_info['tagName']=supply_demand_info['tagName'].str.replace('，',',')
    print("come here")

    # 品类字典(中文转换为英文)
    prodCategory_dict = {"原料": "YL", "改性料": "GXL",
                         "再生料": "ZSL", "助剂": "ZJ",
                         "颜填料": "YTL", "机械设备": "JXSB",
                         "其他": "QT"}
    # postSupDemDTO字段转换
    postSupDemDTOList = ['contactName', 'categoryName', 'deliveryAddressList', 'entName',
                         'materialName', 'negotiable', 'phone', 'price',
                         'prodCategory', 'prodCategoryName', 'prodFactory',
                         'quantity', 'taxInclusive','categoryType']

    supply_demand_info2 = supply_demand_info

    # 1.映射标签

    #获取用户ID
    # customer_df = get_user_id(get_id_url_prefix,['101629','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'])
    supply_demand_info2=supply_demand_info2.loc[~supply_demand_info2['user_id'].isnull(),]
    customer_list=list(supply_demand_info2.loc[supply_demand_info2['user_id'].str.isdecimal(),'user_id'].drop_duplicates())
    if len(customer_list)>=1:
        customer_df=get_user_id(get_id_url_prefix,customer_list)
        supply_demand_info2=pd.merge(supply_demand_info2,customer_df,how='left',on='user_id')
    else:
        supply_demand_info2['customerId']=None
    supply_demand_info2.loc[supply_demand_info2['customerId'].isnull(),'customerId']=supply_demand_info2.loc[supply_demand_info2['customerId'].isnull(),'user_id']

    # 获取标签数据
    tag_data=get_tag_data(tag_id_url)
    tag_data={i:j for j,i in zip(tag_data['id'],tag_data['tagName'])}
    supply_demand_info2_test=supply_demand_info2.drop(['tagName'], axis=1).join(supply_demand_info2['tagName'].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('tagName')).reset_index()[['index','tagName']]
    supply_demand_info2_test1=supply_demand_info2_test.groupby(['index']).apply(deal_tag).reset_index()
    supply_demand_info2_test1.columns=['index','tagIds']
    supply_demand_info2=pd.merge(supply_demand_info2.reset_index(),supply_demand_info2_test1,how='left',on='index')
    del supply_demand_info2['index']
    del supply_demand_info2['tagName']


    # 2.映射城市
    city_data = get_city_data(area_tree_url)
    # def deal_city(df):
    #     print(df[['deliveryAddressList','']])
    #     return df
    #
    #
    # supply_demand_info2.groupby(['deliveryAddressList']).apply(deal_city)

    supply_demand_info3 = pd.merge(left=supply_demand_info2, right=city_data, how='left', on='deliveryAddressList')
    supply_demand_info4 = supply_demand_info3.drop(['deliveryAddressList'], axis=1).rename(
        columns={"deliveryAddressList2": "deliveryAddressList"})
    #
    # 不同数据类型的值填充
    values = {"categoryName": "", "prodFactory": "", "negotiable": "", "taxInclusive": "", "quantity": 0, "price": 0,
              "deliveryAddressList": ''}
    # supply_demand_info4['customerId']=supply_demand_info4['user_id']
    supply_demand_info4 = supply_demand_info4.fillna(values).drop(['user_id'], axis=1)
    # 空字符转为list
    supply_demand_info4['deliveryAddressList'] = supply_demand_info4['deliveryAddressList'].apply(
        lambda x: json.loads('[{"cityName": "", "cityId": "", "provinceId": "", "areaId": ""}]') if x == '' else x)
    supply_demand_info4['negotiable'] = 'True'
    # 3.postSupDemDTO
    supply_demand_info5 = transfer_postSupDemDTO(supply_demand_info4)
    # p3['releaseTime'] = p3['releaseTime'].apply(lambda x : datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
    supply_demand_info5['releaseTime'] = supply_demand_info5['releaseTime'].apply(lambda x: x - timedelta(hours=8))
    # # 4.数据传输
    data_to_json(supply_demand_info5, post_add_byadmin, request_headers)
    print('已完成')
    # time.sleep(5)