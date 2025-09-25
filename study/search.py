import requests
import json  # 用于格式化 JSON 输出

url = 'https://searchalgpre-jy.zuiyouliao.com/system/search_serve'

headers = {
    'version': 'v4.11.0',
    'ZYL-UPAS-TOKEN': '',
    'ZYL-USER-TOKEN': '',
    'deviceId': 'deviceno0010123654id',
    'Content-Type': 'application/json'
}

data = {
    "condition": {
        "if_time_sort": 0,
        "markets": [],
        "position_markets": [],
        "recycle_material_markets": [],  # 修正拼写错误（原代码是 recycle_material_markets）
        "recycle_material_position_markets": []  # 修正拼写错误（原代码是 recycle_material_position_markets）
    },
    "entry_type": 0,
    "if_recycle_material": 0,
    "is_fold": 1,
    "query": "阳竹",
    "size": 500,
    "type": 8
}

try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # 检查请求是否成功

    print("=" * 50)
    print("响应状态码:", response.status_code)
    print("=" * 50)

    # 解析 JSON 并格式化输出
    json_response = response.json()
    formatted_json = json.dumps(json_response, indent=4, ensure_ascii=False)  # 缩进4个空格，支持中文显示

    print("响应内容（格式化 JSON）：")
    print(formatted_json)

except requests.exceptions.RequestException as e:
    print("请求出错:", e)
except ValueError as e:
    print("解析JSON响应出错:", e)
    print("原始响应内容:")
    print(response.text)