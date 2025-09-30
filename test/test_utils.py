import pandas as pd
import json
import re
from datetime import timedelta
import time
from io import StringIO
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from difflib import Differ
import html
import streamlit as st
from doc_manager import show_doc, show_general_guidelines
from ip_query_tool import IPQueryTool
from data_generator import DataGenerator
import sys

print(sys.path)
sys.path.append('/mount/src/test/test')
from data_constants import PROVINCES, COUNTRIES, CATEGORIES, PROVINCE_MAP, TO_SECONDS, RANDOM_STRING_TYPES, \
    PASSWORD_OPTIONS, DOMAINS_PRESET, GENDERS, TOOL_CATEGORIES, CSS_STYLES, HEADLINE_STYLES
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
            # 确保 PROVINCES 是列表类型
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
        st.markdown("**日志统计信息**")
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

        st.markdown("**日志过滤**")
        col1, col2 = st.columns(2)
        with col1:
            filter_level = st.multiselect("日志级别", ["ERROR", "WARN", "INFO", "DEBUG"], default=["ERROR", "WARN"])
            keyword = st.text_input("关键词搜索")
        with col2:
            use_regex = st.checkbox("使用正则表达式")
            case_sensitive = st.checkbox("大小写敏感")

        if st.button("应用过滤", use_container_width=True):
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

            st.markdown("**过滤结果**")
            st.text_area("", "\n".join(filtered_lines), height=300)
            st.metric("匹配行数", len(filtered_lines))

            if st.button("导出结果", use_container_width=True):
                st.success(f"已找到 {len(filtered_lines)} 行匹配结果（导出功能模拟）")

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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["IP/域名查询", "子域名查询", "备案信息查询", "批量查询", "IPv4转换工具", "旁站查询", "IP反查网站"])

    with tab1:
        st.markdown("**IP/域名基本信息查询**")

        # 添加获取当前公网IP的按钮
        if st.button("获取当前公网IP", key="get_public_ip", use_container_width=True):
            with st.spinner("正在获取当前公网IP..."):
                public_ip = ip_tool.get_public_ip()
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
                result = ip_tool.get_ip_domain_info(target_input, is_ip)

                if result['success']:
                    st.success("查询成功！")

                    st.markdown("**基本信息**")
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
                        rdns_result = ip_tool.get_rdns_info(target_input)
                        if rdns_result['success']:
                            st.metric("rDNS", rdns_result['data'].get('rDNS', '未知'))

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
        st.markdown("**子域名查询**")
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
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #4299e1;">
                            <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.5rem;">子域名 {i + 1}</div>
                            <div style="color: #4a5568;"><a href="http://{subdomain}" target="_blank">{subdomain}</a></div>
                        </div>
                        """, unsafe_allow_html=True)
                if len(result) > 20:
                    st.info(f"还有 {len(result) - 20} 个子域名未显示")

    with tab3:
        st.markdown("**备案信息查询**")
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
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                            <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.5rem;">{key}</div>
                            <div style="color: #4a5568;">{value}</div>
                        </div>
                        """, unsafe_allow_html=True)

    with tab4:
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

    with tab5:
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

    with tab6:
        st.markdown("**旁站查询**")
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
                result = ip_tool.find_same_site_sites(site_to_query)
                if result['success']:
                    st.success(f"找到 {len(result['data'])} 个旁站")
                    for i, site in enumerate(result['data'][:15]):
                        with st.container():
                            st.markdown(f"""
                            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #4299e1;">
                                <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.5rem;">旁站 {i + 1}</div>
                                <div style="color: #4a5568;"><a href="http://{site}" target="_blank">{site}</a></div>
                            </div>
                            """, unsafe_allow_html=True)
                    if len(result['data']) > 15:
                        st.info(f"还有 {len(result['data']) - 15} 个旁站未显示")
                else:
                    st.error(f"查询失败: {result['error']}")

    with tab7:
        st.markdown("**IP反查网站**")
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
                result = ip_tool.reverse_ip_lookup(ip_to_reverse)

                if result['success']:
                    st.success(f"找到 {len(result['data'])} 个网站")
                    for i, site in enumerate(result['data'][:20]):
                        with st.container():
                            st.markdown(f"""
                            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #4299e1;">
                                <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.5rem;">网站 {i + 1}</div>
                                <div style="color: #4a5568;"><a href="http://{site}" target="_blank">{site}</a></div>
                            </div>
                            """, unsafe_allow_html=True)
                    if len(result['data']) > 20:
                        st.info(f"还有 {len(result['data']) - 20} 个网站未显示")
                else:
                    st.error(f"反查失败: {result['error']}")

    st.markdown('</div>', unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem 0;">
    <p>🔧 测试工程师常用工具集 | 为高效测试而生</p>
</div>
""", unsafe_allow_html=True)

show_general_guidelines()
