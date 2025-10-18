import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import io


class BIAnalyzer:
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json']

    def show_upload_section(self):
        """显示文件上传区域"""
        st.markdown("### 📁 数据上传")

        # 先显示模板下载
        self.download_templates()

        st.markdown("---")

        # 再显示文件上传
        uploaded_file = st.file_uploader(
            "上传数据文件",
            type=self.supported_formats,
            help=f"支持的文件格式: {', '.join(self.supported_formats)}",
            key="bi_data_upload"
        )

        return uploaded_file

    def download_templates(self):
        """提供标准模板下载"""
        st.markdown("#### 📥 下载数据模板")

        # Excel模板
        excel_template = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02', '2024-01-03'],
            '产品': ['产品A', '产品B', '产品C'],
            '销售额': [1500.00, 2300.50, 1800.00],
            '数量': [10, 15, 12],
            '地区': ['北京', '上海', '广州'],
            '客户评分': [4.5, 4.2, 4.7]
        })

        excel_buffer = io.BytesIO()
        excel_template.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                label="📊 Excel模板",
                data=excel_buffer.getvalue(),
                file_name="BI数据模板.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col2:
            # CSV模板
            csv_template = excel_template.to_csv(index=False)
            st.download_button(
                label="📁 CSV模板",
                data=csv_template,
                file_name="BI数据模板.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col3:
            # JSON模板
            json_template = excel_template.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                label="📋 JSON模板",
                data=json_template,
                file_name="BI数据模板.json",
                mime="application/json",
                use_container_width=True
            )

    def load_data(self, uploaded_file):
        """加载数据文件"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            else:
                return None, "不支持的文件格式"

            return df, "数据加载成功"
        except Exception as e:
            return None, f"数据加载失败: {str(e)}"

    def data_preview(self, df):
        """数据预览"""
        st.subheader("📋 数据预览")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总行数", len(df))
        with col2:
            st.metric("总列数", len(df.columns))
        with col3:
            st.metric("缺失值", df.isnull().sum().sum())
        with col4:
            st.metric("重复行", df.duplicated().sum())

        # 显示数据前几行
        st.dataframe(df.head(10), use_container_width=True)

        # 数据类型信息
        st.subheader("🔍 数据类型信息")
        dtype_info = pd.DataFrame({
            '列名': df.columns,
            '数据类型': df.dtypes,
            '非空值数量': df.count(),
            '缺失值数量': df.isnull().sum(),
            '唯一值数量': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(dtype_info, use_container_width=True)

    def basic_statistics(self, df):
        """基础统计分析"""
        st.subheader("📊 基础统计分析")

        # 选择数值列
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if numeric_cols:
            col1, col2 = st.columns(2)

            with col1:
                selected_num_col = st.selectbox("选择数值列", numeric_cols, key="stats_num_col")
                if selected_num_col:
                    stats = df[selected_num_col].describe()
                    st.dataframe(stats, use_container_width=True)

            with col2:
                # 分布直方图
                if selected_num_col:
                    fig = px.histogram(df, x=selected_num_col,
                                       title=f"{selected_num_col} 分布直方图",
                                       nbins=30)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("未找到数值列进行统计分析")

    def create_pivot_table(self, df):
        """创建数据透视表"""
        st.subheader("🔍 数据透视表分析")

        all_columns = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        col1, col2, col3 = st.columns(3)

        with col1:
            index_col = st.selectbox("行索引", categorical_cols, key="pivot_index")
        with col2:
            columns_col = st.selectbox("列索引", [None] + categorical_cols, key="pivot_columns")
        with col3:
            values_col = st.selectbox("计算值", numeric_cols, key="pivot_values")

        agg_func = st.selectbox("聚合函数", ['sum', 'mean', 'count', 'min', 'max'], key="pivot_agg")

        if st.button("生成透视表", key="generate_pivot"):
            try:
                if values_col and index_col:
                    pivot_df = pd.pivot_table(df,
                                              values=values_col,
                                              index=index_col,
                                              columns=columns_col,
                                              aggfunc=agg_func,
                                              fill_value=0)

                    st.dataframe(pivot_df, use_container_width=True)

                    # 透视表可视化
                    fig = px.imshow(pivot_df,
                                    title=f"透视表热力图 - {values_col} by {index_col}",
                                    aspect="auto")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"生成透视表失败: {str(e)}")

    def time_series_analysis(self, df):
        """时间序列分析"""
        st.subheader("📈 时间序列分析")

        # 自动检测时间列
        date_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col])
                    date_columns.append(col)
                except:
                    continue

        if not date_columns:
            st.warning("未检测到时间序列列")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            date_col = st.selectbox("选择时间列", date_columns, key="ts_date_col")
        with col2:
            value_col = st.selectbox("选择数值列",
                                     df.select_dtypes(include=[np.number]).columns.tolist(),
                                     key="ts_value_col")
        with col3:
            freq = st.selectbox("时间频率", ['D', 'W', 'M', 'Q', 'Y'], key="ts_freq")

        if date_col and value_col:
            try:
                # 转换时间列
                df_temp = df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col])
                df_temp = df_temp.set_index(date_col)

                # 重采样
                resampled = df_temp[value_col].resample(freq).mean()

                # 绘制时间序列图
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=resampled.index, y=resampled.values,
                                         mode='lines+markers',
                                         name=value_col))

                fig.update_layout(title=f"{value_col} 时间序列趋势",
                                  xaxis_title="时间",
                                  yaxis_title=value_col)

                st.plotly_chart(fig, use_container_width=True)

                # 显示统计信息
                st.subheader("时间序列统计")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

                with col_stat1:
                    st.metric("平均值", f"{resampled.mean():.2f}")
                with col_stat2:
                    st.metric("标准差", f"{resampled.std():.2f}")
                with col_stat3:
                    st.metric("最大值", f"{resampled.max():.2f}")
                with col_stat4:
                    st.metric("最小值", f"{resampled.min():.2f}")

            except Exception as e:
                st.error(f"时间序列分析失败: {str(e)}")

    def correlation_analysis(self, df):
        """相关性分析"""
        st.subheader("🔗 相关性分析")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            st.warning("需要至少2个数值列进行相关性分析")
            return

        # 计算相关系数矩阵
        corr_matrix = df[numeric_cols].corr()

        # 绘制热力图
        fig = px.imshow(corr_matrix,
                        title="相关性热力图",
                        aspect="auto",
                        color_continuous_scale='RdBu_r')

        st.plotly_chart(fig, use_container_width=True)

        # 显示详细的相关系数
        st.subheader("详细相关系数")
        st.dataframe(corr_matrix, use_container_width=True)

    def create_dashboard(self, df):
        """创建综合仪表板"""
        st.subheader("🎯 综合数据仪表板")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        if not numeric_cols:
            st.warning("没有数值列可用于创建仪表板")
            return

        # 仪表板配置
        col1, col2 = st.columns(2)

        with col1:
            x_axis = st.selectbox("X轴", categorical_cols + numeric_cols, key="dashboard_x")
        with col2:
            y_axis = st.selectbox("Y轴", numeric_cols, key="dashboard_y")

        chart_type = st.selectbox("图表类型",
                                  ["散点图", "折线图", "柱状图", "箱线图", "面积图"],
                                  key="chart_type")

        if st.button("生成仪表板", key="generate_dashboard"):
            try:
                if chart_type == "散点图" and x_axis and y_axis:
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                elif chart_type == "折线图" and x_axis and y_axis:
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                elif chart_type == "柱状图" and x_axis and y_axis:
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                elif chart_type == "箱线图" and x_axis and y_axis:
                    fig = px.box(df, x=x_axis, y=y_axis, title=f"{y_axis} 分布 by {x_axis}")
                elif chart_type == "面积图" and x_axis and y_axis:
                    fig = px.area(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                else:
                    st.error("请选择有效的图表配置")
                    return

                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"生成图表失败: {str(e)}")

    def export_report(self, df):
        """导出分析报告"""
        st.subheader("💾 导出分析报告")

        report_type = st.selectbox("选择报告格式", ["Excel", "CSV", "HTML"], key="report_type")

        if st.button("生成报告", key="generate_report"):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                if report_type == "Excel":
                    # 创建Excel报告
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='原始数据', index=False)

                        # 添加统计信息
                        stats_df = df.describe()
                        stats_df.to_excel(writer, sheet_name='统计信息')

                        # 添加相关性矩阵
                        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                        if numeric_cols:
                            corr_df = df[numeric_cols].corr()
                            corr_df.to_excel(writer, sheet_name='相关性分析')

                    output.seek(0)
                    st.download_button(
                        label="📥 下载Excel报告",
                        data=output.getvalue(),
                        file_name=f"BI分析报告_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                elif report_type == "CSV":
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 下载CSV数据",
                        data=csv_data,
                        file_name=f"数据导出_{timestamp}.csv",
                        mime="text/csv"
                    )

                elif report_type == "HTML":
                    # 生成HTML报告
                    html_report = self.generate_html_report(df)
                    st.download_button(
                        label="📥 下载HTML报告",
                        data=html_report,
                        file_name=f"BI分析报告_{timestamp}.html",
                        mime="text/html"
                    )

            except Exception as e:
                st.error(f"生成报告失败: {str(e)}")

    def generate_html_report(self, df):
        """生成HTML格式的报告"""
        html_content = f"""
        <html>
        <head>
            <title>BI数据分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .section {{ margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <h1>BI数据分析报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="section">
                <h2>数据概览</h2>
                <p>总行数: {len(df)}</p>
                <p>总列数: {len(df.columns)}</p>
            </div>

            <div class="section">
                <h2>数据预览</h2>
                {df.head(10).to_html()}
            </div>

            <div class="section">
                <h2>统计信息</h2>
                {df.describe().to_html()}
            </div>
        </body>
        </html>
        """
        return html_content