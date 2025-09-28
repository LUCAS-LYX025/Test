"""
JSON和文件操作工具类
包含JSON比较、键计数和文件名提取功能
"""

import os
import re
from pathlib import Path
from typing import Union, List, Any, Dict


class JSONFileUtils:
    """
    JSON和文件操作工具类
    提供JSON比较、键计数和文件名提取等功能
    """

    def __init__(self):
        """初始化工具类"""
        self.comparison_stats = {
            'differences_count': 0,
            'keys_compared': 0
        }

    def get_filename(self, filepath: Union[str, Path], with_extension: bool = True) -> str:
        """
        从文件路径中提取文件名

        Args:
            filepath: 文件路径，可以是字符串或Path对象
            with_extension: 是否包含文件扩展名，默认为True

        Returns:
            str: 提取的文件名

        Examples:
            >>> utils = JSONFileUtils()
            >>> utils.get_filename("/path/to/file.txt")
            'file.txt'
            >>> utils.get_filename("/path/to/file.txt", False)
            'file'
        """
        filepath = str(filepath)
        basename = os.path.basename(filepath)

        if not with_extension:
            basename = os.path.splitext(basename)[0]

        return basename

    def get_filename_advanced(self, filepath: Union[str, Path],
                              with_extension: bool = True,
                              clean_special_chars: bool = False) -> str:
        """
        高级文件名提取函数，提供更多选项

        Args:
            filepath: 文件路径
            with_extension: 是否包含扩展名
            clean_special_chars: 是否清理特殊字符

        Returns:
            str: 处理后的文件名

        Examples:
            >>> utils = JSONFileUtils()
            >>> utils.get_filename_advanced("/path/to/special@file#name.txt", clean_special_chars=True)
            'special_file_name.txt'
        """
        filename = self.get_filename(filepath, with_extension)

        if clean_special_chars:
            if with_extension:
                name, ext = os.path.splitext(filename)
                name = re.sub(r'[^\w\-]', '_', name)
                filename = name + ext
            else:
                filename = re.sub(r'[^\w\-]', '_', filename)

        return filename

    def compare_json(self, obj1: Any, obj2: Any, path: str = "") -> List[str]:
        """
        比较两个JSON对象的差异

        Args:
            obj1: 第一个JSON对象
            obj2: 第二个JSON对象
            path: 当前比较的路径（用于递归）

        Returns:
            List[str]: 差异列表

        Examples:
            >>> utils = JSONFileUtils()
            >>> obj1 = {"name": "John", "age": 30}
            >>> obj2 = {"name": "Jane", "age": 30}
            >>> differences = utils.compare_json(obj1, obj2)
            >>> print(differences)
            ['值不同: name (John vs Jane)']
        """
        differences = []
        self.comparison_stats['keys_compared'] += 1

        if type(obj1) != type(obj2):
            diff_msg = f"类型不同: {path} ({type(obj1).__name__} vs {type(obj2).__name__})"
            differences.append(diff_msg)
            self.comparison_stats['differences_count'] += 1
            return differences

        if isinstance(obj1, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                if key in obj1 and key not in obj2:
                    diff_msg = f"键缺失于JSON2: {new_path}"
                    differences.append(diff_msg)
                    self.comparison_stats['differences_count'] += 1
                elif key not in obj1 and key in obj2:
                    diff_msg = f"键缺失于JSON1: {new_path}"
                    differences.append(diff_msg)
                    self.comparison_stats['differences_count'] += 1
                else:
                    differences.extend(self.compare_json(obj1[key], obj2[key], new_path))
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                diff_msg = f"数组长度不同: {path} ({len(obj1)} vs {len(obj2)})"
                differences.append(diff_msg)
                self.comparison_stats['differences_count'] += 1
            else:
                for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                    differences.extend(self.compare_json(item1, item2, f"{path}[{i}]"))
        else:
            if obj1 != obj2:
                diff_msg = f"值不同: {path} ({obj1} vs {obj2})"
                differences.append(diff_msg)
                self.comparison_stats['differences_count'] += 1

        return differences

    def count_keys(self, obj: Any) -> int:
        """
        计算JSON对象中的键数量

        Args:
            obj: JSON对象（字典、列表或基本类型）

        Returns:
            int: 键的总数量

        Examples:
            >>> utils = JSONFileUtils()
            >>> data = {"user": {"name": "John", "age": 30}, "tags": ["a", "b"]}
            >>> utils.count_keys(data)
            5
        """
        if isinstance(obj, dict):
            count = len(obj)
            for value in obj.values():
                count += self.count_keys(value)
            return count
        elif isinstance(obj, list):
            count = 0
            for item in obj:
                count += self.count_keys(item)
            return count
        else:
            return 0

    def get_comparison_stats(self) -> Dict[str, int]:
        """
        获取比较统计信息

        Returns:
            Dict[str, int]: 统计信息字典
        """
        return self.comparison_stats.copy()

    def reset_stats(self):
        """重置统计信息"""
        self.comparison_stats = {
            'differences_count': 0,
            'keys_compared': 0
        }

    def analyze_json_structure(self, obj: Any, current_level: int = 0) -> Dict[str, Any]:
        """
        分析JSON结构

        Args:
            obj: 要分析的JSON对象
            current_level: 当前层级

        Returns:
            Dict[str, Any]: 结构分析结果
        """
        analysis = {
            'type': type(obj).__name__,
            'level': current_level,
            'size': len(obj) if hasattr(obj, '__len__') else 1,
            'children': []
        }

        if isinstance(obj, dict):
            for key, value in obj.items():
                child_analysis = self.analyze_json_structure(value, current_level + 1)
                child_analysis['key'] = key
                analysis['children'].append(child_analysis)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                child_analysis = self.analyze_json_structure(item, current_level + 1)
                child_analysis['index'] = i
                analysis['children'].append(child_analysis)

        return analysis


# 使用示例
if __name__ == "__main__":
    # 创建工具实例
    utils = JSONFileUtils()

    # 测试文件名提取
    test_paths = [
        "/home/user/documents/file.txt",
        "C:\\Users\\Documents\\image.jpg",
        "relative/path/data.json",
        "file_without_path.ext",
        "/path/with/special@chars#file.name"
    ]

    print("=== 文件名提取测试 ===")
    for path in test_paths:
        print(f"路径: {path}")
        print(f"  文件名(含扩展名): {utils.get_filename(path)}")
        print(f"  文件名(不含扩展名): {utils.get_filename(path, False)}")
        print(f"  清理后文件名: {utils.get_filename_advanced(path, clean_special_chars=True)}")
        print()

    # 测试JSON比较
    print("=== JSON比较测试 ===")
    json1 = {
        "name": "John",
        "age": 30,
        "address": {
            "city": "New York",
            "zipcode": "10001"
        },
        "hobbies": ["reading", "swimming"]
    }

    json2 = {
        "name": "Jane",
        "age": 30,
        "address": {
            "city": "Boston",
            "country": "USA"
        },
        "hobbies": ["reading", "running"]
    }

    differences = utils.compare_json(json1, json2)
    print("差异列表:")
    for diff in differences:
        print(f"  - {diff}")

    print(f"\n比较统计: {utils.get_comparison_stats()}")

    # 测试键计数
    print(f"\n=== 键计数测试 ===")
    key_count = utils.count_keys(json1)
    print(f"JSON1键数量: {key_count}")

    # 测试结构分析
    print(f"\n=== 结构分析测试 ===")
    structure = utils.analyze_json_structure(json1)
    print(f"结构分析: {structure}")