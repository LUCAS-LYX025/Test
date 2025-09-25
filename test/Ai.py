import requests
from bs4 import BeautifulSoup

# 基础URL
base_url = "https://zshq.zuiyouliao.com"

# 获取新闻列表页面的URL
news_list_url = base_url + "/news.html"

# 发送HTTP请求获取页面内容
response = requests.get(news_list_url)
soup = BeautifulSoup(response.content, 'html.parser')

# 找到所有新闻项
news_items = soup.find_all('div', class_='latest-news-item')

# 遍历每个新闻项
for item in news_items:
    # 获取新闻标题
    title_tag = item.find('a', class_='latest-news-item-mainTitle')
    if title_tag:
        title = title_tag.text.strip()
    else:
        title = "标题未找到"

    # 获取新闻内容
    content_tag = item.find('a', class_='item-desc')
    if content_tag:
        content = content_tag.text.strip()
    else:
        content = "内容未找到"

    # 打印标题和内容
    print(f"标题: {title}")
    print(f"内容: {content}")
    print("-" * 80)

