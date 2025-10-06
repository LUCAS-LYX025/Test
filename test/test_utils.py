import os

import pandas as pd
import json
import re
from datetime import timedelta
import time
import streamlit.components.v1 as components
from difflib import Differ
import html
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
from data_constants import PROVINCE_CITY_AREA_CODES
from datetime_utils import DateTimeUtils
from json_file_utils import JSONFileUtils
from collections import Counter
import datetime
import uuid
import random

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


# ================ 辅助函数 ================
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
                            button.style.background = '';
                        }}, 2000);
                    }} else {{
                        button.innerHTML = '❌ 复制失败';
                        button.style.background = '#e53e3e';
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

    button_html = f"""
    <div>
        <button data-copy-button="{key}"
                style="background:linear-gradient(135deg, #48bb78 0%, #38a169 100%);color:white;border:none;padding:10px 20px;border-radius:10px;cursor:pointer;font-size:14px;margin:5px;font-weight:500;transition:all 0.3s ease;">
            {button_text}
        </button>
    </div>
    """

    components.html(button_html + copy_script, height=70)


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

    text_input = st.text_area("输入要统计的文本", height=200, placeholder="在此处输入或粘贴文本...")

    if text_input:
        # 指标卡片布局
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem; font-weight: 600; color: #667eea;">字符数（含空格）</div>
                <div style="font-size: 2rem; font-weight: 700; color: #2d3748;">{len(text_input)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem; font-weight: 600; color: #48bb78;">字符数（不含空格）</div>
                <div style="font-size: 2rem; font-weight: 700; color: #2d3748;">{len(text_input.replace(' ', ''))}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            words = text_input.split()
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem; font-weight: 600; color: #ed8936;">单词数</div>
                <div style="font-size: 2rem; font-weight: 700; color: #2d3748;">{len(words)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            lines = text_input.split('\n')
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem; font-weight: 600; color: #9f7aea;">行数</div>
                <div style="font-size: 2rem; font-weight: 700; color: #2d3748;">{len(lines)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            paragraphs = [p for p in text_input.split('\n\n') if p.strip()]
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem; font-weight: 600; color: #f56565;">段落数</div>
                <div style="font-size: 2rem; font-weight: 700; color: #2d3748;">{len(paragraphs)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="category-card">📊 详细统计信息</div>', unsafe_allow_html=True)
        char_freq = Counter(text_input)
        sorted_chars = char_freq.most_common(10)
        if sorted_chars:
            st.write("**最常见字符（前10个）:**")
            SPECIAL_CHARS_DISPLAY = {
                ' ': "[空格]",
                '\n': "[换行]",
                '\t': "[制表符]"
            }
            for char, freq in sorted_chars:
                display_char = SPECIAL_CHARS_DISPLAY.get(char, char)
                st.write(f"`{display_char}`: {freq}次")

    st.markdown('</div>', unsafe_allow_html=True)

# 文本对比工具
elif tool_category == "文本对比工具":
    show_doc("text_comparison")

    # 简化 session 初始化逻辑
    st.session_state.setdefault('text1_content', "")
    st.session_state.setdefault('text2_content', "")
    st.session_state.setdefault('clear_counter', 0)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.markdown("**原始文本**")
        text1 = st.text_area(" ", height=300,  # 将label改为空格
                             key=f"text1_{st.session_state.clear_counter}",
                             value=st.session_state.text1_content,
                             label_visibility="collapsed")
    with col_input2:
        st.markdown("**对比文本**")
        text2 = st.text_area(" ", height=300,  # 将label改为空格
                             key=f"text2_{st.session_state.clear_counter}",
                             value=st.session_state.text2_content,
                             label_visibility="collapsed")

    button_col1, button_col2 = st.columns([1, 1])
    with button_col1:
        if st.button("开始对比", use_container_width=True):
            if text1 and text2:
                try:
                    d = Differ()
                    diff = list(d.compare(text1.splitlines(), text2.splitlines()))

                    st.markdown("**对比结果**")
                    html_parts = ["<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>"]
                    for line in diff:
                        escaped_line = html.escape(line[2:] if len(line) > 2 else line)
                        if line.startswith('+ '):
                            html_parts.append(
                                f"<div style='background-color: #d4edda; margin: 2px 0; padding: 2px 5px; border-radius: 3px;'>{escaped_line}</div>")
                        elif line.startswith('- '):
                            html_parts.append(
                                f"<div style='background-color: #f8d7da; margin: 2px 0; padding: 2px 5px; border-radius: 3px;'>{escaped_line}</div>")
                        elif line.startswith('? '):
                            html_parts.append(
                                f"<div style='background-color: #fff3cd; margin: 2px 0; padding: 2px 5px; border-radius: 3px;'>{escaped_line}</div>")
                        else:
                            content = escaped_line if line.startswith('  ') else html.escape(line)
                            html_parts.append(f"<div style='margin: 2px 0; padding: 2px 5px;'>{content}</div>")
                    html_parts.append("</div>")
                    result_html = ''.join(html_parts)
                    st.markdown(result_html, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"发生未知错误: {e}")
            else:
                st.warning("请填写原始文本和对比文本")

    with button_col2:
        if st.button("清空所有内容", use_container_width=True):
            st.session_state.text1_content = ""
            st.session_state.text2_content = ""
            st.session_state.clear_counter += 1
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# 正则表达式测试工具
elif tool_category == "正则表达式测试工具":
    show_doc("regex_tester")

    col1, col2 = st.columns(2)
    with col1:
        regex_pattern = st.text_input("正则表达式", placeholder="例如: ^[a-zA-Z0-9]+$")
        test_text = st.text_area("测试文本", height=200, placeholder="在此输入要测试的文本...")
    with col2:
        st.markdown("**匹配选项**")
        global_match = st.checkbox("全局匹配 (g)", value=True)
        ignore_case = st.checkbox("忽略大小写 (i)")
        multiline = st.checkbox("多行模式 (m)")

        st.markdown("**替换功能**")
        replace_text = st.text_input("替换文本", placeholder="输入替换文本（可选）")

    if st.button("测试正则表达式", use_container_width=True):
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
                        st.markdown("**匹配详情**")
                        for i, match in enumerate(matches):
                            st.write(f"匹配 {i + 1}: 位置 {match.start()}-{match.end()}: `{match.group()}`")
                            if match.groups():
                                st.write(f"  分组: {match.groups()}")
                    else:
                        st.warning("未找到匹配项。")

                if replace_text:
                    replaced_text = re.sub(regex_pattern, replace_text, test_text, flags=flags)
                    st.markdown("**替换结果**")
                    st.text_area("", replaced_text, height=150)
            except re.error as e:
                st.error(f"正则表达式错误: {e}")
        else:
            st.warning("请输入正则表达式和测试文本")

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

        st.markdown("""
        <style>
        .json-parse-result {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .json-success {
            background-color: #f0f9ff;
            border: 1px solid #b3e0ff;
        }
        .json-error {
            background-color: #fff5f5;
            border: 1px solid #ffcccc;
        }
        </style>
        """, unsafe_allow_html=True)

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
            if st.button("🚀 解析JSON", use_container_width=True):
                if json_input.strip():
                    try:
                        # 解析JSON
                        parsed_json = json.loads(json_input)
                        st.session_state.parse_result = parsed_json
                        st.session_state.parse_error = None
                        st.rerun()
                    except json.JSONDecodeError as e:
                        st.session_state.parse_result = None
                        st.session_state.parse_error = str(e)
                        st.rerun()
                else:
                    st.warning("请输入JSON字符串")

        with col2:
            if st.button("✨ 格式化", use_container_width=True):
                if json_input.strip():
                    try:
                        parsed_json = json.loads(json_input)
                        formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                        st.session_state.json_input_content = formatted_json
                        st.session_state.parse_result = parsed_json
                        st.session_state.parse_error = None
                        st.rerun()
                    except json.JSONDecodeError as e:
                        st.session_state.parse_error = str(e)
                        st.rerun()

        with col3:
            if st.button("📋 复制结果", use_container_width=True):
                if st.session_state.parse_result is not None:
                    formatted_json = json.dumps(st.session_state.parse_result, indent=2, ensure_ascii=False)
                    st.code(formatted_json, language='json')
                    # 这里可以添加复制到剪贴板的功能
                    st.success("结果已准备好复制")

        with col4:
            if st.button("🗑️ 清空", use_container_width=True):
                st.session_state.json_input_content = ""
                st.session_state.parse_result = None
                st.session_state.parse_error = None
                st.rerun()

        # 显示解析结果
        if st.session_state.parse_result is not None:
            st.markdown("### 📊 解析结果")

            # 显示格式化后的JSON
            formatted_json = json.dumps(st.session_state.parse_result, indent=2, ensure_ascii=False)
            with st.expander("📄 格式化JSON", expanded=True):
                st.code(formatted_json, language='json')

            # 显示JSON信息统计
            st.markdown("### 📈 JSON信息统计")
            info_cols = st.columns(4)

            with info_cols[0]:
                total_keys = utils.count_keys(st.session_state.parse_result)
                st.metric("总键数量", total_keys)

            with info_cols[1]:
                json_size = len(json_input.encode('utf-8'))
                st.metric("JSON大小", f"{json_size} 字节")

            with info_cols[2]:
                depth = utils.get_json_depth(st.session_state.parse_result)
                st.metric("最大深度", depth)

            with info_cols[3]:
                data_type = type(st.session_state.parse_result).__name__
                st.metric("根类型", data_type)

            # 显示JSON结构树
            st.markdown("### 🌳 JSON结构")
            structure = utils.analyze_json_structure(st.session_state.parse_result)
            utils.display_json_structure(structure)

        elif st.session_state.parse_error is not None:
            st.markdown("### ❌ 解析错误")
            st.error(f"JSON解析错误: {st.session_state.parse_error}")

            # 提供错误修正建议
            error_msg = st.session_state.parse_error.lower()
            if "expecting" in error_msg or "unexpected" in error_msg:
                st.info("""
                **🔧 常见错误修正建议：**
                - 检查是否缺少逗号分隔符
                - 检查引号是否匹配（建议使用双引号）
                - 检查大括号、中括号是否匹配
                - 检查最后一个元素后不应有逗号
                """)
            elif "double quotes" in error_msg:
                st.info("""
                **💡 引号使用建议：**
                - JSON规范要求使用双引号
                - 错误的例子: `{name:'Tom'}`
                - 正确的例子: `{"name":"Tom"}`
                """)

    elif tool_mode == "JSON数据对比":
        show_doc("json_comparison")

        # 初始化 session_state
        if 'json1_content' not in st.session_state:
            st.session_state.json1_content = '{"name": "John", "age": 30, "city": "New York"}'
        if 'json2_content' not in st.session_state:
            st.session_state.json2_content = '{"name": "Jane", "age": 25, "country": "USA"}'

        # 输入区域
        input_cols = st.columns(2)
        with input_cols[0]:
            st.markdown("**JSON 1**")
            json1 = st.text_area("", height=300, key="json1", value=st.session_state.json1_content,
                                 placeholder='输入第一个JSON数据...')
        with input_cols[1]:
            st.markdown("**JSON 2**")
            json2 = st.text_area("", height=300, key="json2", value=st.session_state.json2_content,
                                 placeholder='输入第二个JSON数据...')

        # 按钮区域
        button_cols = st.columns(4)
        with button_cols[0]:
            if st.button("✨ 格式化全部", use_container_width=True):
                try:
                    if json1:
                        parsed_json1 = json.loads(json1)
                        formatted_json1 = json.dumps(parsed_json1, indent=2, ensure_ascii=False)
                        st.session_state.json1_content = formatted_json1
                    if json2:
                        parsed_json2 = json.loads(json2)
                        formatted_json2 = json.dumps(parsed_json2, indent=2, ensure_ascii=False)
                        st.session_state.json2_content = formatted_json2
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"JSON格式错误: {e}")

        with button_cols[1]:
            if st.button("🔍 开始对比", use_container_width=True):
                if json1 and json2:
                    try:
                        obj1 = json.loads(json1)
                        obj2 = json.loads(json2)

                        st.markdown("### 📋 对比结果")

                        differences = utils.compare_json(obj1, obj2)

                        if differences:
                            st.error(f"发现 {len(differences)} 个差异:")
                            for diff in differences:
                                st.write(f"- {diff}")
                        else:
                            st.success("✅ 两个JSON对象完全相同")

                        st.markdown("### 📊 对比摘要")
                        summary_cols = st.columns(3)
                        with summary_cols[0]:
                            st.metric("JSON1键数量", utils.count_keys(obj1))
                        with summary_cols[1]:
                            st.metric("JSON2键数量", utils.count_keys(obj2))
                        with summary_cols[2]:
                            st.metric("差异数量", len(differences))

                    except json.JSONDecodeError as e:
                        st.error(f"JSON格式错误: {e}")
                    except Exception as e:
                        st.error(f"对比过程中发生错误: {e}")
                else:
                    st.warning("请填写两个JSON数据进行对比")

        with button_cols[2]:
            if st.button("🔄 交换数据", use_container_width=True):
                st.session_state.json1_content, st.session_state.json2_content = \
                    st.session_state.json2_content, st.session_state.json1_content
                st.rerun()

        with button_cols[3]:
            if st.button("🗑️ 清空全部", use_container_width=True):
                st.session_state.json1_content = ""
                st.session_state.json2_content = ""
                st.rerun()

    elif tool_mode == "JSONPath查询":
        show_doc("jsonpath_tool")

        # st.markdown("### 🔍 JSONPath查询工具")

        # 初始化session_state
        if 'jsonpath_json_content' not in st.session_state:
            st.session_state.jsonpath_json_content = '''{
    "store": {
        "book": [
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99
            }
        ],
        "bicycle": {
            "color": "red",
            "price": 19.95
        }
    },
    "expensive": 10
}'''
        if 'jsonpath_expression' not in st.session_state:
            st.session_state.jsonpath_expression = "$.store.book[*].author"
        if 'jsonpath_result' not in st.session_state:
            st.session_state.jsonpath_result = None

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
                if st.button("🚀 执行查询", use_container_width=True):
                    if json_data_input.strip() and jsonpath_input.strip():
                        try:
                            # 更新session_state为当前输入的值
                            st.session_state.jsonpath_json_content = json_data_input
                            st.session_state.jsonpath_expression = jsonpath_input
                            # 解析JSON数据
                            json_data = json.loads(json_data_input)

                            # 执行JSONPath查询
                            result = utils.execute_jsonpath(json_data, jsonpath_input)
                            st.session_state.jsonpath_result = result
                            st.rerun()

                        except json.JSONDecodeError as e:
                            st.error(f"JSON数据格式错误: {e}")
                        except Exception as e:
                            st.error(f"JSONPath查询错误: {e}")
                    else:
                        st.warning("请填写JSON数据和JSONPath表达式")

            with col2:
                if st.button("🗑️ 清空", use_container_width=True):
                    st.session_state.jsonpath_json_content = ""
                    st.session_state.jsonpath_expression = ""
                    st.session_state.jsonpath_result = None
                    st.rerun()

        with right_col:
            st.markdown("### 📋 查询结果")

            # 显示结果
            if st.session_state.jsonpath_result is not None:
                result = st.session_state.jsonpath_result

                if result:
                    st.success(f"✅ 找到 {len(result)} 个匹配项")

                    # 显示匹配数量
                    st.metric("匹配数量", len(result))

                    # 显示结果详情
                    st.markdown("**📄 匹配结果:**")
                    for i, item in enumerate(result):
                        with st.expander(f"结果 #{i + 1}", expanded=len(result) <= 3):
                            if isinstance(item, (dict, list)):
                                st.json(item)
                            else:
                                st.code(str(item))
                else:
                    st.warning("❌ 未找到匹配项")

            else:
                st.info("👆 请在左侧输入JSON数据和JSONPath表达式，然后点击'执行查询'")

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
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    st.success(f"📁 脚本所在目录123: `{script_dir}`")

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
# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem 0;">
    <p>🔧 测试工程师常用工具集 | 为高效测试而生</p>
</div>
""", unsafe_allow_html=True)

show_general_guidelines()
