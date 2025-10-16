import pandas as pd
import json
import os
import sys
import time
from typing import List, Dict, Any
import subprocess
import unittest


class InterfaceAutoTestCore:
    """接口自动化测试核心类"""

    def __init__(self):
        self.upload_dir = "uploads"
        self.test_dir = "test_cases"
        self.report_dir = "reports"
        self.setup_directories()

    def setup_directories(self):
        """创建必要的目录"""
        for directory in [self.upload_dir, self.test_dir, self.report_dir]:
            os.makedirs(directory, exist_ok=True)

    def parse_document(self, file_path: str) -> List[Dict[str, Any]]:
        """解析接口文档"""
        file_ext = file_path.split('.')[-1].lower()

        if file_ext in ['xlsx', 'xls']:
            return self.parse_excel(file_path)
        elif file_ext == 'json':
            return self.parse_json(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

    def parse_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """解析Excel文件"""
        interfaces = []

        try:
            df = pd.read_excel(file_path)

            for _, row in df.iterrows():
                interface = {
                    'name': str(row.get('接口名称', '')),
                    'method': str(row.get('请求方法', 'GET')).upper(),
                    'path': str(row.get('接口路径', '')),
                    'description': str(row.get('接口描述', '')),
                    'headers': self.parse_json_field(row.get('请求头', '{}')),
                    'parameters': self.parse_json_field(row.get('请求参数', '{}')),
                    'expected_status': int(row.get('期望状态码', 200)),
                    'expected_response': self.parse_json_field(row.get('期望响应', '{}'))
                }
                interfaces.append(interface)

        except Exception as e:
            raise ValueError(f"解析Excel文件失败: {str(e)}")

        return interfaces

    def parse_json(self, file_path: str) -> List[Dict[str, Any]]:
        """解析JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'interfaces' in data:
            return data['interfaces']
        else:
            raise ValueError("不支持的JSON格式")

    def parse_json_field(self, field: Any) -> Dict:
        """解析JSON格式的字段"""
        if not field or not isinstance(field, str):
            return {}

        try:
            return json.loads(field)
        except:
            return {}

    def generate_test_cases(self, interfaces: List[Dict[str, Any]], framework: str,
                            base_url: str, timeout: int, retry_times: int,
                            verify_ssl: bool, request_format: str = "自动检测") -> Dict[str, str]:
        """生成测试用例 - 修复参数处理"""
        # 预处理接口数据，确保参数处理正确
        processed_interfaces = []
        for interface in interfaces:
            processed_interface = interface.copy()

            # 确保路径格式正确
            path = processed_interface.get('path', '')
            if path and not path.startswith('/'):
                processed_interface['path'] = '/' + path

            # 处理参数类型
            parameters = processed_interface.get('parameters', {})
            if parameters:
                # 确保参数值是基本类型，避免JSON序列化问题
                processed_parameters = {}
                for key, value in parameters.items():
                    if isinstance(value, (str, int, float, bool)):
                        processed_parameters[key] = value
                    else:
                        processed_parameters[key] = str(value)
                processed_interface['parameters'] = processed_parameters

            processed_interfaces.append(processed_interface)

        if framework == "unittest":
            return self._generate_unittest_cases(processed_interfaces, base_url, timeout, retry_times, verify_ssl,
                                                 request_format)
        else:
            return self._generate_pytest_cases(processed_interfaces, base_url, timeout, retry_times, verify_ssl,
                                               request_format)

    def _generate_unittest_cases(self, interfaces, base_url, timeout, retry_times, verify_ssl, request_format):
        """生成unittest测试用例"""
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'http://' + base_url

        # 构建模板内容
        lines = [
            '"""',
            '自动生成的接口测试用例 - unittest版本',
            f'生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}',
            '"""',
            '',
            'import unittest',
            'import requests',
            'import json',
            '',
            '',
            'class TestURLValidation(unittest.TestCase):',
            '    """URL验证测试"""',
            '',
            '    def test_url_generation(self):',
            '        """测试URL生成是否正确"""',
            '        # 测试手动成功的URL',
            '        success_url = "http://10.0.3.54:3000/api/login"',
            '        print(f"✅ 成功URL: {success_url}")',
            '        ',
            '        # 测试生成的URL',
            f'        generated_url = "{base_url.rstrip("/")}/api/login"',
            '        print(f"🔍 生成URL: {generated_url}")',
            '        ',
            '        # 比较两者',
            '        self.assertEqual(generated_url, success_url, "生成的URL应该与成功URL一致")',
            '',
            ''
        ]

        # 添加测试用例
        for i, interface in enumerate(interfaces):
            test_case = self._create_unittest_method(interface, i, base_url)
            lines.append(test_case)
            lines.append('')

        # 添加主程序入口
        lines.extend([
            'if __name__ == "__main__":',
            '    unittest.main()',
            ''
        ])

        content = '\n'.join(lines)

        return {
            "test_interfaces.py": content
        }

    def _create_unittest_method(self, interface: Dict[str, Any], index: int, base_url: str) -> str:
        """创建unittest测试方法 - 修复GET请求参数问题"""
        method_name = f"test_interface_{index:03d}"
        if interface.get('name'):
            sanitized_name = self._sanitize_method_name(interface['name'])
            method_name += f"_{sanitized_name}"

        # 确保base_url没有结尾斜杠
        base_url_clean = base_url.rstrip('/')

        # 处理路径参数
        path = interface.get('path', '')
        parameters = interface.get('parameters', {})

        # 替换路径中的参数占位符 {param}
        if parameters and '{' in path and '}' in path:
            import re
            # 提取路径参数占位符
            path_params = re.findall(r'\{(\w+)\}', path)
            for param_name in path_params:
                if param_name in parameters:
                    path = path.replace(f'{{{param_name}}}', str(parameters[param_name]))

        # 确保路径以斜杠开头
        if not path.startswith('/'):
            path = '/' + path

        # 构建完整URL
        full_url = base_url_clean + path

        # 处理查询参数（GET请求）
        query_params = {}
        if interface.get('method', 'GET').upper() == 'GET' and parameters:
            # 对于GET请求，将参数作为查询参数
            for key, value in parameters.items():
                # 如果参数不在路径中，就作为查询参数
                if f'{{{key}}}' not in interface.get('path', ''):
                    query_params[key] = value

        # 构建查询字符串
        if query_params:
            import urllib.parse
            query_string = urllib.parse.urlencode(query_params)
            full_url = f"{full_url}?{query_string}"

        # 调试信息
        print(f"URL调试: base_url='{base_url}', path='{path}', full_url='{full_url}'")

        return f'''
    class Test{method_name.capitalize()}(unittest.TestCase):
        """{interface.get('description', '接口测试')}"""

        def setUp(self):
            self.url = "{full_url}"
            self.headers = {interface.get('headers', {})}
            self.expected_status = {interface.get('expected_status', 200)}
            # 对于非GET请求，保留请求数据
            self.data = {interface.get('parameters', {})} if "{interface.get('method', 'GET')}".upper() != "GET" else None

        def test_{method_name}(self):
            """测试接口: {interface.get('name', f'接口{index}')}"""
            import requests
            import json

            print(f"🔍 调试信息:")
            print(f"  请求URL: {{self.url}}")
            print(f"  请求方法: {interface.get('method', 'GET')}")
            print(f"  请求头: {{self.headers}}")
            print(f"  请求数据: {{self.data}}")
            print(f"  期望状态码: {{self.expected_status}}")

            try:
                # 根据请求方法发送请求
                method = "{interface.get('method', 'GET')}".lower()

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

                print(f"✅ 响应状态码: {{response.status_code}}")
                print(f"✅ 响应内容: {{response.text}}")
                print(f"✅ 实际请求URL: {{response.url}}")

                # 断言
                self.assertEqual(response.status_code, self.expected_status)

            except requests.exceptions.RequestException as e:
                self.fail(f"请求失败: {{e}}")
            except Exception as e:
                self.fail(f"测试执行错误: {{e}}")
    '''

    def _generate_pytest_cases(self, interfaces, base_url, timeout, retry_times, verify_ssl, request_format):
        """生成pytest测试用例"""
        # 确保base_url有协议前缀
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'http://' + base_url

        template = '''"""
    自动生成的接口测试用例 - pytest版本
    生成时间: {timestamp}
    """

    import pytest
    import requests
    import json
    import time


    @pytest.fixture(scope="session")
    def api_session():
        """API会话fixture"""
        session = requests.Session()
        yield session
        session.close()


    @pytest.fixture
    def api_config():
        """API配置fixture"""
        return {{
            "base_url": "{base_url}",
            "timeout": {timeout},
            "retry_times": {retry_times},
            "verify_ssl": {verify_ssl},
            "request_format": "{request_format}"
        }}


    def make_api_request(session, config, method, path, headers=None, data=None, params=None):
        """发送API请求"""
        url = config["base_url"].rstrip('/') + '/' + path.lstrip('/')

        print(f"🔍 调试 - 完整URL: {{url}}")
        print(f"🔍 调试 - 请求方法: {{method}}")
        print(f"🔍 调试 - 请求头: {{headers}}")
        print(f"🔍 调试 - 请求数据: {{data}}")
        print(f"🔍 调试 - 请求格式: {{config['request_format']}}")

        for attempt in range(config["retry_times"] + 1):
            try:
                # 根据配置决定请求数据格式
                content_type = headers.get('Content-Type', '') if headers else ''
                use_data_param = (
                    config["request_format"] == "JSON格式(data)" or 
                    (config["request_format"] == "自动检测" and content_type == 'application/json')
                )

                if use_data_param and data:
                    # 使用data参数并手动JSON编码
                    print("🔍 调试 - 使用 data=json.dumps(data) 格式")
                    response = session.request(
                        method=method,
                        url=url,
                        headers=headers or {{}},
                        data=json.dumps(data),
                        params=params,
                        timeout=config["timeout"],
                        verify=config["verify_ssl"]
                    )
                else:
                    # 使用json参数自动编码
                    print("🔍 调试 - 使用 json=data 格式")
                    response = session.request(
                        method=method,
                        url=url,
                        headers=headers or {{}},
                        json=data,
                        params=params,
                        timeout=config["timeout"],
                        verify=config["verify_ssl"]
                    )

                print(f"🔍 调试 - 响应状态码: {{response.status_code}}")
                print(f"🔍 调试 - 响应体: {{response.text}}")

                return response
            except requests.exceptions.RequestException as e:
                print(f"🔍 调试 - 请求异常 (尝试 {{attempt + 1}}/{{config['retry_times'] + 1}}): {{e}}")
                if attempt == config["retry_times"]:
                    raise e
                time.sleep(1)


    {test_cases}
    '''

        test_cases = ""
        for i, interface in enumerate(interfaces):
            test_case = self._create_pytest_function(interface, i)
            test_cases += test_case + "\n\n"

        return {
            "test_interfaces.py": template.format(
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                base_url=base_url,
                timeout=timeout,
                retry_times=retry_times,
                verify_ssl=verify_ssl,
                request_format=request_format,
                test_cases=test_cases
            )
        }

    def _create_pytest_function(self, interface: Dict[str, Any], index: int) -> str:
        """创建pytest测试函数 - 修复GET请求参数问题"""
        test_name = f"test_interface_{index:03d}"
        if interface.get('name'):
            sanitized_name = self._sanitize_method_name(interface['name'])
            test_name += f"_{sanitized_name}"

        # 处理路径参数
        path = interface.get('path', '')
        parameters = interface.get('parameters', {})
        method = interface.get('method', 'GET').upper()

        # 构建请求逻辑
        request_logic = self._build_request_logic(interface, path, parameters, method)

        return f'''
    def {test_name}(api_session, api_config):
        """测试接口: {interface.get('name', f'接口{index}')}

        {interface.get('description', '接口功能测试')}
        """
        import requests
        import json

        # 准备请求数据
        method = "{method}"
        path = "{path}"
        headers = {interface.get('headers', {})}
        parameters = {parameters}
        expected_status = {interface.get('expected_status', 200)}

        {request_logic}

        # 发送请求
        try:
            response = api_session.request(
                method=method,
                url=url,
                headers=headers,
                {'' if method == 'GET' else 'json=parameters,'}
                timeout=api_config["timeout"],
                verify=api_config["verify_ssl"]
            )

            print(f"🔍 调试信息:")
            print(f"  请求URL: {{url}}")
            print(f"  请求方法: {{method}}")
            print(f"  请求头: {{headers}}")
            print(f"  请求参数: {{parameters}}")
            print(f"  响应状态码: {{response.status_code}}")
            print(f"  响应内容: {{response.text}}")

            # 断言
            assert response.status_code == expected_status, \\
                f"状态码不匹配: 期望{{expected_status}}, 实际{{response.status_code}} - {{response.text}}"

        except requests.exceptions.RequestException as e:
            pytest.fail(f"请求失败: {{e}}")
    '''

    def _build_request_logic(self, interface: Dict[str, Any], path: str, parameters: dict, method: str) -> str:
        """构建请求逻辑"""
        lines = []

        # 处理路径参数
        if parameters and '{' in path and '}' in path:
            lines.append("    # 处理路径参数")
            lines.append("    actual_path = path")
            for key, value in parameters.items():
                if f'{{{key}}}' in path:
                    lines.append(f'    actual_path = actual_path.replace("{{{key}}}", str(parameters.get("{key}")))')
            lines.append("    url = api_config['base_url'].rstrip('/') + '/' + actual_path.lstrip('/')")
        else:
            lines.append("    url = api_config['base_url'].rstrip('/') + '/' + path.lstrip('/')")

        # 处理GET请求的查询参数
        if method == 'GET' and parameters:
            lines.append("    # 处理查询参数")
            lines.append("    import urllib.parse")
            lines.append("    query_params = {}")

            # 区分路径参数和查询参数
            path_params = []
            if '{' in path and '}' in path:
                import re
                path_params = re.findall(r'\{(\w+)\}', path)

            for key in parameters.keys():
                if key not in path_params:
                    lines.append(f'    if "{key}" in parameters:')
                    lines.append(f'        query_params["{key}"] = parameters["{key}"]')

            lines.append("    if query_params:")
            lines.append("        query_string = urllib.parse.urlencode(query_params)")
            lines.append("        url = f\"{url}?{query_string}\"")

        return '\n'.join(lines)

    def _sanitize_method_name(self, name: str) -> str:
        """清理方法名"""
        import re
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    def run_tests(self, framework: str) -> Dict[str, Any]:
        """运行测试用例"""
        if framework == "unittest":
            return self._run_unittest_tests()
        else:
            return self._run_pytest_tests()

    def _run_unittest_tests(self) -> Dict[str, Any]:
        """运行unittest测试"""
        try:
            # 添加测试目录到Python路径
            sys.path.insert(0, self.test_dir)

            # 使用unittest发现并运行测试
            loader = unittest.TestLoader()
            suite = loader.discover(self.test_dir, pattern='test_*.py')

            # 运行测试
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            return {
                'total': result.testsRun,
                'passed': result.testsRun - len(result.failures) - len(result.errors),
                'failed': len(result.failures),
                'errors': len(result.errors),
                'success': result.wasSuccessful()
            }

        except Exception as e:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'success': False,
                'error_message': str(e)
            }

    def _run_pytest_tests(self) -> Dict[str, Any]:
        """运行pytest测试"""
        try:
            # 运行pytest
            pytest_args = [
                self.test_dir,
                '-v',
                '--tb=short'
            ]

            # 执行pytest
            result = subprocess.run(
                [sys.executable, '-m', 'pytest'] + pytest_args,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            # 解析输出结果
            return self._parse_pytest_output(result.stdout)

        except Exception as e:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'success': False,
                'error_message': str(e)
            }

    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """解析pytest输出 - 修复版本"""
        import re

        passed = 0
        failed = 0
        errors = 0

        # 使用正则表达式匹配 pytest 总结行
        # 匹配格式: "X passed, Y failed, Z errors in T seconds"
        summary_pattern = r'(\d+) passed|(\d+) failed|(\d+) error'
        matches = re.findall(summary_pattern, output)

        for match in matches:
            if match[0]:  # passed
                passed = int(match[0])
            if match[1]:  # failed
                failed = int(match[1])
            if match[2]:  # errors
                errors = int(match[2])

        # 如果没有找到匹配，尝试其他格式
        if passed == 0 and failed == 0 and errors == 0:
            # 尝试匹配简单的统计行
            if "PASSED" in output:
                passed = output.count("PASSED")
            if "FAILED" in output:
                failed = output.count("FAILED")
            if "ERROR" in output:
                errors = output.count("ERROR")

        total = passed + failed + errors

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success': failed == 0 and errors == 0,
            'output': output
        }

    def generate_html_report(self, test_results: Dict[str, Any], framework: str) -> str:
        """生成HTML测试报告"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # 计算成功率
        total = test_results.get('total', 0)
        passed = test_results.get('passed', 0)
        success_rate = (passed / total * 100) if total > 0 else 0

        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>接口自动化测试报告</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #eee; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid; }}
        .metric.total {{ border-color: #007bff; }}
        .metric.passed {{ border-color: #28a745; }}
        .metric.failed {{ border-color: #dc3545; }}
        .metric.errors {{ border-color: #ffc107; }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .success-rate {{ font-size: 1.5em; color: #28a745; font-weight: bold; text-align: center; margin: 20px 0; }}
        .details {{ margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-error {{ color: #ffc107; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 接口自动化测试报告</h1>
            <p>测试框架: {framework} | 生成时间: {timestamp}</p>
        </div>

        <div class="success-rate">
            测试成功率: {success_rate:.1f}%
        </div>

        <div class="summary">
            <div class="metric total">
                <div>总用例数</div>
                <div class="metric-value">{total}</div>
            </div>
            <div class="metric passed">
                <div>通过</div>
                <div class="metric-value" style="color: #28a745;">{passed}</div>
            </div>
            <div class="metric failed">
                <div>失败</div>
                <div class="metric-value" style="color: #dc3545;">{test_results.get('failed', 0)}</div>
            </div>
            <div class="metric errors">
                <div>错误</div>
                <div class="metric-value" style="color: #ffc107;">{test_results.get('errors', 0)}</div>
            </div>
        </div>

        <div class="details">
            <h3>📊 测试详情</h3>
            <table>
                <tr>
                    <th>统计项</th>
                    <th>数量</th>
                    <th>比例</th>
                </tr>
                <tr>
                    <td>总测试用例</td>
                    <td>{total}</td>
                    <td>100%</td>
                </tr>
                <tr>
                    <td class="status-passed">通过用例</td>
                    <td>{passed}</td>
                    <td>{(passed / total * 100) if total > 0 else 0:.1f}%</td>
                </tr>
                <tr>
                    <td class="status-failed">失败用例</td>
                    <td>{test_results.get('failed', 0)}</td>
                    <td>{(test_results.get('failed', 0) / total * 100) if total > 0 else 0:.1f}%</td>
                </tr>
                <tr>
                    <td class="status-error">错误用例</td>
                    <td>{test_results.get('errors', 0)}</td>
                    <td>{(test_results.get('errors', 0) / total * 100) if total > 0 else 0:.1f}%</td>
                </tr>
            </table>
        </div>

        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>报告生成时间: {timestamp}</p>
        </div>
    </div>
</body>
</html>
'''

        report_path = os.path.join(self.report_dir, f"test_report_{int(time.time())}.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_path
