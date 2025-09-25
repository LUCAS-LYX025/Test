import datetime
import requests
import re

from dingtalkchatbot.chatbot import DingtalkChatbot
from jinja2 import Template

# 发送请求获取数据
from utils.config import Config

url = "https://prezcloud.zuiyouliao.com/low-code-boot/workflow/eventFlow/hook/bca2124fa54511ee948700163e086121_1hf21rno65s02"
data = {}  # 替换成实际的 hookId
response = requests.post(url, json=data)  # 使用 json 参数传递数据

# 检查请求是否成功
if response.status_code == 200:
    data = response.json()
    # 检查请求返回的数据是否成功
    if data["success"]:
        results = data["result"]

        # 准备数据，将结果转换为适合HTML报告的格式
        bug_data = []
        for result in results:
            bug_title = result["result"]["bug标题"]
            reason = result["result"]["原因"]

            # 使用正则表达式过滤掉 <p> 和 </p> 标签以及图片文件地址
            reason = re.sub(r'<[^>]*>', '', reason)
            reason = re.sub(r'\[.*?\]\(.*?\)', '', reason)

            bug_data.append({"bug_title": bug_title, "reason": reason})

        # 使用 Jinja2 模板生成 HTML 报告
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bug Report</title>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <h2>Bug Report</h2>
            <table>
                <thead>
                    <tr>
                        <th>Bug标题</th>
                        <th>原因</th>
                    </tr>
                </thead>
                <tbody>
                    {% for bug in bug_data %}
                    <tr>
                        <td>{{ bug.bug_title }}</td>
                        <td>{{ bug.reason }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """

        template = Template(template_str)
        html_report = template.render(bug_data=bug_data)

        # 保存 HTML 报告到文件
        html_filename = "bug_report.html"
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_report)
        print("HTML 报告已成功生成。")

        data = Config("/Users/leiyuxing/PycharmProjects/TestFramework/study/db_config.yaml").get('zentao_data')
        title = data.get('markdown').get('title')
        server = data.get('server')
        is_at_all = data.get('is_at_all')
        url = data.get('url')
        sign_mark = data.get('sign_mark')
        print(data)

        xiaoding = DingtalkChatbot(url)
        now = datetime.datetime.now().strftime("%Y%m%d%H%M")
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        xiaoding.send_markdown(title=title,
                               text='#### **{0}线上BUG情况统计**\n\n 各位同学，以下是截止到{1}的线上BUG情况统计 \n\n[查看详情]({2}TestFramework/study/bug_report.html) \n'.format(
                                   sign_mark, sign_mark,server, html_report,), is_at_all=is_at_all)