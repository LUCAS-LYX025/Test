import requests
import json


def test_qwen_http():
    """
    通过HTTP API测试通义千问
    """
    # 1. API 端点 URL
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    # 2. 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-6b67f41754b94e2eb82696b32d29c094"  # 您的API Key
    }

    # 3. 请求体（数据）
    data = {
        "model": "qwen-turbo",  # 指定模型
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "中国的首都是什么城市？请只回答城市名。"
                }
            ]
        },
        "parameters": {
            "temperature": 0.1  # 让回答更确定
        }
    }

    print("正在通过HTTP调用通义千问模型...")

    # 4. 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()

    # 5. 处理响应
    if response.status_code == 200:
        print("✅ API 调用成功！")
        # 提取回答内容
        answer = result['output']['text']
        print(f"模型回答: {answer}")
    else:
        print("❌ API 调用失败")
        print(f"错误码: {response.status_code}")
        print(f"错误详情: {result}")


if __name__ == '__main__':
    test_qwen_http()