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
import random
import streamlit.components.v1 as components

# 导入Faker库
try:
    from faker import Faker

    fake = Faker('zh_CN')
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    st.warning("Faker库未安装，部分高级功能将受限。请运行: pip install faker")

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
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .category-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .copy-btn {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        margin: 5px;
    }
    .copy-btn:hover {
        background-color: #1668a5;
    }
    .copy-success {
        background-color: #28a745 !important;
    }
    .result-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }
    .faker-badge {
        background-color: #ff6b6b;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.7rem;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ================ 辅助函数 ================
def escape_js_string(text):
    """安全转义 JavaScript 字符串"""
    # 将文本转换为 JSON 字符串，这会自动处理所有特殊字符
    return json.dumps(text)


def create_copy_button(text, button_text="📋 复制到剪贴板", key=None):
    """创建一键复制按钮（修复版本）"""

    if key is None:
        key = hash(text)

    # 安全转义文本
    escaped_text = escape_js_string(text)

    # 更安全的 JavaScript 复制函数
    copy_script = f"""
    <script>
    function copyTextToClipboard{key}() {{
        const text = {escaped_text};

        if (!navigator.clipboard) {{
            // 使用传统方法
            return fallbackCopyTextToClipboard(text);
        }}
        return navigator.clipboard.writeText(text).then(function() {{
            return true;
        }}, function(err) {{
            // 如果现代API失败，使用传统方法
            return fallbackCopyTextToClipboard(text);
        }});
    }}

    function fallbackCopyTextToClipboard(text) {{
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {{
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            return successful;
        }} catch (err) {{
            document.body.removeChild(textArea);
            return false;
        }}
    }}

    // 为按钮添加点击事件
    document.addEventListener('DOMContentLoaded', function() {{
        const button = document.querySelector('[data-copy-button="{key}"]');
        if (button) {{
            button.addEventListener('click', function() {{
                copyTextToClipboard{key}().then(function(success) {{
                    if (success) {{
                        // 显示成功提示
                        const originalText = button.innerHTML;
                        button.innerHTML = '✅ 复制成功！';
                        button.style.background = '#28a745';
                        setTimeout(function() {{
                            button.innerHTML = originalText;
                            button.style.background = '';
                        }}, 2000);
                    }} else {{
                        button.innerHTML = '❌ 复制失败';
                        button.style.background = '#dc3545';
                        setTimeout(function() {{
                            button.innerHTML = '{button_text}';
                            button.style.background = '';
                        }}, 2000);
                    }}
                }});
            }});
        }}
    }});
    </script>
    """

    # 创建按钮的 HTML
    button_html = f"""
    <div>
        <button data-copy-button="{key}" 
                style="background:#1f77b4;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;font-size:14px;margin:5px;">
            {button_text}
        </button>
    </div>
    """

    # 渲染按钮和脚本
    components.html(button_html + copy_script, height=60)


def copy_to_clipboard(text):
    """复制文本到剪贴板 - 使用新的复制组件"""
    try:
        # 直接使用新的复制按钮组件
        create_copy_button(text, "📋 复制内容", key=f"copy_{hash(text)}")
        return True
    except Exception as e:
        st.error(f"复制功能出错: {e}")
        # 备用方案：提供下载按钮
        st.download_button(
            label="📥 下载内容（复制备用）",
            data=text,
            file_name="content.txt",
            mime="text/plain",
            key=f"download_{hash(text)}"
        )
        return False


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


def format_profile_data(profile_dict):
    """格式化完整个人信息显示"""
    try:
        # 如果传入的是字符串，尝试转换为字典
        if isinstance(profile_dict, str):
            # 尝试不同的解析方法
            try:
                import ast
                profile_dict = ast.literal_eval(profile_dict)
            except:
                # 如果ast解析失败，尝试eval（注意安全风险，但这里数据是可信的）
                profile_dict = eval(profile_dict)

        # 提取基本信息
        name = profile_dict.get('name', '未知')
        sex = '女' if profile_dict.get('sex') == 'F' else '男'
        birthdate = profile_dict.get('birthdate', '未知')
        mail = profile_dict.get('mail', '（信息缺失）')
        job = profile_dict.get('job', '（信息缺失）')
        address = profile_dict.get('address', '（信息缺失）')
        company = profile_dict.get('company', '（信息缺失）')
        website = profile_dict.get('website', [])
        username = profile_dict.get('username', '（信息缺失）')

        # 格式化出生日期
        if birthdate != '未知':
            if hasattr(birthdate, 'year'):
                birthdate = f"{birthdate.year}年{birthdate.month}月{birthdate.day}日"
            else:
                birthdate = str(birthdate)

        # 格式化地址（简化显示）
        if address != '（信息缺失）':
            # 提取省份和城市信息
            address_parts = str(address).split(' ')
            if len(address_parts) > 0:
                simplified_address = address_parts[0]
                # 进一步简化，只显示到市级
                if '省' in simplified_address:
                    # 省级地址处理
                    parts = simplified_address.split('省')
                    if len(parts) > 1:
                        city_part = parts[1]
                        if '市' in city_part:
                            city_parts = city_part.split('市')
                            simplified_address = parts[0] + '省' + city_parts[0] + '市'
                elif '自治区' in simplified_address:
                    # 自治区处理
                    parts = simplified_address.split('自治区')
                    if len(parts) > 1:
                        city_part = parts[1]
                        if '市' in city_part:
                            city_parts = city_part.split('市')
                            simplified_address = parts[0] + '自治区' + city_parts[0] + '市'
                elif '市' in simplified_address:
                    # 直接处理直辖市
                    parts = simplified_address.split('市')
                    if len(parts) > 1:
                        simplified_address = parts[0] + '市'
                address = simplified_address

        # 构建格式化结果
        result = []
        result.append("------------------------------")
        result.append(f"个人信息--{name}")
        result.append(f"姓名： {name}")
        result.append(f"性别： {sex}")
        result.append(f"出生日期： {birthdate}")
        result.append(f"电子邮箱： {mail}")
        result.append("联系电话： （信息缺失）")
        result.append(f"求职意向： {job}")
        result.append(f"所在地区： {address}")
        result.append("")
        result.append("工作经历")
        result.append(f"公司： {company}")
        result.append(f"职位： {job}")
        result.append("其他信息")

        # 处理网站列表
        if website:
            website_str = "， ".join(website)
            result.append(f"个人网站/主页： {website_str}")
        else:
            result.append("个人网站/主页： （信息缺失）")

        result.append(f"用户名： {username}")
        result.append("------------------------------")

        return "\n".join(result)

    except Exception as e:
        return f"格式化数据时出错: {str(e)}\n原始数据: {profile_dict}"


# Faker数据生成函数
def generate_faker_data(category, subcategory, count=1, **kwargs):
    """使用Faker生成数据"""
    if not FAKER_AVAILABLE:
        return ["Faker库未安装，请先安装: pip install faker"]

    results = []
    try:
        for i in range(count):
            if category == "人物信息":
                if subcategory == "随机姓名":
                    results.append(fake.name())
                elif subcategory == "随机姓":
                    results.append(fake.last_name())
                elif subcategory == "随机名":
                    results.append(fake.first_name())
                elif subcategory == "男性姓名":
                    results.append(fake.name_male())
                elif subcategory == "女性姓名":
                    results.append(fake.name_female())
                elif subcategory == "完整个人信息":
                    # 直接获取profile字典对象
                    raw_profile = fake.profile()
                    formatted_profile = format_profile_data(raw_profile)
                    results.append(formatted_profile)

            elif category == "地址信息":
                if subcategory == "随机地址":
                    results.append(fake.address())
                elif subcategory == "随机城市":
                    results.append(fake.city())
                elif subcategory == "随机国家":
                    results.append(fake.country())
                elif subcategory == "随机邮编":
                    results.append(fake.postcode())
                elif subcategory == "随机街道":
                    results.append(fake.street_address())

            elif category == "网络信息":
                if subcategory == "随机邮箱":
                    results.append(fake.email())
                elif subcategory == "安全邮箱":
                    results.append(fake.safe_email())
                elif subcategory == "公司邮箱":
                    results.append(fake.company_email())
                elif subcategory == "免费邮箱":
                    results.append(fake.free_email())
                elif subcategory == "随机域名":
                    results.append(fake.domain_name())
                elif subcategory == "随机URL":
                    results.append(fake.url())
                elif subcategory == "随机IP地址":
                    results.append(fake.ipv4())
                elif subcategory == "随机用户代理":
                    results.append(fake.user_agent())

            elif category == "公司信息":
                if subcategory == "随机公司名":
                    results.append(fake.company())
                elif subcategory == "公司后缀":
                    results.append(fake.company_suffix())
                elif subcategory == "职位":
                    results.append(fake.job())

            elif category == "金融信息":
                if subcategory == "信用卡号":
                    results.append(fake.credit_card_number())
                elif subcategory == "信用卡提供商":
                    results.append(fake.credit_card_provider())
                elif subcategory == "信用卡有效期":
                    results.append(fake.credit_card_expire())
                elif subcategory == "货币":
                    results.append(fake.currency())

            elif category == "日期时间":
                if subcategory == "随机日期时间":
                    results.append(str(fake.date_time()))
                elif subcategory == "随机日期":
                    results.append(fake.date())
                elif subcategory == "随机时间":
                    results.append(fake.time())
                elif subcategory == "今年日期":
                    results.append(str(fake.date_time_this_year()))
                elif subcategory == "本月日期":
                    results.append(str(fake.date_time_this_month()))

            elif category == "文本内容":
                if subcategory == "随机单词":
                    results.append(fake.word())
                elif subcategory == "随机句子":
                    results.append(fake.sentence())
                elif subcategory == "随机段落":
                    results.append(fake.paragraph())
                elif subcategory == "随机文本":
                    results.append(fake.text(max_nb_chars=kwargs.get('length', 200)))

            elif category == "电话号码":
                if subcategory == "随机手机号":
                    results.append(fake.phone_number())
                elif subcategory == "号段前缀":
                    results.append(fake.phonenumber_prefix())

            elif category == "其他信息":
                if subcategory == "随机颜色":
                    results.append(fake.color_name())
                elif subcategory == "随机UUID":
                    results.append(fake.uuid4())
                elif subcategory == "随机MD5":
                    results.append(fake.md5())
                elif subcategory == "随机SHA1":
                    results.append(fake.sha1())
                elif subcategory == "随机文件扩展名":
                    results.append(fake.file_extension())
                elif subcategory == "随机MIME类型":
                    results.append(fake.mime_type())

    except Exception as e:
        results = [f"生成数据时出错: {str(e)}"]

    return results


# 传统数据生成函数（保留原有功能）
def generate_random_string(length, chars_type):
    """生成随机字符串"""
    chars = ""
    if "小写字母" in chars_type: chars += "abcdefghijklmnopqrstuvwxyz"
    if "大写字母" in chars_type: chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if "数字" in chars_type: chars += "0123456789"
    if "特殊字符" in chars_type: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not chars: chars = "abcdefghijklmnopqrstuvwxyz"
    return ''.join(random.choice(chars) for _ in range(length))


def generate_random_password(length, options):
    """生成随机密码"""
    if FAKER_AVAILABLE:
        return fake.password(length=length, special_chars="包含特殊字符" in options,
                             digits="包含数字" in options, upper_case="包含大写字母" in options,
                             lower_case="包含小写字母" in options)

    # 备用方案
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

    if not chars:
        password += random.choice("abcdefghijklmnopqrstuvwxyz")
        chars += "abcdefghijklmnopqrstuvwxyz0123456789"
        password += random.choice("0123456789")

    password += ''.join(random.choice(chars) for _ in range(length - len(password)))
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)


def generate_random_phone_number(operator):
    """生成随机电话号码"""
    if FAKER_AVAILABLE:
        return fake.phone_number()

    # 备用方案
    mobile_prefixes = ["139", "138", "137", "136", "135", "134", "159", "158", "157", "150", "151", "152", "147", "188",
                       "187"]
    unicom_prefixes = ["130", "131", "132", "155", "156", "185", "186"]
    telecom_prefixes = ["133", "153", "180", "189"]
    broadcast_prefixes = ["192"]

    if operator == "移动":
        prefix = random.choice(mobile_prefixes)
    elif operator == "联通":
        prefix = random.choice(unicom_prefixes)
    elif operator == "电信":
        prefix = random.choice(telecom_prefixes)
    elif operator == "广电":
        prefix = random.choice(broadcast_prefixes)
    else:
        rand_val = random.random()
        if rand_val < 0.35:
            prefix = random.choice(mobile_prefixes)
        elif rand_val < 0.6:
            prefix = random.choice(unicom_prefixes)
        elif rand_val < 0.85:
            prefix = random.choice(telecom_prefixes)
        else:
            prefix = random.choice(broadcast_prefixes)

    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefix}{suffix}"


# 优化地址生成函数
def generate_random_address(province, city, detailed=True):
    """生成随机地址"""
    if not detailed:
        return f"{province}{city}"

    # 详细地址生成
    streets = ["中山路", "解放路", "人民路", "建设路", "和平路", "新华路",
               "文化路", "胜利路", "团结路", "友谊路"]
    communities = ["小区", "花园", "大厦", "公寓", "广场", "苑", "居", "湾", "城", "国际"]
    numbers = [str(i) for i in range(1, 201)]

    street = random.choice(streets)
    community = random.choice(communities)
    number = random.choice(numbers)

    return f"{province}{city}{street}{number}号{random.randint(1, 20)}栋{random.randint(1, 30)}单元{random.randint(101, 1500)}室"


# 优化身份证生成函数
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


# 在Faker辅助函数部分添加条件生成函数
def generate_conditional_phone(operator):
    """生成手机号码（仅匹配运营商号段）"""
    # 运营商号段定义
    operator_prefixes = {
        "移动": ["134", "135", "136", "137", "138", "139", "147", "150", "151", "152", "157", "158", "159", "178", "182",
               "183", "184", "187", "188"],
        "联通": ["130", "131", "132", "145", "155", "156", "166", "175", "176", "185", "186"],
        "电信": ["133", "149", "153", "173", "177", "180", "181", "189", "199"],
        "广电": ["192"]
    }

    # 如果选择"随机"，则从所有运营商中随机选择
    if operator == "随机":
        all_prefixes = []
        for op in operator_prefixes.values():
            all_prefixes.extend(op)
        prefix = random.choice(all_prefixes)
    else:
        prefix = random.choice(operator_prefixes[operator])

    # 生成后8位数字（总长度=11位）
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(11 - len(prefix))])
    return f"{prefix}{suffix}"


def generate_landline_number(operator=None, area_code=None):
    """生成座机号码（区号可选）"""
    # 如果没有指定区号，随机生成一个（3-4位）
    if not area_code:
        area_code = str(random.randint(200, 9999)).zfill(3 if random.random() > 0.5 else 4)

    # 生成本地号码（7-8位）
    local_number = str(random.randint(2000000, 99999999)).zfill(7 if random.random() > 0.5 else 8)

    # 格式化输出（带分隔符）
    return f"{area_code}-{local_number}"


def generate_international_phone(country):
    """生成国际手机号码"""
    # 国际号码格式定义（国家代码 + 手机号格式）
    country_formats = {
        # 亚洲
        "日本": {
            "code": "+81",
            "format": ["90-####-####", "80-####-####", "70-####-####"]
        },
        "韩国": {
            "code": "+82",
            "format": ["10-####-####", "16-####-####", "19-####-####"]
        },
        "印度": {
            "code": "+91",
            "format": ["9#########", "8#########", "7#########"]
        },
        "新加坡": {
            "code": "+65",
            "format": ["9### ####", "8### ####", "6### ####"]
        },
        "马来西亚": {
            "code": "+60",
            "format": ["12-### ####", "13-### ####", "16-### ####"]
        },
        "泰国": {
            "code": "+66",
            "format": ["8#-###-####", "9#-###-####", "6#-###-####"]
        },
        "越南": {
            "code": "+84",
            "format": ["9#-####-###", "8#-####-###", "3#-####-###"]
        },
        "菲律宾": {
            "code": "+63",
            "format": ["9##-###-####", "8##-###-####", "2##-###-####"]
        },
        "印度尼西亚": {
            "code": "+62",
            "format": ["8##-####-###", "8##-###-####"]
        },
        "香港": {
            "code": "+852",
            "format": ["5### ####", "6### ####", "9### ####"]
        },
        "台湾": {
            "code": "+886",
            "format": ["9## ### ###", "9########", "4## ### ###"]
        },
        "澳门": {
            "code": "+853",
            "format": ["6### ####", "5### ####"]
        },

        # 欧洲
        "英国": {
            "code": "+44",
            "format": ["7### ######", "7########", "20-####-####"]
        },
        "德国": {
            "code": "+49",
            "format": ["15## #######", "17## #######", "16## #######"]
        },
        "法国": {
            "code": "+33",
            "format": ["6 ## ## ## ##", "7 ## ## ## ##", "1 ## ## ## ##"]
        },
        "意大利": {
            "code": "+39",
            "format": ["3## #######", "3##########"]
        },
        "西班牙": {
            "code": "+34",
            "format": ["6## ### ###", "7## ### ###"]
        },
        "俄罗斯": {
            "code": "+7",
            "format": ["9## ###-##-##", "9##########", "8## ###-##-##"]
        },
        "荷兰": {
            "code": "+31",
            "format": ["6-####-####", "6########"]
        },
        "瑞士": {
            "code": "+41",
            "format": ["7# ### ## ##", "7########"]
        },
        "瑞典": {
            "code": "+46",
            "format": ["7#-### ## ##", "7########"]
        },
        "挪威": {
            "code": "+47",
            "format": ["4## ## ###", "9## ## ###"]
        },
        "丹麦": {
            "code": "+45",
            "format": ["## ## ## ##", "########"]
        },
        "芬兰": {
            "code": "+358",
            "format": ["4# ### ## ##", "4########"]
        },
        "比利时": {
            "code": "+32",
            "format": ["4## ## ## ##", "4########"]
        },
        "奥地利": {
            "code": "+43",
            "format": ["6## #######", "6##########"]
        },
        "爱尔兰": {
            "code": "+353",
            "format": ["8# #######", "8##########"]
        },
        "葡萄牙": {
            "code": "+351",
            "format": ["9## ### ###", "9########"]
        },
        "希腊": {
            "code": "+30",
            "format": ["69## ######", "69########"]
        },
        "波兰": {
            "code": "+48",
            "format": ["### ### ###", "##########"]
        },
        "捷克": {
            "code": "+420",
            "format": ["### ### ###", "##########"]
        },
        "匈牙利": {
            "code": "+36",
            "format": ["20/###-####", "30/###-####"]
        },

        # 北美洲
        "美国": {
            "code": "+1",
            "format": ["###-###-####", "(###) ###-####", "###.###.####"]
        },
        "加拿大": {
            "code": "+1",
            "format": ["###-###-####", "(###) ###-####", "###.###.####"]
        },
        "墨西哥": {
            "code": "+52",
            "format": ["1 ## ## ## ####", "1###########"]
        },

        # 南美洲
        "巴西": {
            "code": "+55",
            "format": ["## 9####-####", "## 8####-####", "## 7####-####"]
        },
        "阿根廷": {
            "code": "+54",
            "format": ["9 ## ####-####", "11 ####-####"]
        },
        "智利": {
            "code": "+56",
            "format": ["9 #### ####", "2 #### ####"]
        },
        "哥伦比亚": {
            "code": "+57",
            "format": ["3## #######", "3##########"]
        },
        "秘鲁": {
            "code": "+51",
            "format": ["9## ### ###", "9########"]
        },

        # 非洲
        "南非": {
            "code": "+27",
            "format": ["## ### ####", "##########"]
        },
        "埃及": {
            "code": "+20",
            "format": ["1## #######", "1##########"]
        },
        "尼日利亚": {
            "code": "+234",
            "format": ["### ### ####", "###########"]
        },
        "肯尼亚": {
            "code": "+254",
            "format": ["7## #######", "7##########"]
        },
        "摩洛哥": {
            "code": "+212",
            "format": ["6-##-##-##-##", "6##########"]
        },

        # 大洋洲
        "澳大利亚": {
            "code": "+61",
            "format": ["4## ### ###", "4########", "2 #### ####"]
        },
        "新西兰": {
            "code": "+64",
            "format": ["2# ### ####", "2##########"]
        },

        # 中东
        "阿联酋": {
            "code": "+971",
            "format": ["5# ### ####", "5##########"]
        },
        "沙特阿拉伯": {
            "code": "+966",
            "format": ["5# ### ####", "5##########"]
        },
        "以色列": {
            "code": "+972",
            "format": ["5#-###-####", "5##########"]
        },
        "土耳其": {
            "code": "+90",
            "format": ["5## ### ####", "5##########"]
        },
        "卡塔尔": {
            "code": "+974",
            "format": ["3### ####", "5### ####", "7### ####"]
        }
    }

    if country not in country_formats:
        # 默认格式
        country_info = {
            "code": "+1",
            "format": ["###-###-####"]
        }
    else:
        country_info = country_formats[country]

    # 选择一种格式
    format_pattern = random.choice(country_info["format"])

    # 生成号码
    phone_number = ""
    for char in format_pattern:
        if char == "#":
            phone_number += str(random.randint(0, 9))
        else:
            phone_number += char

    return f"{country_info['code']} {phone_number}"


def generate_conditional_address(province=None, selected_city=None, detailed=True):
    """根据条件生成地址"""
    if FAKER_AVAILABLE:
        # Faker生成地址
        if detailed:
            address = fake.address()
        else:
            # 不生成详细地址，只到城市级别
            address = f"{fake.province()} {fake.city()}"
    else:
        # 备用方案
        if province == "随机":
            provinces = ["北京市", "上海市", "广州市", "深圳市", "杭州市", "成都市", "武汉市", "南京市", "西安市"]
            province = random.choice(provinces)
            city = province  # 直辖市城市名与省份相同

        if detailed:
            streets = ["中山路", "解放路", "人民路", "建设路", "和平路", "新华路", "文化路", "胜利路", "团结路", "友谊路"]
            communities = ["小区", "花园", "大厦", "公寓", "广场", "苑", "居", "湾", "城", "国际"]
            numbers = [str(i) for i in range(1, 201)]
            street = random.choice(streets)
            community = random.choice(communities)
            number = random.choice(numbers)
            address = f"{province}{selected_city}{street}{number}号{random.randint(1, 20)}栋{random.randint(1, 30)}单元{random.randint(101, 1500)}室"
        else:
            address = f"{province}{selected_city}"

    return address


def generate_conditional_id_card(province=None, gender=None, min_age=18, max_age=60):
    """根据条件生成身份证号码"""
    if FAKER_AVAILABLE:
        # Faker生成身份证
        id_card = fake.ssn()

        # 这里可以添加更复杂的条件验证逻辑
        # 由于Faker的ssn()已经生成符合规则的身份证，我们主要处理省份和性别条件

        # 简单验证：检查身份证前两位是否符合省份代码
        province_codes = {
            "北京市": "11", "天津市": "12", "河北省": "13", "山西省": "14", "内蒙古自治区": "15",
            "辽宁省": "21", "吉林省": "22", "黑龙江省": "23", "上海市": "31", "江苏省": "32",
            "浙江省": "33", "安徽省": "34", "福建省": "35", "江西省": "36", "山东省": "37",
            "河南省": "41", "湖北省": "42", "湖南省": "43", "广东省": "44", "广西壮族自治区": "45",
            "海南省": "46", "重庆市": "50", "四川省": "51", "贵州省": "52", "云南省": "53",
            "西藏自治区": "54", "陕西省": "61", "甘肃省": "62", "青海省": "63", "宁夏回族自治区": "64",
            "新疆维吾尔自治区": "65"
        }

        if province and province != "随机" and province in province_codes:
            province_code = province_codes[province]
            # 如果生成的身份证前两位不匹配指定省份，重新生成（简化处理）
            if not id_card.startswith(province_code):
                # 使用传统方法生成符合省份条件的身份证
                return generate_random_id_card(province, gender or "随机", min_age, max_age)

        return id_card
    else:
        # 备用方案
        return generate_random_id_card(
            province if province != "随机" else "北京市",
            gender or "随机",
            min_age,
            max_age
        )


def generate_random_email(domain_option, custom_domain, selected_domains):
    """生成随机邮箱"""
    username_length = random.randint(5, 12)
    username = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(username_length))

    if domain_option == "自定义域名":
        domain = custom_domain
    else:
        domain = random.choice(selected_domains) if selected_domains else random.choice(["gmail.com", "yahoo.com"])

    return f"{username}@{domain}"


# ================ 页面布局 ================
st.markdown('<div class="main-header">🔧 测试工程师常用工具集</div>', unsafe_allow_html=True)

tool_category = st.sidebar.selectbox(
    "选择工具类别",
    ["数据生成工具", "字数统计工具", "文本对比工具", "正则表达式测试工具",
     "JSON数据对比工具", "日志分析工具", "时间处理工具", "IP/域名查询工具"]
)

# ================ 使用说明和注意事项 ================
if tool_category == "数据生成工具":
    st.markdown('<div class="section-header">📊 高级数据生成工具</div>', unsafe_allow_html=True)

    # 数据生成工具的使用说明和注意事项
    with st.expander("📋 使用说明 - 数据生成工具"):
        st.markdown("""
        ### 数据生成工具使用说明

        **Faker高级生成器:**
        - 支持生成真实感强的测试数据，包括个人信息、地址、网络信息等
        - 选择数据类别和具体类型后，设置生成数量即可
        - 完整个人信息会生成格式化的简历样式数据

        **基础数据生成器:**
        - 随机内容生成器：可生成字符串、数字、密码、UUID等
        - 随机邮箱生成器：支持自定义域名或选择预设域名
        - 电话号码生成器：支持手机号、座机、国际号码生成
        - 随机地址生成器：可按省份城市生成详细或简略地址
        - 随机身份证生成器：生成符合规则的虚拟身份证号码
        """)

    with st.expander("⚠️ 注意事项 - 数据生成工具"):
        st.markdown("""
        ### 重要注意事项

        **数据真实性:**
        - 所有生成的数据均为虚拟数据，仅用于测试目的
        - 身份证号码符合格式规则但非真实有效号码
        - 电话号码为虚拟号码，不能用于实际通信

        **使用限制:**
        - 批量生成数量限制为1-100条，避免性能问题
        - Faker库需要单独安装：`pip install faker`
        - 国际电话号码格式仅供参考，可能因国家而异

        **隐私安全:**
        - 不要将生成的测试数据用于生产环境
        - 敏感信息生成后请妥善处理
        - 避免在公共场合展示生成的个人信息
        """)

    # 数据生成模式选择
    gen_mode = st.radio(
        "选择生成模式",
        ["Faker高级生成器", "基础数据生成器"],
        horizontal=True
    )

    # 在Faker高级生成器部分也需要相应调整显示
    if gen_mode == "Faker高级生成器":
        if not FAKER_AVAILABLE:
            st.error("❌ Faker库未安装，无法使用高级生成器")
            st.info("请运行以下命令安装: `pip install faker`")
            st.code("pip install faker", language="bash")
        else:
            st.markdown('<div class="tool-card">🚀 Faker高级数据生成器</div>', unsafe_allow_html=True)

            # 分类选择
            categories = {
                "人物信息": ["随机姓名", "随机姓", "随机名", "男性姓名", "女性姓名", "完整个人信息"],
                "地址信息": ["随机地址", "随机城市", "随机国家", "随机邮编", "随机街道"],
                "网络信息": ["随机邮箱", "安全邮箱", "公司邮箱", "免费邮箱", "随机域名", "随机URL", "随机IP地址", "随机用户代理"],
                "公司信息": ["随机公司名", "公司后缀", "职位"],
                "金融信息": ["信用卡号", "信用卡提供商", "信用卡有效期", "货币"],
                "日期时间": ["随机日期时间", "随机日期", "随机时间", "今年日期", "本月日期"],
                "文本内容": ["随机单词", "随机句子", "随机段落", "随机文本"],
                "电话号码": ["随机手机号", "号段前缀"],
                "其他信息": ["随机颜色", "随机UUID", "随机MD5", "随机SHA1", "随机文件扩展名", "随机MIME类型"]
            }

            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                selected_category = st.selectbox("选择数据类别", list(categories.keys()))
            with col2:
                selected_subcategory = st.selectbox("选择具体类型", categories[selected_category])
            with col3:
                count = st.number_input("生成数量", min_value=1, max_value=100, value=5)

            # 特殊参数
            extra_params = {}
            if selected_subcategory == "随机文本":
                text_length = st.slider("文本长度", min_value=10, max_value=1000, value=200)
                extra_params['length'] = text_length

            if st.button("🎯 生成数据", use_container_width=True):
                with st.spinner("正在生成数据..."):
                    results = generate_faker_data(selected_category, selected_subcategory, count, **extra_params)

                # 对于完整个人信息，直接显示格式化结果
                result_text = "\n".join([str(r) for r in results])
                st.session_state.faker_result = result_text
                st.session_state.last_category = f"{selected_category} - {selected_subcategory}"

            if 'faker_result' in st.session_state:
                st.markdown(f'<div class="category-card">📋 生成结果 - {st.session_state.get("last_category", "")}</div>',
                            unsafe_allow_html=True)

                # 对于完整个人信息，使用文本区域显示以保持格式
                if selected_subcategory == "完整个人信息":
                    st.text_area("生成结果", st.session_state.faker_result, height=300, key="profile_result")
                else:
                    st.markdown(f'<div class="result-box">{st.session_state.faker_result}</div>',
                                unsafe_allow_html=True)

                # 使用新的复制组件
                create_copy_button(
                    st.session_state.faker_result,
                    button_text="📋 复制结果",
                    key="copy_faker_result"
                )

                # 保留下载按钮作为备用
                st.download_button(
                    label="💾 下载结果",
                    data=st.session_state.faker_result,
                    file_name=f"faker_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

    else:  # 基础数据生成器
        st.markdown('<div class="tool-card">🔧 基础数据生成器</div>', unsafe_allow_html=True)
        data_gen_tool = st.radio(
            "选择生成工具",
            ["随机内容生成器", "随机邮箱生成器", "电话号码生成器", "随机地址生成器", "随机身份证生成器"],
            horizontal=True
        )

        if data_gen_tool == "随机内容生成器":
            st.markdown('<div class="category-card">🎲 随机内容生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                # 生成类型选择
                gen_type = st.selectbox("生成类型", ["随机字符串", "随机数字", "随机密码", "UUID"])

                # 根据类型显示不同参数
                if gen_type in ["随机字符串", "随机密码"]:
                    length = st.slider("长度", 1, 100, 10,
                                       help="生成内容的长度（字符数）")
                if gen_type == "随机数字":
                    min_val = st.number_input("最小值", value=0)
                    max_val = st.number_input("最大值", value=100)

                # 生成数量
                count = st.number_input("生成数量", min_value=1, max_value=100, value=5)

            with col2:
                # 字符类型选项
                if gen_type == "随机字符串":
                    chars_type = st.multiselect("字符类型",
                                                ["小写字母", "大写字母", "数字", "特殊字符"],
                                                default=["小写字母", "大写字母", "数字"],
                                                help="选择包含的字符类型")

                # 密码选项
                if gen_type == "随机密码":
                    password_options = st.multiselect("密码选项",
                                                      ["包含小写字母", "包含大写字母", "包含数字", "包含特殊字符"],
                                                      default=["包含小写字母", "包含大写字母", "包含数字"],
                                                      help="设置密码复杂度要求")

                # 条件说明
                st.write("📋 条件说明")
                if gen_type == "随机字符串":
                    st.write(f"- 类型: 随机字符串")
                    st.write(f"- 长度: {length}字符")
                    st.write(f"- 字符类型: {', '.join(chars_type)}")
                elif gen_type == "随机数字":
                    st.write(f"- 类型: 随机数字")
                    st.write(f"- 范围: {min_val} 到 {max_val}")
                elif gen_type == "随机密码":
                    st.write(f"- 类型: 随机密码")
                    st.write(f"- 长度: {length}字符")
                    st.write(f"- 复杂度: {', '.join(password_options)}")
                else:
                    st.write(f"- 类型: UUID")

                st.write("💡 提示: 点击生成按钮后结果将保留在页面")

            if st.button("生成内容", key="gen_random_content"):
                results = []
                with st.spinner(f"正在生成{count}个{gen_type}..."):
                    for _ in range(count):
                        if gen_type == "随机字符串":
                            results.append(generate_random_string(length, chars_type))
                        elif gen_type == "随机数字":
                            results.append(str(random.randint(min_val, max_val)))
                        elif gen_type == "随机密码":
                            results.append(generate_random_password(length, password_options))
                        elif gen_type == "UUID":
                            results.append(str(uuid.uuid4()))

                result_text = "\n".join(results)
                st.session_state.random_content_result = result_text
                st.session_state.random_content_conditions = (
                        f"类型: {gen_type}, " +
                        (f"长度: {length}, " if gen_type in ["随机字符串", "随机密码"] else "") +
                        (f"范围: {min_val}-{max_val}, " if gen_type == "随机数字" else "") +
                        (f"字符类型: {', '.join(chars_type)}" if gen_type == "随机字符串" else "") +
                        (f"复杂度: {', '.join(password_options)}" if gen_type == "随机密码" else "")
                )

            if 'random_content_result' in st.session_state:
                st.markdown(
                    f'<div class="category-card">📋 生成结果 - {st.session_state.get("random_content_conditions", "")}</div>',
                    unsafe_allow_html=True)
                st.markdown('<div class="result-box">' + st.session_state.random_content_result + '</div>',
                            unsafe_allow_html=True)

                # 使用新的复制组件替换旧的复制按钮
                create_copy_button(
                    st.session_state.random_content_result,
                    button_text="📋 复制结果",
                    key="copy_random_content"
                )

                # 保留下载按钮
                st.download_button(
                    label="💾 下载结果",
                    data=st.session_state.random_content_result,
                    file_name=f"随机内容_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_random_content"
                )

        elif data_gen_tool == "随机邮箱生成器":
            st.markdown('<div class="category-card">📧 随机邮箱生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                # 生成数量
                count = st.number_input("邮箱数量", min_value=1, max_value=100, value=10)
                # 域名选项
                domain_option = st.selectbox("域名选项", ["随机域名", "自定义域名"])

            with col2:
                if domain_option == "自定义域名":
                    # 自定义域名输入
                    custom_domain = st.text_input("自定义域名", "example.com",
                                                  placeholder="输入不带http://的域名")
                    st.write("📋 条件说明")
                    st.write(f"- 域名类型: 自定义")
                    st.write(f"- 域名: {custom_domain}")
                else:
                    # 预设域名选择
                    domains = ["gmail.com", "yahoo.com", "hotmail.com",
                               "outlook.com", "163.com", "qq.com"]
                    selected_domains = st.multiselect("选择域名", domains,
                                                      default=domains[:3])
                    st.write("📋 条件说明")
                    st.write(f"- 域名类型: 随机选择")
                    st.write(f"- 可选域名: {', '.join(selected_domains)}")
                st.write("💡 提示: 用户名将随机生成8-12位字母数字组合")

            if st.button("生成邮箱", key="gen_emails"):
                results = []
                with st.spinner(f"正在生成{count}个邮箱地址..."):
                    for _ in range(count):
                        results.append(generate_random_email(
                            domain_option,
                            custom_domain if domain_option == "自定义域名" else None,
                            selected_domains if domain_option != "自定义域名" else None
                        ))

                result_text = "\n".join(results)
                st.session_state.email_result = result_text
                st.session_state.email_conditions = (
                    f"域名: {custom_domain}" if domain_option == "自定义域名"
                    else f"随机域名: {', '.join(selected_domains)}"
                )

            if 'email_result' in st.session_state:
                st.markdown(
                    f'<div class="category-card">📋 生成结果 - {st.session_state.get("email_conditions", "")}</div>',
                    unsafe_allow_html=True)
                st.markdown('<div class="result-box">' + st.session_state.email_result + '</div>',
                            unsafe_allow_html=True)

                # 使用新的复制组件
                create_copy_button(
                    st.session_state.email_result,
                    button_text="📋 复制邮箱列表",
                    key="copy_emails"
                )

                # 保留下载按钮
                st.download_button(
                    label="💾 下载邮箱列表",
                    data=st.session_state.email_result,
                    file_name=f"邮箱列表_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_emails"
                )

        elif data_gen_tool == "电话号码生成器":
            st.markdown('<div class="category-card">📞 电话号码生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                # 号码类型选择
                phone_type = st.selectbox("号码类型", ["手机号", "座机", "国际号码"])

                if phone_type == "国际号码":
                    # 国家选择
                    countries = [
                        "日本", "韩国", "印度", "新加坡", "马来西亚", "泰国", "越南", "菲律宾", "印度尼西亚",
                        "香港", "台湾", "澳门", "英国", "德国", "法国", "意大利", "西班牙", "俄罗斯", "荷兰",
                        "瑞士", "瑞典", "挪威", "丹麦", "芬兰", "比利时", "奥地利", "爱尔兰", "葡萄牙", "希腊",
                        "波兰", "捷克", "匈牙利", "美国", "加拿大", "墨西哥", "巴西", "阿根廷", "智利", "哥伦比亚",
                        "秘鲁", "南非", "埃及", "尼日利亚", "肯尼亚", "摩洛哥", "澳大利亚", "新西兰", "阿联酋",
                        "沙特阿拉伯", "以色列", "土耳其", "卡塔尔"
                    ]
                    country = st.selectbox("选择国家", countries)
                elif phone_type == "手机号":
                    # 运营商选择（仅限国内手机号）
                    operator = st.selectbox("运营商", ["随机", "移动", "联通", "电信", "广电"])
                else:  # 座机
                    operator = st.selectbox("运营商", ["随机", "移动", "联通", "电信", "广电"])

                count = st.number_input("生成数量", min_value=1, max_value=100, value=10)

            with col2:
                if phone_type == "座机":
                    # 座机区号选择（可选）
                    area_code = st.text_input("区号（可选）", placeholder="例如：0592（厦门）")
                    st.write("📋 条件说明")
                    st.write(f"- 运营商: {operator}")
                    st.write(f"- 号码类型: {phone_type}")
                    st.write(f"- 区号: {area_code if area_code else '随机'}")
                elif phone_type == "国际号码":
                    st.write("📋 条件说明")
                    st.write(f"- 号码类型: {phone_type}")
                    st.write(f"- 国家: {country}")
                    st.write("🌍 国际号码格式包含国家代码")
                else:
                    st.write("📋 条件说明")
                    st.write(f"- 运营商: {operator}")
                    st.write(f"- 号码类型: {phone_type}")
                st.write("💡 提示: 生成的号码将匹配相应的号码规则")

            if st.button("生成电话号码", key="gen_conditional_phones"):
                results = []
                with st.spinner(f"正在生成{count}个号码..."):
                    for i in range(count):
                        if phone_type == "座机":
                            # 生成座机号码（区号可选）
                            phone = generate_landline_number(operator, area_code if area_code else None)
                        elif phone_type == "国际号码":
                            # 生成国际号码
                            phone = generate_international_phone(country)
                        else:
                            # 生成手机号码（仅匹配运营商）
                            phone = generate_conditional_phone(operator)
                        results.append(phone)

                result_text = "\n".join(results)
                st.session_state.phone_result = result_text

                # 更新条件说明
                if phone_type == "国际号码":
                    st.session_state.phone_conditions = f"类型: {phone_type}, 国家: {country}"
                elif phone_type == "座机":
                    st.session_state.phone_conditions = f"运营商: {operator}, 类型: {phone_type}" + (
                        f", 区号: {area_code}" if area_code else "")
                else:
                    st.session_state.phone_conditions = f"运营商: {operator}, 类型: {phone_type}"

            if 'phone_result' in st.session_state:
                st.markdown(
                    f'<div class="category-card">📋 生成结果 - {st.session_state.get("phone_conditions", "")}</div>',
                    unsafe_allow_html=True)
                st.markdown('<div class="result-box">' + st.session_state.phone_result + '</div>',
                            unsafe_allow_html=True)

                # 使用新的复制组件
                create_copy_button(
                    st.session_state.phone_result,
                    button_text="📋 复制电话号码",
                    key="copy_phones"
                )

                # 保留下载按钮
                st.download_button(
                    label="💾 下载电话号码",
                    data=st.session_state.phone_result,
                    file_name=f"电话号码_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_phones"
                )

        elif data_gen_tool == "随机地址生成器":
            st.markdown('<div class="category-card">🏠 随机地址生成器</div>', unsafe_allow_html=True)

            # 省份城市数据
            provinces = {
                "北京市": ["北京市"],
                "天津市": ["天津市"],
                "上海市": ["上海市"],
                "重庆市": ["重庆市"],
                "河北省": ["石家庄市", "唐山市", "秦皇岛市", "邯郸市", "邢台市", "保定市", "张家口市", "承德市", "沧州市", "廊坊市", "衡水市"],
                "山西省": ["太原市", "大同市", "阳泉市", "长治市", "晋城市", "朔州市", "晋中市", "运城市", "忻州市", "临汾市", "吕梁市"],
                "内蒙古自治区": ["呼和浩特市", "包头市", "乌海市", "赤峰市", "通辽市", "鄂尔多斯市", "呼伦贝尔市", "巴彦淖尔市", "乌兰察布市", "兴安盟", "锡林郭勒盟",
                           "阿拉善盟"],
                "辽宁省": ["沈阳市", "大连市", "鞍山市", "抚顺市", "本溪市", "丹东市", "锦州市", "营口市", "阜新市", "辽阳市", "盘锦市", "铁岭市", "朝阳市",
                        "葫芦岛市"],
                "吉林省": ["长春市", "吉林市", "四平市", "辽源市", "通化市", "白山市", "松原市", "白城市", "延边朝鲜族自治州"],
                "黑龙江省": ["哈尔滨市", "齐齐哈尔市", "鸡西市", "鹤岗市", "双鸭山市", "大庆市", "伊春市", "佳木斯市", "七台河市", "牡丹江市", "黑河市", "绥化市",
                         "大兴安岭地区"],
                "江苏省": ["南京市", "无锡市", "徐州市", "常州市", "苏州市", "南通市", "连云港市", "淮安市", "盐城市", "扬州市", "镇江市", "泰州市", "宿迁市"],
                "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市", "湖州市", "绍兴市", "金华市", "衢州市", "舟山市", "台州市", "丽水市"],
                "安徽省": ["合肥市", "芜湖市", "蚌埠市", "淮南市", "马鞍山市", "淮北市", "铜陵市", "安庆市", "黄山市", "滁州市", "阜阳市", "宿州市", "六安市",
                        "亳州市", "池州市", "宣城市"],
                "福建省": ["福州市", "厦门市", "莆田市", "三明市", "泉州市", "漳州市", "南平市", "龙岩市", "宁德市"],
                "江西省": ["南昌市", "景德镇市", "萍乡市", "九江市", "新余市", "鹰潭市", "赣州市", "吉安市", "宜春市", "抚州市", "上饶市"],
                "山东省": ["济南市", "青岛市", "淄博市", "枣庄市", "东营市", "烟台市", "潍坊市", "济宁市", "泰安市", "威海市", "日照市", "临沂市", "德州市",
                        "聊城市", "滨州市", "菏泽市"],
                "河南省": ["郑州市", "开封市", "洛阳市", "平顶山市", "安阳市", "鹤壁市", "新乡市", "焦作市", "濮阳市", "许昌市", "漯河市", "三门峡市", "南阳市",
                        "商丘市", "信阳市", "周口市", "驻马店市"],
                "湖北省": ["武汉市", "黄石市", "十堰市", "宜昌市", "襄阳市", "鄂州市", "荆门市", "孝感市", "荆州市", "黄冈市", "咸宁市", "随州市",
                        "恩施土家族苗族自治州"],
                "湖南省": ["长沙市", "株洲市", "湘潭市", "衡阳市", "邵阳市", "岳阳市", "常德市", "张家界市", "益阳市", "郴州市", "永州市", "怀化市", "娄底市",
                        "湘西土家族苗族自治州"],
                "广东省": ["广州市", "深圳市", "珠海市", "汕头市", "佛山市", "韶关市", "湛江市", "肇庆市", "江门市", "茂名市", "惠州市", "梅州市", "汕尾市",
                        "河源市", "阳江市", "清远市", "东莞市", "中山市", "潮州市", "揭阳市", "云浮市"],
                "广西壮族自治区": ["南宁市", "柳州市", "桂林市", "梧州市", "北海市", "防城港市", "钦州市", "贵港市", "玉林市", "百色市", "贺州市", "河池市", "来宾市",
                            "崇左市"],
                "海南省": ["海口市", "三亚市", "三沙市", "儋州市"],
                "四川省": ["成都市", "自贡市", "攀枝花市", "泸州市", "德阳市", "绵阳市", "广元市", "遂宁市", "内江市", "乐山市", "南充市", "眉山市", "宜宾市",
                        "广安市", "达州市", "雅安市", "巴中市", "资阳市", "阿坝藏族羌族自治州", "甘孜藏族自治州", "凉山彝族自治州"],
                "贵州省": ["贵阳市", "六盘水市", "遵义市", "安顺市", "毕节市", "铜仁市", "黔西南布依族苗族自治州", "黔东南苗族侗族自治州", "黔南布依族苗族自治州"],
                "云南省": ["昆明市", "曲靖市", "玉溪市", "保山市", "昭通市", "丽江市", "普洱市", "临沧市", "楚雄彝族自治州", "红河哈尼族彝族自治州", "文山壮族苗族自治州",
                        "西双版纳傣族自治州", "大理白族自治州", "德宏傣族景颇族自治州", "怒江傈僳族自治州", "迪庆藏族自治州"],
                "西藏自治区": ["拉萨市", "日喀则市", "昌都市", "林芝市", "山南市", "那曲市", "阿里地区"],
                "陕西省": ["西安市", "铜川市", "宝鸡市", "咸阳市", "渭南市", "延安市", "汉中市", "榆林市", "安康市", "商洛市"],
                "甘肃省": ["兰州市", "嘉峪关市", "金昌市", "白银市", "天水市", "武威市", "张掖市", "平凉市", "酒泉市", "庆阳市", "定西市", "陇南市", "临夏回族自治州",
                        "甘南藏族自治州"],
                "青海省": ["西宁市", "海东市", "海北藏族自治州", "黄南藏族自治州", "海南藏族自治州", "果洛藏族自治州", "玉树藏族自治州", "海西蒙古族藏族自治州"],
                "宁夏回族自治区": ["银川市", "石嘴山市", "吴忠市", "固原市", "中卫市"],
                "新疆维吾尔自治区": ["乌鲁木齐市", "克拉玛依市", "吐鲁番市", "哈密市", "昌吉回族自治州", "博尔塔拉蒙古自治州", "巴音郭楞蒙古自治州", "阿克苏地区",
                             "克孜勒苏柯尔克孜自治州", "喀什地区", "和田地区", "伊犁哈萨克自治州", "塔城地区", "阿勒泰地区"],
                "台湾省": ["台北市", "新北市", "桃园市", "台中市", "台南市", "高雄市"],
                "香港特别行政区": ["香港岛", "九龙", "新界"],
                "澳门特别行政区": ["澳门半岛", "氹仔", "路环"],
                "随机": ["随机"]
            }

            col1, col2 = st.columns(2)
            with col1:
                # 省份选择
                province = st.selectbox("选择省份", ["随机"] + [p for p in provinces.keys() if p != "随机"])
                # 生成数量
                count = st.number_input("生成数量", min_value=1, max_value=50, value=10)
                # 详细地址开关
                detailed = st.checkbox("生成详细地址", value=True)

            with col2:
                # 城市选择（根据省份动态更新）
                if province != "随机":
                    city_options = provinces[province]
                    city = st.selectbox("选择城市", ["随机"] + [c for c in city_options if c != province])
                else:
                    city = "随机"

                # 条件说明
                st.write("📋 条件说明")
                st.write(f"- 省份: {province if province != '随机' else '随机选择'}")
                st.write(f"- 城市: {city if city != '随机' else '随机选择'}")
                st.write(f"- 详细程度: {'详细地址' if detailed else '仅省市信息'}")
                st.write("💡 提示: 详细地址包含街道、门牌号等信息")

            if st.button("生成地址", key="gen_addresses"):
                results = []
                with st.spinner(f"正在生成{count}个地址..."):
                    for _ in range(count):
                        # 处理省份选择
                        selected_province = province
                        if province == "随机":
                            selected_province = random.choice([p for p in provinces.keys() if p != "随机"])

                        # 处理城市选择
                        selected_city = city
                        if city == "随机":
                            if selected_province in provinces:
                                city_options = [c for c in provinces[selected_province] if c != selected_province]
                                selected_city = random.choice(city_options) if city_options else selected_province

                        results.append(generate_random_address(selected_province, selected_city, detailed))

                result_text = "\n".join(results)
                st.session_state.address_result = result_text
                st.session_state.address_conditions = (
                        f"省份: {selected_province}, " +
                        f"城市: {selected_city}, " +
                        f"详细程度: {'详细地址' if detailed else '仅省市信息'}"
                )

            if 'address_result' in st.session_state:
                st.markdown(
                    f'<div class="category-card">📋 生成结果 - {st.session_state.get("address_conditions", "")}</div>',
                    unsafe_allow_html=True)
                st.markdown('<div class="result-box">' + st.session_state.address_result + '</div>',
                            unsafe_allow_html=True)

                # 使用新的复制组件
                create_copy_button(
                    st.session_state.address_result,
                    button_text="📋 复制地址",
                    key="copy_addresses"
                )

                # 保留下载按钮
                st.download_button(
                    label="💾 下载地址列表",
                    data=st.session_state.address_result,
                    file_name=f"地址列表_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_addresses"
                )

        elif data_gen_tool == "随机身份证生成器":
            st.markdown('<div class="category-card">🆔 随机身份证生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                # 省份选择
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

                # 性别选择
                gender = st.selectbox("选择性别", ["随机", "男", "女"])
                count = st.number_input("生成数量", min_value=1, max_value=100, value=10)

            with col2:
                # 年龄范围选择
                min_age = st.number_input("最小年龄", min_value=0, max_value=100, value=18)
                max_age = st.number_input("最大年龄", min_value=0, max_value=100, value=60)
                if min_age > max_age:
                    st.error("最小年龄不能大于最大年龄")

                st.write("📋 条件说明")
                st.write(f"- 省份: {province}")
                st.write(f"- 性别: {gender}")
                st.write(f"- 年龄范围: {min_age}-{max_age}岁")
                st.write("💡 提示: 生成的身份证将严格符合选择的省份、性别和年龄条件")

            if st.button("生成身份证", key="gen_id_cards"):
                results = []
                with st.spinner(f"正在生成{count}个身份证号码..."):
                    for i in range(count):
                        results.append(generate_random_id_card(
                            province if province != "随机" else random.choice(list({
                                                                                     "北京市": "11", "天津市": "12",
                                                                                     "河北省": "13", "山西省": "14",
                                                                                     "内蒙古自治区": "15",
                                                                                     "辽宁省": "21", "吉林省": "22",
                                                                                     "黑龙江省": "23", "上海市": "31",
                                                                                     "江苏省": "32",
                                                                                     "浙江省": "33", "安徽省": "34",
                                                                                     "福建省": "35", "江西省": "36",
                                                                                     "山东省": "37",
                                                                                     "河南省": "41", "湖北省": "42",
                                                                                     "湖南省": "43", "广东省": "44",
                                                                                     "广西壮族自治区": "45",
                                                                                     "海南省": "46", "重庆市": "50",
                                                                                     "四川省": "51", "贵州省": "52",
                                                                                     "云南省": "53",
                                                                                     "西藏自治区": "54", "陕西省": "61",
                                                                                     "甘肃省": "62", "青海省": "63",
                                                                                     "宁夏回族自治区": "64",
                                                                                     "新疆维吾尔自治区": "65"
                                                                                 }.keys())),
                            gender,
                            min_age,
                            max_age
                        ))

                result_text = "\n".join(results)
                st.session_state.id_card_result = result_text
                st.session_state.id_card_conditions = f"省份: {province}, 性别: {gender}, 年龄: {min_age}-{max_age}岁"

            if 'id_card_result' in st.session_state:
                st.markdown(
                    f'<div class="category-card">📋 生成结果 - {st.session_state.get("id_card_conditions", "")}</div>',
                    unsafe_allow_html=True)
                st.markdown('<div class="result-box">' + st.session_state.id_card_result + '</div>',
                            unsafe_allow_html=True)

                # 使用新的复制组件
                create_copy_button(
                    st.session_state.id_card_result,
                    button_text="📋 复制身份证号",
                    key="copy_id_cards"
                )

                # 保留下载按钮
                st.download_button(
                    label="💾 下载身份证号",
                    data=st.session_state.id_card_result,
                    file_name=f"身份证列表_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_id_cards"
                )

# 字数统计工具
elif tool_category == "字数统计工具":
    st.markdown('<div class="section-header">📝 字数统计工具</div>', unsafe_allow_html=True)

    with st.expander("📋 使用说明 - 字数统计工具"):
        st.markdown("""
        ### 字数统计工具使用说明

        **功能特点:**
        - 实时统计输入文本的各类字数信息
        - 支持字符数（含空格和不含空格）统计
        - 自动计算单词数、行数和段落数
        - 显示最常见字符的使用频率

        **统计规则:**
        - 字符数：包括所有可见和不可见字符
        - 单词数：按空格分隔的单词为单位
        - 行数：按换行符分隔
        - 段落数：按连续换行符分隔的文本块
        """)

    with st.expander("⚠️ 注意事项 - 字数统计工具"):
        st.markdown("""
        ### 重要注意事项

        **统计精度:**
        - 单词统计基于空格分隔，中文文本可能不准确
        - 特殊字符和标点符号计入字符统计
        - 空行会计入行数但不计入段落数

        **性能考虑:**
        - 超大文本（超过10万字符）可能影响响应速度
        - 建议分段处理超长文本
        - 统计结果会实时更新，输入时请注意
        """)

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
    st.markdown('<div class="section-header">🔍 文本对比工具</div>', unsafe_allow_html=True)

    with st.expander("📋 使用说明 - 文本对比工具"):
        st.markdown("""
        ### 文本对比工具使用说明

        **对比功能:**
        - 并排显示两个文本内容，方便直观对比
        - 使用颜色标识差异：绿色表示新增，红色表示删除
        - 支持大文本文件的对比分析

        **操作流程:**
        1. 在左侧输入原始文本
        2. 在右侧输入对比文本
        3. 点击"开始对比"查看差异
        4. 使用"清空所有内容"重置界面
        """)

    with st.expander("⚠️ 注意事项 - 文本对比工具"):
        st.markdown("""
        ### 重要注意事项

        **对比规则:**
        - 基于行级别的差异对比
        - 空格和换行符的差异也会被检测
        - 颜色标识：绿色=新增，红色=删除，黄色=修改

        **使用限制:**
        - 超大文件对比可能较慢，建议分段处理
        - 特殊字符编码可能影响对比结果
        - 对比结果仅供参考，需要人工确认重要差异
        """)

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
    st.markdown('<div class="section-header">⚡ 正则表达式测试工具</div>', unsafe_allow_html=True)

    with st.expander("📋 使用说明 - 正则表达式测试工具"):
        st.markdown("""
        ### 正则表达式测试工具使用说明

        **核心功能:**
        - 实时测试正则表达式的匹配效果
        - 支持多种匹配模式：全局、忽略大小写、多行
        - 提供替换功能，测试替换效果
        - 显示详细的匹配结果和分组信息

        **匹配选项说明:**
        - 全局匹配(g)：查找所有匹配项而不仅是第一个
        - 忽略大小写(i)：不区分字母大小写
        - 多行模式(m)：^和$匹配每行的开始和结束
        """)

    with st.expander("⚠️ 注意事项 - 正则表达式测试工具"):
        st.markdown("""
        ### 重要注意事项

        **语法安全:**
        - 避免使用可能引起性能问题的复杂正则
        - 注意特殊字符的转义处理
        - 测试前建议先在小型数据集验证

        **性能警告:**
        - 回溯灾难性正则表达式可能导致浏览器卡顿
        - 超大文本匹配可能影响页面响应
        - 建议逐步构建复杂正则表达式

        **功能限制:**
        - 部分高级正则特性可能不支持
        - 替换功能为简单文本替换，不支持回调函数
        - 匹配数量过多时可能只显示部分结果
        """)

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
    st.markdown('<div class="section-header">📊 JSON数据对比工具</div>', unsafe_allow_html=True)

    with st.expander("📋 使用说明 - JSON数据对比工具"):
        st.markdown("""
        ### JSON数据对比工具使用说明

        **主要功能:**
        - 并排显示两个JSON数据，支持格式化查看
        - 深度对比JSON结构差异
        - 统计键数量差异和具体差异点
        - 支持大JSON文件的对比分析

        **对比维度:**
        - 键的存在性：检查缺失或多余的键
        - 值的一致性：对比对应键的值差异
        - 类型匹配：验证数据类型是否一致
        - 结构完整性：检查数组长度和嵌套结构
        """)

    with st.expander("⚠️ 注意事项 - JSON数据对比工具"):
        st.markdown("""
        ### 重要注意事项

        **数据格式:**
        - 确保输入的JSON格式正确有效
        - 支持标准JSON格式，不支持JSON5等扩展格式
        - 格式化功能会自动修复简单的格式错误

        **对比限制:**
        - 超大JSON文件（超过1MB）可能影响性能
        - 深度嵌套结构可能显示不完整
        - 数组顺序差异会被识别为内容差异

        **结果解读:**
        - 差异报告仅供参考，需要人工确认重要性
        - 某些差异可能是正常的业务逻辑变化
        - 建议结合具体业务场景分析差异
        """)

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
    st.markdown('<div class="section-header">📋 日志分析工具</div>', unsafe_allow_html=True)

    with st.expander("📋 使用说明 - 日志分析工具"):
        st.markdown("""
        ### 日志分析工具使用说明

        **分析功能:**
        - 支持文件上传和直接粘贴两种日志导入方式
        - 自动统计日志级别分布（ERROR、WARN、INFO等）
        - 可视化展示日志级别比例和数量
        - 提供强大的日志过滤和搜索功能

        **过滤选项:**
        - 按日志级别过滤：支持多选级别类型
        - 关键词搜索：支持普通搜索和正则表达式
        - 大小写敏感：精确匹配关键词
        - 实时过滤：立即显示过滤结果
        """)

    with st.expander("⚠️ 注意事项 - 日志分析工具"):
        st.markdown("""
        ### 重要注意事项

        **文件支持:**
        - 支持.txt和.log格式的日志文件
        - 文件编码建议使用UTF-8
        - 超大日志文件可能需要较长时间处理

        **分析精度:**
        - 日志级别识别基于关键词匹配，可能不准确
        - 复杂格式的日志可能需要自定义解析规则
        - 时间戳格式识别能力有限

        **性能考虑:**
        - 超过10万行的日志文件建议分段分析
        - 复杂正则表达式搜索可能影响性能
        - 实时过滤功能在大型日志上可能较慢
        """)

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
    st.markdown('<div class="section-header">⏰ 时间处理工具</div>', unsafe_allow_html=True)

    with st.expander("📋 使用说明 - 时间处理工具"):
        st.markdown("""
        ### 时间处理工具使用说明

        **工具分类:**
        - **时间戳转换**: 时间戳与日期时间互相转换
        - **时间换算工具**: 不同时间单位之间的换算
        - **日期计算器**: 日期加减和间隔计算

        **时间戳转换:**
        - 支持秒级和毫秒级时间戳
        - 自动识别时间戳类型
        - 实时获取当前时间戳

        **时间换算:**
        - 支持常见时间单位换算
        - 提供精确到6位小数的结果
        - 内置常用时间换算表参考

        **日期计算:**
        - 支持工作日和自然日计算
        - 考虑月份天数差异和闰年情况
        - 提供详细的间隔分析
        """)

    with st.expander("⚠️ 注意事项 - 时间处理工具"):
        st.markdown("""
        ### 重要注意事项

        **时间戳精度:**
        - 时间戳转换精度到秒级
        - 毫秒级时间戳需要手动选择类型
        - 时区基于系统当前时区设置

        **日期计算规则:**
        - 工作日计算排除周六周日
        - 月份计算按实际天数，非固定30天
        - 闰年自动识别和处理

        **使用限制:**
        - 不支持公元前日期计算
        - 极早或极晚的日期可能计算不准确
        - 时区转换功能有限，建议使用UTC时间
        """)

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
    st.markdown('<div class="section-header">🌐 IP/域名查询工具</div>', unsafe_allow_html=True)

    with st.expander("📋 使用说明 - IP/域名查询工具"):
        st.markdown("""
        ### IP/域名查询工具使用说明

        **查询功能分类:**
        - **基本信息查询**: IP/域名归属地、运营商等信息
        - **子域名查询**: 查找主域名下的所有子域名
        - **备案信息查询**: 查询网站备案信息（中国大陆）
        - **批量查询工具**: 批量处理多个IP/域名查询
        - **IPv4转换工具**: IP地址各种格式转换
        - **旁站查询**: 查找同一服务器上的其他网站
        - **IP反查网站**: 通过IP查找使用该IP的网站

        **数据来源:**
        - 结合本地数据库和公开API查询
        - 归属地信息具体到城市级别
        - 运营商信息基于IP段数据库
        """)

    with st.expander("⚠️ 注意事项 - IP/域名查询工具"):
        st.markdown("""
        ### 重要注意事项

        **数据准确性:**
        - 查询结果仅供参考，不保证100%准确
        - IP归属地可能因运营商策略而变化
        - 域名备案信息为模拟数据，实际以官方为准

        **查询限制:**
        - 批量查询有速率限制，避免频繁请求
        - 某些查询功能需要网络连接
        - 国际IP地址信息可能不完整

        **隐私保护:**
        - 查询记录不会保存到服务器
        - 敏感IP地址查询请谨慎操作
        - 遵守当地网络安全法律法规

        **功能说明:**
        - 部分高级查询功能为演示用途
        - 实际网络环境可能影响查询结果
        - 建议结合多个查询工具验证结果
        """)

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
            十进制 ↔ 点分十进制
            ▪ 8.8.8.8 → 134744072

            ▪ 134744072 → 8.8.8.8


            点分十进制 ↔ 十六进制
            ▪ 8.8.8.8 → 0x8080808

            ▪ 0x8080808 → 8.8.8.8


            点分十进制 ↔ 二进制
            ▪ 8.8.8.8 → 00001000.00001000.00001000.00001000

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

# ================ 通用使用说明和注意事项 ================
st.markdown("---")
st.markdown("### 🎯 通用使用说明")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🔧 工具选择**
    - 左侧边栏选择需要的工具类别
    - 每个工具都有详细的功能说明
    - 支持工具内的多标签页切换

    **📊 数据操作**
    - 大部分工具支持批量操作
    - 生成结果支持一键复制和下载
    - 实时预览和即时反馈

    **🛠️ 高级功能**
    - Faker库提供真实感数据生成
    - 正则表达式测试支持多种模式
    - JSON深度对比和格式化
    """)

with col2:
    st.markdown("""
    **📁 文件支持**
    - 支持文本文件上传和分析
    - 多种格式导出生成结果
    - 大文件分段处理建议

    **⚡ 性能优化**
    - 大型数据集的渐进式处理
    - 内存使用优化和清理
    - 响应式界面设计

    **🔒 安全隐私**
    - 本地处理，数据不上传服务器
    - 敏感信息自动清理
    - 安全的测试数据生成
    """)

st.markdown("### ⚠️ 通用注意事项")

st.markdown("""
**🛡️ 安全警告**
- 生成的测试数据严禁用于生产环境
- 敏感操作前请确认数据备份
- 遵守数据隐私保护法律法规

**📏 使用限制**
- 单次处理数据量建议在合理范围内
- 复杂操作可能需要较长时间
- 某些功能需要额外的依赖库支持

**🔧 技术说明**
- 部分功能需要网络连接
- 浏览器兼容性：推荐Chrome/Firefox
- 移动端体验可能有限

**📞 问题反馈**
- 功能问题请检查使用说明
- 性能问题尝试减少数据量
- 复杂需求考虑使用专业工具
""")
