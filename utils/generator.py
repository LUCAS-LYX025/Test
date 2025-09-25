# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:一些生成器方法，生成随机数，手机号，以及连续数字等
@file: generator.py
@time: 2021/9/18 3:16 下午
"""

import random

from faker import Factory

fake = Factory().create('zh_CN')


# ----------------------------------------- 人物 -----------------------------------------#

def random_name():
    """随机姓名"""
    return fake.name()


def random_last_name():
    """随机姓"""
    return fake.last_name()


def random_first_name():
    """随机名"""
    return fake.first_name()


def random_name_male():
    """随机男性姓名"""
    return fake.name_male()


def random_last_name_male():
    """随机男性姓"""
    return fake.last_name_male()


def random_first_name_male():
    """随机男性名"""
    return fake.first_name_male()


def random_name_female():
    """随机女性姓名"""
    return fake.name_female()


# --------------------------------------------------------------------------------------#


# ----------------------------------------- address 地址 -----------------------------------------#
def random_country():
    """随机国家"""
    return fake.country()


def random_city():
    """随机城市"""
    return fake.city()


def random_city_suffix():
    """随机城市的后缀,中文是：市或县"""
    return fake.city_suffix()


def random_address():
    """随机地址"""
    return fake.address()


def random_street_address():
    """随机街道"""
    return fake.street_address()


def random_street_name():
    """随机街道名"""
    return fake.street_name()


def random_postcode():
    """随机邮编"""
    return fake.postcode()


def random_latitude():
    """随机维度"""
    return fake.latitude()


def random_longitude():
    """随机经度"""
    return fake.longitude()


# --------------------------------------------------------------------------------------#


# ----------------------------------------- barcode 条码 -----------------------------------------#
def random_ean8():
    """随机8位码"""
    return fake.ean8()


def random_ean13():
    """随机13位码"""
    return fake.ean13()


def random_ean_n(n):
    """随机n位码,n只能选8或者13"""
    return fake.ean(length=n)


# --------------------------------------------------------------------------------------#


# ----------------------------------------- color 颜色-----------------------------------------#
def random_color():
    """随机颜色"""
    return fake.color()


def random_hex_color():
    """随机16进制表示的颜色"""
    return fake.hex_color()


def random_rgb_css_color():
    """css用的rgb色"""
    return fake.rgb_css_color()


def random_rgb_color():
    """表示rgb色的字符串"""
    return fake.rgb_color()


def random_color_name():
    """随机颜色名字"""
    return fake.color_name()


def random_safe_hex_color():
    """随机安全16进制色"""
    return fake.safe_hex_color()


def random_safe_color_name():
    """随机安全16进制色"""
    return fake.safe_color_name()


# --------------------------------------------------------------------------------------#

# ----------------------------------------- company 公司 -----------------------------------------#
def random_company():
    """随机公司"""
    return fake.company()


def random_company_suffix():
    """随机公司"""
    return fake.company_suffix()


# --------------------------------------------------------------------------------------#

# ----------------------------------------- credit_card 银行信用卡 -----------------------------------------#
def random_credit_card_number():
    """随机卡号"""
    return fake.credit_card_number()


def random_credit_card_provider():
    """随机卡提供者"""
    return fake.credit_card_provider()


def random_credit_card_security_code():
    """随机卡的安全密码"""
    return fake.credit_card_security_code()


def random_credit_card_expire():
    """随机卡的有效期"""
    return fake.credit_card_expire()


def random_credit_card_full():
    """随机卡完整信息"""
    return fake.credit_card_full()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- currency 货币 -----------------------------------------#
def random_currency():
    """随机货币"""
    return fake.currency()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- date_time 时间日期-----------------------------------------#
def random_date_time():
    """随机时间日期类：日期、年、月等"""
    return fake.date_time()


def random_iso8601():
    """随机货币"""
    return fake.iso8601()


def random_date_time_this_month():
    """本月的某个日期"""
    return fake.date_time_this_month()


def random_date_time_this_year():
    """本年的某个日期"""
    return fake.date_time_this_year()


def random_date_time_this_decade():
    """本年代内的一个日期"""
    return fake.date_time_this_decade()


def random_date_time_this_century():
    """本世纪的一个日期"""
    return fake.date_time_this_century()


def random_date_time_between():
    """两个时间间的一个随机时间"""
    return fake.date_time_between(start_date="-30y", end_date="now", tzinfo=None)


def random_timezone():
    """随机时区"""
    return fake.timezone()


def random_time():
    """随机时间，格式可自定义"""
    return fake.time(pattern="%H:%M:%S")


def random_am_pm():
    """随机上午下午"""
    return fake.am_pm()


def random_month():
    """随机月份"""
    return fake.month()


def random_month_name():
    """随机月份名字"""
    return fake.month_name()


def random_year():
    """随机年"""
    return fake.year()


def random_day_of_week():
    """随机星期几"""
    return fake.day_of_week()


def random_day_of_month():
    """随机月中某一天"""
    return fake.day_of_month()


def random_time_delta():
    """随机时间延迟"""
    return fake.day_of_month()


def random_date_object():
    """随机日期对象"""
    return fake.date_object()


def random_time_object():
    """随机时间对象"""
    return fake.time_object()


def random_unix_time():
    """随机unix时间（时间戳"""
    return fake.unix_time()


def random_date():
    """随机日期（可自定义格式）"""
    return fake.date(pattern="%Y-%m-%d")


def random_date_time_ad():
    """公元后随机日期"""
    return fake.date_time_ad()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- file 文件 -----------------------------------------#
def assign_file_name():
    """文件名（指定文件类型和后缀名）"""
    return fake.file_name(category="image", extension="png")


def random_file_name():
    """随机生成各类型文件"""
    return fake.file_name()


def random_file_extension():
    """随机文件后缀"""
    return fake.file_extension()


def random_mime_type():
    """mime_type"""
    return fake.mime_type()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- internet 互联网 -----------------------------------------#
def random_ipv4():
    """随机IPV4地址"""
    return fake.ipv4()


def random_ipv6():
    """随机IPV6地址"""
    return fake.ipv6()


def random_uri_path():
    """随机uri路径"""
    return fake.uri_path()


def random_uri_extension():
    """随机uri扩展名"""
    return fake.uri_extension()


def random_uri():
    """随机uri"""
    return fake.uri()


def random_url():
    """随机url"""
    return fake.url()


def random_image_url():
    """随机图片url"""
    return fake.image_url()


def random_domain_word():
    """随机域名主体"""
    return fake.domain_word()


def random_domain_name():
    """随机域名"""
    return fake.domain_name()


def random_tld():
    """随机域名后缀"""
    return fake.tld()


def random_user_name():
    """随机用户名"""
    return fake.user_name()


def random_user_agent():
    """随机UA"""
    return fake.user_agent()


def random_mac_address():
    """随机MAC地址"""
    return fake.mac_address()


def random_safe_email():
    """随机安全邮箱"""
    return fake.safe_email()


def random_free_email():
    """随机免费邮箱"""
    return fake.free_email()


def random_company_email():
    """随机公司邮箱"""
    return fake.company_email()


def random_email():
    """随机email"""
    return fake.email()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- job 工作 -----------------------------------------#
def random_job():
    """随机工作"""
    return fake.job()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- lorem 乱数假文 -----------------------------------------#
def assign_text(n):
    """随机生成一篇指定字数的文章"""
    return fake.text(max_nb_chars=n)


def random_word():
    """随机单词"""
    return fake.word()


def random_words(n):
    """随机生成指定的几个字"""
    return fake.words(nb=n)


def random_sentence(n):
    """随机生成指定的几个字的句子"""
    return fake.sentence(nb_words=n, variable_nb_words=True)


def random_sentences(n):
    """随机生成几个句子"""
    return fake.sentences(nb=n)


def random_paragraph(n):
    """随机生成一段文字(字符串)"""
    return fake.paragraph(nb_sentences=n, variable_nb_sentences=True)


def random_paragraphs(n):
    """随机生成成几段文字(列表)"""
    return fake.paragraphs(nb=n)


# --------------------------------------------------------------------------------------#
# ----------------------------------------- misc 杂项 -----------------------------------------#
def random_binary(n):
    """随机二进制字符串(可指定长度)"""
    return fake.binary(length=n)


def random_language_code():
    """随机语言代码"""
    return fake.language_code()


def random_md5():
    """随机md5，16进制字符串"""
    return fake.md5(raw_output=False)


def random_sha1():
    """随机sha1，16进制字符串"""
    return fake.sha1(raw_output=False)


def random_sha256():
    """随机sha1，16进制字符串"""
    return fake.sha256(raw_output=False)


def random_boolean(n):
    """随机真假值(得到True的几率是n%)"""
    return fake.boolean(chance_of_getting_true=n)


def random_null_boolean():
    """随机真假值和null"""
    return fake.null_boolean()


def random_password(n):
    """随机密码（可指定密码长度）"""
    return fake.password(length=n, special_chars=True, digits=True, upper_case=True, lower_case=True)


def random_locale():
    """随机本地代码"""
    return fake.locale()


def random_uuid4():
    """随机uuid"""
    return fake.uuid4()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- phone_number 电话号码 -----------------------------------------#
def random_phone_number():
    """随机手机号"""
    return fake.phone_number()


def random_phonenumber_prefix():
    """运营商号段，手机号码前三位"""
    return fake.phonenumber_prefix()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- python python数据 -----------------------------------------#
def random_pyint():
    """随机int"""
    return fake.pyint()


def random_pyfloat():
    """随机浮点数"""
    return fake.pyfloat(left_digits=None, right_digits=None, positive=False)


def random_pydecimal():
    """随高精度数机"""
    return fake.pydecimal(left_digits=None, right_digits=None, positive=False)


def random_pystr(n):
    """随机字符串（可指定长度）"""
    return fake.pystr(min_chars=None, max_chars=n)


def random_str(min_chars, max_chars):
    """长度在最大值与最小值之间的随机字符串"""
    return fake.pystr(min_chars=min_chars, max_chars=max_chars)


def random_pybool():
    """随机bool值"""
    return fake.pybool()


def random_pyiterable(n):
    """随机iterable"""
    return fake.pyiterable(nb_elements=n, variable_nb_elements=True)


def random_pylist(n):
    """随机生成一个list"""
    return fake.pylist(nb_elements=n, variable_nb_elements=True)


def random_pydict(n):
    """随机字典"""
    return fake.pydict(nb_elements=n, variable_nb_elements=True)


def random_pyset(n):
    """随机set"""
    return fake.pyset(nb_elements=n, variable_nb_elements=True)


def random_pytuple(n):
    """随机bool值"""
    return fake.pytuple(nb_elements=n, variable_nb_elements=True)


def random_pystruct():
    """随机生成3个有10个元素的python数据结构"""
    return fake.pystruct()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- profile 人物描述信息 -----------------------------------------#
def random_profile():
    """随机人物描述信息：姓名、性别、地址、公司等"""
    return fake.profile()


def random_simple_profile(sex):
    """随机人物精简信息（可指定性别）sex的值为"M"或"F" """
    return fake.simple_profile(sex=sex)


# --------------------------------------------------------------------------------------#

# ----------------------------------------- ssn 社会安全码(身份证) -----------------------------------------#
def random_ssn():
    """随机社会安全码(身份证号码)"""
    return fake.ssn()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- 平台信息伪造 -----------------------------------------#
def random_linux_platform_token():
    """X11; Linux i68"""
    return fake.linux_platform_token()


def random_linux_processor():
    """i686"""
    return fake.linux_processor()


def random_windows_platform_token():
    """Windows CE"""
    return fake.windows_platform_token()


def random_mac_platform_token():
    """Macintosh; Intel Mac OS X 10_7_4"""
    return fake.mac_platform_token()


def random_mac_processor():
    """PPC"""
    return fake.mac_processor()


# --------------------------------------------------------------------------------------#
# ----------------------------------------- 浏览器伪造 -----------------------------------------#

def random_internet_explorer():
    """IE浏览器"""
    return fake.internet_explorer()


def random_opera():
    """opera浏览器"""
    return fake.opera()


def random_firefox():
    """firefox浏览器"""
    return fake.firefox()


def random_safari():
    """safari浏览器"""
    return fake.safari()


def random_chrome():
    """chrome浏览器"""
    return fake.chrome()


# --------------------------------------------------------------------------------------#

# ----------------------------------------- 自定义数据生成器 -----------------------------------------#
def factory_generate_ids(starting_id=1, increment=1):
    """ 返回一个生成器函数，调用这个函数产生生成器，从starting_id开始，步长为increment。 """

    def generate_started_ids():
        val = starting_id
        local_increment = increment
        while True:
            yield val
            val += local_increment

    return generate_started_ids


def factory_choice_generator(values):
    """ 返回一个生成器函数，调用这个函数产生生成器，从给定的list中随机取一项。 """

    def choice_generator():
        my_list = list(values)
        # rand = random.Random()
        while True:
            yield random.choice(my_list)

    return choice_generator


# --------------------------------------------------------------------------------------#

if __name__ == '__main__':
    print("===================== address 地址 =========================")
    print(random_country())
    print(random_city())
    print(random_city_suffix())
    print(random_address())
    print(random_street_address())
    print(random_street_name())
    print(random_postcode())
    print(random_latitude())
    print(random_longitude())
    print("===================== person 人物 =========================")
    print(random_name())
    print(random_last_name())
    print(random_first_name())
    print(random_name_male())
    print(random_last_name_male())
    print(random_first_name_male())
    print(random_name_female())
    print("===================== barcode 条码 =========================")
    print(random_ean8())
    print(random_ean13())
    print(random_ean_n(8))
    print("===================== color 颜色 =========================")
    print(random_color())
    print(random_hex_color())
    print(random_rgb_css_color())
    print(random_rgb_color())
    print(random_color_name())
    print(random_safe_hex_color())
    print(random_safe_color_name())
    print("===================== company 公司 =========================")
    print(random_company())
    print(random_company_suffix())
    print("===================== credit_card 银行信用卡 =========================")
    print(random_credit_card_number())
    print(random_credit_card_provider())
    print(random_credit_card_security_code())
    print(random_credit_card_expire())
    print(random_credit_card_full())
    print("===================== currency 货币 =========================")
    print(random_currency())
    print("===================== date_time 时间日期 =========================")
    print(random_date_time())
    print(random_iso8601())
    print(random_date_time_this_month())
    print(random_date_time_this_year())
    print(random_date_time_this_decade())
    print(random_date_time_this_century())
    print(random_date_time_between())
    print(random_timezone())
    print(random_time())
    print(random_am_pm())
    print(random_month())
    print(random_month_name())
    print(random_year())
    print(random_day_of_week())
    print(random_day_of_month())
    print(random_time_delta())
    print(random_date_object())
    print(random_time_object())
    print(random_unix_time())
    print(random_date())
    print(random_date_time_ad())
    print("===================== file 文件 =========================")
    print(assign_file_name())
    print(random_file_name())
    print(random_file_extension())
    print(random_mime_type())
    print("===================== internet 互联网 =========================")
    print(random_ipv4())
    print(random_ipv6())
    print(random_uri_path())
    print(random_uri_extension())
    print(random_uri())
    print(random_url())
    print(random_image_url())
    print(random_domain_word())
    print(random_domain_name())
    print(random_tld())
    print(random_user_name())
    print(random_user_agent())
    print(random_mac_address())
    print(random_safe_email())
    print(random_free_email())
    print(random_company_email())
    print(random_email())
    print("===================== job 工作 =========================")
    print(random_job())
    print("===================== lorem 乱数假文 =========================")
    print(assign_text(500))
    print("+++++++++++++")
    print(random_word())
    print(random_words(5))
    print(random_sentence(6))
    print(random_sentences(3))
    print(random_paragraph(3))
    print(random_paragraphs(2))
    print("===================== misc 杂项 =========================")
    print(random_binary(10))
    print(random_language_code())
    print(random_md5())
    print(random_sha1())
    print(random_sha256())
    print(random_boolean(40))
    print(random_null_boolean())
    print(random_password(10))
    print(random_locale())
    print(random_uuid4())
    print("===================== phone_number 电话号码 =========================")
    print(random_phone_number())
    print(random_phonenumber_prefix())
    print("===================== python python数据 =========================")
    print(random_pyint())
    print(random_pyfloat())
    print(random_pydecimal())
    print(random_pystr(20))
    print(random_str(6, 8))
    print(random_pybool())
    print(random_pyiterable(10))
    print(random_pylist(10))
    print(random_pydict(10))
    print(random_pyset(10))
    print(random_pytuple(10))
    print(random_pystruct())
    print("===================== profile 人物描述信息 =========================")
    print(random_profile())
    print(random_simple_profile("M"))
    print("===================== ssn 社会安全码(身份证) =========================")
    print(random_ssn())
    print("===================== 平台信息伪造 =========================")
    print(random_linux_platform_token())
    print(random_linux_processor())
    print(random_windows_platform_token())
    print(random_mac_platform_token())
    print(random_mac_processor())
    print("===================== 浏览器伪造 =========================")
    print(random_internet_explorer())
    print(random_opera())
    print(random_firefox())
    print(random_safari())
    print(random_chrome())
    print("===================== 自定义数据生成器 =========================")
    id_gen = factory_generate_ids(starting_id=0, increment=2)()
    for i in range(5):
        print(next(id_gen))

    choices = ['John', 'Sam', 'Lily', 'Rose']
    choice_gen = factory_choice_generator(choices)()
    for i in range(5):
        print(next(choice_gen))
