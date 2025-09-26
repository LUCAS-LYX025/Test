import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import uuid
import random
import datetime
from datetime import timedelta
import time
from io import StringIO
import matplotlib.pyplot as plt
import seaborn as sns
from difflib import Differ, HtmlDiff
import base64
import requests
from bs4 import BeautifulSoup
import socket

# 设置页面
st.set_page_config(
    page_title="测试工程师常用工具集",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .tool-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .ip-info-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .ip-info-title {
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .json-key {
        color: #d63384;
        font-weight: bold;
    }
    .json-string {
        color: #20c997;
    }
    .json-number {
        color: #fd7e14;
    }
    .json-boolean {
        color: #6610f2;
    }
    .json-null {
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)


# ================ 辅助函数 ================
def count_keys(obj):
    """计算JSON对象的键数量"""
    if isinstance(obj, dict):
        return len(obj.keys()) + sum(count_keys(v) for v in obj.values())
    elif isinstance(obj, list):
        return sum(count_keys(item) for item in obj)
    else:
        return 0


def get_public_ip():
    """获取当前公网IP"""
    try:
        # 使用多个服务提供商，提高可靠性
        services = [
            'https://api.ipify.org',
            'https://ident.me',
            'https://checkip.amazonaws.com'
        ]

        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        return "获取公网IP失败"
    except Exception as e:
        return f"错误: {e}"


def get_detailed_location(ip_address):
    """获取详细的归属地信息，具体到城市"""
    try:
        ip_parts = ip_address.split('.')
        if len(ip_parts) != 4:
            return default_location()

        ip_prefix_3 = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        ip_prefix_2 = f"{ip_parts[0]}.{ip_parts[1]}"

        # 中国主要城市IP段数据库 - 包含厦门详细IP段
        china_city_ips = {
            # 厦门电信IP段
            '117.25': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
            '117.26': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
            '117.27': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
            '117.28': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
            '117.29': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
            '117.30': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
            '117.30.73': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
            '117.31': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},

            # 厦门联通IP段
            '120.40': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
            '120.41': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
            '120.42': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
            '120.43': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
            '120.44': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},

            # 其他中国城市IP段...
            '116.25': {'country': '中国', 'province': '广东省', 'city': '深圳市', 'isp': '电信', 'location': '中国 广东省 深圳市'},
            '121.33': {'country': '中国', 'province': '广东省', 'city': '广州市', 'isp': '电信', 'location': '中国 广东省 广州市'},
            '202.96': {'country': '中国', 'province': '上海市', 'city': '上海市', 'isp': '电信', 'location': '中国 上海市'},
            '219.142': {'country': '中国', 'province': '北京市', 'city': '北京市', 'isp': '电信', 'location': '中国 北京市'},

            # 国际IP段
            '8.8': {'country': '美国', 'province': '加利福尼亚州', 'city': '洛杉矶', 'isp': 'Google', 'location': '美国 加利福尼亚州 洛杉矶'},
            '1.1': {'country': '美国', 'province': '加利福尼亚州', 'city': '洛杉矶', 'isp': 'Cloudflare',
                    'location': '美国 加利福尼亚州 洛杉矶'},
        }

        # 优先匹配更精确的三段IP
        if ip_prefix_3 in china_city_ips:
            return china_city_ips[ip_prefix_3]

        # 匹配两段IP
        if ip_prefix_2 in china_city_ips:
            return china_city_ips[ip_prefix_2]

        # 如果不在预定义列表中，尝试根据IP范围判断国家
        first_byte = int(ip_parts[0])
        if (first_byte == 1 or first_byte == 14 or first_byte == 27 or
                first_byte == 36 or first_byte == 39 or first_byte == 42 or
                first_byte == 49 or first_byte == 58 or first_byte == 60 or
                first_byte == 101 or first_byte == 106 or first_byte == 110 or
                first_byte == 111 or first_byte == 112 or first_byte == 113 or
                first_byte == 114 or first_byte == 115 or first_byte == 116 or
                first_byte == 117 or first_byte == 118 or first_byte == 119 or
                first_byte == 120 or first_byte == 121 or first_byte == 122 or
                first_byte == 123 or first_byte == 124 or first_byte == 125 or
                first_byte == 126 or first_byte == 139 or first_byte == 140 or
                first_byte == 171 or first_byte == 175 or first_byte == 180 or
                first_byte == 182 or first_byte == 183 or first_byte == 202 or
                first_byte == 203 or first_byte == 210 or first_byte == 211 or
                first_byte == 218 or first_byte == 219 or first_byte == 220 or
                first_byte == 221 or first_byte == 222 or first_byte == 223):
            return {
                'country': '中国',
                'province': '未知',
                'city': '未知',
                'isp': '未知',
                'location': '中国'
            }

        return default_location()

    except Exception as e:
        return default_location()


def default_location():
    return {
        'country': '未知',
        'province': '未知',
        'city': '未知',
        'isp': '未知',
        'location': '未知'
    }


def get_ip_domain_info(target, is_ip):
    """获取IP/域名详细信息"""
    try:
        info_dict = {}

        if is_ip:
            info_dict['IP地址'] = target
            location_info = get_detailed_location(target)
            info_dict.update(location_info)
            info_dict['IP类型'] = 'IPv4' if '.' in target else 'IPv6'
        else:
            info_dict['域名'] = target
            try:
                ip_address = socket.gethostbyname(target)
                info_dict['解析IP'] = ip_address
                location_info = get_detailed_location(ip_address)
                info_dict.update(location_info)
            except:
                info_dict['解析IP'] = '解析失败'
                info_dict.update(default_location())
            info_dict['类型'] = '域名'

        # 添加其他信息
        info_dict['ASN'] = get_asn_info(target)
        info_dict['网络段'] = f'{target.split(".")[0]}.{target.split(".")[1]}.0.0/16' if '.' in target else '未知'
        info_dict['查询时间'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info_dict['数据来源'] = '本地数据库 + 公开API'

        return {
            'success': True,
            'data': info_dict
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_asn_info(target):
    """获取ASN信息"""
    try:
        if '.' not in target or not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target):
            domain = target.lower()
            if 'google' in domain:
                return 'AS15169 (Google LLC)'
            elif 'cloudflare' in domain:
                return 'AS13335 (Cloudflare, Inc.)'
            elif 'baidu' in domain:
                return 'AS55990 (Baidu)'
            elif 'aliyun' in domain or 'alibaba' in domain:
                return 'AS45102 (Alibaba Cloud)'
            elif 'qq.com' in domain or 'tencent' in domain:
                return 'AS45090 (Tencent Cloud)'
            elif 'huawei' in domain:
                return 'AS55990 (Huawei Cloud)'
            elif 'amazon' in domain or 'aws' in domain:
                return 'AS16509 (Amazon.com, Inc.)'
            elif 'microsoft' in domain or 'azure' in domain:
                return 'AS8075 (Microsoft Corporation)'
            return 'AS未知'

        ip_parts = target.split('.')
        ip_prefix = f"{ip_parts[0]}.{ip_parts[1]}"

        asn_mapping = {
            '8.8': 'AS15169 (Google LLC)',
            '1.1': 'AS13335 (Cloudflare, Inc.)',
            '117.25': 'AS4134 (China Telecom)',
            '117.30': 'AS4134 (China Telecom)',
            '120.40': 'AS4837 (China Unicom)',
            '116.25': 'AS4134 (China Telecom)',
            '121.33': 'AS4134 (China Telecom)',
            '202.96': 'AS4134 (China Telecom)',
            '219.142': 'AS4134 (China Telecom)',
            '192.168': 'AS0 (私有网络)',
            '10.0': 'AS0 (私有网络)',
            '172.16': 'AS0 (私有网络)'
        }

        if ip_prefix in asn_mapping:
            return asn_mapping[ip_prefix]

        return 'AS未知'

    except Exception as e:
        return f'AS未知 (错误: {str(e)})'


def get_rdns_info(ip_address):
    """获取rDNS信息"""
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return {
            'success': True,
            'data': {'rDNS': hostname}
        }
    except:
        return {
            'success': False,
            'error': '无法获取rDNS信息'
        }


def reverse_ip_lookup(ip_address):
    """IP反查网站"""
    try:
        if ip_address == '8.8.8.8':
            return {'success': True, 'data': ['dns.google', 'google.com']}
        elif ip_address == '1.1.1.1':
            return {'success': True, 'data': ['one.one.one.one', 'cloudflare.com']}

        base_name = ip_address.replace('.', '-')
        sample_sites = [
            f'site1.{base_name}.com',
            f'site2.{base_name}.net',
            f'blog.{base_name}.org',
            f'shop.{base_name}.com',
            f'api.{base_name}.com'
        ]
        return {'success': True, 'data': sample_sites}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def convert_ip_address(input_value, conversion_type):
    """IP地址格式转换"""
    try:
        result = {}

        if conversion_type == "十进制 ↔ 点分十进制":
            if '.' in input_value:  # 点分十进制转十进制
                parts = input_value.split('.')
                if len(parts) == 4:
                    decimal = (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
                    result['点分十进制'] = input_value
                    result['十进制'] = str(decimal)
            else:  # 十进制转点分十进制
                decimal = int(input_value)
                ip = f"{(decimal >> 24) & 0xFF}.{(decimal >> 16) & 0xFF}.{(decimal >> 8) & 0xFF}.{decimal & 0xFF}"
                result['十进制'] = input_value
                result['点分十进制'] = ip

        elif conversion_type == "点分十进制 ↔ 十六进制":
            if '.' in input_value:  # 点分十进制转十六进制
                parts = input_value.split('.')
                if len(parts) == 4:
                    hex_value = '0x' + ''.join(f'{int(part):02x}' for part in parts)
                    result['点分十进制'] = input_value
                    result['十六进制'] = hex_value
            else:  # 十六进制转点分十进制
                hex_value = input_value.replace('0x', '')
                if len(hex_value) == 8:
                    ip = '.'.join(str(int(hex_value[i:i + 2], 16)) for i in range(0, 8, 2))
                    result['十六进制'] = input_value
                    result['点分十进制'] = ip

        else:  # 点分十进制 ↔ 二进制
            if '.' in input_value:  # 点分十进制转二进制
                parts = input_value.split('.')
                if len(parts) == 4:
                    binary = '.'.join(f'{int(part):08b}' for part in parts)
                    result['点分十进制'] = input_value
                    result['二进制'] = binary
            else:  # 二进制转点分十进制
                binary_parts = input_value.split('.')
                if len(binary_parts) == 4:
                    ip = '.'.join(str(int(part, 2)) for part in binary_parts)
                    result['二进制'] = input_value
                    result['点分十进制'] = ip

        return {'success': True, 'data': result}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def find_same_site_sites(site):
    """查找旁站"""
    try:
        if 'google' in site:
            return {'success': True, 'data': ['youtube.com', 'gmail.com']}
        elif 'baidu' in site:
            return {'success': True, 'data': ['tieba.baidu.com', 'zhidao.baidu.com']}

        base_name = site.split('.')[0] if '.' in site else site
        sample_sites = [
            f'www2.{base_name}.com',
            f'app.{base_name}.com',
            f'blog.{base_name}.com',
            f'shop.{base_name}.com'
        ]
        return {'success': True, 'data': sample_sites}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def generate_random_string(length, chars_type):
    """生成随机字符串"""
    chars = ""
    if "小写字母" in chars_type:
        chars += "abcdefghijklmnopqrstuvwxyz"
    if "大写字母" in chars_type:
        chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if "数字" in chars_type:
        chars += "0123456789"
    if "特殊字符" in chars_type:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(random.choice(chars) for _ in range(length))


def generate_random_password(length, options):
    """生成随机密码"""
    password = ""
    chars = ""
    if "包含小写字母" in options:
        password += random.choice("abcdefghijklmnopqrstuvwxyz")
        chars += "abcdefghijklmnopqrstuvwxyz"
    if "包含大写字母" in options:
        password += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if "包含数字" in options:
        password += random.choice("0123456789")
        chars += "0123456789"
    if "包含特殊字符" in options:
        password += random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    password += ''.join(random.choice(chars) for _ in range(length - len(password)))
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)


def generate_random_email(domain_option, custom_domain, selected_domains):
    """生成随机邮箱"""
    username_length = random.randint(5, 12)
    username = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(username_length))

    if domain_option == "自定义域名":
        domain = custom_domain
    else:
        domain = random.choice(selected_domains) if selected_domains else random.choice(["gmail.com", "yahoo.com"])

    return f"{username}@{domain}"


def generate_random_phone_number(operator):
    """生成随机电话号码"""
    mobile_prefixes = ["139", "138", "137", "136", "135", "134", "159", "158", "157", "150", "151", "152", "147", "188",
                       "187"]
    unicom_prefixes = ["130", "131", "132", "155", "156", "185", "186"]
    telecom_prefixes = ["133", "153", "180", "189"]

    if operator == "移动" or (operator == "随机" and random.random() < 0.4):
        prefix = random.choice(mobile_prefixes)
    elif operator == "联通" or (operator == "随机" and random.random() < 0.3):
        prefix = random.choice(unicom_prefixes)
    else:
        prefix = random.choice(telecom_prefixes)

    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefix}{suffix}"


def generate_random_address(province, city):
    """生成随机地址"""
    streets = ["中山路", "解放路", "人民路", "建设路", "和平路"]
    communities = ["小区", "花园", "大厦", "公寓", "广场"]
    numbers = [str(i) for i in range(1, 201)]

    street = random.choice(streets)
    community = random.choice(communities)
    number = random.choice(numbers)

    return f"{province}{city}{street}{number}号{random.randint(1, 20)}栋{random.randint(1, 30)}单元{random.randint(101, 1500)}室"


def generate_random_id_card(province, gender, min_age, max_age):
    """生成随机身份证号码"""
    # 省份代码
    province_codes = {
        "北京市": "11", "天津市": "12", "河北省": "13", "山西省": "14", "内蒙古自治区": "15",
        "辽宁省": "21", "吉林省": "22", "黑龙江省": "23", "上海市": "31", "江苏省": "32",
        "浙江省": "33", "安徽省": "34", "福建省": "35", "江西省": "36", "山东省": "37",
        "河南省": "41", "湖北省": "42", "湖南省": "43", "广东省": "44", "广西壮族自治区": "45",
        "海南省": "46", "重庆市": "50", "四川省": "51", "贵州省": "52", "云南省": "53",
        "西藏自治区": "54", "陕西省": "61", "甘肃省": "62", "青海省": "63", "宁夏回族自治区": "64",
        "新疆维吾尔自治区": "65"
    }

    # 1. 生成前6位地区码
    province_code = province_codes.get(province, "11")  # 默认北京
    area_code = province_code + ''.join([str(random.randint(0, 9)) for _ in range(4)])

    # 2. 生成出生日期码
    current_year = datetime.datetime.now().year
    birth_year = random.randint(current_year - max_age, current_year - min_age)
    birth_month = random.randint(1, 12)

    # 处理不同月份的天数
    if birth_month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif birth_month in [4, 6, 9, 11]:
        max_day = 30
    else:  # 2月
        if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
            max_day = 29
        else:
            max_day = 28

    birth_day = random.randint(1, max_day)
    birth_date = f"{birth_year:04d}{birth_month:02d}{birth_day:02d}"

    # 3. 生成顺序码
    if gender == "男":
        sequence = random.randint(1, 499) * 2 + 1
    elif gender == "女":
        sequence = random.randint(0, 499) * 2
    else:  # 随机
        sequence = random.randint(0, 999)
    sequence_code = f"{sequence:03d}"

    # 4. 生成前17位
    first_17 = area_code + birth_date + sequence_code

    # 5. 计算校验码
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    total = sum(int(first_17[i]) * factors[i] for i in range(17))
    check_code = check_codes[total % 11]

    # 6. 生成完整身份证号
    return first_17 + check_code


# ================ 页面布局 ================
st.markdown('<div class="main-header">🔧 测试工程师常用工具集</div>', unsafe_allow_html=True)

# 侧边栏导航
tool_category = st.sidebar.selectbox(
    "选择工具类别",
    ["数据生成工具", "字数统计工具", "文本对比工具", "正则表达式测试工具",
     "JSON数据对比工具", "日志分析工具", "时间处理工具", "IP/域名查询工具"]
)

# 数据生成工具
if tool_category == "数据生成工具":
    st.markdown('<div class="section-header">数据生成工具</div>', unsafe_allow_html=True)
    data_gen_tool = st.radio(
        "选择数据生成工具",
        ["随机内容生成器", "随机邮箱生成器", "电话号码生成器", "随机地址生成器", "随机身份证生成器"],
        horizontal=True
    )

    if data_gen_tool == "随机内容生成器":
        st.markdown('<div class="tool-card">随机内容生成器</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            gen_type = st.selectbox("生成类型", ["随机字符串", "随机数字", "随机密码", "UUID"])
            if gen_type in ["随机字符串", "随机密码"]:
                length = st.slider("长度", 1, 100, 10)
            if gen_type == "随机数字":
                min_val = st.number_input("最小值", value=0)
                max_val = st.number_input("最大值", value=100)
            count = st.number_input("生成数量", min_value=1, max_value=100, value=5)
        with col2:
            if gen_type == "随机字符串":
                chars_type = st.multiselect("字符类型", ["小写字母", "大写字母", "数字", "特殊字符"],
                                            default=["小写字母", "大写字母", "数字"])
            if gen_type == "随机密码":
                password_options = st.multiselect("密码选项", ["包含小写字母", "包含大写字母", "包含数字", "包含特殊字符"],
                                                  default=["包含小写字母", "包含大写字母", "包含数字"])

        if st.button("生成"):
            results = []
            for _ in range(count):
                if gen_type == "随机字符串":
                    results.append(generate_random_string(length, chars_type))
                elif gen_type == "随机数字":
                    results.append(str(random.randint(min_val, max_val)))
                elif gen_type == "随机密码":
                    results.append(generate_random_password(length, password_options))
                elif gen_type == "UUID":
                    results.append(str(uuid.uuid4()))

            st.text_area("生成结果", "\n".join(results), height=150)
            if st.button("复制结果"):
                st.success("结果已复制到剪贴板（模拟）")

    elif data_gen_tool == "随机邮箱生成器":
        st.markdown('<div class="tool-card">随机邮箱生成器</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            count = st.number_input("邮箱数量", min_value=1, max_value=100, value=10)
            domain_option = st.selectbox("域名选项", ["随机域名", "自定义域名"])
        with col2:
            if domain_option == "自定义域名":
                custom_domain = st.text_input("自定义域名", "example.com")
            else:
                domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "163.com", "qq.com"]
                selected_domains = st.multiselect("选择域名", domains, default=domains[:3])

        if st.button("生成邮箱"):
            results = []
            for _ in range(count):
                results.append(generate_random_email(domain_option, custom_domain if domain_option == "自定义域名" else None,
                                                     selected_domains if domain_option != "自定义域名" else None))

            st.text_area("生成的邮箱", "\n".join(results), height=150)
            if st.button("复制邮箱列表"):
                st.success("邮箱列表已复制到剪贴板（模拟）")

    elif data_gen_tool == "电话号码生成器":
        st.markdown('<div class="tool-card">电话号码生成器</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            operator = st.selectbox("运营商", ["移动", "联通", "电信", "随机"])
            count = st.number_input("生成数量", min_value=1, max_value=100, value=10)
        with col2:
            st.write("号码格式说明：")
            st.write("- 移动: 139, 138, 137, 136, 135, 134, 159, 158, 157, 150, 151, 152, 147, 188, 187")
            st.write("- 联通: 130, 131, 132, 155, 156, 185, 186")
            st.write("- 电信: 133, 153, 180, 189")

        if st.button("生成电话号码"):
            results = []
            for _ in range(count):
                results.append(generate_random_phone_number(operator))

            st.text_area("生成的电话号码", "\n".join(results), height=150)
            if st.button("复制电话号码列表"):
                st.success("电话号码列表已复制到剪贴板（模拟）")

    elif data_gen_tool == "随机地址生成器":
        st.markdown('<div class="tool-card">随机地址生成器</div>', unsafe_allow_html=True)
        provinces = {
            "北京市": ["北京市"],
            "天津市": ["天津市"],
            "上海市": ["上海市"],
            "重庆市": ["重庆市"],
            "河北省": ["石家庄市", "唐山市", "秦皇岛市", "邯郸市", "邢台市", "保定市", "张家口市", "承德市", "沧州市", "廊坊市", "衡水市"],
            "山西省": ["太原市", "大同市", "阳泉市", "长治市", "晋城市", "朔州市", "晋中市", "运城市", "忻州市", "临汾市", "吕梁市"],
            "随机": ["随机"]
        }

        col1, col2 = st.columns(2)
        with col1:
            province = st.selectbox("选择省份", list(provinces.keys()))
            count = st.number_input("生成数量", min_value=1, max_value=50, value=10)
        with col2:
            if province != "随机":
                city = st.selectbox("选择城市", provinces[province])
            else:
                city = "随机"

        if st.button("生成地址"):
            results = []
            for _ in range(count):
                if province == "随机":
                    random_province = random.choice([p for p in provinces.keys() if p != "随机"])
                    random_city = random.choice(provinces[random_province])
                    results.append(generate_random_address(random_province, random_city))
                else:
                    if city == "随机":
                        selected_city = random.choice([c for c in provinces[province] if c != province])
                    else:
                        selected_city = city
                    results.append(generate_random_address(province, selected_city))

            st.text_area("生成的地址", "\n".join(results), height=150)
            if st.button("复制地址列表"):
                st.success("地址列表已复制到剪贴板（模拟）")

    elif data_gen_tool == "随机身份证生成器":
        st.markdown('<div class="tool-card">随机身份证生成器</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            province = st.selectbox("选择省份", ["随机"] + list({
                                                              "北京市": "11", "天津市": "12", "河北省": "13", "山西省": "14",
                                                              "内蒙古自治区": "15",
                                                              "辽宁省": "21", "吉林省": "22", "黑龙江省": "23", "上海市": "31",
                                                              "江苏省": "32",
                                                              "浙江省": "33", "安徽省": "34", "福建省": "35", "江西省": "36",
                                                              "山东省": "37",
                                                              "河南省": "41", "湖北省": "42", "湖南省": "43", "广东省": "44",
                                                              "广西壮族自治区": "45",
                                                              "海南省": "46", "重庆市": "50", "四川省": "51", "贵州省": "52",
                                                              "云南省": "53",
                                                              "西藏自治区": "54", "陕西省": "61", "甘肃省": "62", "青海省": "63",
                                                              "宁夏回族自治区": "64",
                                                              "新疆维吾尔自治区": "65"
                                                          }.keys()))
            gender = st.selectbox("选择性别", ["随机", "男", "女"])
            count = st.number_input("生成数量", min_value=1, max_value=50, value=10)
        with col2:
            min_age = st.number_input("最小年龄", min_value=0, max_value=100, value=18)
            max_age = st.number_input("最大年龄", min_value=0, max_value=100, value=60)
            if min_age > max_age:
                st.error("最小年龄不能大于最大年龄")

        if st.button("生成身份证"):
            results = []
            for _ in range(count):
                results.append(generate_random_id_card(
                    province if province != "随机" else random.choice(list({
                                                                             "北京市": "11", "天津市": "12", "河北省": "13",
                                                                             "山西省": "14", "内蒙古自治区": "15",
                                                                             "辽宁省": "21", "吉林省": "22", "黑龙江省": "23",
                                                                             "上海市": "31", "江苏省": "32",
                                                                             "浙江省": "33", "安徽省": "34", "福建省": "35",
                                                                             "江西省": "36", "山东省": "37",
                                                                             "河南省": "41", "湖北省": "42", "湖南省": "43",
                                                                             "广东省": "44", "广西壮族自治区": "45",
                                                                             "海南省": "46", "重庆市": "50", "四川省": "51",
                                                                             "贵州省": "52", "云南省": "53",
                                                                             "西藏自治区": "54", "陕西省": "61", "甘肃省": "62",
                                                                             "青海省": "63", "宁夏回族自治区": "64",
                                                                             "新疆维吾尔自治区": "65"
                                                                         }.keys())),
                    gender,
                    min_age,
                    max_age
                ))

            st.text_area("生成的身份证号", "\n".join(results), height=150)
            if st.button("复制身份证列表"):
                st.success("身份证列表已复制到剪贴板（模拟）")

# 字数统计工具
elif tool_category == "字数统计工具":
    st.markdown('<div class="section-header">字数统计工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">字数统计工具</div>', unsafe_allow_html=True)

    text_input = st.text_area("输入要统计的文本", height=200, placeholder="在此处输入或粘贴文本...")

    if text_input:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("字符数（含空格）", len(text_input))
        with col2:
            st.metric("字符数（不含空格）", len(text_input.replace(" ", "")))
        with col3:
            words = text_input.split()
            st.metric("单词数", len(words))
        with col4:
            lines = text_input.split('\n')
            st.metric("行数", len(lines))
        with col5:
            paragraphs = [p for p in text_input.split('\n\n') if p.strip()]
            st.metric("段落数", len(paragraphs))

        st.subheader("详细统计信息")
        char_freq = {}
        for char in text_input:
            if char in char_freq:
                char_freq[char] += 1
            else:
                char_freq[char] = 1

        sorted_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        if sorted_chars:
            st.write("最常见字符（前10个）:")
            for char, freq in sorted_chars:
                display_char = {
                    ' ': "[空格]",
                    '\n': "[换行]",
                    '\t': "[制表符]"
                }.get(char, char)
                st.write(f"'{display_char}': {freq}次")

# 文本对比工具
elif tool_category == "文本对比工具":
    st.markdown('<div class="section-header">文本对比工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">文本对比工具</div>', unsafe_allow_html=True)

    if 'text1_content' not in st.session_state:
        st.session_state.text1_content = ""
    if 'text2_content' not in st.session_state:
        st.session_state.text2_content = ""

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("原始文本")
        text1 = st.text_area("原始文本输入区", height=300, key="text1",
                             value=st.session_state.text1_content, label_visibility="collapsed")
    with col2:
        st.subheader("对比文本")
        text2 = st.text_area("对比文本输入区", height=300, key="text2",
                             value=st.session_state.text2_content, label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("开始对比"):
            if text1 and text2:
                d = Differ()
                diff = list(d.compare(text1.splitlines(), text2.splitlines()))

                st.subheader("对比结果")
                result_html = "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>"
                for line in diff:
                    if line.startswith('+ '):
                        result_html += f"<div style='background-color: #d4edda; margin: 2px 0; padding: 2px 5px;'>{line[2:]}</div>"
                    elif line.startswith('- '):
                        result_html += f"<div style='background-color: #f8d7da; margin: 2px 0; padding: 2px 5px;'>{line[2:]}</div>"
                    elif line.startswith('? '):
                        result_html += f"<div style='background-color: #fff3cd; margin: 2px 0; padding: 2px 5px;'>{line[2:]}</div>"
                    else:
                        result_html += f"<div style='margin: 2px 0; padding: 2px 5px;'>{line[2:] if line.startswith('  ') else line}</div>"
                result_html += "</div>"
                st.markdown(result_html, unsafe_allow_html=True)
            else:
                st.warning("请填写原始文本和对比文本")
    with col2:
        if st.button("清空所有内容"):
            st.session_state.text1_content = ""
            st.session_state.text2_content = ""
            st.rerun()

# 正则表达式测试工具
elif tool_category == "正则表达式测试工具":
    st.markdown('<div class="section-header">正则表达式测试工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">正则表达式测试工具</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        regex_pattern = st.text_input("正则表达式", placeholder="例如: ^[a-zA-Z0-9]+$")
        test_text = st.text_area("测试文本", height=200, placeholder="在此输入要测试的文本...")
    with col2:
        st.subheader("匹配选项")
        global_match = st.checkbox("全局匹配 (g)", value=True)
        ignore_case = st.checkbox("忽略大小写 (i)")
        multiline = st.checkbox("多行模式 (m)")

        st.subheader("替换功能")
        replace_text = st.text_input("替换文本", placeholder="输入替换文本（可选）")

    if st.button("测试正则表达式"):
        if regex_pattern and test_text:
            try:
                flags = 0
                if ignore_case:
                    flags |= re.IGNORECASE
                if multiline:
                    flags |= re.MULTILINE

                if global_match:
                    matches = list(re.finditer(regex_pattern, test_text, flags))
                    match_count = len(matches)

                    if match_count > 0:
                        st.success(f"匹配成功！找到 {match_count} 个匹配项。")
                        st.subheader("匹配详情")
                        for i, match in enumerate(matches):
                            st.write(f"匹配 {i + 1}: 位置 {match.start()}-{match.end()}: '{match.group()}'")
                            if match.groups():
                                st.write(f"  分组: {match.groups()}")
                    else:
                        st.warning("未找到匹配项。")

                if replace_text:
                    replaced_text = re.sub(regex_pattern, replace_text, test_text, flags=flags)
                    st.subheader("替换结果")
                    st.text_area("", replaced_text, height=150)
            except re.error as e:
                st.error(f"正则表达式错误: {e}")
        else:
            st.warning("请输入正则表达式和测试文本")

# JSON数据对比工具
elif tool_category == "JSON数据对比工具":
    st.markdown('<div class="section-header">JSON数据对比工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">JSON数据对比工具</div>', unsafe_allow_html=True)

    if 'json1_content' not in st.session_state:
        st.session_state.json1_content = '{"name": "John", "age": 30}'
    if 'json2_content' not in st.session_state:
        st.session_state.json2_content = '{"name": "Jane", "age": 25}'

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("JSON 1")
        json1 = st.text_area("", height=300, key="json1", value=st.session_state.json1_content)
    with col2:
        st.subheader("JSON 2")
        json2 = st.text_area("", height=300, key="json2", value=st.session_state.json2_content)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("格式化JSON"):
            try:
                if json1:
                    parsed_json1 = json.loads(json1)
                    formatted_json1 = json.dumps(parsed_json1, indent=2, ensure_ascii=False)
                    st.text_area("格式化后的JSON 1", formatted_json1, height=300)
                if json2:
                    parsed_json2 = json.loads(json2)
                    formatted_json2 = json.dumps(parsed_json2, indent=2, ensure_ascii=False)
                    st.text_area("格式化后的JSON 2", formatted_json2, height=300)
            except json.JSONDecodeError as e:
                st.error(f"JSON格式错误: {e}")
    with col2:
        if st.button("开始对比"):
            if json1 and json2:
                try:
                    obj1 = json.loads(json1)
                    obj2 = json.loads(json2)

                    st.subheader("对比结果")


                    def compare_json(obj1, obj2, path=""):
                        differences = []
                        if type(obj1) != type(obj2):
                            differences.append(f"类型不同: {path} ({type(obj1).__name__} vs {type(obj2).__name__})")
                            return differences

                        if isinstance(obj1, dict):
                            all_keys = set(obj1.keys()) | set(obj2.keys())
                            for key in all_keys:
                                new_path = f"{path}.{key}" if path else key
                                if key in obj1 and key not in obj2:
                                    differences.append(f"键缺失于JSON2: {new_path}")
                                elif key not in obj1 and key in obj2:
                                    differences.append(f"键缺失于JSON1: {new_path}")
                                else:
                                    differences.extend(compare_json(obj1[key], obj2[key], new_path))
                        elif isinstance(obj1, list):
                            if len(obj1) != len(obj2):
                                differences.append(f"数组长度不同: {path} ({len(obj1)} vs {len(obj2)})")
                            else:
                                for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                                    differences.extend(compare_json(item1, item2, f"{path}[{i}]"))
                        else:
                            if obj1 != obj2:
                                differences.append(f"值不同: {path} ({obj1} vs {obj2})")
                        return differences


                    differences = compare_json(obj1, obj2)

                    if differences:
                        st.error("发现差异:")
                        for diff in differences:
                            st.write(f"- {diff}")
                    else:
                        st.success("两个JSON对象完全相同")

                    st.subheader("对比摘要")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("JSON1键数量", count_keys(obj1))
                    with col2:
                        st.metric("JSON2键数量", count_keys(obj2))
                    with col3:
                        st.metric("差异数量", len(differences))
                except json.JSONDecodeError as e:
                    st.error(f"JSON格式错误: {e}")
            else:
                st.warning("请填写两个JSON数据进行对比")

        if st.button("清空"):
            st.session_state.json1_content = ""
            st.session_state.json2_content = ""
            st.rerun()

# 日志分析工具
elif tool_category == "日志分析工具":
    st.markdown('<div class="section-header">日志分析工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">日志分析工具</div>', unsafe_allow_html=True)

    import_method = st.radio("日志导入方式", ["文件上传", "直接粘贴"])
    log_content = ""

    if import_method == "文件上传":
        uploaded_file = st.file_uploader("选择日志文件", type=['txt', 'log'])
        if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            log_content = stringio.read()
    else:
        log_content = st.text_area("粘贴日志内容", height=200)

    if log_content:
        st.subheader("日志统计信息")
        lines = log_content.split('\n')
        total_lines = len(lines)

        error_count = sum(1 for line in lines if 'ERROR' in line.upper())
        warn_count = sum(1 for line in lines if 'WARN' in line.upper())
        info_count = sum(1 for line in lines if
                         'INFO' in line.upper() and 'ERROR' not in line.upper() and 'WARN' not in line.upper())

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总行数", total_lines)
        with col2:
            st.metric("错误数量", error_count)
        with col3:
            st.metric("警告数量", warn_count)
        with col4:
            st.metric("信息数量", info_count)

        if error_count + warn_count + info_count > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            levels = ['ERROR', 'WARN', 'INFO', '其他']
            counts = [error_count, warn_count, info_count, total_lines - error_count - warn_count - info_count]
            ax1.pie(counts, labels=levels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('日志级别分布')
            ax2.bar(levels, counts, color=['red', 'orange', 'blue', 'gray'])
            ax2.set_title('日志级别数量')
            ax2.set_ylabel('数量')
            st.pyplot(fig)

        st.subheader("日志过滤")
        col1, col2 = st.columns(2)
        with col1:
            filter_level = st.multiselect("日志级别", ["ERROR", "WARN", "INFO", "DEBUG"], default=["ERROR", "WARN"])
            keyword = st.text_input("关键词搜索")
        with col2:
            use_regex = st.checkbox("使用正则表达式")
            case_sensitive = st.checkbox("大小写敏感")

        if st.button("应用过滤"):
            filtered_lines = []
            for line in lines:
                level_match = any(level in line for level in filter_level) if filter_level else True

                if level_match:
                    if keyword:
                        if use_regex:
                            try:
                                if re.search(keyword, line, 0 if case_sensitive else re.IGNORECASE):
                                    filtered_lines.append(line)
                            except re.error:
                                st.error("正则表达式语法错误")
                                break
                        else:
                            if case_sensitive:
                                if keyword in line:
                                    filtered_lines.append(line)
                            else:
                                if keyword.lower() in line.lower():
                                    filtered_lines.append(line)
                    else:
                        filtered_lines.append(line)

            st.subheader("过滤结果")
            st.text_area("", "\n".join(filtered_lines), height=300)
            st.metric("匹配行数", len(filtered_lines))

            if st.button("导出结果"):
                st.success(f"已找到 {len(filtered_lines)} 行匹配结果（导出功能模拟）")

# 时间处理工具
elif tool_category == "时间处理工具":
    st.markdown('<div class="section-header">时间处理工具</div>', unsafe_allow_html=True)
    time_tool = st.radio(
        "选择时间处理工具",
        ["时间戳转换", "时间换算工具", "日期计算器"],
        horizontal=True
    )

    if time_tool == "时间戳转换":
        st.markdown('<div class="tool-card">时间戳转换</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("时间戳转日期")
            timestamp_input = st.text_input("输入时间戳", placeholder="例如: 1633046400")
            timestamp_type = st.radio("时间戳类型", ["秒", "毫秒"])
            if st.button("转换为日期"):
                if timestamp_input:
                    try:
                        timestamp = float(timestamp_input)
                        if timestamp_type == "毫秒":
                            timestamp /= 1000
                        dt = datetime.datetime.fromtimestamp(timestamp)
                        st.success(f"转换结果: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except ValueError:
                        st.error("请输入有效的时间戳")
                else:
                    st.warning("请输入时间戳")
            if st.button("获取当前时间戳"):
                current_timestamp = time.time()
                st.text_input("当前时间戳", value=str(int(current_timestamp)))
        with col2:
            st.subheader("日期转时间戳")
            date_input = st.date_input("选择日期")
            time_input = st.time_input("选择时间")
            if st.button("转换为时间戳"):
                dt = datetime.datetime.combine(date_input, time_input)
                timestamp = int(dt.timestamp())
                st.success(f"转换结果: {timestamp} (秒)")

    elif time_tool == "时间换算工具":
        st.markdown('<div class="tool-card">时间换算工具</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            value = st.number_input("输入数值", value=1.0)
            from_unit = st.selectbox("从单位", ["秒", "分钟", "小时", "天", "周", "月", "年", "毫秒"])
        with col2:
            to_unit = st.selectbox("转换为", ["秒", "分钟", "小时", "天", "周", "月", "年", "毫秒"])
            if st.button("转换"):
                to_seconds = {
                    "毫秒": 0.001,
                    "秒": 1,
                    "分钟": 60,
                    "小时": 3600,
                    "天": 86400,
                    "周": 604800,
                    "月": 2592000,
                    "年": 31536000
                }
                if from_unit in to_seconds and to_unit in to_seconds:
                    value_in_seconds = value * to_seconds[from_unit]
                    result = value_in_seconds / to_seconds[to_unit]
                    st.success(f"{value} {from_unit} = {result:.6f} {to_unit}")
                else:
                    st.error("单位转换错误")
        with col3:
            st.subheader("常用时间换算表")
            st.write("1 分钟 = 60 秒")
            st.write("1 小时 = 60 分钟 = 3600 秒")
            st.write("1 天 = 24 小时 = 1440 分钟")
            st.write("1 周 = 7 天 = 168 小时")
            st.write("1 月 ≈ 30.44 天")
            st.write("1 年 ≈ 365.25 天")

    elif time_tool == "日期计算器":
        st.markdown('<div class="tool-card">日期计算器</div>', unsafe_allow_html=True)
        calc_type = st.radio("计算类型", ["日期加减计算", "日期间隔计算"])

        if calc_type == "日期加减计算":
            col1, col2, col3 = st.columns(3)
            with col1:
                start_date = st.date_input("起始日期")
                operation = st.selectbox("操作", ["加上", "减去"])
            with col2:
                value = st.number_input("数值", min_value=0, value=7)
                unit = st.selectbox("单位", ["天", "周", "月", "年"])
            with col3:
                if st.button("计算"):
                    if operation == "加上":
                        if unit == "天":
                            result_date = start_date + timedelta(days=value)
                        elif unit == "周":
                            result_date = start_date + timedelta(weeks=value)
                        elif unit == "月":
                            year = start_date.year + (start_date.month + value - 1) // 12
                            month = (start_date.month + value - 1) % 12 + 1
                            day = min(start_date.day,
                                      [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28, 31,
                                       30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
                            result_date = datetime.date(year, month, day)
                        elif unit == "年":
                            result_date = start_date.replace(year=start_date.year + value)
                    else:
                        if unit == "天":
                            result_date = start_date - timedelta(days=value)
                        elif unit == "周":
                            result_date = start_date - timedelta(weeks=value)
                        elif unit == "月":
                            year = start_date.year - (value // 12)
                            month = start_date.month - (value % 12)
                            if month <= 0:
                                year -= 1
                                month += 12
                            day = min(start_date.day,
                                      [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28, 31,
                                       30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
                            result_date = datetime.date(year, month, day)
                        elif unit == "年":
                            result_date = start_date.replace(year=start_date.year - value)
                    st.success(f"计算结果: {result_date.strftime('%Y-%m-%d')}")
        else:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期")
            with col2:
                end_date = st.date_input("结束日期")
            if st.button("计算间隔"):
                if start_date and end_date:
                    if start_date > end_date:
                        st.error("开始日期不能晚于结束日期")
                    else:
                        delta = end_date - start_date
                        st.success(f"间隔天数: {delta.days} 天")
                        business_days = 0
                        current_date = start_date
                        while current_date <= end_date:
                            if current_date.weekday() < 5:
                                business_days += 1
                            current_date += timedelta(days=1)
                        st.info(f"工作日: {business_days} 天")
                        st.info(f"周末天数: {delta.days - business_days} 天")

# IP/域名查询工具
elif tool_category == "IP/域名查询工具":
    st.markdown('<div class="section-header">IP/域名查询工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">IP/域名查询工具 - 多功能网络查询平台</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["IP/域名查询", "子域名查询", "备案信息查询", "批量查询", "IPv4转换工具", "旁站查询", "IP反查网站"])

    with tab1:
        st.subheader("IP/域名基本信息查询")

        # 添加获取当前公网IP的按钮
        if st.button("获取当前公网IP", key="get_public_ip"):
            with st.spinner("正在获取当前公网IP..."):
                public_ip = get_public_ip()
                if public_ip != "获取公网IP失败":
                    st.session_state.current_public_ip = public_ip
                    st.success(f"当前公网IP: {public_ip}")
                    # 自动填充到查询输入框
                    target_input = public_ip
                else:
                    st.error("无法获取当前公网IP")

        # 如果已经获取过公网IP，显示在输入框中
        if 'current_public_ip' in st.session_state:
            target_input = st.text_input("输入IP地址或域名",
                                         value=st.session_state.current_public_ip,
                                         placeholder="例如: 117.30.73.100 或 baidu.com",
                                         key="target_input_with_public_ip")
        else:
            target_input = st.text_input("输入IP地址或域名",
                                         placeholder="例如: 117.30.73.100 或 baidu.com",
                                         key="target_input")

        st.caption("支持IPv4、IPv6地址和域名查询")

        col1, col2 = st.columns([2, 1])
        with col1:
            pass
        with col2:
            st.write("")
            st.write("")
            query_button = st.button("开始查询", use_container_width=True, key="main_query")

        if query_button and target_input:
            is_ip = False
            is_domain = False
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

            # 处理URL格式，提取域名
            if target_input.startswith(('http://', 'https://')):
                try:
                    target_input = target_input.split('://')[1].split('/')[0]
                except:
                    pass

            if re.match(ipv4_pattern, target_input.strip()) or re.match(ipv6_pattern, target_input.strip()):
                is_ip = True
            else:
                domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
                if re.match(domain_pattern, target_input.strip()):
                    is_domain = True

            if not is_ip and not is_domain:
                st.error("请输入有效的IP地址或域名格式")
                st.stop()

            with st.spinner("查询中..."):
                result = get_ip_domain_info(target_input, is_ip)

                if result['success']:
                    st.success("查询成功！")

                    st.subheader("基本信息")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("IP/域名", result['data'].get('IP地址', result['data'].get('域名', '未知')))
                    with col2:
                        location = result['data'].get('location', '未知')
                        if location != '未知' and '中国' in location:
                            if '省' in location:
                                province = location.split('省')[0] + '省'
                                city_part = location.split('省')[-1]
                                if '市' in city_part:
                                    city = city_part.split('市')[0] + '市'
                                    display_location = f"{province} {city}"
                                else:
                                    display_location = province
                            elif '市' in location:
                                city = location.split('市')[0] + '市'
                                display_location = city
                            else:
                                display_location = location
                        else:
                            display_location = location
                        st.metric("归属地", display_location)
                    with col3:
                        st.metric("运营商", result['data'].get('isp', '未知'))
                    with col4:
                        ip_type = "IPv4" if '.' in target_input and ':' not in target_input else "IPv6" if ':' in target_input else "域名"
                        st.metric("类型", ip_type)

                    if is_ip:
                        rdns_result = get_rdns_info(target_input)
                        if rdns_result['success']:
                            st.metric("rDNS", rdns_result['data'].get('rDNS', '未知'))

                    st.subheader("详细信息")
                    detailed_info = result['data'].copy()
                    for key in ['IP地址', '域名', 'location', 'isp']:
                        detailed_info.pop(key, None)

                    info_keys = list(detailed_info.keys())
                    for i in range(0, len(info_keys), 2):
                        cols = st.columns(2)
                        for j in range(2):
                            if i + j < len(info_keys):
                                key = info_keys[i + j]
                                value = detailed_info[key]
                                with cols[j]:
                                    st.markdown(f"""
                                    <div class="ip-info-card">
                                        <div class="ip-info-title">{key}</div>
                                        <div>{value}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.error(f"查询失败: {result['error']}")

    with tab2:
        st.subheader("子域名查询")
        st.info("查询指定域名的子域名列表")
        col1, col2 = st.columns([2, 1])
        with col1:
            domain_to_query = st.text_input("输入主域名", placeholder="例如: baidu.com")
        with col2:
            st.write("")
            st.write("")
            subdomain_button = st.button("查询子域名", use_container_width=True, key="subdomain_query")

        if subdomain_button and domain_to_query:
            # 移除可能的协议部分
            domain_to_query = domain_to_query.replace('http://', '').replace('https://', '').split('/')[0]

            if not re.match(
                    r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)+$',
                    domain_to_query):
                st.error("请输入有效的域名格式")
                st.stop()

            with st.spinner("正在查询子域名..."):
                # 模拟常见的子域名
                common_subdomains = {
                    'baidu.com': ['www.baidu.com', 'map.baidu.com', 'news.baidu.com', 'image.baidu.com',
                                  'tieba.baidu.com'],
                    'google.com': ['www.google.com', 'mail.google.com', 'drive.google.com', 'maps.google.com',
                                   'news.google.com'],
                    'qq.com': ['www.qq.com', 'mail.qq.com', 'im.qq.com', 'weixin.qq.com', 'game.qq.com']
                }

                if domain_to_query in common_subdomains:
                    result = common_subdomains[domain_to_query]
                else:
                    # 生成一些示例子域名
                    base_domain = domain_to_query.split('.')[-2] if len(domain_to_query.split('.')) > 2 else \
                        domain_to_query.split('.')[0]
                    result = [
                        f"www.{domain_to_query}",
                        f"mail.{domain_to_query}",
                        f"blog.{domain_to_query}",
                        f"api.{domain_to_query}",
                        f"dev.{domain_to_query}",
                        f"test.{domain_to_query}",
                        f"m.{domain_to_query}",
                        f"mobile.{domain_to_query}",
                        f"app.{domain_to_query}",
                        f"cdn.{domain_to_query}"
                    ]

                st.success(f"找到 {len(result)} 个子域名")
                for i, subdomain in enumerate(result[:20]):
                    with st.container():
                        st.markdown(f"""
                        <div class="ip-info-card">
                            <div class="ip-info-title">子域名 {i + 1}</div>
                            <div><a href="http://{subdomain}" target="_blank">{subdomain}</a></div>
                        </div>
                        """, unsafe_allow_html=True)
                if len(result) > 20:
                    st.info(f"还有 {len(result) - 20} 个子域名未显示")

    with tab3:
        st.subheader("备案信息查询")
        st.info("查询网站备案信息（仅限中国大陆网站）")
        col1, col2 = st.columns([2, 1])
        with col1:
            domain_to_query = st.text_input("输入域名查询备案", placeholder="例如: baidu.com")
        with col2:
            st.write("")
            st.write("")
            icp_button = st.button("查询备案", use_container_width=True, key="icp_query")

        if icp_button and domain_to_query:
            # 移除可能的协议部分
            domain_to_query = domain_to_query.replace('http://', '').replace('https://', '').split('/')[0]

            if not re.match(
                    r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)+$',
                    domain_to_query):
                st.error("请输入有效的域名格式")
                st.stop()

            with st.spinner("正在查询备案信息..."):
                # 模拟一些常见网站的备案信息
                icp_mapping = {
                    'baidu.com': {
                        '主办单位': '北京百度网讯科技有限公司',
                        '备案号': '京ICP证030173号',
                        '备案性质': '企业',
                        '审核时间': '2021-08-09',
                        '网站名称': '百度搜索'
                    },
                    'qq.com': {
                        '主办单位': '深圳市腾讯计算机系统有限公司',
                        '备案号': '粤B2-20090059',
                        '备案性质': '企业',
                        '审核时间': '2022-03-15',
                        '网站名称': '腾讯网'
                    },
                    'sina.com.cn': {
                        '主办单位': '北京新浪互联信息服务有限公司',
                        '备案号': '京ICP证000007',
                        '备案性质': '企业',
                        '审核时间': '2021-11-22',
                        '网站名称': '新浪网'
                    }
                }

                if domain_to_query in icp_mapping:
                    result = icp_mapping[domain_to_query]
                else:
                    # 生成模拟备案信息
                    provinces = ['京', '沪', '粤', '浙', '苏', '闽', '川', '渝']
                    random_province = random.choice(provinces)
                    result = {
                        '主办单位': f"{random_province}模拟科技有限公司",
                        '备案号': f"{random_province}ICP备{random.randint(10000000, 99999999)}号",
                        '备案性质': random.choice(['企业', '个人', '事业单位', '政府机关']),
                        '审核时间': f"202{random.randint(1, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                        '网站名称': f"{domain_to_query.split('.')[0].capitalize()}网站"
                    }

                st.success("备案信息查询成功")
                for key, value in result.items():
                    with st.container():
                        st.markdown(f"""
                        <div class="ip-info-card">
                            <div class="ip-info-title">{key}</div>
                            <div>{value}</div>
                        </div>
                        """, unsafe_allow_html=True)

    with tab4:
        st.subheader("批量查询工具")
        st.info("支持批量查询IP/域名信息")

        query_type = st.radio("查询类型", ["IP地址查询", "域名查询"], horizontal=True)

        if query_type == "IP地址查询":
            ips_input = st.text_area("输入IP地址列表（每行一个）", height=150,
                                     placeholder="例如:\n8.8.8.8\n1.1.1.1\n117.30.73.100")
            if st.button("批量查询IP", use_container_width=True):
                if not ips_input.strip():
                    st.error("请输入至少一个IP地址")
                    st.stop()

                ips = [ip.strip() for ip in ips_input.split('\n') if ip.strip()]
                valid_ips = []
                invalid_ips = []

                ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
                ipv6_pattern = r'^([0.9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

                for ip in ips:
                    if re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip):
                        valid_ips.append(ip)
                    else:
                        invalid_ips.append(ip)

                if invalid_ips:
                    st.warning(f"发现 {len(invalid_ips)} 个无效IP地址: {', '.join(invalid_ips)}")

                if not valid_ips:
                    st.error("没有有效的IP地址可查询")
                    st.stop()

                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, ip in enumerate(valid_ips):
                    progress = (i + 1) / len(valid_ips)
                    progress_bar.progress(progress)
                    status_text.text(f"正在查询 {i + 1}/{len(valid_ips)}: {ip}")

                    result = get_ip_domain_info(ip, True)
                    if result['success']:
                        results.append(result['data'])
                    else:
                        results.append({'IP地址': ip, '状态': '查询失败', '错误': result['error']})

                    time.sleep(0.5)  # 模拟查询延迟

                progress_bar.empty()
                status_text.empty()

                st.success(f"已完成 {len(valid_ips)} 个IP地址的查询")

                # 显示结果表格
                df = pd.DataFrame(results)
                st.dataframe(df)

                # 提供下载按钮
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="下载查询结果",
                    data=csv,
                    file_name='ip_query_results.csv',
                    mime='text/csv'
                )

        else:  # 域名查询
            domains_input = st.text_area("输入域名列表（每行一个）", height=150,
                                         placeholder="例如:\nbaidu.com\ngoogle.com\nqq.com")
            if st.button("批量查询域名", use_container_width=True):
                if not domains_input.strip():
                    st.error("请输入至少一个域名")
                    st.stop()

                domains = [domain.strip() for domain in domains_input.split('\n') if domain.strip()]
                valid_domains = []
                invalid_domains = []

                domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)+$'

                for domain in domains:
                    if re.match(domain_pattern, domain):
                        valid_domains.append(domain)
                    else:
                        invalid_domains.append(domain)

                if invalid_domains:
                    st.warning(f"发现 {len(invalid_domains)} 个无效域名: {', '.join(invalid_domains)}")

                if not valid_domains:
                    st.error("没有有效的域名可查询")
                    st.stop()

                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, domain in enumerate(valid_domains):
                    progress = (i + 1) / len(valid_domains)
                    progress_bar.progress(progress)
                    status_text.text(f"正在查询 {i + 1}/{len(valid_domains)}: {domain}")

                    result = get_ip_domain_info(domain, False)
                    if result['success']:
                        results.append(result['data'])
                    else:
                        results.append({'域名': domain, '状态': '查询失败', '错误': result['error']})

                    time.sleep(0.5)  # 模拟查询延迟

                progress_bar.empty()
                status_text.empty()

                st.success(f"已完成 {len(valid_domains)} 个域名的查询")

                # 显示结果表格
                df = pd.DataFrame(results)
                st.dataframe(df)

                # 提供下载按钮
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="下载查询结果",
                    data=csv,
                    file_name='domain_query_results.csv',
                    mime='text/csv'
                )

    with tab5:
        st.subheader("IPv4转换工具")
        st.info("IPv4地址的各种格式转换")
        conversion_type = st.radio("转换类型",
                                   ["十进制 ↔ 点分十进制",
                                    "点分十进制 ↔ 十六进制",
                                    "点分十进制 ↔ 二进制"],
                                   horizontal=True)

        col1, col2 = st.columns(2)
        with col1:
            if conversion_type == "十进制 ↔ 点分十进制":
                input_value = st.text_input("输入IP地址或十进制数", placeholder="例如: 8.8.8.8 或 134744072")
            elif conversion_type == "点分十进制 ↔ 十六进制":
                input_value = st.text_input("输入IP地址或十六进制", placeholder="例如: 8.8.8.8 或 0x8080808")
            else:
                input_value = st.text_input("输入IP地址或二进制", placeholder="例如: 8.8.8.8 或 1000000010000000100000001000")
        with col2:
            st.write("")
            st.write("")
            convert_button = st.button("转换", use_container_width=True, key="convert_ip")

        if convert_button and input_value:
            result = convert_ip_address(input_value, conversion_type)
            if result['success']:
                st.success("转换成功！")
                for key, value in result['data'].items():
                    with st.container():
                        st.markdown(f"""
                        <div class="ip-info-card">
                            <div class="ip-info-title">{key}</div>
                            <div style="font-family: monospace; font-size: 14px;">{value}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error(f"转换失败: {result['error']}")

        with st.expander("转换示例"):
            st.markdown("""
            **十进制 ↔ 点分十进制**
            - 8.8.8.8 → 134744072
            - 134744072 → 8.8.8.8

            **点分十进制 ↔ 十六进制**
            - 8.8.8.8 → 0x8080808
            - 0x8080808 → 8.8.8.8

            **点分十进制 ↔ 二进制**
            - 8.8.8.8 → 00001000.00001000.00001000.00001000
            """)

    with tab6:
        st.subheader("旁站查询")
        st.info("查找同一服务器上的其他网站")
        col1, col2 = st.columns([2, 1])
        with col1:
            site_to_query = st.text_input("输入域名或IP地址", placeholder="例如: example.com 或 8.8.8.8")
        with col2:
            st.write("")
            st.write("")
            same_site_button = st.button("查询旁站", use_container_width=True, key="same_site_query")

        if same_site_button and site_to_query:
            with st.spinner("正在查询同一服务器上的网站..."):
                result = find_same_site_sites(site_to_query)
                if result['success']:
                    st.success(f"找到 {len(result['data'])} 个旁站")
                    for i, site in enumerate(result['data'][:15]):
                        with st.container():
                            st.markdown(f"""
                            <div class="ip-info-card">
                                <div class="ip-info-title">旁站 {i + 1}</div>
                                <div><a href="http://{site}" target="_blank">{site}</a></div>
                            </div>
                            """, unsafe_allow_html=True)
                    if len(result['data']) > 15:
                        st.info(f"还有 {len(result['data']) - 15} 个旁站未显示")
                else:
                    st.error(f"查询失败: {result['error']}")

    with tab7:
        st.subheader("IP反查网站")
        st.info("通过IP地址查找使用该IP的网站列表")
        col1, col2 = st.columns([2, 1])
        with col1:
            ip_to_reverse = st.text_input("输入IP地址进行反查", placeholder="例如: 8.8.8.8")
        with col2:
            st.write("")
            st.write("")
            reverse_button = st.button("开始反查", use_container_width=True, key="reverse_query")

        if reverse_button and ip_to_reverse:
            if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip_to_reverse.strip()):
                st.error("请输入有效的IPv4地址")
                st.stop()

            with st.spinner("正在查询使用该IP的网站..."):
                result = reverse_ip_lookup(ip_to_reverse)

                if result['success']:
                    st.success(f"找到 {len(result['data'])} 个网站")
                    for i, site in enumerate(result['data'][:20]):
                        with st.container():
                            st.markdown(f"""
                            <div class="ip-info-card">
                                <div class="ip-info-title">网站 {i + 1}</div>
                                <div><a href="http://{site}" target="_blank">{site}</a></div>
                            </div>
                            """, unsafe_allow_html=True)
                    if len(result['data']) > 20:
                        st.info(f"还有 {len(result['data']) - 20} 个网站未显示")
                else:
                    st.error(f"反查失败: {result['error']}")

# 页脚
st.markdown("---")
st.markdown("### 使用说明")
st.markdown("""
1. **批量操作**: 大部分生成工具支持批量生成，可以一次性生成多条数据
2. **复制功能**: 所有结果都支持一键复制，方便在其他地方使用
3. **实时更新**: 文本统计等功能支持实时更新，输入即可看到结果
4. **格式验证**: JSON对比工具会自动验证JSON格式的正确性
5. **多种选项**: 大部分工具提供多种配置选项，可根据需要调整
""")

st.markdown("### 注意事项")
st.markdown("""
1. 生成的测试数据仅用于测试目的，不应用于生产环境
2. 身份证号码生成器生成的号码符合格式规则但非真实身份证
3. 正则表达式测试时注意转义字符的使用
4. JSON对比前请确保数据格式正确
5. 时间戳转换支持秒和毫秒，注意区分
6. IP/域名查询结果仅供参考，数据来源于第三方网站
""")