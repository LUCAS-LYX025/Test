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
</style>
""", unsafe_allow_html=True)


# 辅助函数：计算JSON对象的键数量
def count_keys(obj):
    if isinstance(obj, dict):
        return len(obj.keys()) + sum(count_keys(v) for v in obj.values())
    elif isinstance(obj, list):
        return sum(count_keys(item) for item in obj)
    else:
        return 0


# 页面标题
st.markdown('<div class="main-header">🔧 测试工程师常用工具集</div>', unsafe_allow_html=True)

# 侧边栏导航
st.sidebar.title("导航菜单")
tool_category = st.sidebar.selectbox(
    "选择工具类别",
    ["数据生成工具", "字数统计工具", "文本对比工具", "正则表达式测试工具",
     "JSON数据对比工具", "日志分析工具", "时间处理工具"]
)

# 数据生成工具
if tool_category == "数据生成工具":
    st.markdown('<div class="section-header">数据生成工具</div>', unsafe_allow_html=True)

    # 子工具选择
    data_gen_tool = st.radio(
        "选择数据生成工具",
        ["随机内容生成器", "随机邮箱生成器", "电话号码生成器", "随机地址生成器", "随机身份证生成器"],
        horizontal=True
    )

    # 随机内容生成器
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
            for i in range(count):
                if gen_type == "随机字符串":
                    chars = ""
                    if "小写字母" in chars_type:
                        chars += "abcdefghijklmnopqrstuvwxyz"
                    if "大写字母" in chars_type:
                        chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    if "数字" in chars_type:
                        chars += "0123456789"
                    if "特殊字符" in chars_type:
                        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

                    if not chars:
                        st.error("请至少选择一种字符类型")
                        break

                    result = ''.join(random.choice(chars) for _ in range(length))
                    results.append(result)

                elif gen_type == "随机数字":
                    result = random.randint(min_val, max_val)
                    results.append(str(result))

                elif gen_type == "随机密码":
                    # 确保密码包含所选类型的字符
                    password_chars = ""
                    if "包含小写字母" in password_options:
                        password_chars += "abcdefghijklmnopqrstuvwxyz"
                    if "包含大写字母" in password_options:
                        password_chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    if "包含数字" in password_options:
                        password_chars += "0123456789"
                    if "包含特殊字符" in password_options:
                        password_chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

                    if not password_chars:
                        st.error("请至少选择一种字符类型")
                        break

                    # 确保密码至少包含每种类型的一个字符
                    password = ""
                    if "包含小写字母" in password_options:
                        password += random.choice("abcdefghijklmnopqrstuvwxyz")
                    if "包含大写字母" in password_options:
                        password += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    if "包含数字" in password_options:
                        password += random.choice("0123456789")
                    if "包含特殊字符" in password_options:
                        password += random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")

                    # 填充剩余长度
                    remaining_length = length - len(password)
                    if remaining_length > 0:
                        password += ''.join(random.choice(password_chars) for _ in range(remaining_length))

                    # 随机打乱字符顺序
                    password_list = list(password)
                    random.shuffle(password_list)
                    result = ''.join(password_list)
                    results.append(result)

                elif gen_type == "UUID":
                    result = str(uuid.uuid4())
                    results.append(result)

            if results:
                result_text = "\n".join(results)
                st.text_area("生成结果", result_text, height=150)
                if st.button("复制结果"):
                    st.code(result_text)
                    st.success("结果已复制到剪贴板（模拟）")

    # 随机邮箱生成器
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
            for i in range(count):
                username_length = random.randint(5, 12)
                username = ''.join(
                    random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(username_length))

                if domain_option == "自定义域名":
                    domain = custom_domain
                else:
                    if selected_domains:
                        domain = random.choice(selected_domains)
                    else:
                        domain = random.choice(["gmail.com", "yahoo.com", "hotmail.com"])

                email = f"{username}@{domain}"
                results.append(email)

            result_text = "\n".join(results)
            st.text_area("生成的邮箱", result_text, height=150)
            if st.button("复制邮箱列表"):
                st.code(result_text)
                st.success("邮箱列表已复制到剪贴板（模拟）")

    # 电话号码生成器
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
            # 运营商前缀
            mobile_prefixes = ["139", "138", "137", "136", "135", "134", "159", "158", "157", "150", "151", "152",
                               "147", "188", "187"]
            unicom_prefixes = ["130", "131", "132", "155", "156", "185", "186"]
            telecom_prefixes = ["133", "153", "180", "189"]

            results = []
            for i in range(count):
                if operator == "移动" or (operator == "随机" and random.random() < 0.4):
                    prefix = random.choice(mobile_prefixes)
                elif operator == "联通" or (operator == "随机" and random.random() < 0.3):
                    prefix = random.choice(unicom_prefixes)
                else:
                    prefix = random.choice(telecom_prefixes)

                # 生成后8位数字
                suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
                phone_number = f"{prefix}{suffix}"
                results.append(phone_number)

            result_text = "\n".join(results)
            st.text_area("生成的电话号码", result_text, height=150)
            if st.button("复制电话号码列表"):
                st.code(result_text)
                st.success("电话号码列表已复制到剪贴板（模拟）")

    # 随机地址生成器
    elif data_gen_tool == "随机地址生成器":
        st.markdown('<div class="tool-card">随机地址生成器</div>', unsafe_allow_html=True)

        # 中国省份和城市数据
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
            # 街道和门牌号模板
            streets = ["中山路", "解放路", "人民路", "建设路", "和平路", "新华路", "胜利街", "文化路", "青年路", "东风路"]
            communities = ["小区", "花园", "大厦", "公寓", "广场", "中心", "苑", "居", "湾", "庭"]
            numbers = [str(i) for i in range(1, 201)]

            results = []
            for i in range(count):
                if province == "随机":
                    # 随机选择一个省份（排除"随机"选项）
                    random_province = random.choice([p for p in provinces.keys() if p != "随机"])
                    random_city = random.choice(provinces[random_province])
                    address_province = random_province
                    address_city = random_city
                else:
                    address_province = province
                    if city == "随机":
                        address_city = random.choice([c for c in provinces[province] if c != province])
                    else:
                        address_city = city

                street = random.choice(streets)
                community = random.choice(communities)
                number = random.choice(numbers)

                # 生成完整地址
                full_address = f"{address_province}{address_city}{street}{number}号{random.randint(1, 20)}栋{random.randint(1, 30)}单元{random.randint(101, 1500)}室"
                results.append(full_address)

            result_text = "\n".join(results)
            st.text_area("生成的地址", result_text, height=150)
            if st.button("复制地址列表"):
                st.code(result_text)
                st.success("地址列表已复制到剪贴板（模拟）")

    # 随机身份证生成器
    elif data_gen_tool == "随机身份证生成器":
        st.markdown('<div class="tool-card">随机身份证生成器</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 省份代码（前两位）
            province_codes = {
                "11": "北京市", "12": "天津市", "13": "河北省", "14": "山西省", "15": "内蒙古自治区",
                "21": "辽宁省", "22": "吉林省", "23": "黑龙江省", "31": "上海市", "32": "江苏省",
                "33": "浙江省", "34": "安徽省", "35": "福建省", "36": "江西省", "37": "山东省",
                "41": "河南省", "42": "湖北省", "43": "湖南省", "44": "广东省", "45": "广西壮族自治区",
                "46": "海南省", "50": "重庆市", "51": "四川省", "52": "贵州省", "53": "云南省",
                "54": "西藏自治区", "61": "陕西省", "62": "甘肃省", "63": "青海省", "64": "宁夏回族自治区",
                "65": "新疆维吾尔自治区"
            }

            province = st.selectbox("选择省份", ["随机"] + list(province_codes.values()))
            gender = st.selectbox("选择性别", ["随机", "男", "女"])
            count = st.number_input("生成数量", min_value=1, max_value=50, value=10)

        with col2:
            min_age = st.number_input("最小年龄", min_value=0, max_value=100, value=18)
            max_age = st.number_input("最大年龄", min_value=0, max_value=100, value=60)
            if min_age > max_age:
                st.error("最小年龄不能大于最大年龄")

        if st.button("生成身份证"):
            results = []
            for i in range(count):
                # 1. 生成前6位地区码
                if province == "随机":
                    province_code = random.choice(list(province_codes.keys()))
                else:
                    # 根据省份名称查找代码
                    for code, name in province_codes.items():
                        if name == province:
                            province_code = code
                            break
                    else:
                        province_code = "11"  # 默认北京

                # 随机生成地区码后4位
                area_code = province_code + ''.join([str(random.randint(0, 9)) for _ in range(4)])

                # 2. 生成出生日期码（8位）
                # 计算出生年份范围
                current_year = datetime.datetime.now().year
                birth_year = random.randint(current_year - max_age, current_year - min_age)
                birth_month = random.randint(1, 12)

                # 处理不同月份的天数
                if birth_month in [1, 3, 5, 7, 8, 10, 12]:
                    max_day = 31
                elif birth_month in [4, 6, 9, 11]:
                    max_day = 30
                else:  # 2月
                    # 简单处理闰年
                    if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
                        max_day = 29
                    else:
                        max_day = 28

                birth_day = random.randint(1, max_day)
                birth_date = f"{birth_year:04d}{birth_month:02d}{birth_day:02d}"

                # 3. 生成顺序码（3位）
                if gender == "男":
                    # 男性奇数
                    sequence = random.randint(1, 499) * 2 + 1
                elif gender == "女":
                    # 女性偶数
                    sequence = random.randint(0, 499) * 2
                else:  # 随机
                    sequence = random.randint(0, 999)

                sequence_code = f"{sequence:03d}"

                # 4. 生成前17位
                first_17 = area_code + birth_date + sequence_code

                # 5. 计算校验码（第18位）
                # 加权因子
                factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
                # 校验码对应关系
                check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

                total = 0
                for j in range(17):
                    total += int(first_17[j]) * factors[j]

                check_code = check_codes[total % 11]

                # 6. 生成完整身份证号
                id_card = first_17 + check_code
                results.append(id_card)

            result_text = "\n".join(results)
            st.text_area("生成的身份证号", result_text, height=150)
            if st.button("复制身份证列表"):
                st.code(result_text)
                st.success("身份证列表已复制到剪贴板（模拟）")

# 字数统计工具
elif tool_category == "字数统计工具":
    st.markdown('<div class="section-header">字数统计工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">字数统计工具</div>', unsafe_allow_html=True)

    text_input = st.text_area("输入要统计的文本", height=200, placeholder="在此处输入或粘贴文本...")

    if text_input:
        # 实时统计
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("字符数（含空格）", len(text_input))

        with col2:
            st.metric("字符数（不含空格）", len(text_input.replace(" ", "")))

        with col3:
            # 简单的单词数统计（按空格分割）
            words = text_input.split()
            st.metric("单词数", len(words))

        with col4:
            lines = text_input.split('\n')
            st.metric("行数", len(lines))

        with col5:
            # 段落数（连续的非空行视为一个段落）
            paragraphs = [p for p in text_input.split('\n\n') if p.strip()]
            st.metric("段落数", len(paragraphs))

        # 详细统计信息
        st.subheader("详细统计信息")

        # 字符频率统计
        char_freq = {}
        for char in text_input:
            if char in char_freq:
                char_freq[char] += 1
            else:
                char_freq[char] = 1

        # 显示前10个最常见字符
        sorted_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        if sorted_chars:
            st.write("最常见字符（前10个）:")
            for char, freq in sorted_chars:
                # 处理特殊字符显示
                if char == ' ':
                    display_char = "[空格]"
                elif char == '\n':
                    display_char = "[换行]"
                elif char == '\t':
                    display_char = "[制表符]"
                else:
                    display_char = char

                st.write(f"'{display_char}': {freq}次")

# 文本对比工具
elif tool_category == "文本对比工具":
    st.markdown('<div class="section-header">文本对比工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">文本对比工具</div>', unsafe_allow_html=True)

    # 初始化session_state
    if 'text1_content' not in st.session_state:
        st.session_state.text1_content = ""
    if 'text2_content' not in st.session_state:
        st.session_state.text2_content = ""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("原始文本")
        text1 = st.text_area("原始文本输入区",
                           height=300,
                           key="text1",
                           value=st.session_state.text1_content,
                           label_visibility="collapsed")

    with col2:
        st.subheader("对比文本")
        text2 = st.text_area("对比文本输入区",
                           height=300,
                           key="text2",
                           value=st.session_state.text2_content,
                           label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("开始对比"):
            if text1 and text2:
                # 使用difflib进行文本对比
                d = Differ()
                diff = list(d.compare(text1.splitlines(), text2.splitlines()))

                # 显示对比结果
                st.subheader("对比结果")

                result_html = "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>"
                for line in diff:
                    if line.startswith('+ '):
                        # 新增内容 - 绿色背景
                        result_html += f"<div style='background-color: #d4edda; margin: 2px 0; padding: 2px 5px;'>{line[2:]}</div>"
                    elif line.startswith('- '):
                        # 删除内容 - 红色背景
                        result_html += f"<div style='background-color: #f8d7da; margin: 2px 0; padding: 2px 5px;'>{line[2:]}</div>"
                    elif line.startswith('? '):
                        # 修改提示 - 黄色背景
                        result_html += f"<div style='background-color: #fff3cd; margin: 2px 0; padding: 2px 5px;'>{line[2:]}</div>"
                    else:
                        # 相同内容
                        result_html += f"<div style='margin: 2px 0; padding: 2px 5px;'>{line[2:] if line.startswith('  ') else line}</div>"

                result_html += "</div>"
                st.markdown(result_html, unsafe_allow_html=True)
            else:
                st.warning("请填写原始文本和对比文本")

    with col2:
        if st.button("清空所有内容"):
            # 清空session_state中的内容
            st.session_state.text1_content = ""
            st.session_state.text2_content = ""
            # 使用st.rerun()刷新页面
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
                # 构建标志
                flags = 0
                if ignore_case:
                    flags |= re.IGNORECASE
                if multiline:
                    flags |= re.MULTILINE

                if global_match:
                    # 查找所有匹配
                    matches = list(re.finditer(regex_pattern, test_text, flags))
                    match_count = len(matches)

                    if match_count > 0:
                        st.success(f"匹配成功！找到 {match_count} 个匹配项。")

                        # 显示匹配详情
                        st.subheader("匹配详情")
                        for i, match in enumerate(matches):
                            st.write(f"匹配 {i + 1}: 位置 {match.start()}-{match.end()}: '{match.group()}'")

                            # 显示分组信息
                            if match.groups():
                                st.write(f"  分组: {match.groups()}")
                    else:
                        st.warning("未找到匹配项。")

                # 替换功能
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

    # 初始化session_state
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
                    # 解析JSON
                    obj1 = json.loads(json1)
                    obj2 = json.loads(json2)

                    # 简单的对比逻辑
                    st.subheader("对比结果")


                    # 对比两个JSON对象
                    def compare_json(obj1, obj2, path=""):
                        differences = []

                        if type(obj1) != type(obj2):
                            differences.append(f"类型不同: {path} ({type(obj1).__name__} vs {type(obj2).__name__})")
                            return differences

                        if isinstance(obj1, dict):
                            # 检查所有键
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

                    # 显示摘要统计
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
            # 清空session_state中的内容
            st.session_state.json1_content = ""
            st.session_state.json2_content = ""
            st.rerun()

# 日志分析工具
elif tool_category == "日志分析工具":
    st.markdown('<div class="section-header">日志分析工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-card">日志分析工具</div>', unsafe_allow_html=True)

    # 日志导入方式
    import_method = st.radio("日志导入方式", ["文件上传", "直接粘贴"])

    log_content = ""

    if import_method == "文件上传":
        uploaded_file = st.file_uploader("选择日志文件", type=['txt', 'log'])
        if uploaded_file is not None:
            # 读取文件内容
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            log_content = stringio.read()

    else:  # 直接粘贴
        log_content = st.text_area("粘贴日志内容", height=200)

    if log_content:
        # 基本统计信息
        st.subheader("日志统计信息")

        lines = log_content.split('\n')
        total_lines = len(lines)

        # 简单的日志级别统计
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

        # 可视化图表
        st.subheader("可视化分析")

        # 日志级别分布
        if error_count + warn_count + info_count > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

            # 饼图
            levels = ['ERROR', 'WARN', 'INFO', '其他']
            counts = [error_count, warn_count, info_count, total_lines - error_count - warn_count - info_count]

            ax1.pie(counts, labels=levels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('日志级别分布')

            # 柱状图
            ax2.bar(levels, counts, color=['red', 'orange', 'blue', 'gray'])
            ax2.set_title('日志级别数量')
            ax2.set_ylabel('数量')

            st.pyplot(fig)

        # 日志过滤功能
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
                # 级别过滤
                level_match = False
                for level in filter_level:
                    if level in line:
                        level_match = True
                        break

                if not filter_level or level_match:
                    # 关键词搜索
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
                # 模拟导出功能
                st.success(f"已找到 {len(filtered_lines)} 行匹配结果（导出功能模拟）")

# 时间处理工具
elif tool_category == "时间处理工具":
    st.markdown('<div class="section-header">时间处理工具</div>', unsafe_allow_html=True)

    # 子工具选择
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
                # 转换到秒的系数
                to_seconds = {
                    "毫秒": 0.001,
                    "秒": 1,
                    "分钟": 60,
                    "小时": 3600,
                    "天": 86400,
                    "周": 604800,
                    "月": 2592000,  # 近似值
                    "年": 31536000  # 近似值
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
                            # 月份的加减需要更复杂的处理
                            year = start_date.year + (start_date.month + value - 1) // 12
                            month = (start_date.month + value - 1) % 12 + 1
                            day = min(start_date.day,
                                      [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28, 31,
                                       30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
                            result_date = datetime.date(year, month, day)
                        elif unit == "年":
                            result_date = start_date.replace(year=start_date.year + value)

                    else:  # 减去
                        if unit == "天":
                            result_date = start_date - timedelta(days=value)
                        elif unit == "周":
                            result_date = start_date - timedelta(weeks=value)
                        elif unit == "月":
                            # 月份的加减需要更复杂的处理
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

        else:  # 日期间隔计算
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

                        # 计算工作日（简单实现，不考虑节假日）
                        # 这里只是一个示例，实际实现需要考虑更多因素
                        business_days = 0
                        current_date = start_date
                        while current_date <= end_date:
                            if current_date.weekday() < 5:  # 周一到周五
                                business_days += 1
                            current_date += timedelta(days=1)

                        st.info(f"工作日: {business_days} 天")
                        st.info(f"周末天数: {delta.days - business_days} 天")

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
""")