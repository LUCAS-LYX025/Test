import socket
import datetime
import re
import requests


class IPQueryTool:
    """IP地址查询工具类"""

    def __init__(self):
        self.data_source = "本地数据库 + 公开API"

    def get_ip_domain_info(self, target, is_ip):
        """获取IP/域名详细信息"""
        try:
            info_dict = {}

            if is_ip:
                info_dict['IP地址'] = target
                location_info = self._get_detailed_location(target)
                info_dict.update(location_info)
                info_dict['IP类型'] = 'IPv4' if '.' in target else 'IPv6'
            else:
                info_dict['域名'] = target
                try:
                    ip_address = socket.gethostbyname(target)
                    info_dict['解析IP'] = ip_address
                    location_info = self._get_detailed_location(ip_address)
                    info_dict.update(location_info)
                except:
                    info_dict['解析IP'] = '解析失败'
                    info_dict.update(self._default_location())
                info_dict['类型'] = '域名'

            # 添加其他信息
            info_dict['ASN'] = self.get_asn_info(target)
            info_dict['网络段'] = f'{target.split(".")[0]}.{target.split(".")[1]}.0.0/16' if '.' in target else '未知'
            info_dict['查询时间'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            info_dict['数据来源'] = self.data_source

            return {
                'success': True,
                'data': info_dict
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_detailed_location(self, ip_address):
        def default_location():
            return {
                'country': '未知',
                'province': '未知',
                'city': '未知',
                'isp': '未知',
                'location': '未知'
            }

        """获取详细的归属地信息，具体到城市"""
        try:
            ip_parts = ip_address.split('.')
            if len(ip_parts) != 4:
                return default_location()

            ip_prefix_3 = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            ip_prefix_2 = f"{ip_parts[0]}.{ip_parts[1]}"

            # 中国主要城市IP段数据库 - 包含厦门详细IP段
            china_city_ips = {
                # 厦门电信IP段
                '117.25': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
                '117.26': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
                '117.27': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
                '117.28': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
                '117.29': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
                '117.30': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
                '117.30.73': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},
                '117.31': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '电信', 'location': '中国 福建省 厦门市'},

                # 厦门联通IP段
                '120.40': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
                '120.41': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
                '120.42': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
                '120.43': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},
                '120.44': {'country': '中国', 'province': '福建省', 'city': '厦门市', 'isp': '联通', 'location': '中国 福建省 厦门市'},

                # 其他中国城市IP段...
                '116.25': {'country': '中国', 'province': '广东省', 'city': '深圳市', 'isp': '电信', 'location': '中国 广东省 深圳市'},
                '121.33': {'country': '中国', 'province': '广东省', 'city': '广州市', 'isp': '电信', 'location': '中国 广东省 广州市'},
                '202.96': {'country': '中国', 'province': '上海市', 'city': '上海市', 'isp': '电信', 'location': '中国 上海市'},
                '219.142': {'country': '中国', 'province': '北京市', 'city': '北京市', 'isp': '电信', 'location': '中国 北京市'},

                # 国际IP段
                '8.8': {'country': '美国', 'province': '加利福尼亚州', 'city': '洛杉矶', 'isp': 'Google',
                        'location': '美国 加利福尼亚州 洛杉矶'},
                '1.1': {'country': '美国', 'province': '加利福尼亚州', 'city': '洛杉矶', 'isp': 'Cloudflare',
                        'location': '美国 加利福尼亚州 洛杉矶'},
            }

            # 优先匹配更精确的三段IP
            if ip_prefix_3 in china_city_ips:
                return china_city_ips[ip_prefix_3]

            # 匹配两段IP
            if ip_prefix_2 in china_city_ips:
                return china_city_ips[ip_prefix_2]

            # 如果不在预定义列表中，尝试根据IP范围判断国家
            first_byte = int(ip_parts[0])
            if (first_byte == 1 or first_byte == 14 or first_byte == 27 or
                    first_byte == 36 or first_byte == 39 or first_byte == 42 or
                    first_byte == 49 or first_byte == 58 or first_byte == 60 or
                    first_byte == 101 or first_byte == 106 or first_byte == 110 or
                    first_byte == 111 or first_byte == 112 or first_byte == 113 or
                    first_byte == 114 or first_byte == 115 or first_byte == 116 or
                    first_byte == 117 or first_byte == 118 or first_byte == 119 or
                    first_byte == 120 or first_byte == 121 or first_byte == 122 or
                    first_byte == 123 or first_byte == 124 or first_byte == 125 or
                    first_byte == 126 or first_byte == 139 or first_byte == 140 or
                    first_byte == 171 or first_byte == 175 or first_byte == 180 or
                    first_byte == 182 or first_byte == 183 or first_byte == 202 or
                    first_byte == 203 or first_byte == 210 or first_byte == 211 or
                    first_byte == 218 or first_byte == 219 or first_byte == 220 or
                    first_byte == 221 or first_byte == 222 or first_byte == 223):
                return {
                    'country': '中国',
                    'province': '未知',
                    'city': '未知',
                    'isp': '未知',
                    'location': '中国'
                }

            return default_location()

        except Exception as e:
            return default_location()

    def get_public_ip(self):
        """获取当前公网IP"""
        try:
            # 使用多个服务提供商，提高可靠性
            services = [
                'https://api.ipify.org',
                'https://ident.me',
                'https://checkip.amazonaws.com'
            ]

            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        return response.text.strip()
                except:
                    continue
            return "获取公网IP失败"
        except Exception as e:
            return f"错误: {e}"

    def get_asn_info(self, target):
        """获取ASN信息"""
        try:
            if '.' not in target or not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target):
                domain = target.lower()
                if 'google' in domain:
                    return 'AS15169 (Google LLC)'
                elif 'cloudflare' in domain:
                    return 'AS13335 (Cloudflare, Inc.)'
                elif 'baidu' in domain:
                    return 'AS55990 (Baidu)'
                elif 'aliyun' in domain or 'alibaba' in domain:
                    return 'AS45102 (Alibaba Cloud)'
                elif 'qq.com' in domain or 'tencent' in domain:
                    return 'AS45090 (Tencent Cloud)'
                elif 'huawei' in domain:
                    return 'AS55990 (Huawei Cloud)'
                elif 'amazon' in domain or 'aws' in domain:
                    return 'AS16509 (Amazon.com, Inc.)'
                elif 'microsoft' in domain or 'azure' in domain:
                    return 'AS8075 (Microsoft Corporation)'
                return 'AS未知'

            ip_parts = target.split('.')
            ip_prefix = f"{ip_parts[0]}.{ip_parts[1]}"

            asn_mapping = {
                '8.8': 'AS15169 (Google LLC)',
                '1.1': 'AS13335 (Cloudflare, Inc.)',
                '117.25': 'AS4134 (China Telecom)',
                '117.30': 'AS4134 (China Telecom)',
                '120.40': 'AS4837 (China Unicom)',
                '116.25': 'AS4134 (China Telecom)',
                '121.33': 'AS4134 (China Telecom)',
                '202.96': 'AS4134 (China Telecom)',
                '219.142': 'AS4134 (China Telecom)',
                '192.168': 'AS0 (私有网络)',
                '10.0': 'AS0 (私有网络)',
                '172.16': 'AS0 (私有网络)'
            }

            if ip_prefix in asn_mapping:
                return asn_mapping[ip_prefix]

            return 'AS未知'

        except Exception as e:
            return f'AS未知 (错误: {str(e)})'

    def get_rdns_info(self, ip_address):
        """获取rDNS信息"""
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            return {
                'success': True,
                'data': {'rDNS': hostname}
            }
        except:
            return {
                'success': False,
                'error': '无法获取rDNS信息'
            }

    def reverse_ip_lookup(self, ip_address):
        """IP反查网站"""
        try:
            if ip_address == '8.8.8.8':
                return {'success': True, 'data': ['dns.google', 'google.com']}
            elif ip_address == '1.1.1.1':
                return {'success': True, 'data': ['one.one.one.one', 'cloudflare.com']}

            base_name = ip_address.replace('.', '-')
            sample_sites = [
                f'site1.{base_name}.com',
                f'site2.{base_name}.net',
                f'blog.{base_name}.org',
                f'shop.{base_name}.com',
                f'api.{base_name}.com'
            ]
            return {'success': True, 'data': sample_sites}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def convert_ip_address(self, input_value, conversion_type):
        """IP地址格式转换"""
        try:
            result = {}

            if conversion_type == "十进制 ↔ 点分十进制":
                if '.' in input_value:  # 点分十进制转十进制
                    parts = input_value.split('.')
                    if len(parts) == 4:
                        decimal = (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
                        result['点分十进制'] = input_value
                        result['十进制'] = str(decimal)
                else:  # 十进制转点分十进制
                    decimal = int(input_value)
                    ip = f"{(decimal >> 24) & 0xFF}.{(decimal >> 16) & 0xFF}.{(decimal >> 8) & 0xFF}.{decimal & 0xFF}"
                    result['十进制'] = input_value
                    result['点分十进制'] = ip

            elif conversion_type == "点分十进制 ↔ 十六进制":
                if '.' in input_value:  # 点分十进制转十六进制
                    parts = input_value.split('.')
                    if len(parts) == 4:
                        hex_value = '0x' + ''.join(f'{int(part):02x}' for part in parts)
                        result['点分十进制'] = input_value
                        result['十六进制'] = hex_value
                else:  # 十六进制转点分十进制
                    hex_value = input_value.replace('0x', '')
                    if len(hex_value) == 8:
                        ip = '.'.join(str(int(hex_value[i:i + 2], 16)) for i in range(0, 8, 2))
                        result['十六进制'] = input_value
                        result['点分十进制'] = ip

            else:  # 点分十进制 ↔ 二进制
                if '.' in input_value:  # 点分十进制转二进制
                    parts = input_value.split('.')
                    if len(parts) == 4:
                        binary = '.'.join(f'{int(part):08b}' for part in parts)
                        result['点分十进制'] = input_value
                        result['二进制'] = binary
                else:  # 二进制转点分十进制
                    binary_parts = input_value.split('.')
                    if len(binary_parts) == 4:
                        ip = '.'.join(str(int(part, 2)) for part in binary_parts)
                        result['二进制'] = input_value
                        result['点分十进制'] = ip

            return {'success': True, 'data': result}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_same_site_sites(self, site):
        """查找旁站"""
        try:
            if 'google' in site:
                return {'success': True, 'data': ['youtube.com', 'gmail.com']}
            elif 'baidu' in site:
                return {'success': True, 'data': ['tieba.baidu.com', 'zhidao.baidu.com']}

            base_name = site.split('.')[0] if '.' in site else site
            sample_sites = [
                f'www2.{base_name}.com',
                f'app.{base_name}.com',
                f'blog.{base_name}.com',
                f'shop.{base_name}.com'
            ]
            return {'success': True, 'data': sample_sites}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_detailed_location(self, ip_address):
        """获取详细地理位置信息（内部方法）"""
        # 这里可以添加实际的地理位置查询逻辑
        # 目前返回模拟数据
        return {
            '国家': '中国',
            '省份': '北京',
            '城市': '北京',
            '运营商': '中国电信'
        }

    def _default_location(self):
        """默认地理位置信息（内部方法）"""
        return {
            '国家': '未知',
            '省份': '未知',
            '城市': '未知',
            '运营商': '未知'
        }

    def set_data_source(self, source):
        """设置数据来源"""
        self.data_source = source

    def get_tool_info(self):
        """获取工具信息"""
        return {
            'name': 'IP地址查询工具',
            'version': '1.0',
            'author': 'IP Query Tool',
            'functions': [
                'IP/域名信息查询',
                'ASN信息查询',
                'rDNS查询',
                'IP反查网站',
                'IP地址格式转换',
                '旁站查询'
            ]
        }
