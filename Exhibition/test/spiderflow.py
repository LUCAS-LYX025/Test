import pymysql
import requests
import json
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': '10.0.3.190',
    "port": 3306,
    'user': 'spider',
    'password': 'sp1der#2024f',
    'database': 'spiderflow',
    'charset': 'utf8mb4'
}

# 钉钉通知配置
sign_mark = "本周"
test_webhook = 'https://oapi.dingtalk.com/robot/send?access_token=adf0d08ffcebec69eabb0e2ba14ad0df1a5bb5de0414ee9f8aefdbbd5a4c92da'


def query_abnormal_spiders():
    """
    查询异常爬虫名称
    """
    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            # 执行SQL查询
            sql = "SELECT `name` FROM sp_flow WHERE enabled='1' and next_execute_time is null"
            cursor.execute(sql)

            # 获取所有结果
            results = cursor.fetchall()

            # 提取名称列表
            names = [result[0] for result in results]

            return names

    except Exception as e:
        print(f"数据库查询错误: {e}")
        return []
    finally:
        if connection:
            connection.close()


def send_dingtalk_message(names, webhook_url):
    """
    发送钉钉通知
    """
    if not names:
        print("没有异常爬虫，无需发送通知")
        return False

    # 构建消息内容
    names_str = "、".join(names)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = {
        "msgtype": "text",
        "text": {
            "content": f"爬虫【{names_str}】发生异常，请及时关注！\n{sign_mark}时间: {current_time}\n "
        },
        "at": {
            "isAtAll": False  # 不@所有人，可以根据需要修改
        }
    }

    try:
        # 发送请求
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            webhook_url,
            data=json.dumps(message),
            headers=headers
        )

        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('errcode') == 0:
                print("钉钉通知发送成功")
                return True
            else:
                print(f"钉钉通知发送失败: {result.get('errmsg')}")
                return False
        else:
            print(f"HTTP请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"发送钉钉通知错误: {e}")
        return False


def main():
    """
    主函数
    """
    print("开始检查异常爬虫...")

    # 查询异常爬虫
    abnormal_names = query_abnormal_spiders()

    if abnormal_names:
        print(f"发现 {len(abnormal_names)} 个异常爬虫: {abnormal_names}")

        # 发送钉钉通知
        success = send_dingtalk_message(abnormal_names, test_webhook)

        if success:
            print("通知发送完成")
        else:
            print("通知发送失败")
    else:
        print("未发现异常爬虫")


if __name__ == "__main__":
    main()