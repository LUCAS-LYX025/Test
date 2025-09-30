import random
import datetime
from typing import List, Union, Dict, Any
import streamlit as st
# # 在页面中直接定义完整的映射数据
PROVINCE_CITY_AREA_CODES = {
    "北京市": {
        "北京市": "010"
    },
    "上海市": {
        "上海市": "021"
    },
    "天津市": {
        "天津市": "022"
    },
    "重庆市": {
        "重庆市": "023"
    },
    "广东省": {
        "广州市": "020",
        "深圳市": "0755",
        "东莞市": "0769",
        "佛山市": "0757",
        "中山市": "0760",
        "珠海市": "0756",
        "惠州市": "0752",
        "江门市": "0750",
        "汕头市": "0754",
        "湛江市": "0759",
        "肇庆市": "0758",
        "茂名市": "0668",
        "韶关市": "0751",
        "潮州市": "0768",
        "揭阳市": "0663",
        "汕尾市": "0660",
        "阳江市": "0662",
        "清远市": "0763",
        "梅州市": "0753",
        "河源市": "0762",
        "云浮市": "0766"
    },
    "江苏省": {
        "南京市": "025",
        "苏州市": "0512",
        "无锡市": "0510",
        "常州市": "0519",
        "徐州市": "0516",
        "南通市": "0513",
        "扬州市": "0514",
        "盐城市": "0515",
        "淮安市": "0517",
        "连云港市": "0518",
        "镇江市": "0511",
        "泰州市": "0523",
        "宿迁市": "0527"
    },
    "浙江省": {
        "杭州市": "0571",
        "宁波市": "0574",
        "温州市": "0577",
        "嘉兴市": "0573",
        "湖州市": "0572",
        "绍兴市": "0575",
        "金华市": "0579",
        "衢州市": "0570",
        "舟山市": "0580",
        "台州市": "0576",
        "丽水市": "0578"
    },
    "山东省": {
        "济南市": "0531",
        "青岛市": "0532",
        "淄博市": "0533",
        "枣庄市": "0632",
        "东营市": "0546",
        "烟台市": "0535",
        "潍坊市": "0536",
        "济宁市": "0537",
        "泰安市": "0538",
        "威海市": "0631",
        "日照市": "0633",
        "临沂市": "0539",
        "德州市": "0534",
        "聊城市": "0635",
        "滨州市": "0543",
        "菏泽市": "0530"
    },
    "四川省": {
        "成都市": "028",
        "绵阳市": "0816",
        "德阳市": "0838",
        "南充市": "0817",
        "宜宾市": "0831",
        "泸州市": "0830",
        "达州市": "0818",
        "乐山市": "0833",
        "内江市": "0832",
        "自贡市": "0813",
        "攀枝花市": "0812",
        "广安市": "0826",
        "遂宁市": "0825",
        "广元市": "0839",
        "眉山市": "0833",
        "资阳市": "0832",
        "雅安市": "0835",
        "巴中市": "0827"
    },
    "湖北省": {
        "武汉市": "027",
        "黄石市": "0714",
        "十堰市": "0719",
        "宜昌市": "0717",
        "襄阳市": "0710",
        "鄂州市": "0711",
        "荆门市": "0724",
        "孝感市": "0712",
        "荆州市": "0716",
        "黄冈市": "0713",
        "咸宁市": "0715",
        "随州市": "0722"
    },
    "湖南省": {
        "长沙市": "0731",
        "株洲市": "0731",
        "湘潭市": "0731",
        "衡阳市": "0734",
        "邵阳市": "0739",
        "岳阳市": "0730",
        "常德市": "0736",
        "张家界市": "0744",
        "益阳市": "0737",
        "郴州市": "0735",
        "永州市": "0746",
        "怀化市": "0745",
        "娄底市": "0738"
    },
    "河南省": {
        "郑州市": "0371",
        "开封市": "0371",
        "洛阳市": "0379",
        "平顶山市": "0375",
        "安阳市": "0372",
        "鹤壁市": "0392",
        "新乡市": "0373",
        "焦作市": "0391",
        "濮阳市": "0393",
        "许昌市": "0374",
        "漯河市": "0395",
        "三门峡市": "0398",
        "南阳市": "0377",
        "商丘市": "0370",
        "信阳市": "0376",
        "周口市": "0394",
        "驻马店市": "0396"
    },
    "河北省": {
        "石家庄市": "0311",
        "唐山市": "0315",
        "秦皇岛市": "0335",
        "邯郸市": "0310",
        "邢台市": "0319",
        "保定市": "0312",
        "张家口市": "0313",
        "承德市": "0314",
        "沧州市": "0317",
        "廊坊市": "0316",
        "衡水市": "0318"
    },
    "辽宁省": {
        "沈阳市": "024",
        "大连市": "0411",
        "鞍山市": "0412",
        "抚顺市": "0413",
        "本溪市": "0414",
        "丹东市": "0415",
        "锦州市": "0416",
        "营口市": "0417",
        "阜新市": "0418",
        "辽阳市": "0419",
        "盘锦市": "0427",
        "铁岭市": "0410",
        "朝阳市": "0421",
        "葫芦岛市": "0429"
    },
    "陕西省": {
        "西安市": "029",
        "铜川市": "0919",
        "宝鸡市": "0917",
        "咸阳市": "0910",
        "渭南市": "0913",
        "延安市": "0911",
        "汉中市": "0916",
        "榆林市": "0912",
        "安康市": "0915",
        "商洛市": "0914"
    },
    "福建省": {
        "福州市": "0591",
        "厦门市": "0592",
        "莆田市": "0594",
        "三明市": "0598",
        "泉州市": "0595",
        "漳州市": "0596",
        "南平市": "0599",
        "龙岩市": "0597",
        "宁德市": "0593"
    },
    "安徽省": {
        "合肥市": "0551",
        "芜湖市": "0553",
        "蚌埠市": "0552",
        "淮南市": "0554",
        "马鞍山市": "0555",
        "淮北市": "0561",
        "铜陵市": "0562",
        "安庆市": "0556",
        "黄山市": "0559",
        "滁州市": "0550",
        "阜阳市": "0558",
        "宿州市": "0557",
        "六安市": "0564",
        "亳州市": "0558",
        "池州市": "0566",
        "宣城市": "0563"
    }
}

# # 确保 PROVINCES 是列表类型
# PROVINCES = list(PROVINCE_CITY_AREA_CODES.keys())


class DataGenerator:
    """数据生成器类，封装了多种数据生成功能"""

    def __init__(self, locale='zh_CN'):
        """初始化数据生成器

        Args:
            locale: 地区设置，默认为中文
        """
        self.locale = locale
        self.faker_available = False
        self.fake = None

        # 尝试导入Faker
        try:
            from faker import Faker
            self.fake = Faker(locale)
            self.faker_available = True
        except ImportError:
            self.faker_available = False
            print("Faker库未安装，部分高级功能将受限。请运行: pip install faker")

    def safe_generate(self, generator_func, *args, **kwargs):
        """安全执行生成函数"""
        try:
            return generator_func(*args, **kwargs)
        except Exception as e:
            st.error(f"生成过程中发生错误：{e}")
            return None

    def format_profile_data(self, profile_dict: Union[Dict, str]) -> str:
        """格式化完整个人信息显示

        Args:
            profile_dict: 个人信息字典或字符串

        Returns:
            格式化后的个人信息字符串
        """
        try:
            # 如果传入的是字符串，尝试转换为字典
            if isinstance(profile_dict, str):
                try:
                    import ast
                    profile_dict = ast.literal_eval(profile_dict)
                except:
                    profile_dict = eval(profile_dict)

            # 提取基本信息
            name = profile_dict.get('name', '未知')
            sex = '女' if profile_dict.get('sex') == 'F' else '男'
            birthdate = profile_dict.get('birthdate', '未知')
            mail = profile_dict.get('mail', '（信息缺失）')
            job = profile_dict.get('job', '（信息缺失）')
            address = profile_dict.get('address', '（信息缺失）')
            company = profile_dict.get('company', '（信息缺失）')
            website = profile_dict.get('website', [])
            username = profile_dict.get('username', '（信息缺失）')

            # 格式化出生日期
            if birthdate != '未知':
                if hasattr(birthdate, 'year'):
                    birthdate = f"{birthdate.year}年{birthdate.month}月{birthdate.day}日"
                else:
                    birthdate = str(birthdate)

            # 格式化地址（简化显示）
            if address != '（信息缺失）':
                address_parts = str(address).split(' ')
                if len(address_parts) > 0:
                    simplified_address = address_parts[0]
                    if '省' in simplified_address:
                        parts = simplified_address.split('省')
                        if len(parts) > 1:
                            city_part = parts[1]
                            if '市' in city_part:
                                city_parts = city_part.split('市')
                                simplified_address = parts[0] + '省' + city_parts[0] + '市'
                    elif '自治区' in simplified_address:
                        parts = simplified_address.split('自治区')
                        if len(parts) > 1:
                            city_part = parts[1]
                            if '市' in city_part:
                                city_parts = city_part.split('市')
                                simplified_address = parts[0] + '自治区' + city_parts[0] + '市'
                    elif '市' in simplified_address:
                        parts = simplified_address.split('市')
                        if len(parts) > 1:
                            simplified_address = parts[0] + '市'
                    address = simplified_address

            # 构建格式化结果
            result = []
            result.append("------------------------------")
            result.append(f"个人信息--{name}")
            result.append(f"姓名： {name}")
            result.append(f"性别： {sex}")
            result.append(f"出生日期： {birthdate}")
            result.append(f"电子邮箱： {mail}")
            result.append("联系电话： （信息缺失）")
            result.append(f"求职意向： {job}")
            result.append(f"所在地区： {address}")
            result.append("")
            result.append("工作经历")
            result.append(f"公司： {company}")
            result.append(f"职位： {job}")
            result.append("其他信息")

            if website:
                website_str = "， ".join(website)
                result.append(f"个人网站/主页： {website_str}")
            else:
                result.append("个人网站/主页： （信息缺失）")

            result.append(f"用户名： {username}")
            result.append("------------------------------")

            return "\n".join(result)

        except Exception as e:
            return f"格式化数据时出错: {str(e)}\n原始数据: {profile_dict}"

    def generate_faker_data(self, category: str, subcategory: str, count: int = 1, **kwargs) -> List[str]:
        """使用Faker生成数据

        Args:
            category: 数据类别（如：人物信息、地址信息等）
            subcategory: 数据子类别（如：随机姓名、随机地址等）
            count: 生成数量
            **kwargs: 其他参数

        Returns:
            生成的数据列表
        """
        if not self.faker_available:
            return ["Faker库未安装，部分高级功能受限。请运行: pip install faker"]

        results = []
        try:
            for i in range(count):
                if category == "人物信息":
                    if subcategory == "随机姓名":
                        results.append(self.fake.name())
                    elif subcategory == "随机姓":
                        results.append(self.fake.last_name())
                    elif subcategory == "随机名":
                        results.append(self.fake.first_name())
                    elif subcategory == "男性姓名":
                        results.append(self.fake.name_male())
                    elif subcategory == "女性姓名":
                        results.append(self.fake.name_female())
                    elif subcategory == "完整个人信息":
                        raw_profile = self.fake.profile()
                        formatted_profile = self.format_profile_data(raw_profile)
                        results.append(formatted_profile)

                elif category == "地址信息":
                    if subcategory == "随机地址":
                        results.append(self.fake.address())
                    elif subcategory == "随机城市":
                        results.append(self.fake.city())
                    elif subcategory == "随机国家":
                        results.append(self.fake.country())
                    elif subcategory == "随机邮编":
                        results.append(self.fake.postcode())
                    elif subcategory == "随机街道":
                        results.append(self.fake.street_address())

                elif category == "网络信息":
                    if subcategory == "随机邮箱":
                        results.append(self.fake.email())
                    elif subcategory == "安全邮箱":
                        results.append(self.fake.safe_email())
                    elif subcategory == "公司邮箱":
                        results.append(self.fake.company_email())
                    elif subcategory == "免费邮箱":
                        results.append(self.fake.free_email())
                    elif subcategory == "随机域名":
                        results.append(self.fake.domain_name())
                    elif subcategory == "随机URL":
                        results.append(self.fake.url())
                    elif subcategory == "随机IP地址":
                        results.append(self.fake.ipv4())
                    elif subcategory == "随机用户代理":
                        results.append(self.fake.user_agent())

                elif category == "公司信息":
                    if subcategory == "随机公司名":
                        results.append(self.fake.company())
                    elif subcategory == "公司后缀":
                        results.append(self.fake.company_suffix())
                    elif subcategory == "职位":
                        results.append(self.fake.job())

                elif category == "金融信息":
                    if subcategory == "信用卡号":
                        results.append(self.fake.credit_card_number())
                    elif subcategory == "信用卡提供商":
                        results.append(self.fake.credit_card_provider())
                    elif subcategory == "信用卡有效期":
                        results.append(self.fake.credit_card_expire())
                    elif subcategory == "货币":
                        results.append(self.fake.currency())

                elif category == "日期时间":
                    if subcategory == "随机日期时间":
                        results.append(str(self.fake.date_time()))
                    elif subcategory == "随机日期":
                        results.append(self.fake.date())
                    elif subcategory == "随机时间":
                        results.append(self.fake.time())
                    elif subcategory == "今年日期":
                        results.append(str(self.fake.date_time_this_year()))
                    elif subcategory == "本月日期":
                        results.append(str(self.fake.date_time_this_month()))

                elif category == "文本内容":
                    if subcategory == "随机单词":
                        results.append(self.fake.word())
                    elif subcategory == "随机句子":
                        results.append(self.fake.sentence())
                    elif subcategory == "随机段落":
                        results.append(self.fake.paragraph())
                    elif subcategory == "随机文本":
                        results.append(self.fake.text(max_nb_chars=kwargs.get('length', 200)))

                elif category == "电话号码":
                    if subcategory == "随机手机号":
                        results.append(self.fake.phone_number())
                    elif subcategory == "号段前缀":
                        results.append(self.fake.phonenumber_prefix())

                elif category == "其他信息":
                    if subcategory == "随机颜色":
                        results.append(self.fake.color_name())
                    elif subcategory == "随机UUID":
                        results.append(self.fake.uuid4())
                    elif subcategory == "随机MD5":
                        results.append(self.fake.md5())
                    elif subcategory == "随机SHA1":
                        results.append(self.fake.sha1())
                    elif subcategory == "随机文件扩展名":
                        results.append(self.fake.file_extension())
                    elif subcategory == "随机MIME类型":
                        results.append(self.fake.mime_type())

        except Exception as e:
            results = [f"生成数据时出错: {str(e)}"]

        return results

    def generate_random_string(self, length: int, chars_type: List[str]) -> str:
        """生成随机字符串

        Args:
            length: 字符串长度
            chars_type: 字符类型列表

        Returns:
            随机字符串
        """
        chars = ""
        if "小写字母" in chars_type: chars += "abcdefghijklmnopqrstuvwxyz"
        if "大写字母" in chars_type: chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if "数字" in chars_type: chars += "0123456789"
        if "特殊字符" in chars_type: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not chars: chars = "abcdefghijklmnopqrstuvwxyz"
        return ''.join(random.choice(chars) for _ in range(length))

    def generate_random_password(self, length: int, options: List[str]) -> str:
        """生成随机密码

        Args:
            length: 密码长度
            options: 密码选项

        Returns:
            随机密码
        """
        if self.faker_available:
            return self.fake.password(
                length=length,
                special_chars="包含特殊字符" in options,
                digits="包含数字" in options,
                upper_case="包含大写字母" in options,
                lower_case="包含小写字母" in options
            )

        # 备用方案
        password = ""
        chars = ""
        if "包含小写字母" in options:
            password += random.choice("abcdefghijklmnopqrstuvwxyz")
            chars += "abcdefghijklmnopqrstuvwxyz"
        if "包含大写字母" in options:
            password += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if "包含数字" in options:
            password += random.choice("0123456789")
            chars += "0123456789"
        if "包含特殊字符" in options:
            password += random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not chars:
            password += random.choice("abcdefghijklmnopqrstuvwxyz")
            chars += "abcdefghijklmnopqrstuvwxyz0123456789"
            password += random.choice("0123456789")

        password += ''.join(random.choice(chars) for _ in range(length - len(password)))
        password_list = list(password)
        random.shuffle(password_list)
        return ''.join(password_list)

    def generate_random_phone_number(self, operator: str) -> str:
        """生成随机电话号码"""
        if self.faker_available:
            return self.fake.phone_number()

        # 备用方案
        mobile_prefixes = ["134", "135", "136", "137", "138", "139", "147", "150", "151", "152", "157", "158", "159",
                           "172", "178", "182", "183", "184", "187", "188", "198", "1703", "1705", "1706"]
        unicom_prefixes = ["130", "131", "132", "145", "155", "156", "166", "171", "175", "176", "185", "186", "1704",
                           "1707", "1708", "1709"]
        telecom_prefixes = ["133", "153", "173", "177", "180", "181", "189", "191", "193", "199", "1700", "1701",
                            "1702"]
        broadcast_prefixes = ["192", "190", "196", "197"]

        if operator == "移动":
            prefix = random.choice(mobile_prefixes)
        elif operator == "联通":
            prefix = random.choice(unicom_prefixes)
        elif operator == "电信":
            prefix = random.choice(telecom_prefixes)
        elif operator == "广电":
            prefix = random.choice(broadcast_prefixes)
        else:
            rand_val = random.random()
            if rand_val < 0.35:
                prefix = random.choice(mobile_prefixes)
            elif rand_val < 0.6:
                prefix = random.choice(unicom_prefixes)
            elif rand_val < 0.85:
                prefix = random.choice(telecom_prefixes)
            else:
                prefix = random.choice(broadcast_prefixes)

        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{suffix}"

    def generate_random_address(self, province: str, city: str, detailed: bool = True) -> str:
        """生成随机地址"""
        if not detailed:
            return f"{province}{city}"

        # 详细地址生成
        streets = ["中山路", "解放路", "人民路", "建设路", "和平路", "新华路", "文化路", "胜利路", "团结路", "友谊路"]
        communities = ["小区", "花园", "大厦", "公寓", "广场", "苑", "居", "湾", "城", "国际"]
        numbers = [str(i) for i in range(1, 201)]

        street = random.choice(streets)
        community = random.choice(communities)
        number = random.choice(numbers)

        return f"{province}{city}{street}{number}号{random.randint(1, 20)}栋{random.randint(1, 30)}单元{random.randint(101, 1500)}室"

    def generate_random_id_card(self, province: str, gender: str, min_age: int, max_age: int) -> str:
        """生成随机身份证号码"""
        # 省份代码
        province_codes = {
            "北京市": "11", "天津市": "12", "河北省": "13", "山西省": "14", "内蒙古自治区": "15",
            "辽宁省": "21", "吉林省": "22", "黑龙江省": "23", "上海市": "31", "江苏省": "32",
            "浙江省": "33", "安徽省": "34", "福建省": "35", "江西省": "36", "山东省": "37",
            "河南省": "41", "湖北省": "42", "湖南省": "43", "广东省": "44", "广西壮族自治区": "45",
            "海南省": "46", "重庆市": "50", "四川省": "51", "贵州省": "52", "云南省": "53",
            "西藏自治区": "54", "陕西省": "61", "甘肃省": "62", "青海省": "63", "宁夏回族自治区": "64",
            "新疆维吾尔自治区": "65"
        }

        # 1. 生成前6位地区码
        province_code = province_codes.get(province, "11")  # 默认北京
        area_code = province_code + ''.join([str(random.randint(0, 9)) for _ in range(4)])

        # 2. 生成出生日期码
        current_year = datetime.datetime.now().year
        birth_year = random.randint(current_year - max_age, current_year - min_age)
        birth_month = random.randint(1, 12)

        # 处理不同月份的天数
        if birth_month in [1, 3, 5, 7, 8, 10, 12]:
            max_day = 31
        elif birth_month in [4, 6, 9, 11]:
            max_day = 30
        else:  # 2月
            if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
                max_day = 29
            else:
                max_day = 28

        birth_day = random.randint(1, max_day)
        birth_date = f"{birth_year:04d}{birth_month:02d}{birth_day:02d}"

        # 3. 生成顺序码
        if gender == "男":
            sequence = random.randint(1, 499) * 2 + 1
        elif gender == "女":
            sequence = random.randint(0, 499) * 2
        else:  # 随机
            sequence = random.randint(0, 999)
        sequence_code = f"{sequence:03d}"

        # 4. 生成前17位
        first_17 = area_code + birth_date + sequence_code

        # 5. 计算校验码
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

        total = sum(int(first_17[i]) * factors[i] for i in range(17))
        check_code = check_codes[total % 11]

        # 6. 生成完整身份证号
        return first_17 + check_code

    def generate_conditional_phone(self, operator: str) -> str:
        """生成手机号码（仅匹配运营商号段）"""
        # 运营商号段定义
        operator_prefixes = {
            "移动": ["134", "135", "136", "137", "138", "139", "147", "150", "151", "152", "157", "158", "159",
                   "172", "178", "182", "183", "184", "187", "188", "198", "1703", "1705", "1706"],
            "联通": ["130", "131", "132", "145", "155", "156", "166", "171", "175", "176", "185", "186", "1704",
                   "1707", "1708", "1709"],
            "电信": ["133", "153", "173", "177", "180", "181", "189", "191", "193", "199", "1700", "1701",
                   "1702"],
            "广电": ["192", "190", "196", "197"]
        }

        # 如果选择"随机"，则从所有运营商中随机选择
        if operator == "随机":
            all_prefixes = []
            for op in operator_prefixes.values():
                all_prefixes.extend(op)
            prefix = random.choice(all_prefixes)
        else:
            prefix = random.choice(operator_prefixes[operator])

        # 生成后8位数字（总长度=11位）
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(11 - len(prefix))])
        return f"{prefix}{suffix}"


    def generate_landline_number(self, operator: str = None, area_code: str = None) -> str:
        """生成座机号码（区号可选）"""
        # 1. 区号生成逻辑
        if not area_code:
            # 从完整的省份城市映射中随机选择一个区号
            all_area_codes = []
            for province, cities in PROVINCE_CITY_AREA_CODES.items():
                for city, code in cities.items():
                    all_area_codes.append(code)

            # 去重并确保有可用的区号
            if all_area_codes:
                area_code = random.choice(all_area_codes)
            else:
                # 备用区号列表
                backup_area_codes = [
                    '010', '021', '022', '023', '020', '024',  # 三位区号
                    '025', '027', '028', '029',  # 省会城市
                    '0512', '0516', '0571', '0574', '0755', '0757'  # 其他常见城市
                ]
                area_code = random.choice(backup_area_codes)

        # 确保区号格式正确（去掉可能的前导0，然后重新加上）
        area_code = str(int(area_code)).zfill(len(area_code))

        # 2. 根据区号确定本地号码位数
        # 三位区号的城市通常是8位本地号码，其他通常是7位
        if len(area_code) == 3 and area_code in ['010', '021', '022', '023', '020', '024', '025', '027', '028', '029']:
            local_length = 8
        else:
            local_length = 7

        # 3. 生成本地号码（符合运营商规则）
        # 第一位：2-9（不能是0或1）
        first_digit = random.randint(2, 9)

        # 剩余位数
        if local_length == 8:
            # 8位号码格式：PQR + ABCD 或 PQ + ABCDE
            remaining_length = 7
            remaining = str(random.randint(0, 10 ** remaining_length - 1)).zfill(remaining_length)
            local_number = str(first_digit) + remaining
        else:
            # 7位号码格式：P + ABCDEF
            remaining_length = 6
            remaining = str(random.randint(0, 10 ** remaining_length - 1)).zfill(remaining_length)
            local_number = str(first_digit) + remaining

        # 4. 格式化输出
        return f"0{area_code}-{local_number}" if not area_code.startswith('0') else f"{area_code}-{local_number}"

    def generate_international_phone(self, country: str) -> str:
        """生成国际手机号码"""
        # 国际号码格式定义（国家代码 + 手机号格式）
        country_formats = {
            # 亚洲
            "日本": {
                "code": "+81",
                "format": ["90-####-####", "80-####-####", "70-####-####"]
            },
            "韩国": {
                "code": "+82",
                "format": ["10-####-####", "16-####-####", "19-####-####"]
            },
            "印度": {
                "code": "+91",
                "format": ["9#########", "8#########", "7#########"]
            },
            "新加坡": {
                "code": "+65",
                "format": ["9### ####", "8### ####", "6### ####"]
            },
            "马来西亚": {
                "code": "+60",
                "format": ["12-### ####", "13-### ####", "16-### ####"]
            },
            "泰国": {
                "code": "+66",
                "format": ["8#-###-####", "9#-###-####", "6#-###-####"]
            },
            "越南": {
                "code": "+84",
                "format": ["9#-####-###", "8#-####-###", "3#-####-###"]
            },
            "菲律宾": {
                "code": "+63",
                "format": ["9##-###-####", "8##-###-####", "2##-###-####"]
            },
            "印度尼西亚": {
                "code": "+62",
                "format": ["8##-####-###", "8##-###-####"]
            },
            "香港": {
                "code": "+852",
                "format": ["5### ####", "6### ####", "9### ####"]
            },
            "台湾": {
                "code": "+886",
                "format": ["9## ### ###", "9########", "4## ### ###"]
            },
            "澳门": {
                "code": "+853",
                "format": ["6### ####", "5### ####"]
            },

            # 欧洲
            "英国": {
                "code": "+44",
                "format": ["7### ######", "7########", "20-####-####"]
            },
            "德国": {
                "code": "+49",
                "format": ["15## #######", "17## #######", "16## #######"]
            },
            "法国": {
                "code": "+33",
                "format": ["6 ## ## ## ##", "7 ## ## ## ##", "1 ## ## ## ##"]
            },
            "意大利": {
                "code": "+39",
                "format": ["3## #######", "3##########"]
            },
            "西班牙": {
                "code": "+34",
                "format": ["6## ### ###", "7## ### ###"]
            },
            "俄罗斯": {
                "code": "+7",
                "format": ["9## ###-##-##", "9##########", "8## ###-##-##"]
            },
            "荷兰": {
                "code": "+31",
                "format": ["6-####-####", "6########"]
            },
            "瑞士": {
                "code": "+41",
                "format": ["7# ### ## ##", "7########"]
            },
            "瑞典": {
                "code": "+46",
                "format": ["7#-### ## ##", "7########"]
            },
            "挪威": {
                "code": "+47",
                "format": ["4## ## ###", "9## ## ###"]
            },
            "丹麦": {
                "code": "+45",
                "format": ["## ## ## ##", "########"]
            },
            "芬兰": {
                "code": "+358",
                "format": ["4# ### ## ##", "4########"]
            },
            "比利时": {
                "code": "+32",
                "format": ["4## ## ## ##", "4########"]
            },
            "奥地利": {
                "code": "+43",
                "format": ["6## #######", "6##########"]
            },
            "爱尔兰": {
                "code": "+353",
                "format": ["8# #######", "8##########"]
            },
            "葡萄牙": {
                "code": "+351",
                "format": ["9## ### ###", "9########"]
            },
            "希腊": {
                "code": "+30",
                "format": ["69## ######", "69########"]
            },
            "波兰": {
                "code": "+48",
                "format": ["### ### ###", "##########"]
            },
            "捷克": {
                "code": "+420",
                "format": ["### ### ###", "##########"]
            },
            "匈牙利": {
                "code": "+36",
                "format": ["20/###-####", "30/###-####"]
            },

            # 北美洲
            "美国": {
                "code": "+1",
                "format": ["###-###-####", "(###) ###-####", "###.###.####"]
            },
            "加拿大": {
                "code": "+1",
                "format": ["###-###-####", "(###) ###-####", "###.###.####"]
            },
            "墨西哥": {
                "code": "+52",
                "format": ["1 ## ## ## ####", "1###########"]
            },

            # 南美洲
            "巴西": {
                "code": "+55",
                "format": ["## 9####-####", "## 8####-####", "## 7####-####"]
            },
            "阿根廷": {
                "code": "+54",
                "format": ["9 ## ####-####", "11 ####-####"]
            },
            "智利": {
                "code": "+56",
                "format": ["9 #### ####", "2 #### ####"]
            },
            "哥伦比亚": {
                "code": "+57",
                "format": ["3## #######", "3##########"]
            },
            "秘鲁": {
                "code": "+51",
                "format": ["9## ### ###", "9########"]
            },

            # 非洲
            "南非": {
                "code": "+27",
                "format": ["## ### ####", "##########"]
            },
            "埃及": {
                "code": "+20",
                "format": ["1## #######", "1##########"]
            },
            "尼日利亚": {
                "code": "+234",
                "format": ["### ### ####", "###########"]
            },
            "肯尼亚": {
                "code": "+254",
                "format": ["7## #######", "7##########"]
            },
            "摩洛哥": {
                "code": "+212",
                "format": ["6-##-##-##-##", "6##########"]
            },

            # 大洋洲
            "澳大利亚": {
                "code": "+61",
                "format": ["4## ### ###", "4########", "2 #### ####"]
            },
            "新西兰": {
                "code": "+64",
                "format": ["2# ### ####", "2##########"]
            },

            # 中东
            "阿联酋": {
                "code": "+971",
                "format": ["5# ### ####", "5##########"]
            },
            "沙特阿拉伯": {
                "code": "+966",
                "format": ["5# ### ####", "5##########"]
            },
            "以色列": {
                "code": "+972",
                "format": ["5#-###-####", "5##########"]
            },
            "土耳其": {
                "code": "+90",
                "format": ["5## ### ####", "5##########"]
            },
            "卡塔尔": {
                "code": "+974",
                "format": ["3### ####", "5### ####", "7### ####"]
            }
        }

        if country not in country_formats:
            # 默认格式
            country_info = {"code": "+1", "format": ["###-###-####"]}
        else:
            country_info = country_formats[country]

        # 选择一种格式
        format_pattern = random.choice(country_info["format"])

        # 生成号码
        phone_number = ""
        for char in format_pattern:
            if char == "#":
                phone_number += str(random.randint(0, 9))
            else:
                phone_number += char

        return f"{country_info['code']} {phone_number}"

    def generate_conditional_address(self, province: str = None, selected_city: str = None,
                                     detailed: bool = True) -> str:
        """根据条件生成地址"""
        if self.faker_available:
            # Faker生成地址
            if detailed:
                address = self.fake.address()
            else:
                # 不生成详细地址，只到城市级别
                address = f"{self.fake.province()} {self.fake.city()}"
        else:
            # 备用方案
            if province == "随机":
                provinces = ["北京市", "上海市", "广州市", "深圳市", "杭州市", "成都市", "武汉市", "南京市", "西安市"]
                province = random.choice(provinces)
                selected_city = province  # 直辖市城市名与省份相同

            if detailed:
                streets = ["中山路", "解放路", "人民路", "建设路", "和平路", "新华路", "文化路", "胜利路", "团结路", "友谊路"]
                communities = ["小区", "花园", "大厦", "公寓", "广场", "苑", "居", "湾", "城", "国际"]
                numbers = [str(i) for i in range(1, 201)]
                street = random.choice(streets)
                community = random.choice(communities)
                number = random.choice(numbers)
                address = f"{province}{selected_city}{street}{number}号{random.randint(1, 20)}栋{random.randint(1, 30)}单元{random.randint(101, 1500)}室"
            else:
                address = f"{province}{selected_city}"

        return address

    def generate_conditional_id_card(self, province: str = None, gender: str = None, min_age: int = 18,
                                     max_age: int = 60) -> str:
        """根据条件生成身份证号码"""
        if self.faker_available:
            # Faker生成身份证
            id_card = self.fake.ssn()

            # 简单验证：检查身份证前两位是否符合省份代码
            province_codes = {
                "北京市": "11", "天津市": "12", "河北省": "13", "山西省": "14", "内蒙古自治区": "15",
                "辽宁省": "21", "吉林省": "22", "黑龙江省": "23", "上海市": "31", "江苏省": "32",
                "浙江省": "33", "安徽省": "34", "福建省": "35", "江西省": "36", "山东省": "37",
                "河南省": "41", "湖北省": "42", "湖南省": "43", "广东省": "44", "广西壮族自治区": "45",
                "海南省": "46", "重庆市": "50", "四川省": "51", "贵州省": "52", "云南省": "53",
                "西藏自治区": "54", "陕西省": "61", "甘肃省": "62", "青海省": "63", "宁夏回族自治区": "64",
                "新疆维吾尔自治区": "65"
            }

            if province and province != "随机" and province in province_codes:
                province_code = province_codes[province]
                # 如果生成的身份证前两位不匹配指定省份，重新生成
                if not id_card.startswith(province_code):
                    return self.generate_random_id_card(province, gender or "随机", min_age, max_age)

            return id_card
        else:
            # 备用方案
            return self.generate_random_id_card(
                province if province != "随机" else "北京市",
                gender or "随机",
                min_age,
                max_age
            )

    def generate_random_email(self, domain_option: str, custom_domain: str, selected_domains: List[str]) -> str:
        """生成随机邮箱"""
        username_length = random.randint(5, 12)
        username = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(username_length))

        if domain_option == "自定义域名":
            domain = custom_domain
        else:
            domain = random.choice(selected_domains) if selected_domains else random.choice(["gmail.com", "yahoo.com"])

        return f"{username}@{domain}"

    def is_faker_available(self) -> bool:
        """检查Faker是否可用"""
        return self.faker_available
