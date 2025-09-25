# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: test_overseas_backend_search_serve.py
@time: 2025/7/22 14:59
"""
import requests
import time


def measure_response_time(url, payload, num_requests=10):
    """
    统计API的响应时间

    :param url: API地址
    :param payload: 请求体
    :param num_requests: 请求次数，默认为10
    :return: 统计结果字典
    """
    response_times = []

    for i in range(num_requests):
        start_time = time.time()

        try:
            response = requests.post(url, json=payload)
            response_time = time.time() - start_time
            response_times.append(response_time)

            print(f"请求 {i + 1}/{num_requests} - 状态码: {response.status_code} - 响应时间: {response_time:.3f}秒")

        except Exception as e:
            print(f"请求 {i + 1}/{num_requests} 失败: {str(e)}")
            continue

    if not response_times:
        return None

    # 计算统计指标
    stats = {
        'total_requests': num_requests,
        'successful_requests': len(response_times),
        'min_time': min(response_times),
        'max_time': max(response_times),
        'avg_time': sum(response_times) / len(response_times),
        'response_times': response_times
    }

    return stats


if __name__ == "__main__":
    # API配置
    url = "https://searchalgpre-jy.zuiyouliao.com/overseas_search/overseas_backend_search_serve"
    payload = {
        "page": 1,
        "size": 20,
        "type": 8,
        "search_condition": {},
        "condition": {}
    }

    # 测量响应时间（默认10次请求）
    results = measure_response_time(url, payload)
    print(results)

    # 打印统计结果
    if results:
        print("\n响应时间统计结果:")
        print(f"总请求次数: {results['total_requests']}")
        print(f"成功请求次数: {results['successful_requests']}")
        print(f"最短响应时间: {results['min_time']:.3f}秒")
        print(f"最长响应时间: {results['max_time']:.3f}秒")
        print(f"平均响应时间: {results['avg_time']:.3f}秒")
    else:
        print("所有请求都失败了")
