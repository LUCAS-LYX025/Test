import streamlit as st
import streamlit.components.v1 as components
import json
import datetime


class StreamlitUIComponents:
    """Streamlit UI 组件封装类"""

    def __init__(self):
        """初始化UI组件（不包含set_page_config）"""
        self._inject_styles()

    def setup_page_config(self, page_title=None, page_icon=None, layout="wide", initial_sidebar_state="expanded"):
        """单独设置页面配置方法

        Args:
            page_title: 页面标题
            page_icon: 页面图标
            layout: 布局方式 ("centered" 或 "wide")
            initial_sidebar_state: 侧边栏初始状态
        """
        if page_title:
            st.set_page_config(
                page_title=page_title,
                page_icon=page_icon,
                layout=layout,
                initial_sidebar_state=initial_sidebar_state
            )
        return self

    def _inject_styles(self):
        """注入全局CSS样式"""
        st.markdown("""
        <style>
            /* 全局样式 */
            .main {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }

            .main-header {
                font-size: 3rem;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                font-weight: 700;
                text-shadow: 0 4px 6px rgba(0,0,0,0.1);
                padding: 1rem;
            }

            .sub-header {
                font-size: 1.5rem;
                color: #2d3748;
                font-weight: 600;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 3px solid #667eea;
            }

            /* 工具卡片网格布局 */
            .tools-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }

            .tool-card {
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                border: 1px solid #e2e8f0;
                transition: all 0.3s ease;
                cursor: pointer;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }

            .tool-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                border-color: #667eea;
            }

            .tool-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: #667eea;
            }

            .tool-title {
                font-size: 1.3rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 0.5rem;
            }

            .tool-desc {
                color: #718096;
                font-size: 0.95rem;
                line-height: 1.5;
            }

            /* 功能区域样式 */
            .section-card {
                background: white;
                border-radius: 16px;
                padding: 2rem;
                margin: 1.5rem 0;
                box-shadow: 0 8px 20px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
            }

            .category-card {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }

            /* 按钮样式 */
            .stButton button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 0.75rem 2rem;
                border-radius: 12px;
                font-weight: 600;
                transition: all 0.3s ease;
                width: 100%;
            }

            .stButton button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            }

            .copy-btn {
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                color: white;
                border: none;
                padding: 0.6rem 1.5rem;
                border-radius: 10px;
                font-weight: 500;
                transition: all 0.3s ease;
                margin: 5px;
            }

            .copy-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 15px rgba(72, 187, 120, 0.3);
            }

            /* 结果框样式 */
            .result-box {
                background: #f8fafc;
                border: 2px dashed #cbd5e0;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                font-family: 'Courier New', monospace;
                white-space: pre-wrap;
                max-height: 400px;
                overflow-y: auto;
                font-size: 0.9rem;
            }

            /* 标签页样式 */
            .stTabs [data-baseweb="tab-list"] {
                gap: 2rem;
                background-color: #f7fafc;
                padding: 0.5rem;
                border-radius: 12px;
            }

            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #f7fafc;
                border-radius: 8px 8px 0px 0px;
                gap: 1rem;
                padding: 0 1.5rem;
                font-weight: 500;
            }

            .stTabs [aria-selected="true"] {
                background-color: #667eea !important;
                color: white !important;
            }

            /* 侧边栏样式 */
            .css-1d391kg {
                background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            }

            /* 指标卡片 */
            .metric-card {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                text-align: center;
                border-left: 4px solid #667eea;
            }

            /* 响应式调整 */
            @media (max-width: 768px) {
                .tools-grid {
                    grid-template-columns: 1fr;
                }

                .main-header {
                    font-size: 2rem;
                }
            }
        </style>
        """, unsafe_allow_html=True)

    # ================ 布局组件方法 ================

    def main_header(self, text):
        """主标题"""
        st.markdown(f'<div class="main-header">{text}</div>', unsafe_allow_html=True)

    def sub_header(self, text):
        """副标题"""
        st.markdown(f'<div class="sub-header">{text}</div>', unsafe_allow_html=True)

    def section_card(self, content):
        """区域卡片"""
        st.markdown(f'<div class="section-card">{content}</div>', unsafe_allow_html=True)

    def category_card(self, text):
        """分类卡片"""
        st.markdown(f'<div class="category-card">{text}</div>', unsafe_allow_html=True)

    def metric_card(self, title, value):
        """指标卡片"""
        st.markdown(f'''
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #718096; margin-bottom: 0.5rem;">{title}</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #2d3748;">{value}</div>
        </div>
        ''', unsafe_allow_html=True)

    # ================ 工具卡片网格 ================

    def create_tool_card(self, icon, title, description, onclick_js=""):
        """创建单个工具卡片HTML"""
        return f'''
        <div class="tool-card" onclick="{onclick_js}">
            <div>
                <div class="tool-icon">{icon}</div>
                <div class="tool-title">{title}</div>
                <div class="tool-desc">{description}</div>
            </div>
        </div>
        '''

    def display_tools_grid(self, tools_data):
        """显示工具卡片网格

        Args:
            tools_data: 工具数据列表，每个元素为字典，包含:
                - icon: 图标
                - title: 标题
                - description: 描述
                - onclick: 点击JS代码(可选)
        """
        cards_html = ""
        for tool in tools_data:
            onclick_js = tool.get('onclick', '')
            cards_html += self.create_tool_card(
                tool['icon'], tool['title'], tool['description'], onclick_js
            )

        st.markdown(f'<div class="tools-grid">{cards_html}</div>', unsafe_allow_html=True)

    # ================ 功能方法 ================

    def escape_js_string(self, text):
        """安全转义 JavaScript 字符串"""
        return json.dumps(text)

    def create_copy_button(self, text, button_text="📋 复制到剪贴板", key=None):
        """创建一键复制按钮"""
        if key is None:
            key = hash(text)

        escaped_text = self.escape_js_string(text)

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

    def display_generated_results(self, title, content, filename_prefix):
        """统一展示生成结果 + 复制 + 下载"""
        self.category_card(f"📋 生成结果 - {title}")
        st.markdown(f'<div class="result-box">{content}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            self.create_copy_button(content, button_text="📋 复制结果", key=f"copy_{filename_prefix}")
        with col2:
            st.download_button(
                label="💾 下载结果",
                data=content,
                file_name=f"{filename_prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )


# 创建全局实例
ui = StreamlitUIComponents()
