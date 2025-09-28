import datetime
import time
from datetime import timedelta


class DateTimeUtils:
    """
    时间处理工具类
    提供日期相关的各种计算和判断功能
    """

    @staticmethod
    def is_leap_year(year):
        """判断是否为闰年"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    @staticmethod
    def days_in_month(year, month):
        """获取指定年月的天数"""
        days_per_month = [31, 29 if DateTimeUtils.is_leap_year(year) else 28, 31,
                          30, 31, 30, 31, 31, 30, 31, 30, 31]
        return days_per_month[month - 1]

    @staticmethod
    def add_months(source_date, months):
        """添加指定月数到日期"""
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, DateTimeUtils.days_in_month(year, month))
        return datetime.date(year, month, day)

    @staticmethod
    def subtract_months(source_date, months):
        """从日期减去指定月数"""
        month = source_date.month - 1 - months
        year = source_date.year + month // 12
        month = month % 12 + 1
        if month <= 0:
            year -= 1
            month += 12
        day = min(source_date.day, DateTimeUtils.days_in_month(year, month))
        return datetime.date(year, month, day)

    @staticmethod
    def count_business_days(start_date, end_date):
        """计算两个日期之间的工作日数量（周一到周五）"""
        total_days = (end_date - start_date).days + 1
        full_weeks, extra_days = divmod(total_days, 7)
        business_days = full_weeks * 5
        for i in range(extra_days):
            current_day = start_date + timedelta(days=i)
            if current_day.weekday() < 5:
                business_days += 1
        return business_days

    @staticmethod
    def get_current_date():
        """获取当前日期"""
        return datetime.date.today()

    @staticmethod
    def get_current_datetime():
        """获取当前日期时间"""
        return datetime.datetime.now()

    @staticmethod
    def date_to_string(date, format_str="%Y-%m-%d"):
        """将日期对象转换为字符串"""
        return date.strftime(format_str)

    @staticmethod
    def string_to_date(date_string, format_str="%Y-%m-%d"):
        """将字符串转换为日期对象"""
        return datetime.datetime.strptime(date_string, format_str).date()

    @staticmethod
    def is_weekend(date):
        """判断是否为周末"""
        return date.weekday() >= 5

    @staticmethod
    def add_days(source_date, days):
        """添加指定天数到日期"""
        return source_date + timedelta(days=days)

    @staticmethod
    def subtract_days(source_date, days):
        """从日期减去指定天数"""
        return source_date - timedelta(days=days)

    @staticmethod
    def date_difference(start_date, end_date):
        """计算两个日期之间的天数差"""
        return (end_date - start_date).days


# 使用示例
if __name__ == "__main__":
    # 创建工具实例
    dt_utils = DateTimeUtils()

    # 测试功能
    today = dt_utils.get_current_date()
    print(f"今天: {dt_utils.date_to_string(today)}")

    # 添加月份
    future_date = dt_utils.add_months(today, 3)
    print(f"三个月后: {dt_utils.date_to_string(future_date)}")

    # 计算工作日
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 1, 31)
    business_days = dt_utils.count_business_days(start_date, end_date)
    print(f"2024年1月工作日: {business_days}天")

    # 判断闰年
    print(f"2024是闰年: {dt_utils.is_leap_year(2024)}")