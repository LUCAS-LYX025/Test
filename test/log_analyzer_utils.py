import pandas as pd
import json


class LogAnalyzerUtils:
    """日志分析工具辅助类"""

    @staticmethod
    def apply_text_filters(line, text_filters, logic_operator="AND"):
        """应用文本过滤器 - 支持多条件组合查询"""
        if not text_filters:
            return True

        include_line = True if logic_operator == "AND" else False

        for filter_config in text_filters:
            filter_type = filter_config.get('type')
            filter_value = filter_config.get('value')
            filter_match = False

            if not filter_value:  # 空条件跳过
                continue

            if filter_type == "log_level":
                # 日志级别过滤
                level_match = False
                if "错误" in filter_value and any(word in line.upper() for word in ['ERROR', 'ERR']):
                    level_match = True
                if "警告" in filter_value and any(word in line.upper() for word in ['WARN', 'WARNING']):
                    level_match = True
                if "信息" in filter_value and any(word in line.upper() for word in ['INFO', 'INFORMATION']):
                    level_match = True
                if "调试" in filter_value and any(word in line.upper() for word in ['DEBUG', 'DBG']):
                    level_match = True
                filter_match = level_match

            elif filter_type == "ip_filter":
                # IP地址过滤
                filter_match = filter_value in line

            elif filter_type == "status_code":
                # 状态码过滤
                codes = [code.strip() for code in filter_value.split(',')]
                filter_match = any(
                    f" {code} " in line or line.endswith(f" {code}") or f" {code}" in line for code in codes)

            elif filter_type == "keyword":
                # 关键词过滤
                filter_match = filter_value.lower() in line.lower()

            elif filter_type == "show_only_errors":
                # 仅显示错误
                filter_match = any(word in line.upper() for word in ['ERROR', 'ERR', 'FAIL', 'EXCEPTION'])

            elif filter_type == "hide_debug":
                # 隐藏调试
                filter_match = not any(word in line.upper() for word in ['DEBUG', 'DBG'])

            # 根据逻辑运算符组合结果
            if logic_operator == "AND":
                include_line = include_line and filter_match
                if not include_line:  # AND 逻辑下有一个不匹配就可以提前退出
                    break
            else:  # OR 逻辑
                include_line = include_line or filter_match
                if include_line:  # OR 逻辑下有一个匹配就可以提前退出
                    break

        return include_line

    @staticmethod
    def apply_json_filters(df, json_filters, logic_operator="AND"):
        """应用JSON字段过滤器 - 支持多条件组合查询"""
        if not json_filters or df.empty:
            return df

        mask = pd.Series([True] * len(df))

        for filter_config in json_filters:
            column = filter_config.get('column')
            field = filter_config.get('field')
            value = filter_config.get('value')
            value_range = filter_config.get('value_range')

            if not column or not field:
                continue

            def check_json_condition(row):
                try:
                    if pd.isna(row[column]):
                        return False
                    if isinstance(row[column], str):
                        json_data = json.loads(row[column])
                        if field in json_data:
                            field_value = json_data[field]

                            # 范围筛选
                            if value_range:
                                if isinstance(field_value, (int, float)):
                                    return value_range[0] <= field_value <= value_range[1]
                                return False

                            # 值筛选
                            if value:
                                return str(value).lower() in str(field_value).lower()

                            return True  # 如果没有值和范围，只要有这个字段就返回True
                except:
                    pass
                return False

            column_mask = df.apply(check_json_condition, axis=1)

            if logic_operator == "AND":
                mask = mask & column_mask
            else:  # OR 逻辑
                mask = mask | column_mask

        return df[mask]

    @staticmethod
    def detect_log_level(line):
        """检测日志级别"""
        line_upper = line.upper()
        if any(word in line_upper for word in ['ERROR', 'ERR']):
            return "🔴 错误"
        elif any(word in line_upper for word in ['WARN', 'WARNING']):
            return "🟡 警告"
        elif any(word in line_upper for word in ['INFO', 'INFORMATION']):
            return "🔵 信息"
        elif any(word in line_upper for word in ['DEBUG', 'DBG']):
            return "🟢 调试"
        else:
            return "⚪ 其他"

    @staticmethod
    def extract_timestamp(line):
        """提取时间戳（简化版本）"""
        import re
        # 常见的时间戳格式
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
            r'\d{2}:\d{2}:\d{2}',
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()
        return "未知时间"

    @staticmethod
    def find_keyword_position(line, keyword):
        """查找关键词位置"""
        if not keyword:
            return "未指定"
        position = line.lower().find(keyword.lower())
        if position != -1:
            return f"第 {position + 1} 字符"
        return "未找到"