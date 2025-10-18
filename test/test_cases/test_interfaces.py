"""
自动生成的接口测试用例 - unittest版本
生成时间: 2025-10-16 20:38:44
"""

import unittest


class TestURLValidation(unittest.TestCase):
    """URL验证测试"""

    def test_url_generation(self):
        """测试URL生成是否正确"""
        # 测试手动成功的URL
        success_url = "http://10.0.3.54:3000/api/login"
        print(f"✅ 成功URL: {success_url}")

        # 测试生成的URL
        generated_url = "https://jsonplaceholder.typicode.com/api/login"
        print(f"🔍 生成URL: {generated_url}")

        # 比较两者
        self.assertEqual(generated_url, success_url, "生成的URL应该与成功URL一致")

    class TestTest_interface_000_______(unittest.TestCase):
        """获取所有帖子列表"""

        def setUp(self):
            self.url = "https://jsonplaceholder.typicode.com/posts"
            self.headers = {}
            self.expected_status = 200
            # 对于非GET请求，保留请求数据
            self.data = {} if "GET".upper() != "GET" else None

        def test_test_interface_000_______(self):
            """测试接口: 获取所有帖子"""
            import requests
            import json

            print(f"🔍 调试信息:")
            print(f"  请求URL: {self.url}")
            print(f"  请求方法: GET")
            print(f"  请求头: {self.headers}")
            print(f"  请求数据: {self.data}")
            print(f"  期望状态码: {self.expected_status}")

            try:
                # 根据请求方法发送请求
                method = "GET".lower()

                if method == 'get':
                    response = requests.get(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                elif method == 'post':
                    response = requests.post(
                        self.url,
                        headers=self.headers,
                        json=self.data,  # 使用json参数自动处理Content-Type
                        timeout=30
                    )
                elif method == 'put':
                    response = requests.put(
                        self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )
                elif method == 'delete':
                    response = requests.delete(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                else:
                    response = requests.request(
                        method=method,
                        url=self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )

                print(f"✅ 响应状态码: {response.status_code}")
                print(f"✅ 响应内容: {response.text}")
                print(f"✅ 实际请求URL: {response.url}")

                # 断言
                self.assertEqual(response.status_code, self.expected_status)

            except requests.exceptions.RequestException as e:
                self.fail(f"请求失败: {e}")
            except Exception as e:
                self.fail(f"测试执行错误: {e}")

    class TestTest_interface_001_______(unittest.TestCase):
        """获取ID为1的帖子详情"""

        def setUp(self):
            self.url = "https://jsonplaceholder.typicode.com/posts/1"
            self.headers = {}
            self.expected_status = 200
            # 对于非GET请求，保留请求数据
            self.data = {} if "GET".upper() != "GET" else None

        def test_test_interface_001_______(self):
            """测试接口: 获取单个帖子"""
            import requests
            import json

            print(f"🔍 调试信息:")
            print(f"  请求URL: {self.url}")
            print(f"  请求方法: GET")
            print(f"  请求头: {self.headers}")
            print(f"  请求数据: {self.data}")
            print(f"  期望状态码: {self.expected_status}")

            try:
                # 根据请求方法发送请求
                method = "GET".lower()

                if method == 'get':
                    response = requests.get(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                elif method == 'post':
                    response = requests.post(
                        self.url,
                        headers=self.headers,
                        json=self.data,  # 使用json参数自动处理Content-Type
                        timeout=30
                    )
                elif method == 'put':
                    response = requests.put(
                        self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )
                elif method == 'delete':
                    response = requests.delete(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                else:
                    response = requests.request(
                        method=method,
                        url=self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )

                print(f"✅ 响应状态码: {response.status_code}")
                print(f"✅ 响应内容: {response.text}")
                print(f"✅ 实际请求URL: {response.url}")

                # 断言
                self.assertEqual(response.status_code, self.expected_status)

            except requests.exceptions.RequestException as e:
                self.fail(f"请求失败: {e}")
            except Exception as e:
                self.fail(f"测试执行错误: {e}")

    class TestTest_interface_002_______(unittest.TestCase):
        """获取指定用户的帖子"""

        def setUp(self):
            self.url = "https://jsonplaceholder.typicode.com/posts?userId=1"
            self.headers = {}
            self.expected_status = 200
            # 对于非GET请求，保留请求数据
            self.data = {'userId': 1} if "GET".upper() != "GET" else None

        def test_test_interface_002_______(self):
            """测试接口: 获取用户帖子"""
            import requests
            import json

            print(f"🔍 调试信息:")
            print(f"  请求URL: {self.url}")
            print(f"  请求方法: GET")
            print(f"  请求头: {self.headers}")
            print(f"  请求数据: {self.data}")
            print(f"  期望状态码: {self.expected_status}")

            try:
                # 根据请求方法发送请求
                method = "GET".lower()

                if method == 'get':
                    response = requests.get(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                elif method == 'post':
                    response = requests.post(
                        self.url,
                        headers=self.headers,
                        json=self.data,  # 使用json参数自动处理Content-Type
                        timeout=30
                    )
                elif method == 'put':
                    response = requests.put(
                        self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )
                elif method == 'delete':
                    response = requests.delete(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                else:
                    response = requests.request(
                        method=method,
                        url=self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )

                print(f"✅ 响应状态码: {response.status_code}")
                print(f"✅ 响应内容: {response.text}")
                print(f"✅ 实际请求URL: {response.url}")

                # 断言
                self.assertEqual(response.status_code, self.expected_status)

            except requests.exceptions.RequestException as e:
                self.fail(f"请求失败: {e}")
            except Exception as e:
                self.fail(f"测试执行错误: {e}")

    class TestTest_interface_003______(unittest.TestCase):
        """创建新的帖子"""

        def setUp(self):
            self.url = "https://jsonplaceholder.typicode.com/posts"
            self.headers = {'Content-Type': 'application/json'}
            self.expected_status = 201
            # 对于非GET请求，保留请求数据
            self.data = {'title': '自动化测试帖子', 'body': '这是通过自动化测试工具创建的帖子',
                         'userId': 1} if "POST".upper() != "GET" else None

        def test_test_interface_003______(self):
            """测试接口: 创建新帖子"""
            import requests
            import json

            print(f"🔍 调试信息:")
            print(f"  请求URL: {self.url}")
            print(f"  请求方法: POST")
            print(f"  请求头: {self.headers}")
            print(f"  请求数据: {self.data}")
            print(f"  期望状态码: {self.expected_status}")

            try:
                # 根据请求方法发送请求
                method = "POST".lower()

                if method == 'get':
                    response = requests.get(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                elif method == 'post':
                    response = requests.post(
                        self.url,
                        headers=self.headers,
                        json=self.data,  # 使用json参数自动处理Content-Type
                        timeout=30
                    )
                elif method == 'put':
                    response = requests.put(
                        self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )
                elif method == 'delete':
                    response = requests.delete(
                        self.url,
                        headers=self.headers,
                        timeout=30
                    )
                else:
                    response = requests.request(
                        method=method,
                        url=self.url,
                        headers=self.headers,
                        json=self.data,
                        timeout=30
                    )

                print(f"✅ 响应状态码: {response.status_code}")
                print(f"✅ 响应内容: {response.text}")
                print(f"✅ 实际请求URL: {response.url}")

                # 断言
                self.assertEqual(response.status_code, self.expected_status)

            except requests.exceptions.RequestException as e:
                self.fail(f"请求失败: {e}")
            except Exception as e:
                self.fail(f"测试执行错误: {e}")


if __name__ == "__main__":
    unittest.main()
