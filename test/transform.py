import xmind

def parse_markdown_to_xmind(markdown_content):
    # 创建一个新的工作簿
    workbook = xmind.load("template.xmind")  # 先加载一个模板文件，如果没有可以创建空白模板
    sheet = workbook.createSheet()
    sheet.setTitle("Markdown to XMind")

    root_topic = sheet.getRootTopic()
    root_topic.setTitle("Root")

    current_topic = root_topic  # 设置当前主题为根主题

    lines = markdown_content.splitlines()
    for line in lines:
        if line.startswith("## "):  # 解析子主题
            sub_topic = current_topic.addSubTopic()
            sub_topic.setTitle(line[3:])
        elif line.startswith("# "):  # 解析根主题
            current_topic = root_topic.addSubTopic()
            current_topic.setTitle(line[2:])

    # 保存 XMind 文件
    xmind.save(workbook, "output.xmind")
    print("XMind file has been created as output.xmind")


# 从Markdown文件读取内容
with open("/Users/leiyuxing/PycharmProjects/TestFramework/test/a.md", "r", encoding="utf-8") as f:
    markdown_content = f.read()

parse_markdown_to_xmind(markdown_content)
