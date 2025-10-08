import difflib

import pandas as pd
import json
import re
from datetime import timedelta
import time
import streamlit.components.v1 as components
from difflib import Differ
import streamlit as st
from doc_manager import show_doc, show_general_guidelines
from ip_query_tool import IPQueryTool
from data_generator import DataGenerator
import sys
from PIL import Image
import io

print(sys.path)
sys.path.append('/mount/src/test/test')
from data_constants import PROVINCES, COUNTRIES, CATEGORIES, PROVINCE_MAP, TO_SECONDS, RANDOM_STRING_TYPES, \
    PASSWORD_OPTIONS, DOMAINS_PRESET, GENDERS, TOOL_CATEGORIES, CSS_STYLES, HEADLINE_STYLES, PRESET_SIZES
from data_constants import LANGUAGE_TEMPLATES
from data_constants import PREDEFINED_PATTERNS
from data_constants import PROVINCE_CITY_AREA_CODES
from datetime_utils import DateTimeUtils
from json_file_utils import JSONFileUtils
from collections import Counter
import datetime
import uuid
import random
import base64
import hashlib
import hmac
import binascii
from Crypto.Cipher import AES, DES, DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import urllib.parse
import html
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import codecs
import sys
import os
import pytesseract

# 在导入部分添加

try:
    import pytesseract
    from io import BytesIO
    import cv2
    import xmind
    from xmind.core.markerref import MarkerId
    from PIL import Image
    import numpy as np
    import openpyxl
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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

# 现代化CSS样式
st.markdown(CSS_STYLES, unsafe_allow_html=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
custom_tesseract_path = os.path.join(current_dir, "fonts", "tesseract")

# 配置pytesseract使用自定义的tesseract路径
pytesseract.pytesseract.tesseract_cmd = custom_tesseract_path
# ================ 辅助函数 ================
# 添加辅助函数
def call_ali_testcase_api(requirement, api_key, id_prefix):
    """调用阿里大模型API生成测试用例"""
    import requests
    import json
    import re

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""你是一位资深软件测试专家，请基于以下需求生成测试用例：

需求描述：
{requirement}

请生成全面、精准的测试用例，每个测试用例包含以下字段：
- 用例ID：格式为{id_prefix}001, {id_prefix}002等
- 用例名称：清晰描述测试场景
- 前置条件：执行测试前需要满足的条件
- 测试步骤：详细的测试操作步骤
- 预期结果：期望的输出或行为
- 优先级：高、中、低

请确保测试用例：
1. 覆盖所有主要功能点
2. 包含正常和异常场景
3. 考虑边界条件和错误处理
4. 优先级设置合理

请以严格的JSON数组格式返回。"""

    payload = {
        "model": "qwen-turbo",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        "parameters": {
            "result_format": "text"
        }
    }

    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        response_data = response.json()

        if "output" in response_data and "text" in response_data["output"]:
            result_text = response_data["output"]["text"]

            # 提取JSON
            json_pattern = r'\[\s*\{.*\}\s*\]'
            match = re.search(json_pattern, result_text, re.DOTALL)
            if match:
                json_str = match.group()
                test_cases = json.loads(json_str)

                # 确保用例ID格式正确
                for i, test_case in enumerate(test_cases):
                    if "用例ID" not in test_case or not test_case["用例ID"].startswith(id_prefix):
                        test_case["用例ID"] = f"{id_prefix}{i + 1:03d}"

                return test_cases
            else:
                raise Exception("无法从API响应中解析出测试用例数据")
        else:
            raise Exception("API响应格式错误")

    except Exception as e:
        raise Exception(f"API调用失败: {str(e)}")


def generate_regex_from_examples(text, examples):
    """根据示例文本生成正则表达式"""
    if not text or not examples:
        return ""

    example_list = [ex.strip() for ex in examples.split(",") if ex.strip()]

    if not example_list:
        return ""

    # 简化的模式识别逻辑
    common_pattern = example_list[0]

    for example in example_list[1:]:
        # 找出共同前缀
        i = 0
        while i < min(len(common_pattern), len(example)) and common_pattern[i] == example[i]:
            i += 1
        common_pattern = common_pattern[:i]

    if len(common_pattern) < 2:
        return re.escape(example_list[0])

    escaped_pattern = re.escape(common_pattern)

    # 简单的模式推断
    if len(example_list) > 1:
        if all(ex.replace(common_pattern, "").isdigit() for ex in example_list):
            return escaped_pattern + r"\d+"
        elif all(ex.replace(common_pattern, "").isalpha() for ex in example_list):
            return escaped_pattern + r"[A-Za-z]+"

    return escaped_pattern + ".*"


# 过滤辅助函数
def _apply_text_filters(line, log_levels, ip_filter, status_codes, show_only_errors, hide_debug):
    """应用文本过滤器"""
    include_line = True

    # 日志级别过滤
    if log_levels:
        level_match = False
        if "错误" in log_levels and any(word in line.upper() for word in ['ERROR', 'ERR']):
            level_match = True
        if "警告" in log_levels and any(word in line.upper() for word in ['WARN', 'WARNING']):
            level_match = True
        if "信息" in log_levels and any(word in line.upper() for word in ['INFO', 'INFORMATION']):
            level_match = True
        if "调试" in log_levels and any(word in line.upper() for word in ['DEBUG', 'DBG']):
            level_match = True
        include_line = include_line and level_match

    # IP地址过滤
    if ip_filter and include_line:
        if ip_filter not in line:
            include_line = False

    # 状态码过滤
    if status_codes and include_line:
        codes = [code.strip() for code in status_codes.split(',')]
        code_match = any(f" {code} " in line or line.endswith(f" {code}") or f" {code}" in line for code in codes)
        include_line = include_line and code_match

    # 其他条件
    if show_only_errors and include_line:
        if not any(word in line.upper() for word in ['ERROR', 'ERR', 'FAIL', 'EXCEPTION']):
            include_line = False

    if hide_debug and include_line:
        if any(word in line.upper() for word in ['DEBUG', 'DBG']):
            include_line = False

    return include_line


def escape_js_string(text):
    """安全转义 JavaScript 字符串"""
    return json.dumps(text)


def create_copy_button(text, button_text="📋 复制到剪贴板", key=None):
    """创建一键复制按钮"""
    if key is None:
        key = hash(text)

    escaped_text = escape_js_string(text)

    copy_script = f"""
    <script>
    function copyTextToClipboard{key}() {{
        const text = {escaped_text};
        if (!navigator.clipboard) {{
            return fallbackCopyTextToClipboard(text);
        }}
        return navigator.clipboard.writeText(text).then(function() {{
            return true;
        }}, function(err) {{
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

    document.addEventListener('DOMContentLoaded', function() {{
        const button = document.querySelector('[data-copy-button="{key}"]');
        if (button) {{
            button.addEventListener('click', function() {{
                copyTextToClipboard{key}().then(function(success) {{
                    if (success) {{
                        const originalText = button.innerHTML;
                        button.innerHTML = '✅ 复制成功！';
                        button.style.background = '#48bb78';
                        setTimeout(function() {{
                            button.innerHTML = originalText;
                            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                        }}, 2000);
                    }} else {{
                        button.innerHTML = '❌ 复制失败';
                        button.style.background = '#e53e3e';
                        setTimeout(function() {{
                            button.innerHTML = '{button_text}';
                            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                        }}, 2000);
                    }}
                }});
            }});
        }}
    }});
    </script>
    """

    button_html = f"""
    <div>
        <button data-copy-button="{key}"
                style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:white;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:14px;margin:5px;font-weight:500;transition:all 0.3s ease;width:100%;height:42px;font-family:inherit;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            {button_text}
        </button>
    </div>
    """

    components.html(button_html + copy_script, height=60)


def display_generated_results(title, content, filename_prefix):
    """统一展示生成结果 + 复制 + 下载"""
    st.markdown(f'<div class="category-card">📋 生成结果 - {title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{content}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        create_copy_button(content, button_text="📋 复制结果", key=f"copy_{filename_prefix}")
    with col2:
        st.download_button(
            label="💾 下载结果",
            data=content,
            file_name=f"{filename_prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


# 初始化session state
if 'selected_tool' not in st.session_state:
    st.session_state.selected_tool = "数据生成工具"

# 顶部标题区域
st.markdown(HEADLINE_STYLES, unsafe_allow_html=True)

# 工具卡片网格布局
st.markdown('<div class="sub-header">🚀 可用工具</div>', unsafe_allow_html=True)

# 创建3列布局
cols = st.columns(3)
col_index = 0

for category, info in TOOL_CATEGORIES.items():
    with cols[col_index]:
        is_selected = st.session_state.selected_tool == category

        button_style = f"""
        <style>
            button[key="select_{category}"] {{
                background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if is_selected else 'white'} !important;
                color: {'white' if is_selected else '#2d3748'} !important;
            }}
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)

        if st.button(
                f"{info['icon']} **{category}**\n\n{info['description']}",
                key=f"select_{category}",
                use_container_width=True,
        ):
            st.session_state.selected_tool = category
            st.rerun()

    col_index = (col_index + 1) % 3

# 添加分隔线
st.markdown("---")
# 直接使用session state中的选择
tool_category = st.session_state.selected_tool

# 显示当前选择的工具
st.markdown(f'<div class="sub-header">{TOOL_CATEGORIES[tool_category]["icon"]} {tool_category}</div>',
            unsafe_allow_html=True)

# === 工具功能实现 ===
if tool_category == "数据生成工具":
    show_doc("data_generator")
    generator = DataGenerator()

    gen_mode = st.radio(
        "选择生成模式",
        ["Faker高级生成器", "基础数据生成器"],
        horizontal=True
    )

    if gen_mode == "Faker高级生成器":
        if not FAKER_AVAILABLE:
            st.error("❌ Faker库未安装，无法使用高级生成器")
            st.info("请运行以下命令安装: `pip install faker`")
            st.code("pip install faker", language="bash")
        else:
            st.markdown('<div class="category-card">🚀 Faker高级数据生成器</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                selected_category = st.selectbox("选择数据类别", list(CATEGORIES.keys()))
            with col2:
                selected_subcategory = st.selectbox("选择具体类型", CATEGORIES[selected_category])
            with col3:
                count = st.number_input("生成数量", min_value=1, max_value=100, value=5)

            extra_params = {}
            if selected_subcategory == "随机文本":
                text_length = st.slider("文本长度", min_value=10, max_value=1000, value=200)
                extra_params['length'] = text_length

            if st.button("🎯 生成数据", use_container_width=True):
                with st.spinner("正在生成数据..."):
                    results = generator.safe_generate(generator.generate_faker_data, selected_category,
                                                      selected_subcategory, count, **extra_params)
                    if results is not None:
                        result_text = "\n".join([str(r) for r in results])
                        st.session_state.faker_result = result_text
                        st.session_state.last_category = f"{selected_category} - {selected_subcategory}"

            if 'faker_result' in st.session_state:
                title = st.session_state.get("last_category", "")
                if selected_subcategory == "完整个人信息":
                    st.text_area("生成结果", st.session_state.faker_result, height=300, key="profile_result")
                else:
                    st.markdown(f'<div class="result-box">{st.session_state.faker_result}</div>',
                                unsafe_allow_html=True)
                create_copy_button(st.session_state.faker_result, button_text="📋 复制结果", key="copy_faker_result")
                st.download_button(
                    label="💾 下载结果",
                    data=st.session_state.faker_result,
                    file_name=f"faker_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

    else:  # 基础数据生成器
        st.markdown('<div class="category-card">🔧 基础数据生成器</div>', unsafe_allow_html=True)
        data_gen_tool = st.radio(
            "选择生成工具",
            ["随机内容生成器", "随机邮箱生成器", "电话号码生成器", "随机地址生成器", "随机身份证生成器"],
            horizontal=True
        )

        if data_gen_tool == "随机内容生成器":
            st.markdown('<div class="category-card">🎲 随机内容生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                gen_type = st.selectbox("生成类型", ["随机字符串", "随机数字", "随机密码", "UUID"])

                if gen_type in ["随机字符串", "随机密码"]:
                    length = st.slider("长度", 1, 100, 10, help="生成内容的长度（字符数）")
                if gen_type == "随机数字":
                    min_val = st.number_input("最小值", value=0)
                    max_val = st.number_input("最大值", value=100)

                count = st.number_input("生成数量", min_value=1, max_value=100, value=5)

            with col2:
                if gen_type == "随机字符串":
                    chars_type = st.multiselect("字符类型", RANDOM_STRING_TYPES, default=RANDOM_STRING_TYPES[:3],
                                                help="选择包含的字符类型")
                if gen_type == "随机密码":
                    password_options = st.multiselect("密码选项", PASSWORD_OPTIONS, default=PASSWORD_OPTIONS[:3],
                                                      help="设置密码复杂度要求")

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
                            res = generator.safe_generate(generator.generate_random_string, length, chars_type)
                        elif gen_type == "随机数字":
                            res = str(random.randint(min_val, max_val))
                        elif gen_type == "随机密码":
                            res = generator.safe_generate(generator.generate_random_password, length, password_options)
                        elif gen_type == "UUID":
                            res = str(uuid.uuid4())
                        if res is not None:
                            results.append(res)

                result_text = "\n".join(results)
                conditions = (
                        f"类型: {gen_type}, " +
                        (f"长度: {length}, " if gen_type in ["随机字符串", "随机密码"] else "") +
                        (f"范围: {min_val}-{max_val}, " if gen_type == "随机数字" else "") +
                        (f"字符类型: {', '.join(chars_type)}" if gen_type == "随机字符串" else "") +
                        (f"复杂度: {', '.join(password_options)}" if gen_type == "随机密码" else "")
                )
                display_generated_results(conditions, result_text, "随机内容")

        elif data_gen_tool == "随机邮箱生成器":
            st.markdown('<div class="category-card">📧 随机邮箱生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                count = st.number_input("邮箱数量", min_value=1, max_value=100, value=10)
                domain_option = st.selectbox("域名选项", ["随机域名", "自定义域名"])

            with col2:
                if domain_option == "自定义域名":
                    custom_domain = st.text_input("自定义域名", "example.com", placeholder="输入不带http://的域名")
                    conditions = f"域名: {custom_domain}"
                else:
                    selected_domains = st.multiselect("选择域名", DOMAINS_PRESET, default=DOMAINS_PRESET[:3])
                    conditions = f"随机域名: {', '.join(selected_domains)}"
                st.write("💡 提示: 用户名将随机生成8-12位字母数字组合")

            if st.button("生成邮箱", key="gen_emails"):
                results = []
                with st.spinner(f"正在生成{count}个邮箱地址..."):
                    for _ in range(count):
                        email = generator.safe_generate(generator.generate_random_email, domain_option,
                                                        custom_domain if domain_option == "自定义域名" else None,
                                                        selected_domains if domain_option != "自定义域名" else None)
                        if email is not None:
                            results.append(email)

                result_text = "\n".join(results)
                display_generated_results(conditions, result_text, "邮箱列表")
        elif data_gen_tool == "电话号码生成器":
            st.markdown('<div class="category-card">📞 电话号码生成器</div>', unsafe_allow_html=True)
            # 确保PROVINCES是列表类型
            PROVINCES = list(PROVINCE_CITY_AREA_CODES.keys())


            def get_cities_by_province(province):
                """根据省份获取城市列表"""
                return list(PROVINCE_CITY_AREA_CODES.get(province, {}).keys())


            def get_area_code(province, city):
                """根据省份和城市获取区号"""
                return PROVINCE_CITY_AREA_CODES.get(province, {}).get(city, "")


            col1, col2 = st.columns(2)
            with col1:
                phone_type = st.selectbox("号码类型", ["手机号", "座机", "国际号码"])

                # 初始化变量
                operator = None
                country = None
                province = None
                city = None
                area_code = None

                if phone_type == "国际号码":
                    country = st.selectbox("选择国家", COUNTRIES)
                elif phone_type == "手机号":
                    operator = st.selectbox("运营商", ["随机", "移动", "联通", "电信", "广电"])
                elif phone_type == "座机":
                    # 使用本地定义的 PROVINCES - 确保是列表
                    province_options = ["随机"] + PROVINCES
                    province = st.selectbox("选择省份", province_options)

                    if province and province != "随机":
                        cities = get_cities_by_province(province)
                        city = st.selectbox("选择城市", ["随机"] + cities)

                        # 如果选择了具体城市，获取对应的区号
                        if city and city != "随机":
                            area_code = get_area_code(province, city)
                            if area_code:
                                st.success(f"✅ 所选城市区号: {area_code}")
                            else:
                                st.warning("⚠️ 未找到该城市的区号")
                    else:
                        city = "随机"
                        st.info("将随机生成区号")

                count = st.number_input("生成数量", min_value=1, max_value=100, value=10)

            with col2:
                if phone_type == "座机":
                    if province == "随机":
                        conditions = f"类型: {phone_type}, 区号: 随机"
                    elif city == "随机":
                        conditions = f"类型: {phone_type}, 省份: {province}, 区号: 随机"
                    else:
                        conditions = f"类型: {phone_type}, 城市: {city}, 区号: {area_code}"
                elif phone_type == "国际号码":
                    conditions = f"类型: {phone_type}, 国家: {country}"
                else:
                    conditions = f"运营商: {operator}, 类型: {phone_type}"

                st.write("💡 提示: 生成的号码将匹配相应的号码规则")

            if st.button("生成电话号码", key="gen_conditional_phones"):
                results = []
                selected_area_codes = []  # 用于记录实际使用的区号

                with st.spinner(f"正在生成{count}个号码..."):
                    for i in range(count):
                        try:
                            if phone_type == "座机":
                                # 根据选择确定最终的区号
                                final_area_code = None

                                if province != "随机":
                                    if city != "随机" and area_code:
                                        # 使用具体城市的区号
                                        final_area_code = area_code
                                    else:
                                        # 随机选择该省份下的一个城市区号
                                        cities = get_cities_by_province(province)
                                        if cities:
                                            random_city = random.choice(cities)
                                            final_area_code = get_area_code(province, random_city)

                                # 记录实际使用的区号
                                if final_area_code:
                                    selected_area_codes.append(final_area_code)

                                # 调用生成函数
                                phone = generator.generate_landline_number(area_code=final_area_code)

                            elif phone_type == "国际号码":
                                phone = generator.generate_international_phone(country)
                            else:  # 手机号
                                phone = generator.generate_conditional_phone(operator)

                            if phone is not None:
                                results.append(phone)

                        except Exception as e:
                            # 处理可能的生成错误，继续生成其他号码
                            st.error(f"生成第 {i + 1} 个号码时出错: {str(e)}")
                            continue

                if results:
                    result_text = "\n".join(results)

                    # 删除原来的显示代码，直接使用封装的函数
                    display_generated_results("电话号码", result_text, "电话号码")

                    # 显示调试信息（实际使用的区号）
                    if phone_type == "座机" and selected_area_codes:
                        unique_codes = list(set(selected_area_codes))
                        st.info(f"实际使用的区号: {', '.join(unique_codes)}")

                    # 显示生成统计
                    st.success(f"✅ 成功生成 {len(results)} 个电话号码")
                else:
                    st.warning("⚠️ 未能生成任何有效的电话号码，请检查参数设置")

        elif data_gen_tool == "随机地址生成器":
            st.markdown('<div class="category-card">🏠 随机地址生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                province = st.selectbox("选择省份", ["随机"] + [p for p in PROVINCES.keys() if p != "随机"])
                count = st.number_input("生成数量", min_value=1, max_value=50, value=10)
                detailed = st.checkbox("生成详细地址", value=True)

            with col2:
                if province != "随机":
                    city_options = PROVINCES[province]
                    city = st.selectbox("选择城市", ["随机"] + [c for c in city_options if c != province])
                else:
                    city = "随机"

                conditions = (
                        f"省份: {province if province != '随机' else '随机选择'}, " +
                        f"城市: {city if city != '随机' else '随机选择'}, " +
                        f"详细程度: {'详细地址' if detailed else '仅省市信息'}"
                )
                st.write("💡 提示: 详细地址包含街道、门牌号等信息")

            if st.button("生成地址", key="gen_addresses"):
                results = []
                with st.spinner(f"正在生成{count}个地址..."):
                    for _ in range(count):
                        selected_province = province
                        if province == "随机":
                            selected_province = random.choice([p for p in PROVINCES.keys() if p != "随机"])

                        selected_city = city
                        if city == "随机":
                            if selected_province in PROVINCES:
                                city_options = [c for c in PROVINCES[selected_province] if c != selected_province]
                                selected_city = random.choice(city_options) if city_options else selected_province

                        addr = generator.safe_generate(generator.generate_random_address, selected_province,
                                                       selected_city, detailed)
                        if addr is not None:
                            results.append(addr)

                result_text = "\n".join(results)
                display_generated_results(conditions, result_text, "地址列表")

        elif data_gen_tool == "随机身份证生成器":
            st.markdown('<div class="category-card">🆔 随机身份证生成器</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                province = st.selectbox("选择省份", ["随机"] + list(PROVINCE_MAP.keys()))
                gender = st.selectbox("选择性别", GENDERS)
                count = st.number_input("生成数量", min_value=1, max_value=100, value=10)

            with col2:
                min_age = st.number_input("最小年龄", min_value=0, max_value=100, value=18)
                max_age = st.number_input("最大年龄", min_value=0, max_value=100, value=60)
                if min_age > max_age:
                    st.error("最小年龄不能大于最大年龄")

                conditions = f"省份: {province}, 性别: {gender}, 年龄: {min_age}-{max_age}岁"
                st.write("💡 提示: 生成的身份证将严格符合选择的省份、性别和年龄条件")

            if st.button("生成身份证", key="gen_id_cards"):
                results = []
                with st.spinner(f"正在生成{count}个身份证号码..."):
                    for _ in range(count):
                        id_card = generator.safe_generate(generator.generate_random_id_card,
                                                          province if province != "随机" else random.choice(
                                                              list(PROVINCE_MAP.keys())),
                                                          gender,
                                                          min_age,
                                                          max_age)
                        if id_card is not None:
                            results.append(id_card)

                result_text = "\n".join(results)
                display_generated_results(conditions, result_text, "身份证列表")

    st.markdown('</div>', unsafe_allow_html=True)

# 字数统计工具
elif tool_category == "字数统计工具":
    show_doc("word_counter")

    # 添加CSS样式
    st.markdown("""
    <style>
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 4px solid;
        margin-bottom: 1rem;
    }
    .progress-bar {
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # 侧边栏设置
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 字数目标设置")

    target_words = st.sidebar.number_input("设定目标单词数", min_value=0, value=1000, step=100)
    target_chars = st.sidebar.number_input("设定目标字符数", min_value=0, value=5000, step=500)

    st.sidebar.markdown("### 🎨 显示选项")
    show_charts = st.sidebar.checkbox("显示图表", value=True)
    show_advanced = st.sidebar.checkbox("显示高级分析", value=False)
    show_suggestions = st.sidebar.checkbox("显示编辑建议", value=True)

    text_input = st.text_area("输入要统计的文本", height=200, placeholder="在此处输入或粘贴文本...", key="word_counter_text")

    if text_input:
        # 基础统计计算
        words = text_input.split()
        lines = text_input.split('\n')
        paragraphs = [p for p in text_input.split('\n\n') if p.strip()]
        char_freq = Counter(text_input)

        # 字符类型统计
        import string

        letters = sum(1 for char in text_input if char.isalpha())
        digits = sum(1 for char in text_input if char.isdigit())
        spaces = text_input.count(' ')
        punctuation = sum(1 for char in text_input if char in string.punctuation)
        chinese_chars = sum(1 for char in text_input if '\u4e00' <= char <= '\u9fff')

        # 句子统计（简单实现）
        sentences = []
        for sep in ['.', '!', '?', '。', '！', '？']:
            sentences.extend([s.strip() for s in text_input.split(sep) if s.strip()])
        sentences = [s for s in sentences if s]

        # 计算常用指标
        total_chars = len(text_input)
        total_chars_no_spaces = len(text_input.replace(' ', ''))
        total_words = len(words)
        total_lines = len(lines)
        total_paragraphs = len(paragraphs)
        total_sentences = len(sentences)

        # 质量指标计算
        avg_word_length = sum(len(word) for word in words) / total_words if words else 0
        avg_sentence_length = total_words / total_sentences if total_sentences else 0
        avg_paragraph_length = total_words / total_paragraphs if total_paragraphs else 0
        reading_time = total_words / 200  # 按200词/分钟

        # 主要指标卡片布局
        st.markdown("### 📊 主要统计指标")
        col1, col2, col3, col4, col5 = st.columns(5)

        metrics_data = [
            {"title": "字符数（含空格）", "value": total_chars, "color": "#667eea"},
            {"title": "字符数（不含空格）", "value": total_chars_no_spaces, "color": "#48bb78"},
            {"title": "单词数", "value": total_words, "color": "#ed8936"},
            {"title": "行数", "value": total_lines, "color": "#9f7aea"},
            {"title": "段落数", "value": total_paragraphs, "color": "#f56565"}
        ]

        for i, metric in enumerate(metrics_data):
            with [col1, col2, col3, col4, col5][i]:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {metric['color']};">
                    <div style="font-size: 1rem; font-weight: 600; color: {metric['color']};">{metric['title']}</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #2d3748;">{metric['value']:,}</div>
                </div>
                """, unsafe_allow_html=True)

        # 进度跟踪
        if target_words > 0 or target_chars > 0:
            st.markdown("### 🎯 目标进度")
            progress_col1, progress_col2 = st.columns(2)

            progress_data = [
                {"target": target_words, "current": total_words, "label": "单词"},
                {"target": target_chars, "current": total_chars, "label": "字符"}
            ]

            for i, progress in enumerate(progress_data):
                if progress["target"] > 0:
                    with [progress_col1, progress_col2][i]:
                        progress_value = min(progress["current"] / progress["target"], 1.0)
                        st.write(f"{progress['label']}进度: {progress['current']}/{progress['target']}")
                        st.markdown(f"""
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress_value * 100}%"></div>
                        </div>
                        <div style="text-align: center; font-size: 0.9rem; color: #666;">{progress_value * 100:.1f}%</div>
                        """, unsafe_allow_html=True)

                        if progress["current"] >= progress["target"]:
                            st.success(f"🎉 恭喜！已达到目标{progress['label']}数！")

        # 字符类型统计
        st.markdown("### 🔤 字符类型分析")
        col6, col7, col8, col9, col10 = st.columns(5)

        char_type_data = [
            ("字母数", letters),
            ("数字数", digits),
            ("标点符号", punctuation),
            ("空格数", spaces),
            ("中文字符", chinese_chars)
        ]

        for i, (title, value) in enumerate(char_type_data):
            with [col6, col7, col8, col9, col10][i]:
                st.metric(title, f"{value:,}")

        # 文本质量指标
        st.markdown("### 📈 文本质量指标")
        col11, col12, col13, col14 = st.columns(4)

        quality_metrics = [
            ("平均词长", f"{avg_word_length:.1f}字符"),
            ("平均句长", f"{avg_sentence_length:.1f}词"),
            ("阅读时间", f"{reading_time:.1f}分钟"),
            ("平均段落长", f"{avg_paragraph_length:.1f}词")
        ]

        for i, (title, value) in enumerate(quality_metrics):
            with [col11, col12, col13, col14][i]:
                st.metric(title, value)

        # 图表显示
        if show_charts:
            st.markdown("### 📊 可视化分析")

            try:
                import plotly.express as px
                import plotly.graph_objects as go
                import pandas as pd

                tab1, tab2, tab3 = st.tabs(["字符频率", "类型分布", "文本结构"])

                with tab1:
                    top_chars = char_freq.most_common(15)
                    if top_chars:
                        chars, freqs = zip(*top_chars)
                        SPECIAL_CHARS_DISPLAY = {
                            ' ': "空格",
                            '\n': "换行",
                            '\t': "制表符",
                            '\r': "回车"
                        }
                        char_display = [SPECIAL_CHARS_DISPLAY.get(char, char) for char in chars]

                        fig = px.bar(
                            x=freqs, y=char_display,
                            orientation='h',
                            title='Top 15 字符频率',
                            labels={'x': '出现次数', 'y': '字符'}
                        )
                        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                        st.plotly_chart(fig)

                with tab2:
                    type_data = {
                        '字母': letters,
                        '数字': digits,
                        '标点': punctuation,
                        '空格': spaces,
                        '中文': chinese_chars,
                        '其他': total_chars - (letters + digits + punctuation + spaces + chinese_chars)
                    }
                    type_data = {k: v for k, v in type_data.items() if v > 0}

                    if type_data:
                        fig = px.pie(
                            values=list(type_data.values()),
                            names=list(type_data.keys()),
                            title='字符类型分布'
                        )
                        st.plotly_chart(fig)

                with tab3:
                    structure_data = {
                        '字符': total_chars,
                        '单词': total_words,
                        '句子': total_sentences,
                        '行数': total_lines,
                        '段落': total_paragraphs
                    }

                    fig = px.bar(
                        x=list(structure_data.keys()),
                        y=list(structure_data.values()),
                        title='文本结构概览',
                        labels={'x': '统计类型', 'y': '数量'},
                        color=list(structure_data.keys()),
                        color_discrete_sequence=['#667eea', '#48bb78', '#ed8936', '#9f7aea', '#f56565']
                    )
                    st.plotly_chart(fig)

            except ImportError:
                st.warning("高级图表需要 plotly 库。请安装: `pip install plotly`")
                # 回退到 streamlit 原生图表
                st.info("使用基础图表显示...")

        # 字符频率详情
        st.markdown("### 🔍 字符频率详情")
        SPECIAL_CHARS_DISPLAY = {
            ' ': "[空格]",
            '\n': "[换行]",
            '\t': "[制表符]",
            '\r': "[回车]"
        }

        col_freq1, col_freq2 = st.columns(2)

        with col_freq1:
            st.write("**最常见字符（前10个）:**")
            sorted_chars = char_freq.most_common(10)
            for char, freq in sorted_chars:
                display_char = SPECIAL_CHARS_DISPLAY.get(char, char)
                st.write(f"`{display_char}`: {freq:,}次 ({freq / total_chars * 100:.2f}%)")

        with col_freq2:
            st.write("**最罕见字符（后10个）:**")
            rare_chars = char_freq.most_common()[-10:]
            for char, freq in rare_chars:
                display_char = SPECIAL_CHARS_DISPLAY.get(char, char)
                st.write(f"`{display_char}`: {freq:,}次")

        # 编辑建议
        if show_suggestions:
            st.markdown("### 📝 编辑建议")
            suggestions = []

            # 文本长度分析
            if total_chars < 50:
                suggestions.append("📝 **文本较短**: 当前仅{}字，建议补充更多细节、例证或分析以丰富内容".format(total_chars))
            elif total_chars > 10000:
                suggestions.append("📝 **文本较长**: 当前{}字，考虑是否可拆分为多个部分或精简冗余内容".format(total_chars))

            # 句子结构分析
            if total_sentences > 0:
                if avg_sentence_length > 25:
                    suggestions.append("📝 **句子偏长**: 平均句长{:.1f}词，建议拆分复杂长句，每句控制在15-25词为宜".format(avg_sentence_length))
                elif avg_sentence_length < 8:
                    suggestions.append("📝 **句子偏短**: 平均句长仅{:.1f}词，可适当合并短句以增强表达连贯性".format(avg_sentence_length))

            # 词汇层面分析
            long_words = [word for word in words if len(word) > 20]
            if long_words:
                suggestions.append("📝 **超长单词**: 发现{}个超长单词（如'{}'），建议使用更简洁的表达替代".format(len(long_words), long_words[0]))

            # 段落结构分析
            if total_paragraphs > 0:
                if avg_paragraph_length > 300:
                    suggestions.append("📝 **段落过长**: 平均每段{:.0f}词，建议将长段落按主题拆分为2-3个段落".format(avg_paragraph_length))
                elif avg_paragraph_length < 50:
                    suggestions.append("📝 **段落过短**: 平均每段仅{:.0f}词，可适当合并相关短段落".format(avg_paragraph_length))

            # 词汇多样性分析
            if total_words > 0:
                lexical_diversity = len(set(words)) / total_words
                if lexical_diversity < 0.5:
                    suggestions.append("📝 **词汇重复**: 词汇多样性指数{:.2f}，建议使用同义词替换高频重复词汇".format(lexical_diversity))
                elif lexical_diversity > 0.8:
                    suggestions.append("🌈 **词汇丰富**: 词汇多样性指数{:.2f}，用词变化丰富，表现良好".format(lexical_diversity))

            # 可读性增强建议
            if len([word for word in words if word.isupper() and len(word) > 1]) > 3:
                suggestions.append("📝 **全大写使用**: 文本中全大写词汇较多，建议适度使用以保持阅读舒适度")

            # 输出建议
            if suggestions:
                st.markdown("#### 改进建议")
                for i, suggestion in enumerate(suggestions, 1):
                    if "表现良好" in suggestion:
                        st.success(f"{i}. {suggestion}")
                    else:
                        st.warning(f"{i}. {suggestion}")

                # 总结性建议
                st.markdown("---")
                improvement_count = len([s for s in suggestions if "表现良好" not in s])
                if improvement_count == 0:
                    st.balloons()
                    st.success("🎉 文本质量优秀！所有指标均达到理想标准")
                else:
                    st.info(f"**总结**: 共发现{improvement_count}个可改进方面，按照建议调整可提升文本质量")
            else:
                st.success("✅ 文本结构良好，无明显问题")
                st.balloons()

        # 高级分析
        if show_advanced:
            st.markdown("### 🔬 高级分析")

            advanced_tab1, advanced_tab2, advanced_tab3 = st.tabs(["重复内容分析", "文本结构洞察", "文本预览"])

            with advanced_tab1:
                # 重复单词分析
                word_freq = Counter(words)

                # 高频词分析
                repeated_words = [(word, freq) for word, freq in word_freq.items()
                                  if freq > 3 and len(word) > 2 and word.isalpha()]

                if repeated_words:
                    st.subheader("🔁 高频重复词汇")
                    st.write(f"**出现3次以上的词汇 (共{len(repeated_words)}个):**")

                    # 按频率排序
                    repeated_words.sort(key=lambda x: x[1], reverse=True)

                    # 使用Streamlit内置图表替代matplotlib
                    top_words = repeated_words[:10]
                    if top_words:
                        chart_data = {
                            '词汇': [word for word, freq in top_words],
                            '出现次数': [freq for word, freq in top_words]
                        }
                        st.bar_chart(chart_data.set_index('词汇'))

                    # 详细列表
                    repeated_col1, repeated_col2 = st.columns(2)
                    mid_point = len(repeated_words) // 2

                    with repeated_col1:
                        st.write("**详细列表:**")
                        for word, freq in repeated_words[:mid_point]:
                            percentage = (freq / total_words) * 100
                            st.write(f"`{word}`: {freq}次 ({percentage:.1f}%)")

                    with repeated_col2:
                        st.write("&nbsp;")  # 空行占位
                        for word, freq in repeated_words[mid_point:]:
                            percentage = (freq / total_words) * 100
                            st.write(f"`{word}`: {freq}次 ({percentage:.1f}%)")

                    # 重复度评分
                    repetition_score = len(repeated_words) / len(word_freq) * 100
                    st.metric("词汇重复度", f"{repetition_score:.1f}%")

                else:
                    st.info("✅ 未发现高频重复词汇")

            with advanced_tab2:
                st.subheader("📊 文本结构洞察")

                col1, col2 = st.columns(2)

                with col1:
                    # 句子长度分布
                    if total_sentences > 0:
                        sentence_lengths = [len(sentence.split()) for sentence in sentences]

                        st.metric("平均句子长度", f"{avg_sentence_length:.1f}词")

                        # 使用Streamlit内置图表
                        if sentence_lengths:
                            # 创建句子长度分布数据
                            length_ranges = {'1-10词': 0, '11-20词': 0, '21-30词': 0, '31-40词': 0, '41+词': 0}
                            for length in sentence_lengths:
                                if length <= 10:
                                    length_ranges['1-10词'] += 1
                                elif length <= 20:
                                    length_ranges['11-20词'] += 1
                                elif length <= 30:
                                    length_ranges['21-30词'] += 1
                                elif length <= 40:
                                    length_ranges['31-40词'] += 1
                                else:
                                    length_ranges['41+词'] += 1

                            st.write("**句子长度分布:**")
                            for range_name, count in length_ranges.items():
                                if count > 0:
                                    percentage = (count / total_sentences) * 100
                                    st.write(f"- {range_name}: {count}句 ({percentage:.1f}%)")

                with col2:
                    # 段落分析
                    if total_paragraphs > 0:
                        paragraph_lengths = [len(para.split()) for para in paragraphs if para.strip()]

                        st.metric("平均段落长度", f"{avg_paragraph_length:.1f}词")
                        st.metric("段落数量", total_paragraphs)

                        # 段落长度分析
                        st.write("**段落长度分布:**")
                        short_paras = len([l for l in paragraph_lengths if l < 50])
                        medium_paras = len([l for l in paragraph_lengths if 50 <= l <= 200])
                        long_paras = len([l for l in paragraph_lengths if l > 200])

                        st.write(f"- 短段落 (<50词): {short_paras}个")
                        st.write(f"- 中段落 (50-200词): {medium_paras}个")
                        st.write(f"- 长段落 (>200词): {long_paras}个")

                # 词汇复杂度分析
                st.subheader("📈 词汇复杂度")
                col3, col4, col5 = st.columns(3)

                with col3:
                    unique_words = len(set(words))
                    st.metric("独特词汇量", unique_words)

                with col4:
                    lexical_density = (unique_words / total_words) * 100
                    st.metric("词汇密度", f"{lexical_density:.1f}%")

                with col5:
                    st.metric("平均词长", f"{avg_word_length:.1f}字符")

            with advanced_tab3:
                st.subheader("👁️ 文本预览")

                # 文本统计概览
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                with stat_col1:
                    st.metric("总字符数", total_chars)
                with stat_col2:
                    st.metric("总词数", total_words)
                with stat_col3:
                    st.metric("总句数", total_sentences)
                with stat_col4:
                    st.metric("总段落数", total_paragraphs)

                # 文本预览
                st.write("**内容预览:**")
                preview = text_input[:500] + "..." if total_chars > 500 else text_input

                # 高亮显示长句子
                preview_highlighted = preview
                for sentence in sentences:
                    sentence_words = sentence.split()
                    if len(sentence_words) > 25 and sentence in preview:
                        # 使用HTML标记高亮
                        preview_highlighted = preview_highlighted.replace(
                            sentence, f"<mark style='background-color: #ffd70033'>{sentence}</mark>"
                        )

                st.markdown(
                    f'<div style="border: 1px solid #e0e0e0; padding: 15px; border-radius: 5px; background-color: #fafafa; white-space: pre-wrap;">{preview_highlighted}</div>',
                    unsafe_allow_html=True)

                # 阅读时间估算
                st.info(f"📖 预计阅读时间: {reading_time:.1f}分钟 (按200词/分钟计算)")

        # 导出功能
        st.markdown("### 📤 导出统计结果")

        import json
        import pandas as pd

        # 创建完整的统计字典
        stats = {
            "基础统计": {
                "字符数（含空格）": total_chars,
                "字符数（不含空格）": total_chars_no_spaces,
                "单词数": total_words,
                "句子数": total_sentences,
                "行数": total_lines,
                "段落数": total_paragraphs
            },
            "字符类型": {
                "字母数": letters,
                "数字数": digits,
                "标点符号": punctuation,
                "空格数": spaces,
                "中文字符": chinese_chars
            },
            "质量指标": {
                "平均词长": round(avg_word_length, 2),
                "平均句长": round(avg_sentence_length, 2),
                "平均段落长": round(avg_paragraph_length, 2),
                "阅读时间(分钟)": round(reading_time, 2)
            }
        }

        export_col1, export_col2, export_col3 = st.columns(3)

        with export_col1:
            # JSON导出
            st.download_button(
                label="📥 导出为JSON",
                data=json.dumps(stats, indent=2, ensure_ascii=False),
                file_name="文本统计报告.json",
                mime="application/json"
            )

        with export_col2:
            # CSV导出
            csv_data = []
            for category, items in stats.items():
                for key, value in items.items():
                    csv_data.append({"类别": category, "指标": key, "数值": value})

            df = pd.DataFrame(csv_data)
            csv_string = df.to_csv(index=False)
            st.download_button(
                label="📥 导出为CSV",
                data=csv_string,
                file_name="文本统计报告.csv",
                mime="text/csv"
            )

        with export_col3:
            # 文本报告导出
            report_text = f"""文本统计报告
生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
==============================

基础统计:
--------
字符数（含空格）: {total_chars:,}
字符数（不含空格）: {total_chars_no_spaces:,}
单词数: {total_words:,}
句子数: {total_sentences:,}
行数: {total_lines:,}
段落数: {total_paragraphs:,}

字符类型:
--------
字母数: {letters:,}
数字数: {digits:,}
标点符号: {punctuation:,}
空格数: {spaces:,}
中文字符: {chinese_chars:,}

质量指标:
--------
平均词长: {avg_word_length:.2f}
平均句长: {avg_sentence_length:.2f}
平均段落长: {avg_paragraph_length:.2f}
阅读时间: {reading_time:.2f}分钟
"""
            st.download_button(
                label="📥 导出为文本报告",
                data=report_text,
                file_name="文本统计报告.txt",
                mime="text/plain"
            )

    else:
        # 没有输入时的提示
        st.info("👆 请在上方文本框中输入文本以开始统计")

        # 示例文本
        with st.expander("📋 点击查看示例文本"):
            sample_text = """这是一个示例文本，用于展示字数统计工具的功能。

你可以在这里输入任意文本，工具会自动计算：
- 字符数（包含和不包含空格）
- 单词数量
- 行数和段落数
- 各种字符类型的分布

此外，工具还提供：
📊 可视化图表分析
📝 文本编辑建议
📈 质量评估指标
📤 多种格式导出功能

尝试复制你自己的文本到这里，看看详细的统计结果！"""
            st.text_area("示例文本", sample_text, height=200, key="sample_text")

    st.markdown('</div>', unsafe_allow_html=True)

# 文本对比工具
elif tool_category == "文本对比工具":
    show_doc("text_comparison")

    # 简化 session 初始化逻辑
    st.session_state.setdefault('text1_content', "")
    st.session_state.setdefault('text2_content', "")
    st.session_state.setdefault('clear_counter', 0)
    st.session_state.setdefault('diff_mode', 'line')
    st.session_state.setdefault('show_legend', True)


    # 新增：词对比相关函数
    def word_diff(text1, text2):
        """实现词级别的对比"""
        # 使用正则表达式分割单词，保留标点符号
        words1 = re.findall(r'\b\w+\b|[^\w\s]|\s+', text1)
        words2 = re.findall(r'\b\w+\b|[^\w\s]|\s+', text2)

        d = Differ()
        diff = list(d.compare(words1, words2))

        return diff, words1, words2


    def render_word_diff(diff):
        """渲染词对比结果"""
        html_parts = [
            "<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; line-height: 1.6;'>"]

        current_line = []
        for item in diff:
            if item.startswith('+ '):
                word = html.escape(item[2:])
                current_line.append(
                    f"<span style='background-color: #d4edda; color: #155724; padding: 1px 3px; margin: 0 1px; border-radius: 2px; border: 1px solid #c3e6cb;'>+{word}</span>")
            elif item.startswith('- '):
                word = html.escape(item[2:])
                current_line.append(
                    f"<span style='background-color: #f8d7da; color: #721c24; padding: 1px 3px; margin: 0 1px; border-radius: 2px; border: 1px solid #f5c6cb;'>-{word}</span>")
            elif item.startswith('? '):
                # 在词模式中，? 通常不需要特殊显示
                continue
            else:
                word = html.escape(item[2:] if len(item) > 2 else item)
                # 处理换行符
                if word == '\n' or word == '\r\n':
                    if current_line:
                        html_parts.append(''.join(current_line))
                        current_line = []
                    html_parts.append("<br>")
                else:
                    current_line.append(f"<span style='padding: 1px 2px;'>{word}</span>")

        # 添加最后一行
        if current_line:
            html_parts.append(''.join(current_line))

        html_parts.append("</div>")
        return ''.join(html_parts)


    def render_enhanced_word_diff(text1, text2):
        """增强的词对比，显示更详细的词级变化"""
        # 使用 difflib 的 SequenceMatcher 进行更精确的词级对比
        words1 = re.findall(r'\b\w+\b|[^\w\s]|\s+', text1)
        words2 = re.findall(r'\b\w+\b|[^\w\s]|\s+', text2)

        matcher = difflib.SequenceMatcher(None, words1, words2)

        html_parts = [
            "<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; line-height: 1.6; word-wrap: break-word;'>"]

        for opcode in matcher.get_opcodes():
            tag, i1, i2, j1, j2 = opcode

            if tag == 'equal':
                # 相同的部分
                for word in words1[i1:i2]:
                    escaped_word = html.escape(word)
                    html_parts.append(f"<span style='padding: 1px 2px; color: #6c757d;'>{escaped_word}</span>")
            elif tag == 'replace':
                # 替换的部分 - 显示删除和新增
                # 删除的单词
                for word in words1[i1:i2]:
                    escaped_word = html.escape(word)
                    html_parts.append(
                        f"<span style='background-color: #f8d7da; color: #721c24; padding: 1px 3px; margin: 0 1px; border-radius: 2px; border: 1px solid #f5c6cb; text-decoration: line-through;'>-{escaped_word}</span>")
                # 新增的单词
                for word in words2[j1:j2]:
                    escaped_word = html.escape(word)
                    html_parts.append(
                        f"<span style='background-color: #d4edda; color: #155724; padding: 1px 3px; margin: 0 1px; border-radius: 2px; border: 1px solid #c3e6cb;'>+{escaped_word}</span>")
            elif tag == 'delete':
                # 删除的部分
                for word in words1[i1:i2]:
                    escaped_word = html.escape(word)
                    html_parts.append(
                        f"<span style='background-color: #f8d7da; color: #721c24; padding: 1px 3px; margin: 0 1px; border-radius: 2px; border: 1px solid #f5c6cb; text-decoration: line-through;'>-{escaped_word}</span>")
            elif tag == 'insert':
                # 新增的部分
                for word in words2[j1:j2]:
                    escaped_word = html.escape(word)
                    html_parts.append(
                        f"<span style='background-color: #d4edda; color: #155724; padding: 1px 3px; margin: 0 1px; border-radius: 2px; border: 1px solid #c3e6cb;'>+{escaped_word}</span>")

        html_parts.append("</div>")
        return ''.join(html_parts)


    # 设置选项区域
    with st.expander("⚙️ 对比设置", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            diff_mode = st.selectbox(
                "对比模式",
                options=['line', 'word', 'enhanced_word'],
                index=0,
                help="行模式：按行对比；词模式：按单词对比；增强词模式：更精确的词级对比"
            )
        with col2:
            show_legend = st.checkbox("显示图例", value=True)
            ignore_case = st.checkbox("忽略大小写", value=False)
            ignore_whitespace = st.checkbox("忽略空白字符", value=False)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.markdown("**原始文本**")
        text1 = st.text_area(" ", height=300,
                             key=f"text1_{st.session_state.clear_counter}",
                             value=st.session_state.text1_content,
                             label_visibility="collapsed")

        if text1:
            lines1 = len(text1.splitlines())
            words1 = len(re.findall(r'\b\w+\b', text1))
            chars1 = len(text1)
            st.caption(f"📊 统计: {lines1} 行, {words1} 词, {chars1} 字符")

    with col_input2:
        st.markdown("**对比文本**")
        text2 = st.text_area(" ", height=300,
                             key=f"text2_{st.session_state.clear_counter}",
                             value=st.session_state.text2_content,
                             label_visibility="collapsed")

        if text2:
            lines2 = len(text2.splitlines())
            words2 = len(re.findall(r'\b\w+\b', text2))
            chars2 = len(text2)
            st.caption(f"📊 统计: {lines2} 行, {words2} 词, {chars2} 字符")

    # 操作按钮区域
    button_col1, button_col2, button_col3, button_col4 = st.columns([1, 1, 1, 1])

    with button_col1:
        compare_clicked = st.button("🔄 开始对比", use_container_width=True)

    with button_col2:
        if st.button("📋 交换文本", use_container_width=True):
            # 先同步当前输入框的内容到 session state
            st.session_state.text1_content = text1
            st.session_state.text2_content = text2
            # 然后交换
            st.session_state.text1_content, st.session_state.text2_content = \
                st.session_state.text2_content, st.session_state.text1_content
            st.session_state.clear_counter += 1
            st.rerun()

    with button_col3:
        if st.button("📁 导入示例", use_container_width=True):
            # 提供更适合词对比的示例文本
            st.session_state.text1_content = """这是一个示例文本，用于演示词对比功能。
    第一行包含一些单词。
    第二行有更多的内容。
    第三行是最后一行。"""

            st.session_state.text2_content = """这是一个示范文本，用于演示词汇对比功能。
    第一行包含某些词语。
    第二行有更多不同的内容。
    新增的第四行文本。"""
            st.session_state.clear_counter += 1
            st.rerun()

    with button_col4:
        if st.button("🗑️ 清空所有", use_container_width=True):
            st.session_state.text1_content = ""
            st.session_state.text2_content = ""
            st.session_state.clear_counter += 1
            st.rerun()

    # 图例说明
    if show_legend:
        st.markdown("---")
        if diff_mode == 'line':
            col_legend1, col_legend2, col_legend3 = st.columns(3)
            with col_legend1:
                st.markdown(
                    "<div style='background-color: #f8d7da; padding: 5px; border-radius: 3px; text-align: center;'>"
                    "❌ 删除的行</div>",
                    unsafe_allow_html=True
                )
            with col_legend2:
                st.markdown(
                    "<div style='background-color: #d4edda; padding: 5px; border-radius: 3px; text-align: center;'>"
                    "✅ 新增的行</div>",
                    unsafe_allow_html=True
                )
            with col_legend3:
                st.markdown(
                    "<div style='background-color: #fff3cd; padding: 5px; border-radius: 3px; text-align: center;'>"
                    "⚠️ 修改的行</div>",
                    unsafe_allow_html=True
                )
        else:
            col_legend1, col_legend2 = st.columns(2)
            with col_legend1:
                st.markdown(
                    "<div style='background-color: #f8d7da; padding: 5px; border-radius: 3px; text-align: center; border: 1px solid #f5c6cb;'>"
                    "<span style='color: #721c24;'>-删除的单词</span></div>",
                    unsafe_allow_html=True
                )
            with col_legend2:
                st.markdown(
                    "<div style='background-color: #d4edda; padding: 5px; border-radius: 3px; text-align: center; border: 1px solid #c3e6cb;'>"
                    "<span style='color: #155724;'>+新增的单词</span></div>",
                    unsafe_allow_html=True
                )

    if compare_clicked:
        st.session_state.text1_content = text1
        st.session_state.text2_content = text2
        if text1 and text2:
            try:
                # 预处理文本
                processed_text1 = text1
                processed_text2 = text2

                if ignore_case:
                    processed_text1 = processed_text1.lower()
                    processed_text2 = processed_text2.lower()

                if ignore_whitespace:
                    processed_text1 = ' '.join(processed_text1.split())
                    processed_text2 = ' '.join(processed_text2.split())

                st.markdown("### 📊 对比结果")

                if diff_mode == 'line':
                    # 行对比模式
                    d = Differ()
                    diff = list(d.compare(processed_text1.splitlines(), processed_text2.splitlines()))

                    # 差异统计
                    added_lines = sum(1 for line in diff if line.startswith('+ '))
                    removed_lines = sum(1 for line in diff if line.startswith('- '))
                    unchanged_lines = sum(1 for line in diff if line.startswith('  '))

                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("新增行数", added_lines)
                    with col_stat2:
                        st.metric("删除行数", removed_lines)
                    with col_stat3:
                        st.metric("相同行数", unchanged_lines)

                    # 显示行对比结果
                    html_parts = [
                        "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace;'>"]
                    for line in diff:
                        escaped_line = html.escape(line[2:] if len(line) > 2 else line)
                        if line.startswith('+ '):
                            html_parts.append(
                                f"<div style='background-color: #d4edda; margin: 2px 0; padding: 2px 5px; border-radius: 3px; border-left: 3px solid #28a745;'>"
                                f"<span style='color: #28a745; font-weight: bold;'>+ </span>{escaped_line}</div>")
                        elif line.startswith('- '):
                            html_parts.append(
                                f"<div style='background-color: #f8d7da; margin: 2px 0; padding: 2px 5px; border-radius: 3px; border-left: 3px solid #dc3545;'>"
                                f"<span style='color: #dc3545; font-weight: bold;'>- </span>{escaped_line}</div>")
                        elif line.startswith('? '):
                            html_parts.append(
                                f"<div style='background-color: #fff3cd; margin: 2px 0; padding: 2px 5px; border-radius: 3px; border-left: 3px solid #ffc107;'>"
                                f"<span style='color: #856404; font-weight: bold;'>? </span>{escaped_line}</div>")
                        else:
                            content = escaped_line if line.startswith('  ') else html.escape(line)
                            html_parts.append(
                                f"<div style='margin: 2px 0; padding: 2px 5px; border-left: 3px solid #6c757d; color: #6c757d;'>"
                                f"{content}</div>")
                    html_parts.append("</div>")
                    result_html = ''.join(html_parts)
                    st.markdown(result_html, unsafe_allow_html=True)

                elif diff_mode == 'word':
                    # 基本词对比模式
                    with st.spinner("正在进行词级对比..."):
                        diff, words1, words2 = word_diff(processed_text1, processed_text2)

                        # 词级统计
                        added_words = sum(1 for word in diff if word.startswith('+ '))
                        removed_words = sum(1 for word in diff if word.startswith('- '))
                        unchanged_words = sum(1 for word in diff if word.startswith('  '))

                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("新增词汇", added_words)
                        with col_stat2:
                            st.metric("删除词汇", removed_words)
                        with col_stat3:
                            st.metric("相同词汇", unchanged_words)

                        result_html = render_word_diff(diff)
                        st.markdown(result_html, unsafe_allow_html=True)

                else:  # enhanced_word
                    # 增强词对比模式
                    with st.spinner("正在进行增强词级对比..."):
                        result_html = render_enhanced_word_diff(processed_text1, processed_text2)

                        # 简单统计
                        words1 = re.findall(r'\b\w+\b', processed_text1)
                        words2 = re.findall(r'\b\w+\b', processed_text2)

                        col_stat1, col_stat2 = st.columns(2)
                        with col_stat1:
                            st.metric("原文词汇数", len(words1))
                        with col_stat2:
                            st.metric("对比文词汇数", len(words2))

                        st.markdown(result_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"发生错误: {e}")
                st.info("建议尝试使用行对比模式或检查文本格式")
        else:
            st.warning("⚠️ 请填写原始文本和对比文本")

    st.markdown('</div>', unsafe_allow_html=True)

# 正则表达式测试工具
elif tool_category == "正则测试工具":
    show_doc("regex_tester")

    # 初始化session_state
    if 'regex_clear_counter' not in st.session_state:
        st.session_state.regex_clear_counter = 0

    # 添加工具选择选项卡
    tab1, tab2, tab3 = st.tabs(["正则表达式测试", "代码生成器", "从示例生成"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            # 预定义模式选择
            st.markdown("**选择预定义模式**")
            selected_pattern = st.selectbox("", ["自定义"] + list(PREDEFINED_PATTERNS.keys()), key="pattern_select")

            # 使用不同的key策略来避免session_state冲突
            if selected_pattern != "自定义":
                regex_pattern = PREDEFINED_PATTERNS[selected_pattern]
                st.code(f"当前模式: {regex_pattern}")
                # 同时允许用户修改预定义模式
                custom_regex = st.text_input("或自定义正则表达式", value=regex_pattern, placeholder="可在此修改表达式",
                                             key=f"custom_regex_input_{st.session_state.regex_clear_counter}")
                if custom_regex != regex_pattern:
                    regex_pattern = custom_regex
            else:
                regex_pattern = st.text_input("正则表达式", placeholder="例如: ^[a-zA-Z0-9]+$",
                                              key=f"manual_regex_input_{st.session_state.regex_clear_counter}")

            test_text = st.text_area("测试文本", height=200, placeholder="在此输入要测试的文本...",
                                     key=f"test_text_area_{st.session_state.regex_clear_counter}")

        with col2:
            st.markdown("**匹配选项**")
            global_match = st.checkbox("全局匹配 (g)", value=True, key="global_match_check")
            ignore_case = st.checkbox("忽略大小写 (i)", key="ignore_case_check")
            multiline = st.checkbox("多行模式 (m)", key="multiline_check")
            dotall = st.checkbox("点号匹配换行 (s)", key="dotall_check")

            st.markdown("**替换功能**")
            replace_text = st.text_input("替换文本", placeholder="输入替换文本（可选）",
                                         key=f"replace_text_input_{st.session_state.regex_clear_counter}")

        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("测试正则表达式", use_container_width=True, key="test_regex"):
                # 获取当前输入框的值
                current_regex = ""
                if selected_pattern != "自定义":
                    current_regex = custom_regex
                else:
                    current_regex = regex_pattern

                current_test_text = test_text

                if current_regex and current_test_text:
                    try:
                        flags = 0
                        if ignore_case:
                            flags |= re.IGNORECASE
                        if multiline:
                            flags |= re.MULTILINE
                        if dotall:
                            flags |= re.DOTALL

                        if global_match:
                            matches = list(re.finditer(current_regex, current_test_text, flags))
                            match_count = len(matches)

                            if match_count > 0:
                                st.success(f"匹配成功！找到 {match_count} 个匹配项。")

                                # 增强的匹配详情显示
                                st.markdown("**匹配详情**")
                                for i, match in enumerate(matches):
                                    with st.expander(f"匹配 {i + 1}: 位置 {match.start()}-{match.end()}"):
                                        st.write(f"匹配文本: `{match.group()}`")
                                        if match.groups():
                                            st.write("**捕获组:**")
                                            for j, group in enumerate(match.groups(), 1):
                                                st.write(f"  组 {j}: `{group}`")
                                        if match.groupdict():
                                            st.write("**命名分组:**")
                                            for name, group in match.groupdict().items():
                                                st.write(f"  {name}: `{group}`")
                            else:
                                st.warning("未找到匹配项。")
                        else:
                            match = re.search(current_regex, current_test_text, flags)
                            if match:
                                st.success("匹配成功！")
                                st.write(f"匹配文本: `{match.group()}`")
                                st.write(f"匹配位置: {match.start()}-{match.end()}")
                                if match.groups():
                                    st.write("**捕获组:**")
                                    for i, group in enumerate(match.groups(), 1):
                                        st.write(f"组 {i}: `{group}`")
                            else:
                                st.warning("未找到匹配项。")

                        if replace_text:
                            replaced_text = re.sub(current_regex, replace_text, current_test_text, flags=flags)
                            st.markdown("**替换结果**")
                            display_generated_results("替换后的文本", replaced_text, "regex_replaced")
                    except re.error as e:
                        st.error(f"正则表达式错误: {e}")
                else:
                    st.warning("请输入正则表达式和测试文本")

        with button_col2:
            if st.button("🗑️ 清空输入", use_container_width=True, key="clear_input"):
                # 通过增加计数器并重新渲染来清空
                st.session_state.regex_clear_counter += 1
                st.rerun()

    with tab2:
        st.markdown("### 正则表达式代码生成器")

        col1, col2 = st.columns(2)

        with col1:
            # 模式选择：预定义或自定义
            pattern_source = st.radio("正则表达式来源", ["预定义模式", "自定义表达式"],
                                      key=f"pattern_source_{st.session_state.regex_clear_counter}")

            if pattern_source == "预定义模式":
                code_pattern = st.selectbox("选择预定义模式", list(PREDEFINED_PATTERNS.keys()),
                                            key=f"code_pattern_{st.session_state.regex_clear_counter}")
                pattern_display = PREDEFINED_PATTERNS[code_pattern]
                st.code(f"模式: {pattern_display}")
            else:
                pattern_display = st.text_input("输入自定义正则表达式", placeholder="例如: ^[a-zA-Z0-9]+$",
                                                key=f"custom_pattern_input_{st.session_state.regex_clear_counter}")
                if pattern_display:
                    st.code(f"模式: {pattern_display}")

            # 编程语言选择
            target_language = st.selectbox("选择目标语言", list(LANGUAGE_TEMPLATES.keys()),
                                           key=f"target_lang_{st.session_state.regex_clear_counter}")

            # 操作类型
            operation_type = st.radio("选择操作类型", ["匹配", "测试", "替换"],
                                      key=f"operation_type_{st.session_state.regex_clear_counter}")

            # 替换文本
            replacement_code = ""
            if operation_type == "替换":
                replacement_code = st.text_input("替换文本", placeholder="输入替换文本",
                                                 key=f"replacement_input_{st.session_state.regex_clear_counter}")

        with col2:
            st.markdown("**代码生成选项**")

            # 标志选择
            flags_selected = []
            lang_flags = LANGUAGE_TEMPLATES[target_language]["flags"]

            for flag_name, flag_char in lang_flags.items():
                if st.checkbox(f"{flag_name} ({flag_char})",
                               key=f"flag_{flag_char}_{target_language}_{st.session_state.regex_clear_counter}"):
                    flags_selected.append(flag_name)

            # 生成代码按钮
            if st.button("生成代码", use_container_width=True, key="generate_code"):
                current_pattern = ""
                if pattern_source == "预定义模式":
                    current_pattern = PREDEFINED_PATTERNS[code_pattern]
                else:
                    current_pattern = pattern_display

                if not current_pattern:
                    st.warning("请输入或选择正则表达式")
                else:
                    # 构建标志
                    if target_language in ["Python", "Java", "C#"]:
                        flags_value = " | ".join(flags_selected) if flags_selected else "0"
                    else:
                        flags_value = "".join([lang_flags[flag] for flag in flags_selected])

                    # 获取模板
                    template_key = "match" if operation_type == "匹配" else "test" if operation_type == "测试" else "replace"
                    template = LANGUAGE_TEMPLATES[target_language][template_key]

                    # 生成代码
                    try:
                        generated_code = template.format(
                            pattern=current_pattern,
                            flags=flags_value,
                            flags_value=flags_value,
                            replacement=replacement_code
                        )

                        st.session_state.generated_code = generated_code
                        st.session_state.generated_language = target_language

                    except KeyError as e:
                        st.error(f"代码生成错误: {e}")

            # 显示已生成的代码（如果有）
            if 'generated_code' in st.session_state and st.session_state.generated_code:
                language = st.session_state.generated_language if 'generated_language' in st.session_state else target_language
                display_generated_results(
                    f"{language} 代码",
                    st.session_state.generated_code,
                    f"regex_{language.lower()}_code"
                )

        # 清空所有按钮
        button_col3, _ = st.columns(2)
        with button_col3:
            if st.button("🗑️ 清空所有", use_container_width=True, key="clear_all_code"):
                # 清除生成的代码状态
                if 'generated_code' in st.session_state:
                    del st.session_state.generated_code
                if 'generated_language' in st.session_state:
                    del st.session_state.generated_language
                # 通过增加计数器清空输入
                st.session_state.regex_clear_counter += 1
                st.rerun()

    with tab3:
        st.markdown("### 从示例生成正则表达式")

        col1, col2 = st.columns(2)

        with col1:
            source_text = st.text_area("原文内容", height=150,
                                       placeholder="输入包含要提取内容的原文...",
                                       key=f"source_text_area_{st.session_state.regex_clear_counter}")

        with col2:
            examples_text = st.text_area("示例文本（用逗号分隔）", height=150,
                                         placeholder="输入要匹配的示例，用逗号分隔...",
                                         key=f"examples_text_area_{st.session_state.regex_clear_counter}")

        button_col4, button_col5 = st.columns(2)
        with button_col4:
            if st.button("生成正则表达式", use_container_width=True, key="generate_from_examples"):
                current_source = source_text
                current_examples = examples_text

                if current_source and current_examples:
                    generated_regex = generate_regex_from_examples(current_source, current_examples)

                    if generated_regex:
                        st.success("已生成正则表达式！")

                        # 使用统一的显示函数
                        display_generated_results("生成的正则表达式", generated_regex, "generated_regex")

                        # 测试生成的正则表达式
                        try:
                            matches = re.findall(generated_regex, current_source)
                            if matches:
                                st.write(f"在原文中找到 {len(matches)} 个匹配项:")
                                for i, match in enumerate(matches):
                                    st.write(f"{i + 1}. `{match}`")
                            else:
                                st.warning("生成的正则表达式在原文中未找到匹配项")
                        except re.error as e:
                            st.error(f"生成的正则表达式有误: {e}")
                    else:
                        st.warning("无法生成合适的正则表达式，请提供更多或更明确的示例")
                else:
                    st.warning("请输入原文内容和示例文本")

        with button_col5:
            if st.button("🗑️ 清空示例", use_container_width=True, key="clear_examples"):
                # 通过增加计数器清空输入
                st.session_state.regex_clear_counter += 1
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
# JSON数据对比工具
elif tool_category == "JSON处理工具":
    utils = JSONFileUtils()

    # 工具选择
    tool_mode = st.radio(
        "选择处理模式",
        ["JSON解析与格式化", "JSON数据对比", "JSONPath查询"],
        horizontal=True
    )

    if tool_mode == "JSON解析与格式化":
        show_doc("json_parser")

        # 初始化session_state
        if 'json_input_content' not in st.session_state:
            st.session_state.json_input_content = '{"name": "Tom", "age": 25, "hobbies": ["reading", "swimming"]}'
        if 'parse_result' not in st.session_state:
            st.session_state.parse_result = None
        if 'parse_error' not in st.session_state:
            st.session_state.parse_error = None

        # 输入区域
        st.markdown("**JSON输入**")
        json_input = st.text_area("", height=300, key="json_input", value=st.session_state.json_input_content,
                                  placeholder='请输入JSON字符串，例如: {"name": "Tom", "age": 25}')

        # 按钮区域
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if st.button("🚀 解析JSON", use_container_width=True, key="parse_json"):
                if json_input.strip():
                    try:
                        parsed_json = json.loads(json_input)
                        st.session_state.parse_result = parsed_json
                        st.session_state.parse_error = None
                    except json.JSONDecodeError as e:
                        st.session_state.parse_result = None
                        st.session_state.parse_error = str(e)
                else:
                    st.warning("请输入JSON字符串")

        with col2:
            if st.button("✨ 格式化", use_container_width=True, key="format_json"):
                if json_input.strip():
                    try:
                        parsed_json = json.loads(json_input)
                        formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                        st.session_state.json_input_content = formatted_json
                        st.session_state.parse_result = parsed_json
                        st.session_state.parse_error = None
                    except json.JSONDecodeError as e:
                        st.session_state.parse_error = str(e)

        with col3:
            # 使用统一的复制按钮
            if st.session_state.parse_result is not None:
                formatted_json = json.dumps(st.session_state.parse_result, indent=2, ensure_ascii=False)
                create_copy_button(
                    formatted_json,
                    button_text="📋 复制结果",
                    key="copy_json_result"
                )
            else:
                # 禁用状态的按钮
                st.button("📋 复制结果", use_container_width=True, disabled=True, key="copy_disabled")

        with col4:
            if st.button("🗑️ 清空", use_container_width=True, key="clear_json"):
                st.session_state.json_input_content = ""
                st.session_state.parse_result = None
                st.session_state.parse_error = None

        # 显示解析结果
        if st.session_state.parse_result is not None:
            st.markdown("### 📊 解析结果")
            formatted_json = json.dumps(st.session_state.parse_result, indent=2, ensure_ascii=False)

            with st.expander("📄 格式化JSON", expanded=True):
                st.code(formatted_json, language='json')

            # 显示错误信息（如果有）
            if st.session_state.parse_error:
                st.error(f"解析错误: {st.session_state.parse_error}")


    elif tool_mode == "JSON数据对比":
        show_doc("json_comparison")

        # 初始化 session_state
        if 'json1_content' not in st.session_state:
            st.session_state.json1_content = '{"name": "John", "age": 30, "city": "New York"}'
        if 'json2_content' not in st.session_state:
            st.session_state.json2_content = '{"name": "Jane", "age": 25, "country": "USA"}'
        if 'comparison_result' not in st.session_state:
            st.session_state.comparison_result = None
        if 'differences_text' not in st.session_state:
            st.session_state.differences_text = ""
        if 'clear_counter' not in st.session_state:
            st.session_state.clear_counter = 0  # 添加计数器用于强制重新渲染

        # 输入区域 - 使用计数器确保重新渲染
        input_cols = st.columns(2)
        with input_cols[0]:
            st.markdown("**JSON 1**")
            json1 = st.text_area("", height=300,
                                 key=f"json1_{st.session_state.clear_counter}",  # 使用动态key
                                 value=st.session_state.json1_content,
                                 placeholder='输入第一个JSON数据...')
        with input_cols[1]:
            st.markdown("**JSON 2**")
            json2 = st.text_area("", height=300,
                                 key=f"json2_{st.session_state.clear_counter}",  # 使用动态key
                                 value=st.session_state.json2_content,
                                 placeholder='输入第二个JSON数据...')

        # 按钮区域
        button_cols = st.columns(4)
        with button_cols[0]:
            if st.button("✨ 格式化全部", use_container_width=True, key="format_all"):
                try:
                    # 先同步当前输入的内容到 session state
                    st.session_state.json1_content = json1
                    st.session_state.json2_content = json2

                    if json1.strip():
                        parsed_json1 = json.loads(json1)
                        formatted_json1 = json.dumps(parsed_json1, indent=2, ensure_ascii=False)
                        st.session_state.json1_content = formatted_json1
                    if json2.strip():
                        parsed_json2 = json.loads(json2)
                        formatted_json2 = json.dumps(parsed_json2, indent=2, ensure_ascii=False)
                        st.session_state.json2_content = formatted_json2

                    st.session_state.clear_counter += 1  # 增加计数器强制重新渲染
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"JSON格式错误: {e}")

        with button_cols[1]:
            compare_clicked = st.button("🔍 开始对比", use_container_width=True, key="compare")

        with button_cols[2]:
            if st.button("🔄 交换数据", use_container_width=True, key="swap_data"):
                # 先同步当前输入的内容到 session state
                st.session_state.json1_content = json1
                st.session_state.json2_content = json2
                # 然后交换数据
                st.session_state.json1_content, st.session_state.json2_content = \
                    st.session_state.json2_content, st.session_state.json1_content
                st.session_state.clear_counter += 1  # 增加计数器强制重新渲染
                st.rerun()

        with button_cols[3]:
            if st.button("🗑️ 清空全部", use_container_width=True, key="clear_all"):
                st.session_state.json1_content = ""
                st.session_state.json2_content = ""
                st.session_state.comparison_result = None
                st.session_state.differences_text = ""
                st.session_state.clear_counter += 1  # 增加计数器强制重新渲染
                st.rerun()

        # 处理对比结果
        if compare_clicked:
            # 同步当前输入的内容到 session state
            st.session_state.json1_content = json1
            st.session_state.json2_content = json2

            if json1 and json2:
                try:
                    obj1 = json.loads(json1)
                    obj2 = json.loads(json2)

                    st.markdown("### 📋 对比结果")

                    utils.reset_stats()
                    differences = utils.compare_json(obj1, obj2)
                    st.session_state.comparison_result = differences

                    difference_text = "\n".join([f"- {diff}" for diff in differences])
                    st.session_state.differences_text = difference_text

                    if differences:
                        st.error(f"发现 {len(differences)} 个差异:")
                        st.write(difference_text)

                        # 使用下载按钮作为复制替代方案
                        st.download_button(
                            "📋 下载差异结果",
                            difference_text,
                            file_name="json_differences.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key="download_diff"
                        )

                        # 同时提供文本区域用于手动复制
                        st.text_area("差异结果", difference_text, height=200, key="diff_copy_area")
                    else:
                        st.success("✅ 两个JSON对象完全相同")

                except json.JSONDecodeError as e:
                    st.error(f"JSON格式错误: {e}")

    elif tool_mode == "JSONPath查询":
        show_doc("jsonpath_tool")

        # 初始化session_state
        if 'jsonpath_json_content' not in st.session_state:
            st.session_state.jsonpath_json_content = '{"store": {"book": [{"title": "Book 1", "author": "Author 1"}, {"title": "Book 2", "author": "Author 2"}]}}'
        if 'jsonpath_expression' not in st.session_state:
            st.session_state.jsonpath_expression = "$.store.book[*].author"
        if 'jsonpath_result' not in st.session_state:
            st.session_state.jsonpath_result = None
        if 'jsonpath_result_text' not in st.session_state:
            st.session_state.jsonpath_result_text = ""

        # 布局：左右分栏
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.markdown("**📝 JSON数据**")
            json_data_input = st.text_area("", height=400, key="jsonpath_json",
                                           value=st.session_state.jsonpath_json_content,
                                           placeholder='输入JSON数据...')

            st.markdown("**🎯 JSONPath表达式**")
            jsonpath_input = st.text_input("", key="jsonpath_expr",
                                           value=st.session_state.jsonpath_expression,
                                           placeholder='例如: $.store.book[*].author')

            # 操作按钮
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 执行查询", use_container_width=True, key="execute_jsonpath"):
                    if json_data_input.strip() and jsonpath_input.strip():
                        try:
                            json_data = json.loads(json_data_input)
                            result = utils.execute_jsonpath(json_data, jsonpath_input)
                            st.session_state.jsonpath_result = result
                            result_text = "\n".join([str(item) for item in result])
                            st.session_state.jsonpath_result_text = result_text
                        except json.JSONDecodeError as e:
                            st.error(f"JSON数据格式错误: {e}")
                        except Exception as e:
                            st.error(f"JSONPath查询错误: {e}")

        with right_col:
            st.markdown("### 📋 查询结果")

            if st.session_state.jsonpath_result is not None:
                result = st.session_state.jsonpath_result
                result_text = st.session_state.jsonpath_result_text

                if result:
                    st.success(f"✅ 找到 {len(result)} 个匹配项")
                    st.metric("匹配数量", len(result))

                    st.markdown("**📄 匹配结果:**")
                    for i, item in enumerate(result):
                        with st.expander(f"结果 #{i + 1}", expanded=len(result) <= 3):
                            if isinstance(item, (dict, list)):
                                st.json(item)
                            else:
                                st.code(str(item))

                    # 使用下载按钮
                    st.download_button(
                        "📋 下载查询结果",
                        result_text,
                        file_name="jsonpath_results.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key="download_jsonpath"
                    )

                    # 提供文本区域用于手动复制
                    st.text_area("查询结果", result_text, height=200, key="jsonpath_copy_area")
                else:
                    st.warning("❌ 未找到匹配项")

# 日志分析工具
elif tool_category == "日志分析工具":
    show_doc("log_analyzer")

    # 初始化所有session_state变量
    if 'log_data' not in st.session_state:
        st.session_state.log_data = None
    if 'file_info' not in st.session_state:
        st.session_state.file_info = None
    if 'filtered_lines' not in st.session_state:
        st.session_state.filtered_lines = []
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'search_count' not in st.session_state:
        st.session_state.search_count = 0
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'is_csv' not in st.session_state:
        st.session_state.is_csv = False
    if 'csv_columns' not in st.session_state:
        st.session_state.csv_columns = []
    if 'json_columns' not in st.session_state:
        st.session_state.json_columns = []
    if 'json_fields' not in st.session_state:
        st.session_state.json_fields = {}
    # 新增搜索相关状态变量
    if 'search_keyword' not in st.session_state:
        st.session_state.search_keyword = ""
    if 'search_cleared' not in st.session_state:
        st.session_state.search_cleared = False

    # 使用tab布局
    tab1, tab2, tab3 = st.tabs(["日志导入", "日志过滤", "关键词搜索"])

    # Tab1: 日志导入
    with tab1:
        st.header("日志导入")

        import_method = st.radio("日志导入方式", ["文件上传", "直接粘贴"])
        log_content = ""
        file_info = None

        if import_method == "文件上传":
            uploaded_file = st.file_uploader("选择日志文件", type=['txt', 'log', 'csv'],
                                             help="支持 txt, log, csv 格式文件")

            if uploaded_file is not None:
                # 文件信息
                import datetime
                import json

                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                file_info = {
                    "文件名": uploaded_file.name,
                    "文件大小": f"{uploaded_file.size / 1024:.2f} KB",
                    "文件类型": uploaded_file.type or "未知类型",
                    "上传时间": current_time
                }

                # 文件预览
                st.subheader("文件预览")
                preview_lines = 10

                try:
                    if uploaded_file.name.endswith('.csv'):
                        # CSV文件处理
                        import pandas as pd

                        df = pd.read_csv(uploaded_file)
                        st.write("前10行数据预览:")
                        st.dataframe(df.head(preview_lines))

                        # 保存DataFrame和列信息
                        st.session_state.df = df
                        st.session_state.csv_columns = df.columns.tolist()
                        st.session_state.is_csv = True

                        # 检测JSON格式的列并提取字段
                        st.session_state.json_columns = []
                        st.session_state.json_fields = {}

                        for column in df.columns:
                            # 检查列中是否包含JSON格式的数据
                            json_sample = None
                            for value in df[column].dropna().head(5):
                                if isinstance(value, str) and value.strip().startswith('{') and value.strip().endswith(
                                        '}'):
                                    try:
                                        json_data = json.loads(value)
                                        if isinstance(json_data, dict):
                                            json_sample = json_data
                                            break
                                    except:
                                        continue

                            if json_sample:
                                st.session_state.json_columns.append(column)
                                st.session_state.json_fields[column] = list(json_sample.keys())
                                st.info(f"检测到列 '{column}' 包含JSON数据，提取到 {len(json_sample.keys())} 个字段")

                        # 将DataFrame转换为文本格式用于显示
                        log_content = ""
                        for _, row in df.iterrows():
                            log_content += " | ".join([str(x) for x in row]) + "\n"
                    else:
                        # 文本文件处理
                        content = uploaded_file.getvalue().decode("utf-8")
                        lines = content.split('\n')
                        preview_content = "\n".join(lines[:preview_lines])
                        st.text_area("预览内容", preview_content, height=150, key="preview")
                        log_content = content
                        st.session_state.is_csv = False
                        st.session_state.df = None
                        st.session_state.csv_columns = []
                        st.session_state.json_columns = []
                        st.session_state.json_fields = {}

                except Exception as e:
                    st.error(f"文件读取错误: {e}")
                    log_content = ""

                # 显示文件信息
                if file_info:
                    st.subheader("文件信息")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**文件名:** {file_info['文件名']}")
                        st.write(f"**文件大小:** {file_info['文件大小']}")
                    with col2:
                        st.write(f"**文件类型:** {file_info['文件类型']}")
                        st.write(f"**上传时间:** {file_info['上传时间']}")

                # 自动导入日志数据
                if log_content and uploaded_file is not None:
                    st.session_state.log_data = log_content
                    st.session_state.file_info = file_info
                    st.session_state.filtered_lines = []
                    st.session_state.search_results = []
                    st.session_state.search_count = 0

        else:  # 直接粘贴
            log_content = st.text_area("粘贴日志内容", height=200,
                                       placeholder="请将日志内容粘贴到此处...",
                                       key="paste_content")

            # 自动导入粘贴的日志内容
            if log_content:
                st.session_state.log_data = log_content
                st.session_state.file_info = None
                st.session_state.filtered_lines = []
                st.session_state.search_results = []
                st.session_state.search_count = 0
                st.session_state.is_csv = False
                st.session_state.df = None
                st.session_state.csv_columns = []
                st.session_state.json_columns = []
                st.session_state.json_fields = {}

    # 检查是否有导入的日志数据并显示统计信息
    if st.session_state.log_data:
        log_content = st.session_state.log_data

        # 根据文件类型处理数据
        if st.session_state.is_csv and st.session_state.df is not None:
            # CSV数据
            df = st.session_state.df
            lines = []
            for _, row in df.iterrows():
                line = " | ".join([str(x) for x in row])
                lines.append(line)
            total_lines = len(df)
        else:
            # 文本数据
            lines = log_content.split('\n')
            total_lines = len(lines)

        # 在主内容区显示统计信息
        st.header("📊 日志统计信息")

        # 改进的日志级别统计
        error_count = sum(1 for line in lines if any(word in line.upper() for word in ['ERROR', 'ERR']))
        warn_count = sum(1 for line in lines if any(word in line.upper() for word in ['WARN', 'WARNING']))
        info_count = sum(1 for line in lines if any(word in line.upper() for word in ['INFO', 'INFORMATION']))
        debug_count = sum(1 for line in lines if any(word in line.upper() for word in ['DEBUG', 'DBG']))
        other_count = total_lines - error_count - warn_count - info_count - debug_count

        # 统计指标
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("总行数", total_lines)
        with col2:
            st.metric("错误", error_count, delta_color="off")
        with col3:
            st.metric("警告", warn_count, delta_color="off")
        with col4:
            st.metric("信息", info_count, delta_color="off")
        with col5:
            st.metric("调试", debug_count, delta_color="off")

        # Tab2: 日志过滤
        with tab2:
            st.header("日志过滤")

            if st.session_state.is_csv and st.session_state.csv_columns:
                # CSV文件的字段筛选
                st.subheader("CSV字段筛选")

                # 选择筛选类型：普通列或JSON字段
                filter_type = st.radio("筛选类型", ["普通列筛选", "JSON字段筛选"], horizontal=True)

                if filter_type == "普通列筛选":
                    col1, col2 = st.columns(2)

                    with col1:
                        selected_column = st.selectbox(
                            "选择筛选字段",
                            st.session_state.csv_columns,
                            help="选择要筛选的CSV列"
                        )

                        filter_value = st.text_input(
                            "筛选值",
                            placeholder=f"输入{selected_column}的筛选值...",
                            help="支持部分匹配"
                        )

                    with col2:
                        # 数值范围筛选（如果字段是数值类型）
                        if (st.session_state.df is not None and
                                selected_column in st.session_state.df.columns and
                                pd.api.types.is_numeric_dtype(st.session_state.df[selected_column])):
                            min_val = float(st.session_state.df[selected_column].min())
                            max_val = float(st.session_state.df[selected_column].max())
                            value_range = st.slider(
                                f"{selected_column}范围",
                                min_val, max_val, (min_val, max_val)
                            )
                        else:
                            value_range = None

                else:  # JSON字段筛选
                    if st.session_state.json_columns:
                        col1, col2 = st.columns(2)

                        with col1:
                            selected_json_column = st.selectbox(
                                "选择JSON列",
                                st.session_state.json_columns,
                                help="选择包含JSON数据的列"
                            )

                            if selected_json_column in st.session_state.json_fields:
                                json_fields = st.session_state.json_fields[selected_json_column]
                                selected_json_field = st.selectbox(
                                    "选择JSON字段",
                                    json_fields,
                                    help="选择要筛选的JSON字段"
                                )

                                json_filter_value = st.text_input(
                                    "字段筛选值",
                                    placeholder=f"输入{selected_json_field}的值...",
                                    help="支持部分匹配"
                                )
                            else:
                                st.warning("未找到JSON字段")
                                selected_json_field = None
                                json_filter_value = ""

                        with col2:
                            # JSON字段的数值范围筛选
                            if (selected_json_field and
                                    st.session_state.df is not None and
                                    selected_json_column in st.session_state.df.columns):
                                # 尝试提取数值字段进行范围筛选
                                try:
                                    # 提取该字段的所有数值
                                    numeric_values = []
                                    for value in st.session_state.df[selected_json_column].dropna():
                                        if isinstance(value, str) and value.strip().startswith(
                                                '{') and value.strip().endswith('}'):
                                            try:
                                                json_data = json.loads(value)
                                                if (selected_json_field in json_data and
                                                        isinstance(json_data[selected_json_field], (int, float))):
                                                    numeric_values.append(json_data[selected_json_field])
                                            except:
                                                continue

                                    if numeric_values:
                                        min_val = min(numeric_values)
                                        max_val = max(numeric_values)
                                        json_value_range = st.slider(
                                            f"{selected_json_field}范围",
                                            min_val, max_val, (min_val, max_val),
                                            key="json_range"
                                        )
                                    else:
                                        json_value_range = None
                                        st.info("该JSON字段不包含数值数据")
                                except:
                                    json_value_range = None
                    else:
                        st.info("未检测到包含JSON数据的列")

            col1, col2 = st.columns(2)

            with col1:
                # 日志级别筛选
                log_levels = st.multiselect(
                    "日志级别",
                    ["错误", "警告", "信息", "调试"],
                    default=["错误", "警告"],
                    help="选择要显示的日志级别"
                )

                # IP地址筛选
                ip_filter = st.text_input(
                    "IP地址/IP段",
                    placeholder="例如: 192.168.1.1 或 192.168.1.0/24",
                    help="支持单个IP或IP段筛选"
                )

            with col2:
                # 状态码筛选
                status_codes = st.text_input(
                    "状态码",
                    placeholder="例如: 200,404,500",
                    help="用逗号分隔多个状态码"
                )

                # 其他筛选选项
                st.subheader("其他筛选条件")
                show_only_errors = st.checkbox("仅显示错误相关日志")
                hide_debug = st.checkbox("隐藏调试信息")

            # 应用过滤按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("应用过滤条件", key="filter_btn", use_container_width=True):
                    filtered_lines = []

                    if st.session_state.is_csv and st.session_state.df is not None:
                        # CSV数据过滤
                        filtered_df = st.session_state.df.copy()

                        if filter_type == "普通列筛选":
                            # 普通列筛选
                            if filter_value and selected_column:
                                filtered_df = filtered_df[
                                    filtered_df[selected_column].astype(str).str.contains(filter_value, case=False,
                                                                                          na=False)]

                            # 数值范围筛选
                            if (value_range and
                                    selected_column in filtered_df.columns and
                                    pd.api.types.is_numeric_dtype(filtered_df[selected_column])):
                                filtered_df = filtered_df[
                                    (filtered_df[selected_column] >= value_range[0]) &
                                    (filtered_df[selected_column] <= value_range[1])
                                    ]

                        else:  # JSON字段筛选
                            if (selected_json_column and selected_json_field and
                                    json_filter_value and selected_json_column in filtered_df.columns):

                                def filter_json_rows(row):
                                    try:
                                        if pd.isna(row[selected_json_column]):
                                            return False
                                        if isinstance(row[selected_json_column], str):
                                            json_data = json.loads(row[selected_json_column])
                                            if selected_json_field in json_data:
                                                field_value = str(json_data[selected_json_field])
                                                return json_filter_value.lower() in field_value.lower()
                                    except:
                                        pass
                                    return False


                                # 应用JSON过滤
                                mask = filtered_df.apply(filter_json_rows, axis=1)
                                filtered_df = filtered_df[mask]

                                # JSON数值范围筛选
                                if json_value_range:
                                    def filter_json_numeric(row):
                                        try:
                                            if pd.isna(row[selected_json_column]):
                                                return False
                                            if isinstance(row[selected_json_column], str):
                                                json_data = json.loads(row[selected_json_column])
                                                if (selected_json_field in json_data and
                                                        isinstance(json_data[selected_json_field], (int, float))):
                                                    value = json_data[selected_json_field]
                                                    return json_value_range[0] <= value <= json_value_range[1]
                                        except:
                                            pass
                                        return False


                                    mask_numeric = filtered_df.apply(filter_json_numeric, axis=1)
                                    filtered_df = filtered_df[mask_numeric]

                        # 转换为文本行并应用文本过滤
                        for _, row in filtered_df.iterrows():
                            line = " | ".join([str(x) for x in row])
                            if _apply_text_filters(line, log_levels, ip_filter, status_codes, show_only_errors,
                                                   hide_debug):
                                filtered_lines.append(line)
                    else:
                        # 文本数据过滤
                        for line in lines:
                            if _apply_text_filters(line, log_levels, ip_filter, status_codes, show_only_errors,
                                                   hide_debug):
                                filtered_lines.append(line)

                    st.session_state.filtered_lines = filtered_lines
                    st.success(f"过滤完成，找到 {len(filtered_lines)} 行日志")

            # 显示过滤结果
            if st.session_state.filtered_lines:
                st.subheader(f"过滤结果 (共 {len(st.session_state.filtered_lines)} 行)")
                st.text_area("过滤后的日志", "\n".join(st.session_state.filtered_lines), height=400, key="filtered_output")

                # 导出结果
                st.download_button(
                    label="导出过滤结果",
                    data="\n".join(st.session_state.filtered_lines),
                    file_name=f"filtered_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.info("暂无过滤结果，请先应用过滤条件")

        # Tab3: 关键词搜索
        with tab3:
            st.header("关键词搜索")

            # 处理清空搜索条件
            if st.session_state.search_cleared:
                # 使用唯一的key来重新创建小部件
                search_key = f"search_input_{datetime.datetime.now().timestamp()}"
                case_key = f"case_sensitive_{datetime.datetime.now().timestamp()}"
                whole_key = f"whole_word_{datetime.datetime.now().timestamp()}"
                regex_key = f"use_regex_{datetime.datetime.now().timestamp()}"

                # 重置标志
                st.session_state.search_cleared = False
            else:
                search_key = "search_input"
                case_key = "case_sensitive"
                whole_key = "whole_word"
                regex_key = "use_regex"

            col1, col2 = st.columns([2, 1])

            with col1:
                # 搜索关键词输入框
                search_keyword = st.text_input(
                    "搜索关键词",
                    value="",  # 总是从空开始，由session_state控制实际值
                    placeholder="输入要搜索的关键词...",
                    help="支持普通文本和正则表达式搜索",
                    key=search_key
                )

            with col2:
                st.write("搜索选项")
                # 搜索选项 - 使用默认值False
                case_sensitive = st.checkbox("区分大小写", value=False, key=case_key)
                whole_word = st.checkbox("全词匹配", value=False, key=whole_key)
                use_regex = st.checkbox("正则表达式", value=False, key=regex_key)

            # 按钮布局
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("执行搜索", type="primary", use_container_width=True):
                    if search_keyword:
                        # 更新搜索关键词状态
                        st.session_state.search_keyword = search_keyword

                        search_results = []

                        for line in lines:
                            search_text = line
                            original_line = line

                            if not case_sensitive:
                                search_text = search_text.lower()
                                keyword = search_keyword.lower()
                            else:
                                keyword = search_keyword

                            match_found = False

                            if use_regex:
                                try:
                                    if re.search(keyword, search_text, 0 if case_sensitive else re.IGNORECASE):
                                        match_found = True
                                except re.error as e:
                                    st.error(f"正则表达式错误: {e}")
                                    break
                            elif whole_word:
                                # 全词匹配
                                words = re.findall(r'\b\w+\b', search_text)
                                if any(word == keyword for word in words):
                                    match_found = True
                            else:
                                # 普通搜索
                                if keyword in search_text:
                                    match_found = True

                            if match_found:
                                search_results.append(original_line)

                        st.session_state.search_results = search_results
                        st.session_state.search_count = len(search_results)
                        if search_results:
                            st.success(f"找到 {len(search_results)} 条匹配结果")
                        else:
                            st.warning("未找到匹配的搜索结果")

                    else:
                        st.warning("请输入搜索关键词")

            with col2:
                if st.button("清空搜索条件", key="clear_search", use_container_width=True):
                    # 清空所有搜索相关的状态
                    st.session_state.search_results = []
                    st.session_state.search_count = 0
                    st.session_state.search_keyword = ""
                    st.session_state.search_cleared = True
                    st.success("搜索条件已清空！")
                    st.rerun()

            # 显示搜索结果
            if st.session_state.search_results:
                st.subheader(f"搜索结果 (共 {len(st.session_state.search_results)} 条)")

                # 显示搜索结果
                result_text = "\n".join(st.session_state.search_results)
                st.text_area("搜索结果", result_text, height=400, key="search_output")

                # 导出搜索结果
                st.download_button(
                    label="导出搜索结果",
                    data=result_text,
                    file_name=f"search_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            elif st.session_state.search_count == 0 and st.session_state.search_keyword:
                st.info("暂无搜索结果")

    else:
        st.info("请先导入日志数据以开始分析")

    st.markdown('</div>', unsafe_allow_html=True)

elif tool_category == "时间处理工具":
    show_doc("time_processor")

    dt_utils = DateTimeUtils
    time_tool = st.radio(
        "选择时间处理工具",
        ["时间戳转换", "时间换算工具", "日期计算器"],
        horizontal=True
    )

    if time_tool == "时间戳转换":
        st.markdown('<div class="category-card">⏰ 时间戳转换</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**时间戳转日期**")
            timestamp_input = st.text_input("输入时间戳", placeholder="例如: 1633046400")
            timestamp_type = st.radio("时间戳类型", ["秒", "毫秒"])
            if st.button("转换为日期", use_container_width=True):
                if not timestamp_input:
                    st.warning("请输入时间戳")
                else:
                    try:
                        timestamp = float(timestamp_input)
                        if timestamp_type == "毫秒":
                            timestamp /= 1000
                        dt = datetime.datetime.fromtimestamp(timestamp)
                        st.success(f"转换结果: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except (ValueError, OSError) as e:
                        st.error(f"请输入有效的时间戳: {e}")
            if st.button("获取当前时间戳", use_container_width=True):
                current_timestamp = int(time.time())
                st.text_input("当前时间戳", value=str(current_timestamp))
        with col2:
            st.markdown("**日期转时间戳**")
            date_input = st.date_input("选择日期")
            time_input = st.time_input("选择时间")
            if st.button("转换为时间戳", use_container_width=True):
                try:
                    dt = datetime.datetime.combine(date_input, time_input)
                    timestamp = int(dt.timestamp())
                    st.success(f"转换结果: {timestamp} (秒)")
                except Exception as e:
                    st.error(f"日期转换失败: {e}")

    elif time_tool == "时间换算工具":
        st.markdown('<div class="category-card">🔄 时间换算工具</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            value = st.number_input("输入数值", value=1.0)
            from_unit = st.selectbox("从单位", list(TO_SECONDS.keys()))
        with col2:
            to_unit = st.selectbox("转换为", list(TO_SECONDS.keys()))
            if st.button("转换", use_container_width=True):
                if from_unit in TO_SECONDS and to_unit in TO_SECONDS:
                    value_in_seconds = value * TO_SECONDS[from_unit]
                    result = value_in_seconds / TO_SECONDS[to_unit]
                    st.success(f"{value} {from_unit} = {result:.6f} {to_unit}")
                else:
                    st.error("单位转换错误")
        with col3:
            st.markdown("**常用时间换算表**")
            st.write("1 分钟 = 60 秒")
            st.write("1 小时 = 60 分钟 = 3600 秒")
            st.write("1 天 = 24 小时 = 1440 分钟")
            st.write("1 周 = 7 天 = 168 小时")
            st.write("1 月 ≈ 30.44 天")
            st.write("1 年 ≈ 365.25 天")

    elif time_tool == "日期计算器":
        st.markdown('<div class="category-card">📅 日期计算器</div>', unsafe_allow_html=True)
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
                if st.button("计算", use_container_width=True):
                    try:
                        if operation == "加上":
                            if unit == "天":
                                result_date = start_date + timedelta(days=value)
                            elif unit == "周":
                                result_date = start_date + timedelta(weeks=value)
                            elif unit == "月":
                                result_date = dt_utils.add_months(start_date, value)
                            elif unit == "年":
                                result_date = start_date.replace(year=start_date.year + value)
                        else:
                            if unit == "天":
                                result_date = start_date - timedelta(days=value)
                            elif unit == "周":
                                result_date = start_date - timedelta(weeks=value)
                            elif unit == "月":
                                result_date = dt_utils.subtract_months(start_date, value)
                            elif unit == "年":
                                result_date = start_date.replace(year=start_date.year - value)
                        st.success(f"计算结果: {result_date.strftime('%Y-%m-%d')}")
                    except Exception as e:
                        st.error(f"日期运算错误: {e}")
        else:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期")
            with col2:
                end_date = st.date_input("结束日期")
            if st.button("计算间隔", use_container_width=True):
                if not start_date or not end_date:
                    st.warning("请选择完整的日期范围")
                elif start_date > end_date:
                    st.error("开始日期不能晚于结束日期")
                else:
                    delta = end_date - start_date
                    business_days = dt_utils.count_business_days(start_date, end_date)
                    weekend_days = delta.days + 1 - business_days
                    st.success(f"间隔天数: {delta.days} 天")
                    st.info(f"工作日: {business_days} 天")
                    st.info(f"周末天数: {weekend_days} 天")

    st.markdown('</div>', unsafe_allow_html=True)

# IP/域名查询工具
elif tool_category == "IP/域名查询工具":
    show_doc("ip_domain_query")

    # 创建实例
    ip_tool = IPQueryTool()

    tab1, tab2, tab3 = st.tabs(
        ["IP/域名查询", "批量查询", "IPv4转换工具"])

    with tab1:
        st.markdown("**IP/域名基本信息查询**")

        # 获取当前公网IP
        if st.button("获取当前公网IP", key="get_public_ip", use_container_width=True):
            with st.spinner("正在获取当前公网IP..."):
                public_ip = ip_tool.get_public_ip()
                if public_ip != "获取公网IP失败":
                    st.session_state.current_public_ip = public_ip
                    st.success(f"当前公网IP: {public_ip}")
                else:
                    st.error("无法获取当前公网IP")

        # 输入框
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
        with col2:
            st.write("")
            st.write("")
            query_button = st.button("开始查询", use_container_width=True, key="main_query")

        if query_button and target_input:
            is_ip = False
            is_domain = False
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

            # 处理URL格式
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
                result = ip_tool.get_ip_domain_info(target_input, is_ip)

                if result['success']:
                    st.success("查询成功！")

                    # rDNS查询
                    if is_ip:
                        rdns_result = ip_tool.get_rdns_info(target_input)
                        if rdns_result['success']:
                            st.metric("rDNS", rdns_result['data'].get('rDNS', '未知'))

                    # 详细信息展示
                    st.markdown("**详细信息**")
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
                                    <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                                        <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.5rem;">{key}</div>
                                        <div style="color: #4a5568;">{value}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.error(f"查询失败: {result['error']}")

    with tab2:
        st.markdown("**批量查询工具**")
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

                    result = ip_tool.get_ip_domain_info(ip, True)
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

                    result = ip_tool.get_ip_domain_info(domain, False)
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

    with tab3:
        st.markdown("**IPv4转换工具**")
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
            result = ip_tool.convert_ip_address(input_value, conversion_type)
            if result['success']:
                st.success("转换成功！")
                for key, value in result['data'].items():
                    with st.container():
                        st.markdown(f"""
                         <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                             <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.5rem;">{key}</div>
                             <div style="font-family: monospace; font-size: 14px; color: #4a5568;">{value}</div>
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

# 在图片处理工具部分，添加翻转、旋转、裁剪、水印功能
elif tool_category == "图片处理工具":
    # 延迟导入图片处理模块
    try:
        from image_processor import ImageProcessor

        image_tool = ImageProcessor()
    except ImportError as e:
        st.error(f"❌ 图片处理模块加载失败: {e}")
        st.info("请确保 image_processor.py 文件存在于正确的位置")
        st.stop()

    show_doc("image_processor")

    # 初始化session state
    if 'original_image' not in st.session_state:
        st.session_state.original_image = None
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    if 'image_info' not in st.session_state:
        st.session_state.image_info = None
    if 'processed_info' not in st.session_state:
        st.session_state.processed_info = None
    if 'crop_coordinates' not in st.session_state:
        st.session_state.crop_coordinates = None
    if 'crop_preview' not in st.session_state:
        st.session_state.crop_preview = None
    if 'processed_image_data' not in st.session_state:
        st.session_state.processed_image_data = None
    if 'processed_image_format' not in st.session_state:
        st.session_state.processed_image_format = None

    st.markdown('<div class="category-card">🖼️ 图片处理工具</div>', unsafe_allow_html=True)

    # 文件上传区域
    st.markdown("### 1. 上传图片")
    uploaded_file = st.file_uploader(
        "点击或拖拽图片到此处上传",
        type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
        help="支持 JPG、PNG、GIF、BMP、WEBP 格式",
        key="image_uploader"
    )

    if uploaded_file is not None:
        try:
            # 打开图片并保存到session state
            image = Image.open(uploaded_file)
            st.session_state.original_image = image
            st.session_state.processed_image = image.copy()

            # 获取图片信息
            img_format = image.format
            img_size = image.size
            img_mode = image.mode
            file_size = len(uploaded_file.getvalue())

            # 保存图片信息
            st.session_state.image_info = {
                "文件名": uploaded_file.name,
                "格式": img_format,
                "模式": img_mode,
                "尺寸": f"{img_size[0]} × {img_size[1]} 像素",
                "文件大小": f"{file_size / 1024:.2f} KB",
                "原始大小字节": file_size
            }

        except Exception as e:
            st.error(f"图片读取失败: {e}")

    # 显示原图信息
    if st.session_state.original_image and st.session_state.image_info:
        st.markdown("### 2. 原图信息")

        col1, col2 = st.columns(2)
        with col1:
            st.image(st.session_state.original_image, caption="原图预览", use_container_width=True)
        with col2:
            st.markdown("**图片详细信息:**")
            for key, value in st.session_state.image_info.items():
                if key != "原始大小字节":
                    st.write(f"**{key}:** {value}")

    # 转换设置
    if st.session_state.original_image:
        st.markdown("### 3. 转换设置")

        # 处理模式选择
        processing_mode = st.radio(
            "处理模式",
            ["格式转换和质量调整", "调整尺寸", "图片翻转", "图片旋转", "图片裁剪", "添加水印"],
            horizontal=True
        )

        if processing_mode == "格式转换和质量调整":
            col1, col2, col3 = st.columns(3)

            with col1:
                output_format = st.selectbox("输出格式", ["JPG", "PNG", "GIF", "BMP", "WEBP"], index=0)
                if output_format in ["JPG", "WEBP"]:
                    quality = st.slider("图片质量", 1, 100, 85)
                else:
                    quality = 100
                    st.info("PNG、GIF、BMP格式不支持质量调整")

            with col2:
                compression_mode = st.radio("压缩模式", ["质量优先", "体积优先", "平衡模式"], horizontal=True)
                if compression_mode == "体积优先" and output_format in ["JPG", "WEBP"]:
                    quality = max(1, quality - 30)
                elif compression_mode == "平衡模式" and output_format in ["JPG", "WEBP"]:
                    quality = max(1, quality - 15)

            with col3:
                resize_option = st.radio("尺寸调整", ["保持原尺寸", "自定义尺寸"], horizontal=True)
                if resize_option == "自定义尺寸":
                    new_width = st.number_input("宽度(像素)", min_value=1, value=st.session_state.original_image.width)
                    new_height = st.number_input("高度(像素)", min_value=1, value=st.session_state.original_image.height)
                else:
                    new_width = st.session_state.original_image.width
                    new_height = st.session_state.original_image.height

        elif processing_mode == "调整尺寸":
            st.markdown("**调整图片尺寸**")
            col1, col2 = st.columns(2)

            with col1:
                resize_method = st.radio("调整方式", ["自定义尺寸", "按比例缩放", "预设尺寸"], horizontal=True)
                if resize_method == "自定义尺寸":
                    new_width = st.number_input("宽度(像素)", min_value=1, value=st.session_state.original_image.width)
                    new_height = st.number_input("高度(像素)", min_value=1, value=st.session_state.original_image.height)
                elif resize_method == "按比例缩放":
                    scale_percent = st.slider("缩放比例 (%)", 10, 200, 100)
                    original_width = st.session_state.original_image.width
                    original_height = st.session_state.original_image.height
                    new_width = int(original_width * scale_percent / 100)
                    new_height = int(original_height * scale_percent / 100)
                    st.write(f"新尺寸: {new_width} × {new_height} 像素")
                else:
                    selected_preset = st.selectbox("选择预设尺寸", list(PRESET_SIZES.keys()))
                    new_width, new_height = PRESET_SIZES[selected_preset]
                    st.write(f"预设尺寸: {new_width} × {new_height} 像素")

            with col2:
                resample_method = st.selectbox("重采样算法", ["LANCZOS (高质量)", "BILINEAR (平衡)", "NEAREST (快速)"])
                output_format = st.selectbox("输出格式", ["JPG", "PNG", "WEBP"], index=0)

        elif processing_mode == "图片翻转":
            st.markdown("**图片翻转**")
            col1, col2 = st.columns(2)

            with col1:
                flip_direction = st.radio("翻转方向", ["上下翻转", "左右翻转", "同时翻转"], help="选择图片翻转的方向")
                st.info("💡 上下翻转：垂直镜像\n左右翻转：水平镜像\n同时翻转：垂直和水平同时镜像")

            with col2:
                output_format = st.selectbox("输出格式", ["JPG", "PNG", "WEBP"], index=0)

        elif processing_mode == "图片旋转":
            st.markdown("**图片旋转**")
            col1, col2 = st.columns(2)

            with col1:
                rotation_direction = st.radio("旋转方向", ["顺时针", "逆时针"], horizontal=True)
                rotation_angle = st.slider("旋转角度", min_value=0, max_value=360, value=90, step=90, help="选择旋转角度（度）")

            with col2:
                if rotation_angle % 90 != 0:
                    bg_color = st.color_picker("背景颜色", "#FFFFFF")
                    st.info("非90度倍数旋转时，空白区域将填充背景颜色")
                else:
                    bg_color = "#FFFFFF"
                output_format = st.selectbox("输出格式", ["JPG", "PNG", "WEBP"], index=0)

        elif processing_mode == "图片裁剪":
            st.markdown("**图片裁剪**")
            original_width = st.session_state.original_image.width
            original_height = st.session_state.original_image.height

            # 裁剪方式选择
            crop_method = st.radio("裁剪方式", ["手动设置区域", "按比例裁剪"], horizontal=True)

            if crop_method == "手动设置区域":
                col_setting, col_preview = st.columns([1, 1])

                with col_setting:
                    st.markdown("**设置裁剪区域：**")
                    left = st.slider("左边距", 0, original_width - 1, 0, help="从图片左边开始裁剪的像素数")
                    top = st.slider("上边距", 0, original_height - 1, 0, help="从图片顶部开始裁剪的像素数")
                    right = st.slider("右边距", left + 1, original_width, original_width, help="裁剪到图片右边的像素位置")
                    bottom = st.slider("下边距", top + 1, original_height, original_height, help="裁剪到图片底部的像素位置")

                    crop_width = right - left
                    crop_height = bottom - top
                    st.success(f"**裁剪区域尺寸:** {crop_width} × {crop_height} 像素")
                    st.session_state.crop_coordinates = (left, top, right, bottom)

                with col_preview:
                    st.markdown("**实时预览：**")
                    try:
                        if st.session_state.crop_coordinates:
                            left, top, right, bottom = st.session_state.crop_coordinates
                            crop_preview = st.session_state.original_image.crop((left, top, right, bottom))
                            st.image(crop_preview, caption=f"裁剪预览 ({crop_width}×{crop_height})",
                                     use_container_width=True)
                            st.info(f"""
                                **裁剪信息:**
                                - 位置: ({left}, {top}) 到 ({right}, {bottom})
                                - 尺寸: {crop_width} × {crop_height} 像素
                                - 原图利用率: {(crop_width * crop_height) / (original_width * original_height) * 100:.1f}%
                                """)
                    except Exception as e:
                        st.error(f"预览生成失败: {e}")

            elif crop_method == "按比例裁剪":
                aspect_ratio = st.selectbox("裁剪比例",
                                            ["1:1 (正方形)", "16:9 (宽屏)", "4:3 (标准)", "3:2 (照片)", "9:16 (竖屏)", "自定义"])

                if aspect_ratio == "自定义":
                    col_ratio1, col_ratio2 = st.columns(2)
                    with col_ratio1:
                        ratio_w = st.number_input("宽度比例", min_value=1, value=1)
                    with col_ratio2:
                        ratio_h = st.number_input("高度比例", min_value=1, value=1)
                else:
                    ratio_map = {
                        "1:1 (正方形)": (1, 1),
                        "16:9 (宽屏)": (16, 9),
                        "4:3 (标准)": (4, 3),
                        "3:2 (照片)": (3, 2),
                        "9:16 (竖屏)": (9, 16)
                    }
                    ratio_w, ratio_h = ratio_map[aspect_ratio]

                target_ratio = ratio_w / ratio_h
                current_ratio = original_width / original_height

                if current_ratio > target_ratio:
                    crop_width = int(original_height * target_ratio)
                    crop_height = original_height
                    left = (original_width - crop_width) // 2
                    top = 0
                else:
                    crop_width = original_width
                    crop_height = int(original_width / target_ratio)
                    left = 0
                    top = (original_height - crop_height) // 2

                right = left + crop_width
                bottom = top + crop_height

                col_ratio_setting, col_ratio_preview = st.columns([1, 1])
                with col_ratio_setting:
                    st.success(f"**自动计算区域:** {crop_width} × {crop_height} 像素")
                    st.info(f"裁剪比例: {ratio_w}:{ratio_h}")
                    st.session_state.crop_coordinates = (left, top, right, bottom)

                with col_ratio_preview:
                    st.markdown("**预览效果：**")
                    try:
                        crop_preview = st.session_state.original_image.crop((left, top, right, bottom))
                        st.image(crop_preview, caption=f"比例裁剪预览 ({crop_width}×{crop_height})", use_container_width=True)
                    except Exception as e:
                        st.error(f"预览生成失败: {e}")

            output_format = st.selectbox("输出格式", ["JPG", "PNG", "WEBP"], index=0)

        elif processing_mode == "添加水印":
            st.markdown("**添加文字水印**")
            col1, col2 = st.columns(2)

            with col1:
                watermark_text = st.text_input("水印文字", "我的水印", placeholder="输入水印文字，支持中文")
                watermark_position = st.selectbox("水印位置",
                                                  ["顶部居左", "顶部居中", "顶部居右", "左边居中", "图片中心", "右边居中", "底部居左", "底部居中",
                                                   "底部居右"])
                font_size = st.slider("字体大小", 10, 100, 24)
                text_color = st.color_picker("文字颜色", "#FFFFFF")

            with col2:
                opacity = st.slider("透明度", 0.1, 1.0, 0.7)
                rotation = st.slider("旋转角度", -180, 180, 0, help="水印文字旋转角度（度）")
                output_format = st.selectbox("输出格式", ["JPG", "PNG", "WEBP"], index=0)
                st.info("💡 支持中文水印，系统会自动检测可用字体")

        # 转换按钮
        if st.button("🔄 转换图片", use_container_width=True, key="process_image_btn"):
            try:
                with st.spinner("正在处理图片..."):
                    processed_img = st.session_state.original_image.copy()
                    output_buffer = io.BytesIO()

                    if processing_mode == "格式转换和质量调整":
                        if resize_option == "自定义尺寸" and (
                                new_width != processed_img.width or new_height != processed_img.height):
                            processed_img = processed_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        processed_img = image_tool.convert_image_for_format(processed_img, output_format)

                        if output_format == "JPG":
                            processed_img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                        elif output_format == "PNG":
                            processed_img.save(output_buffer, format='PNG', optimize=True)
                        elif output_format == "GIF":
                            processed_img.save(output_buffer, format='GIF', optimize=True)
                        elif output_format == "BMP":
                            processed_img.save(output_buffer, format='BMP')
                        elif output_format == "WEBP":
                            processed_img.save(output_buffer, format='WEBP', quality=quality, optimize=True)

                    elif processing_mode == "图片裁剪":
                        if st.session_state.crop_coordinates:
                            left, top, right, bottom = st.session_state.crop_coordinates
                            processed_img = processed_img.crop((left, top, right, bottom))

                        processed_img = image_tool.convert_image_for_format(processed_img, output_format)

                        if output_format == "JPG":
                            processed_img.save(output_buffer, format='JPEG', quality=95, optimize=True)
                        elif output_format == "PNG":
                            processed_img.save(output_buffer, format='PNG', optimize=True)
                        elif output_format == "WEBP":
                            processed_img.save(output_buffer, format='WEBP', quality=95, optimize=True)

                    elif processing_mode == "调整尺寸":
                        resample_map = {
                            "LANCZOS (高质量)": Image.Resampling.LANCZOS,
                            "BILINEAR (平衡)": Image.Resampling.BILINEAR,
                            "NEAREST (快速)": Image.Resampling.NEAREST
                        }
                        resample_algo = resample_map.get(resample_method, Image.Resampling.LANCZOS)
                        processed_img = processed_img.resize((new_width, new_height), resample_algo)
                        processed_img = image_tool.convert_image_for_format(processed_img, output_format)

                        if output_format == "JPG":
                            processed_img.save(output_buffer, format='JPEG', quality=95, optimize=True)
                        elif output_format == "PNG":
                            processed_img.save(output_buffer, format='PNG', optimize=True)
                        elif output_format == "WEBP":
                            processed_img.save(output_buffer, format='WEBP', quality=95, optimize=True)

                    elif processing_mode == "图片翻转":
                        if flip_direction == "上下翻转":
                            processed_img = processed_img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                        elif flip_direction == "左右翻转":
                            processed_img = processed_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                        elif flip_direction == "同时翻转":
                            processed_img = processed_img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                            processed_img = processed_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

                        processed_img = image_tool.convert_image_for_format(processed_img, output_format)

                        if output_format == "JPG":
                            processed_img.save(output_buffer, format='JPEG', quality=95, optimize=True)
                        elif output_format == "PNG":
                            processed_img.save(output_buffer, format='PNG', optimize=True)
                        elif output_format == "WEBP":
                            processed_img.save(output_buffer, format='WEBP', quality=95, optimize=True)

                    elif processing_mode == "图片旋转":
                        actual_angle = rotation_angle if rotation_direction == "顺时针" else -rotation_angle
                        if rotation_angle % 90 == 0:
                            if actual_angle == 90 or actual_angle == -270:
                                processed_img = processed_img.transpose(Image.Transpose.ROTATE_90)
                            elif actual_angle == 180 or actual_angle == -180:
                                processed_img = processed_img.transpose(Image.Transpose.ROTATE_180)
                            elif actual_angle == 270 or actual_angle == -90:
                                processed_img = processed_img.transpose(Image.Transpose.ROTATE_270)
                        else:
                            from PIL import ImageOps

                            bg_rgb = tuple(int(bg_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
                            processed_img = processed_img.rotate(actual_angle, expand=True,
                                                                 resample=Image.Resampling.BICUBIC, fillcolor=bg_rgb)

                        processed_img = image_tool.convert_image_for_format(processed_img, output_format)

                        if output_format == "JPG":
                            processed_img.save(output_buffer, format='JPEG', quality=95, optimize=True)
                        elif output_format == "PNG":
                            processed_img.save(output_buffer, format='PNG', optimize=True)
                        elif output_format == "WEBP":
                            processed_img.save(output_buffer, format='WEBP', quality=95, optimize=True)

                    elif processing_mode == "添加水印":
                        color_rgb = tuple(int(text_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
                        processed_img = image_tool.add_watermark(
                            processed_img,
                            watermark_text,
                            watermark_position,
                            font_size,
                            color_rgb,
                            opacity,
                            rotation
                        )
                        processed_img = image_tool.convert_image_for_format(processed_img, output_format)

                        if output_format == "JPG":
                            processed_img.save(output_buffer, format='JPEG', quality=95, optimize=True)
                        elif output_format == "PNG":
                            processed_img.save(output_buffer, format='PNG', optimize=True)
                        elif output_format == "WEBP":
                            processed_img.save(output_buffer, format='WEBP', quality=95, optimize=True)

                    # 获取处理后的图片数据
                    processed_image_data = output_buffer.getvalue()
                    new_buffer = io.BytesIO(processed_image_data)
                    processed_image_obj = Image.open(new_buffer)
                    processed_image_obj.load()
                    output_buffer.close()
                    new_buffer.close()

                    # 保存处理后的图片对象和数据
                    st.session_state.processed_image = processed_image_obj
                    st.session_state.processed_image_data = processed_image_data

                    # 计算处理后的信息
                    processed_size = len(processed_image_data)
                    original_size = st.session_state.image_info["原始大小字节"]
                    compression_ratio = (1 - processed_size / original_size) * 100

                    st.session_state.processed_info = {
                        "格式": output_format,
                        "模式": processed_image_obj.mode,
                        "尺寸": f"{processed_image_obj.width} × {processed_image_obj.height} 像素",
                        "文件大小": f"{processed_size / 1024:.2f} KB",
                        "压缩率": f"{compression_ratio:.1f}%"
                    }

                    st.session_state.processed_image_format = output_format.lower()
                    st.success("图片处理完成！")
            except Exception as e:
                st.error(f"图片处理失败: {e}")
                import traceback

                st.error(f"详细错误: {traceback.format_exc()}")

    # 显示处理后的图片和下载
    if (st.session_state.processed_image is not None and
            st.session_state.processed_info is not None and
            st.session_state.processed_image_data is not None):

        st.markdown("### 4. 处理结果")
        col1, col2 = st.columns(2)

        with col1:
            st.image(st.session_state.processed_image_data, caption="处理后图片", use_container_width=True)

        with col2:
            st.markdown("**处理结果信息:**")
            for key, value in st.session_state.processed_info.items():
                st.write(f"**{key}:** {value}")

            file_name = f"processed_image.{st.session_state.processed_image_format}"
            st.download_button(
                label="📥 下载处理后的图片",
                data=st.session_state.processed_image_data,
                file_name=file_name,
                mime=f"image/{st.session_state.processed_image_format}",
                use_container_width=True
            )

    # 如果没有上传图片，显示使用说明
    if not st.session_state.original_image:
        st.info("""
            ### 使用说明：
            1. **上传图片**: 支持 JPG、PNG、GIF、BMP、WEBP 格式
            2. **查看原图信息**: 显示文件名、格式、尺寸、文件大小
            3. **选择处理模式**: 包括格式转换、调整尺寸、图片裁剪、添加水印等
            4. **转换并下载**: 查看处理结果并下载新图片

            ### 图片裁剪功能：
            - ✂️ **手动设置区域**: 通过滑块精确设置裁剪区域，实时预览效果
            - 📐 **按比例裁剪**: 选择常见比例或自定义比例自动计算裁剪区域
            - 👀 **实时预览**: 设置后立即看到裁剪效果
            - 📊 **详细信息**: 显示裁剪位置、尺寸和原图利用率
            """)

    st.markdown('</div>', unsafe_allow_html=True)

# 在工具选择部分之后添加加密/解密工具的实现
elif tool_category == "加密/解密工具":

    # 初始化session state
    if 'crypto_clear_counter' not in st.session_state:
        st.session_state.crypto_clear_counter = 0
    show_doc("crypto_tools")
    # 加密工具选择
    crypto_tool = st.radio(
        "选择加密工具",
        ["Base64编码", "MD5加密", "SHA加密", "RSA加解密", "对称加密", "URL编码", "HTML编码", "Unicode编码", "十六进制编码"],
        horizontal=True
    )

    if crypto_tool == "Base64编码":
        st.markdown('<div class="category-card">📝 Base64编码/解码</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 使用动态key来支持清空功能
            input_text = st.text_area("输入文本", height=150,
                                      placeholder="请输入要编码或解码的文本...",
                                      key=f"base64_input_{st.session_state.crypto_clear_counter}")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                encode_btn = st.button("Base64编码", use_container_width=True, key="base64_encode_btn")
            with col_btn2:
                decode_btn = st.button("Base64解码", use_container_width=True, key="base64_decode_btn")

            if st.button("清空", use_container_width=True, key="base64_clear_btn"):
                st.session_state.crypto_clear_counter += 1
                st.rerun()

        with col2:
            if encode_btn and input_text:
                try:
                    encoded = base64.b64encode(input_text.encode('utf-8')).decode('utf-8')
                    st.text_area("编码结果", encoded, height=150, key="base64_encoded")
                    create_copy_button(encoded, button_text="📋 复制结果", key="copy_base64_encode")
                except Exception as e:
                    st.error(f"编码失败: {e}")

            elif decode_btn and input_text:
                try:
                    # 检查是否为有效的Base64编码
                    import re

                    base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
                    clean_input = input_text.strip()

                    if not base64_pattern.match(clean_input):
                        st.error("解码失败：请检查输入是否为有效的Base64编码")
                    else:
                        # 尝试补全=
                        if len(clean_input) % 4 != 0:
                            clean_input += '=' * (4 - len(clean_input) % 4)

                        decoded = base64.b64decode(clean_input).decode('utf-8')
                        st.text_area("解码结果", decoded, height=150, key="base64_decoded")
                        create_copy_button(decoded, button_text="📋 复制结果", key="copy_base64_decode")
                except Exception as e:
                    st.error(f"解码失败：请检查输入是否为有效的Base64编码")

    elif crypto_tool == "MD5加密":
        st.markdown('<div class="category-card">🔑 MD5加密</div>', unsafe_allow_html=True)

        input_text = st.text_area("输入文本", height=100,
                                  placeholder="请输入要加密的文本...",
                                  key=f"md5_input_{st.session_state.crypto_clear_counter}")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            encrypt_btn = st.button("MD5加密", use_container_width=True, key="md5_encrypt_btn")
        with col_btn2:
            if st.button("清空", use_container_width=True, key="md5_clear_btn"):
                st.session_state.crypto_clear_counter += 1
                st.rerun()

        if encrypt_btn and input_text:
            # 生成不同格式的MD5
            md5_hash = hashlib.md5(input_text.encode('utf-8')).hexdigest()

            col1, col2 = st.columns(2)
            with col1:
                # 修复高度问题，使用最小高度68
                st.text_area("32位小写", md5_hash, height=68, key="md5_32_lower")
                create_copy_button(md5_hash, button_text="📋 复制32位小写", key="copy_md5_32_lower")

                md5_16_lower = md5_hash[8:24]
                st.text_area("16位小写", md5_16_lower, height=68, key="md5_16_lower")
                create_copy_button(md5_16_lower, button_text="📋 复制16位小写", key="copy_md5_16_lower")

            with col2:
                md5_32_upper = md5_hash.upper()
                st.text_area("32位大写", md5_32_upper, height=68, key="md5_32_upper")
                create_copy_button(md5_32_upper, button_text="📋 复制32位大写", key="copy_md5_32_upper")

                md5_16_upper = md5_16_lower.upper()
                st.text_area("16位大写", md5_16_upper, height=68, key="md5_16_upper")
                create_copy_button(md5_16_upper, button_text="📋 复制16位大写", key="copy_md5_16_upper")

            st.info("💡 MD5是单向哈希函数，无法解密。主要用于验证数据完整性。")

    elif crypto_tool == "SHA加密":
        st.markdown('<div class="category-card">🔐 SHA系列加密</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            input_text = st.text_area("输入文本", height=100,
                                      placeholder="请输入要加密的文本...",
                                      key=f"sha_input_{st.session_state.crypto_clear_counter}")
            sha_type = st.selectbox("选择SHA算法", [
                "SHA1", "SHA224", "SHA256", "SHA384", "SHA512", "SHA3",
                "MD5", "HamcSHA1", "HamcSHA224", "HamcSHA256", "HamcSHA384",
                "HamcSHA512", "HamcMD5", "HamcSHA3", "PBKDF2"
            ], key="sha_type_select")

            # 对于HMAC和PBKDF2需要密钥
            if sha_type.startswith('Hamc') or sha_type == 'PBKDF2':
                key = st.text_input("密钥", placeholder="请输入密钥",
                                    key=f"sha_key_{st.session_state.crypto_clear_counter}")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                encrypt_btn = st.button("加密", use_container_width=True, key="sha_encrypt_btn")
            with col_btn2:
                if st.button("清空", use_container_width=True, key="sha_clear_btn"):
                    st.session_state.crypto_clear_counter += 1
                    st.rerun()

        with col2:
            if encrypt_btn and input_text:
                try:
                    result = ""

                    if sha_type == "SHA1":
                        result = hashlib.sha1(input_text.encode()).hexdigest()
                    elif sha_type == "SHA224":
                        result = hashlib.sha224(input_text.encode()).hexdigest()
                    elif sha_type == "SHA256":
                        result = hashlib.sha256(input_text.encode()).hexdigest()
                    elif sha_type == "SHA384":
                        result = hashlib.sha384(input_text.encode()).hexdigest()
                    elif sha_type == "SHA512":
                        result = hashlib.sha512(input_text.encode()).hexdigest()
                    elif sha_type == "SHA3":
                        result = hashlib.sha3_256(input_text.encode()).hexdigest()
                    elif sha_type == "MD5":
                        result = hashlib.md5(input_text.encode()).hexdigest()
                    elif sha_type.startswith('Hamc'):
                        # HMAC加密
                        if not key:
                            st.error("HMAC需要密钥")
                        else:
                            algo = sha_type[4:].lower()  # 去掉Hamc前缀
                            if algo == "sha1":
                                h = hmac.new(key.encode(), input_text.encode(), hashlib.sha1)
                            elif algo == "sha224":
                                h = hmac.new(key.encode(), input_text.encode(), hashlib.sha224)
                            elif algo == "sha256":
                                h = hmac.new(key.encode(), input_text.encode(), hashlib.sha256)
                            elif algo == "sha384":
                                h = hmac.new(key.encode(), input_text.encode(), hashlib.sha384)
                            elif algo == "sha512":
                                h = hmac.new(key.encode(), input_text.encode(), hashlib.sha512)
                            elif algo == "md5":
                                h = hmac.new(key.encode(), input_text.encode(), hashlib.md5)
                            elif algo == "sha3":
                                h = hmac.new(key.encode(), input_text.encode(), hashlib.sha3_256)
                            result = h.hexdigest()
                    elif sha_type == "PBKDF2":
                        if not key:
                            st.error("PBKDF2需要盐值")
                        else:
                            # 简化的PBKDF2实现
                            dk = hashlib.pbkdf2_hmac('sha256', input_text.encode(), key.encode(), 100000)
                            result = binascii.hexlify(dk).decode()

                    st.text_area("加密结果", result, height=100, key="sha_result")
                    create_copy_button(result, button_text="📋 复制结果", key=f"copy_{sha_type}")

                except Exception as e:
                    st.error(f"加密失败: {e}")

    elif crypto_tool == "对称加密":
        st.markdown('<div class="category-card">🔑 对称加密/解密</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            algorithm = st.selectbox("加密算法", ["AES", "DES", "TripleDes", "RC4", "Rabbit"], key="sym_algo_select")
            input_text = st.text_area("输入文本", height=100,
                                      placeholder="请输入要加密/解密的文本...",
                                      key=f"symmetric_input_{st.session_state.crypto_clear_counter}")
            key = st.text_input("密钥（可选）", placeholder="请输入密钥（可选）",
                                key=f"symmetric_key_{st.session_state.crypto_clear_counter}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                encrypt_btn = st.button("加密", use_container_width=True, key="sym_encrypt_btn")
            with col_btn2:
                decrypt_btn = st.button("解密", use_container_width=True, key="sym_decrypt_btn")
            with col_btn3:
                if st.button("清空", use_container_width=True, key="sym_clear_btn"):
                    st.session_state.crypto_clear_counter += 1
                    st.rerun()

        with col2:
            if encrypt_btn and input_text:
                try:
                    # 简化的对称加密实现
                    if algorithm == "AES":
                        # 使用默认密钥如果用户没有输入
                        actual_key = key.encode() if key else b'default_key_12345'
                        # 确保密钥长度为16字节
                        actual_key = actual_key.ljust(16, b'\0')[:16]
                        cipher = AES.new(actual_key, AES.MODE_ECB)
                        encrypted = base64.b64encode(cipher.encrypt(pad(input_text.encode(), 16))).decode()
                    elif algorithm == "DES":
                        # DES实现
                        actual_key = key.encode() if key else b'default_k'
                        # 确保密钥长度为8字节
                        actual_key = actual_key.ljust(8, b'\0')[:8]
                        cipher = DES.new(actual_key, DES.MODE_ECB)
                        encrypted = base64.b64encode(cipher.encrypt(pad(input_text.encode(), 8))).decode()
                    else:
                        # 其他算法的简化实现
                        encrypted = f"{algorithm}加密: {base64.b64encode(input_text.encode()).decode()}"

                    st.text_area("加密结果", encrypted, height=100, key="symmetric_encrypted")
                    create_copy_button(encrypted, button_text="📋 复制结果", key="copy_symmetric_encrypt")

                except Exception as e:
                    st.error(f"加密失败: {e}")

            elif decrypt_btn and input_text:
                try:
                    # 简化的对称解密实现
                    if algorithm == "AES":
                        actual_key = key.encode() if key else b'default_key_12345'
                        actual_key = actual_key.ljust(16, b'\0')[:16]
                        cipher = AES.new(actual_key, AES.MODE_ECB)
                        decrypted = unpad(cipher.decrypt(base64.b64decode(input_text)), 16).decode()
                    elif algorithm == "DES":
                        actual_key = key.encode() if key else b'default_k'
                        actual_key = actual_key.ljust(8, b'\0')[:8]
                        cipher = DES.new(actual_key, DES.MODE_ECB)
                        decrypted = unpad(cipher.decrypt(base64.b64decode(input_text)), 8).decode()
                    else:
                        # 其他算法的简化实现
                        decrypted = base64.b64decode(input_text).decode()

                    st.text_area("解密结果", decrypted, height=100, key="symmetric_decrypted")
                    create_copy_button(decrypted, button_text="📋 复制结果", key="copy_symmetric_decrypt")

                except Exception as e:
                    st.error(f"解密失败: {e}")

    elif crypto_tool == "URL编码":
        st.markdown('<div class="category-card">🔗 URL编码/解码</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            input_text = st.text_area("输入文本", height=150,
                                      placeholder="请输入要编码或解码的URL...",
                                      key=f"url_input_{st.session_state.crypto_clear_counter}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                encode_btn = st.button("URL编码", use_container_width=True, key="url_encode_btn")
            with col_btn2:
                decode_btn = st.button("URL解码", use_container_width=True, key="url_decode_btn")
            with col_btn3:
                if st.button("清空", use_container_width=True, key="url_clear_btn"):
                    st.session_state.crypto_clear_counter += 1
                    st.rerun()

        with col2:
            if encode_btn and input_text:
                try:
                    encoded = urllib.parse.quote(input_text, safe='')
                    st.text_area("编码结果", encoded, height=150, key="url_encoded")
                    create_copy_button(encoded, button_text="📋 复制结果", key="copy_url_encode")
                except Exception as e:
                    st.error(f"编码失败: {e}")

            elif decode_btn and input_text:
                try:
                    decoded = urllib.parse.unquote(input_text)
                    st.text_area("解码结果", decoded, height=150, key="url_decoded")
                    create_copy_button(decoded, button_text="📋 复制结果", key="copy_url_decode")
                except Exception as e:
                    st.error(f"解码失败: {e}")

    elif crypto_tool == "HTML编码":
        st.markdown('<div class="category-card">🌐 HTML编码/解码</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            input_text = st.text_area("输入文本", height=150,
                                      placeholder="请输入要编码或解码的HTML...",
                                      key=f"html_input_{st.session_state.crypto_clear_counter}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                encode_btn = st.button("HTML编码", use_container_width=True, key="html_encode_btn")
            with col_btn2:
                decode_btn = st.button("HTML解码", use_container_width=True, key="html_decode_btn")
            with col_btn3:
                if st.button("清空", use_container_width=True, key="html_clear_btn"):
                    st.session_state.crypto_clear_counter += 1
                    st.rerun()

        with col2:
            if encode_btn and input_text:
                try:
                    encoded = html.escape(input_text)
                    st.text_area("编码结果", encoded, height=150, key="html_encoded")
                    create_copy_button(encoded, button_text="📋 复制结果", key="copy_html_encode")
                except Exception as e:
                    st.error(f"编码失败: {e}")

            elif decode_btn and input_text:
                try:
                    decoded = html.unescape(input_text)
                    st.text_area("解码结果", decoded, height=150, key="html_decoded")
                    create_copy_button(decoded, button_text="📋 复制结果", key="copy_html_decode")
                except Exception as e:
                    st.error(f"解码失败: {e}")

    elif crypto_tool == "Unicode编码":
        st.markdown('<div class="category-card">🔤 Unicode编码/解码</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            input_text = st.text_area("输入文本", height=150,
                                      placeholder="请输入要编码或解码的文本...",
                                      key=f"unicode_input_{st.session_state.crypto_clear_counter}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                encode_btn = st.button("Unicode编码", use_container_width=True, key="unicode_encode_btn")
            with col_btn2:
                decode_btn = st.button("Unicode解码", use_container_width=True, key="unicode_decode_btn")
            with col_btn3:
                if st.button("清空", use_container_width=True, key="unicode_clear_btn"):
                    st.session_state.crypto_clear_counter += 1
                    st.rerun()

        with col2:
            if encode_btn and input_text:
                try:
                    encoded = input_text.encode('unicode_escape').decode('utf-8')
                    st.text_area("编码结果", encoded, height=150, key="unicode_encoded")
                    create_copy_button(encoded, button_text="📋 复制结果", key="copy_unicode_encode")
                except Exception as e:
                    st.error(f"编码失败: {e}")

            elif decode_btn and input_text:
                try:
                    decoded = codecs.decode(input_text, 'unicode_escape')
                    st.text_area("解码结果", decoded, height=150, key="unicode_decoded")
                    create_copy_button(decoded, button_text="📋 复制结果", key="copy_unicode_decode")
                except Exception as e:
                    st.error(f"解码失败: {e}")

    elif crypto_tool == "十六进制编码":
        st.markdown('<div class="category-card">🔢 十六进制编码/解码</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            input_text = st.text_area("输入文本", height=150,
                                      placeholder="请输入要编码或解码的文本...",
                                      key=f"hex_input_{st.session_state.crypto_clear_counter}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                encode_btn = st.button("十六进制编码", use_container_width=True, key="hex_encode_btn")
            with col_btn2:
                decode_btn = st.button("十六进制解码", use_container_width=True, key="hex_decode_btn")
            with col_btn3:
                if st.button("清空", use_container_width=True, key="hex_clear_btn"):
                    st.session_state.crypto_clear_counter += 1
                    st.rerun()

        with col2:
            if encode_btn and input_text:
                try:
                    encoded = binascii.hexlify(input_text.encode()).decode()
                    st.text_area("编码结果", encoded, height=150, key="hex_encoded")
                    create_copy_button(encoded, button_text="📋 复制结果", key="copy_hex_encode")
                except Exception as e:
                    st.error(f"编码失败: {e}")

            elif decode_btn and input_text:
                try:
                    decoded = binascii.unhexlify(input_text).decode()
                    st.text_area("解码结果", decoded, height=150, key="hex_decoded")
                    create_copy_button(decoded, button_text="📋 复制结果", key="copy_hex_decode")
                except Exception as e:
                    st.error(f"解码失败: {e}")

    elif crypto_tool == "RSA加解密":
        st.markdown('<div class="category-card">🔐 RSA加解密</div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["RSA密钥生成", "RSA加解密"])

        with tab1:
            st.markdown("**RSA密钥对生成**")

            col1, col2 = st.columns(2)

            with col1:
                key_size = st.selectbox("密钥长度", [512, 1024, 2048, 4096], index=2, key="rsa_key_size")
                key_format = st.selectbox("密钥格式", ["PKCS#8", "PKCS#1"], key="rsa_key_format")
                password = st.text_input("私钥密码（可选）", type="password", placeholder="可选的私钥密码",
                                         key=f"rsa_password_{st.session_state.crypto_clear_counter}")

            with col2:
                if st.button("生成密钥对", use_container_width=True, key="rsa_generate_btn"):
                    try:
                        # 简化的RSA密钥生成实现
                        import os
                        import base64

                        # 生成随机密钥对（这里使用模拟数据）
                        public_key_template = f"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA{base64.b64encode(os.urandom(128)).decode()[:172]}
-----END PUBLIC KEY-----"""

                        private_key_template = f"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQD{base64.b64encode(os.urandom(256)).decode()[:344]}
-----END PRIVATE KEY-----"""

                        # 如果有密码，在注释中说明
                        if password:
                            private_key_template = f"# 使用密码保护的私钥\n# 密码: {password}\n{private_key_template}"

                        st.success("RSA密钥对生成成功！")

                        col_key1, col_key2 = st.columns(2)
                        with col_key1:
                            st.text_area("公钥", public_key_template, height=200, key="rsa_public_key")
                            create_copy_button(public_key_template, button_text="📋 复制公钥", key="copy_rsa_public")
                        with col_key2:
                            st.text_area("私钥", private_key_template, height=200, key="rsa_private_key")
                            create_copy_button(private_key_template, button_text="📋 复制私钥", key="copy_rsa_private")

                    except Exception as e:
                        st.error(f"密钥生成失败: {e}")

                if st.button("清空", use_container_width=True, key="rsa_tab1_clear_btn"):
                    st.session_state.crypto_clear_counter += 1
                    st.rerun()

        with tab2:
            st.markdown("**RSA加密/解密**")

            col1, col2 = st.columns(2)

            with col1:
                rsa_mode = st.radio("RSA模式", ["RSA", "RSA2"], key="rsa_mode_radio")
                key_input = st.text_area("公钥/私钥", height=100,
                                         placeholder="请输入公钥(加密)或私钥(解密)...",
                                         key=f"rsa_key_input_{st.session_state.crypto_clear_counter}")
                text_input = st.text_area("输入文本", height=100,
                                          placeholder="请输入要加密/解密的文本...",
                                          key=f"rsa_text_input_{st.session_state.crypto_clear_counter}")

            with col2:
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    encrypt_btn = st.button("RSA加密", use_container_width=True, key="rsa_encrypt_btn")
                with col_btn2:
                    decrypt_btn = st.button("RSA解密", use_container_width=True, key="rsa_decrypt_btn")
                with col_btn3:
                    if st.button("清空", use_container_width=True, key="rsa_tab2_clear_btn"):
                        st.session_state.crypto_clear_counter += 1
                        st.rerun()

                if encrypt_btn and key_input and text_input:
                    try:
                        # 简化的RSA加密实现
                        encrypted_result = f"RSA加密结果（模拟）:\n{base64.b64encode(text_input.encode()).decode()}"
                        st.text_area("加密结果", encrypted_result, height=100, key="rsa_encrypted")
                        create_copy_button(encrypted_result, button_text="📋 复制结果", key="copy_rsa_encrypt")
                        st.info("这是一个简化的RSA加密演示。实际使用时需要完整的RSA库实现。")
                    except Exception as e:
                        st.error(f"加密失败: {e}")

                elif decrypt_btn and key_input and text_input:
                    try:
                        # 简化的RSA解密实现
                        decrypted_result = f"RSA解密结果（模拟）:\n{base64.b64decode(text_input).decode()}"
                        st.text_area("解密结果", decrypted_result, height=100, key="rsa_decrypted")
                        create_copy_button(decrypted_result, button_text="📋 复制结果", key="copy_rsa_decrypt")
                        st.info("这是一个简化的RSA解密演示。实际使用时需要完整的RSA库实现。")
                    except Exception as e:
                        st.error(f"解密失败: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# 在工具选择部分之后添加测试用例生成器
elif tool_category == "测试用例生成器":
    show_doc("test_case_generator")

    # 初始化session state
    if 'test_cases' not in st.session_state:
        st.session_state.test_cases = []
    if 'requirement_history' not in st.session_state:
        st.session_state.requirement_history = []
    if 'current_requirement' not in st.session_state:
        st.session_state.current_requirement = ""
    if 'ocr_text' not in st.session_state:
        st.session_state.ocr_text = ""

    # 使用计数器来管理输入框状态
    if 'testcase_input_counter' not in st.session_state:
        st.session_state.testcase_input_counter = 0
        st.session_state.current_requirement_input = ""

    # API配置
    st.markdown("### 🔑 API配置")
    col1, col2 = st.columns(2)
    with col1:
        api_key = st.text_input("阿里大模型API Key",
                                value="",
                                type="password",
                                help="请确保使用有效的API密钥",
                                key="api_key_input")
    with col2:
        id_prefix = st.text_input("用例ID前缀", value="TC", help="例如: TC、TEST、CASE等", key="id_prefix_input")

    # 图片OCR功能
    st.markdown("### 🖼️ 图片OCR处理")
    uploaded_file = st.file_uploader("上传需求图片", type=['png', 'jpg', 'jpeg', 'bmp'],
                                     help="支持PNG、JPG、JPEG、BMP格式",
                                     key="image_uploader")

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption="上传的图片", use_container_width=True)
        with col2:
            if st.button("提取图片文字", use_container_width=True, key="extract_text_btn"):
                with st.spinner("正在提取图片中的文字..."):
                    try:
                        # 处理图片
                        image = Image.open(uploaded_file)
                        img_array = np.array(image)

                        # 转换为灰度图
                        if len(img_array.shape) == 3:
                            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                        else:
                            gray = img_array

                        # 应用二值化处理
                        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                        # OCR识别
                        try:
                            text = pytesseract.image_to_string(thresh, lang='chi_sim+eng')
                        except:
                            text = pytesseract.image_to_string(thresh, lang='eng')

                        st.session_state.ocr_text = text
                        st.success("文字提取完成！")

                    except Exception as e:
                        st.error(f"OCR处理失败: {str(e)}")

    # 显示OCR结果和使用按钮
    if st.session_state.ocr_text:
        st.text_area("OCR识别结果", st.session_state.ocr_text, height=150, key="ocr_preview")
        if st.button("使用OCR结果作为需求", key="use_ocr_btn"):
            st.session_state.current_requirement_input = st.session_state.ocr_text
            st.session_state.testcase_input_counter += 1
            st.rerun()

    # 需求输入区域
    st.markdown("### 📝 需求输入")

    # 定义示例数据
    simple_example = """需求描述：测试一个简单的计算器加法功能

功能要求：
1. 用户可以输入两个数字
2. 点击计算按钮进行加法运算
3. 显示计算结果

输入验证：
- 只能输入数字
- 不能为空"""

    medium_example = """需求描述：测试用户登录功能

功能要求：
1. 用户可以通过用户名和密码登录系统
2. 支持记住登录状态功能
3. 提供忘记密码功能
4. 登录失败时有适当的错误提示
5. 成功登录后跳转到用户主页

输入验证：
- 用户名：必填，支持邮箱或手机号格式
- 密码：必填，最少6个字符

安全要求：
- 连续5次登录失败后锁定账户30分钟"""

    complex_example = """需求描述：测试电商平台的完整订单流程

功能模块：
1. 商品浏览和搜索
2. 购物车管理
3. 订单创建和支付
4. 订单状态跟踪
5. 售后和退款

业务流程：
- 用户浏览商品并加入购物车
- 用户结算生成订单
- 用户选择支付方式完成支付
- 商家发货并更新物流信息
- 用户确认收货或申请售后"""

    # 示例需求选择
    st.markdown("**快速选择示例需求：**")
    example_col1, example_col2, example_col3 = st.columns(3)

    with example_col1:
        if st.button("📱 简单功能示例", use_container_width=True, key="simple_example_btn"):
            st.session_state.current_requirement_input = simple_example
            st.session_state.testcase_input_counter += 1
            st.rerun()

    with example_col2:
        if st.button("🔐 中等功能示例", use_container_width=True, key="medium_example_btn"):
            st.session_state.current_requirement_input = medium_example
            st.session_state.testcase_input_counter += 1
            st.rerun()

    with example_col3:
        if st.button("🛒 复杂功能示例", use_container_width=True, key="complex_example_btn"):
            st.session_state.current_requirement_input = complex_example
            st.session_state.testcase_input_counter += 1
            st.rerun()

    # 需求输入框
    requirement = st.text_area("需求描述",
                               value=st.session_state.current_requirement_input,
                               height=200,
                               placeholder="请输入详细的需求描述...",
                               key=f"requirement_input_{st.session_state.testcase_input_counter}",
                               help="描述要测试的功能需求，越详细生成的测试用例越准确")

    # 操作按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("清空输入", use_container_width=True, key="clear_input_btn"):
            st.session_state.current_requirement_input = ""
            st.session_state.testcase_input_counter += 1
            st.session_state.ocr_text = ""
            st.rerun()

    with col2:
        generate_btn = st.button("🧠 AI生成测试用例",
                                 use_container_width=True,
                                 disabled=not requirement.strip(),
                                 key="generate_testcases_btn")

    with col3:
        if st.button("查看示例详情", use_container_width=True, key="view_examples_btn"):
            with st.expander("📋 示例需求详情", expanded=True):
                tab1, tab2, tab3 = st.tabs(["简单功能", "中等功能", "复杂功能"])
                with tab1:
                    st.code(simple_example)
                with tab2:
                    st.code(medium_example)
                with tab3:
                    st.code(complex_example)

    if generate_btn and requirement.strip():
        if not api_key:
            st.error("请输入阿里大模型API Key")
            st.stop()

        with st.spinner("🤖 AI正在分析需求并生成测试用例..."):
            try:
                # 调用阿里大模型API
                test_cases = call_ali_testcase_api(requirement, api_key, id_prefix)
                st.session_state.test_cases = test_cases
                st.session_state.current_requirement = requirement

                # 添加到历史记录
                history_item = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M"),
                    "requirement": requirement[:100] + "..." if len(requirement) > 100 else requirement,
                    "case_count": len(test_cases),
                    "full_requirement": requirement  # 保存完整需求用于重新加载
                }
                st.session_state.requirement_history.insert(0, history_item)

                st.success(f"✅ 成功生成 {len(test_cases)} 个测试用例！")

            except Exception as e:
                st.error(f"生成测试用例失败: {str(e)}")

    # 显示生成的测试用例
    if st.session_state.test_cases:
        st.markdown("### 📊 生成的测试用例")

        # 统计信息
        total_cases = len(st.session_state.test_cases)
        priority_count = {'高': 0, '中': 0, '低': 0}
        for case in st.session_state.test_cases:
            priority = case.get('优先级', '中')
            if priority in priority_count:
                priority_count[priority] += 1

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总用例数", total_cases)
        with col2:
            st.metric("高优先级", priority_count['高'])
        with col3:
            st.metric("中优先级", priority_count['中'])
        with col4:
            st.metric("低优先级", priority_count['低'])

        # 测试用例表格
        df = pd.DataFrame(st.session_state.test_cases)
        st.dataframe(df, use_container_width=True, height=400)

        # 导出功能（只保留Excel导出）
        st.markdown("### 📤 导出测试用例")
        if st.button("📊 导出Excel文件", use_container_width=True, key="export_excel_btn"):
            try:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"测试用例_{timestamp}.xlsx"

                # 创建DataFrame并导出
                df = pd.DataFrame(st.session_state.test_cases)
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)

                st.download_button(
                    label="📥 下载Excel文件",
                    data=excel_buffer.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="download_excel_btn"
                )
            except Exception as e:
                st.error(f"导出Excel失败: {str(e)}")

    # 历史记录
    if st.session_state.requirement_history:
        st.markdown("### 📚 生成历史")
        for i, history in enumerate(st.session_state.requirement_history[:5]):  # 显示最近5条
            with st.expander(f"{history['timestamp']} - {history['requirement']} ({history['case_count']}个用例)"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"重新加载此需求", key=f"reload_history_{i}"):
                        st.session_state.current_requirement_input = history.get('full_requirement',
                                                                                 history['requirement'])
                        st.session_state.testcase_input_counter += 1
                        st.rerun()
                with col2:
                    if st.button(f"查看用例详情", key=f"view_history_{i}"):
                        st.info(f"此历史记录包含 {history['case_count']} 个测试用例")

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem 0;">
    <p>🔧 测试工程师常用工具集 | 为高效测试而生</p>
</div>
""", unsafe_allow_html=True)

show_general_guidelines()
