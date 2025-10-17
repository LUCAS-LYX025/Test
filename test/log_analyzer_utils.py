class LogAnalyzerUtils:
    """日志分析工具辅助类"""

    @staticmethod
    def apply_text_filters(line, log_levels, ip_filter, status_codes, show_only_errors, hide_debug):
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