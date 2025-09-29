"""
基础数据常量模块
用于存储省份、城市、国家、分类等基础数据
"""

# 省份和直辖市数据
PROVINCES = {
    "北京市": ["北京市"],
    "天津市": ["天津市"],
    "上海市": ["上海市"],
    "重庆市": ["重庆市"],
    "河北省": ["石家庄市", "唐山市", "秦皇岛市", "邯郸市", "邢台市", "保定市", "张家口市", "承德市", "沧州市", "廊坊市", "衡水市"],
    "山西省": ["太原市", "大同市", "阳泉市", "长治市", "晋城市", "朔州市", "晋中市", "运城市", "忻州市", "临汾市", "吕梁市"],
    "内蒙古自治区": ["呼和浩特市", "包头市", "乌海市", "赤峰市", "通辽市", "鄂尔多斯市", "呼伦贝尔市", "巴彦淖尔市", "乌兰察布市", "兴安盟", "锡林郭勒盟", "阿拉善盟"],
    "辽宁省": ["沈阳市", "大连市", "鞍山市", "抚顺市", "本溪市", "丹东市", "锦州市", "营口市", "阜新市", "辽阳市", "盘锦市", "铁岭市", "朝阳市", "葫芦岛市"],
    "吉林省": ["长春市", "吉林市", "四平市", "辽源市", "通化市", "白山市", "松原市", "白城市", "延边朝鲜族自治州"],
    "黑龙江省": ["哈尔滨市", "齐齐哈尔市", "鸡西市", "鹤岗市", "双鸭山市", "大庆市", "伊春市", "佳木斯市", "七台河市", "牡丹江市", "黑河市", "绥化市", "大兴安岭地区"],
    "江苏省": ["南京市", "无锡市", "徐州市", "常州市", "苏州市", "南通市", "连云港市", "淮安市", "盐城市", "扬州市", "镇江市", "泰州市", "宿迁市"],
    "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市", "湖州市", "绍兴市", "金华市", "衢州市", "舟山市", "台州市", "丽水市"],
    "安徽省": ["合肥市", "芜湖市", "蚌埠市", "淮南市", "马鞍山市", "淮北市", "铜陵市", "安庆市", "黄山市", "滁州市", "阜阳市", "宿州市", "六安市", "亳州市", "池州市",
            "宣城市"],
    "福建省": ["福州市", "厦门市", "莆田市", "三明市", "泉州市", "漳州市", "南平市", "龙岩市", "宁德市"],
    "江西省": ["南昌市", "景德镇市", "萍乡市", "九江市", "新余市", "鹰潭市", "赣州市", "吉安市", "宜春市", "抚州市", "上饶市"],
    "山东省": ["济南市", "青岛市", "淄博市", "枣庄市", "东营市", "烟台市", "潍坊市", "济宁市", "泰安市", "威海市", "日照市", "临沂市", "德州市", "聊城市", "滨州市",
            "菏泽市"],
    "河南省": ["郑州市", "开封市", "洛阳市", "平顶山市", "安阳市", "鹤壁市", "新乡市", "焦作市", "濮阳市", "许昌市", "漯河市", "三门峡市", "南阳市", "商丘市", "信阳市",
            "周口市", "驻马店市"],
    "湖北省": ["武汉市", "黄石市", "十堰市", "宜昌市", "襄阳市", "鄂州市", "荆门市", "孝感市", "荆州市", "黄冈市", "咸宁市", "随州市", "恩施土家族苗族自治州"],
    "湖南省": ["长沙市", "株洲市", "湘潭市", "衡阳市", "邵阳市", "岳阳市", "常德市", "张家界市", "益阳市", "郴州市", "永州市", "怀化市", "娄底市", "湘西土家族苗族自治州"],
    "广东省": ["广州市", "深圳市", "珠海市", "汕头市", "佛山市", "韶关市", "湛江市", "肇庆市", "江门市", "茂名市", "惠州市", "梅州市", "汕尾市", "河源市", "阳江市",
            "清远市", "东莞市", "中山市", "潮州市", "揭阳市", "云浮市"],
    "广西壮族自治区": ["南宁市", "柳州市", "桂林市", "梧州市", "北海市", "防城港市", "钦州市", "贵港市", "玉林市", "百色市", "贺州市", "河池市", "来宾市", "崇左市"],
    "海南省": ["海口市", "三亚市", "三沙市", "儋州市"],
    "四川省": ["成都市", "自贡市", "攀枝花市", "泸州市", "德阳市", "绵阳市", "广元市", "遂宁市", "内江市", "乐山市", "南充市", "眉山市", "宜宾市", "广安市", "达州市",
            "雅安市", "巴中市", "资阳市", "阿坝藏族羌族自治州", "甘孜藏族自治州", "凉山彝族自治州"],
    "贵州省": ["贵阳市", "六盘水市", "遵义市", "安顺市", "毕节市", "铜仁市", "黔西南布依族苗族自治州", "黔东南苗族侗族自治州", "黔南布依族苗族自治州"],
    "云南省": ["昆明市", "曲靖市", "玉溪市", "保山市", "昭通市", "丽江市", "普洱市", "临沧市", "楚雄彝族自治州", "红河哈尼族彝族自治州", "文山壮族苗族自治州", "西双版纳傣族自治州",
            "大理白族自治州", "德宏傣族景颇族自治州", "怒江傈僳族自治州", "迪庆藏族自治州"],
    "西藏自治区": ["拉萨市", "日喀则市", "昌都市", "林芝市", "山南市", "那曲市", "阿里地区"],
    "陕西省": ["西安市", "铜川市", "宝鸡市", "咸阳市", "渭南市", "延安市", "汉中市", "榆林市", "安康市", "商洛市"],
    "甘肃省": ["兰州市", "嘉峪关市", "金昌市", "白银市", "天水市", "武威市", "张掖市", "平凉市", "酒泉市", "庆阳市", "定西市", "陇南市", "临夏回族自治州", "甘南藏族自治州"],
    "青海省": ["西宁市", "海东市", "海北藏族自治州", "黄南藏族自治州", "海南藏族自治州", "果洛藏族自治州", "玉树藏族自治州", "海西蒙古族藏族自治州"],
    "宁夏回族自治区": ["银川市", "石嘴山市", "吴忠市", "固原市", "中卫市"],
    "新疆维吾尔自治区": ["乌鲁木齐市", "克拉玛依市", "吐鲁番市", "哈密市", "昌吉回族自治州", "博尔塔拉蒙古自治州", "巴音郭楞蒙古自治州", "阿克苏地区", "克孜勒苏柯尔克孜自治州", "喀什地区",
                 "和田地区", "伊犁哈萨克自治州", "塔城地区", "阿勒泰地区"],
    "台湾省": ["台北市", "新北市", "桃园市", "台中市", "台南市", "高雄市"],
    "香港特别行政区": ["香港岛", "九龙", "新界"],
    "澳门特别行政区": ["澳门半岛", "氹仔", "路环"],
    "随机": ["随机"]
}

# 国家列表
COUNTRIES = [
    "日本", "韩国", "印度", "新加坡", "马来西亚", "泰国", "越南", "菲律宾", "印度尼西亚",
    "香港", "台湾", "澳门", "英国", "德国", "法国", "意大利", "西班牙", "俄罗斯", "荷兰",
    "瑞士", "瑞典", "挪威", "丹麦", "芬兰", "比利时", "奥地利", "爱尔兰", "葡萄牙", "希腊",
    "波兰", "捷克", "匈牙利", "美国", "加拿大", "墨西哥", "巴西", "阿根廷", "智利", "哥伦比亚",
    "秘鲁", "南非", "埃及", "尼日利亚", "肯尼亚", "摩洛哥", "澳大利亚", "新西兰", "阿联酋",
    "沙特阿拉伯", "以色列", "土耳其", "卡塔尔"
]

# 分类数据
CATEGORIES = {
    "人物信息": ["随机姓名", "随机姓", "随机名", "男性姓名", "女性姓名", "完整个人信息"],
    "地址信息": ["随机地址", "随机城市", "随机国家", "随机邮编", "随机街道"],
    "网络信息": ["随机邮箱", "安全邮箱", "公司邮箱", "免费邮箱", "随机域名", "随机URL", "随机IP地址", "随机用户代理"],
    "公司信息": ["随机公司名", "公司后缀", "职位"],
    "金融信息": ["信用卡号", "信用卡提供商", "信用卡有效期", "货币"],
    "日期时间": ["随机日期时间", "随机日期", "随机时间", "今年日期", "本月日期"],
    "文本内容": ["随机单词", "随机句子", "随机段落", "随机文本"],
    "电话号码": ["随机手机号", "号段前缀"],
    "其他信息": ["随机颜色", "随机UUID", "随机MD5", "随机SHA1", "随机文件扩展名", "随机MIME类型"]
}

# 省份代码映射
PROVINCE_MAP = {
    "北京市": "11", "天津市": "12", "河北省": "13", "山西省": "14",
    "内蒙古自治区": "15", "辽宁省": "21", "吉林省": "22", "黑龙江省": "23",
    "上海市": "31", "浙江省": "33", "安徽省": "34", "福建省": "35",
    "江西省": "36", "山东省": "37", "河南省": "41", "湖北省": "42",
    "湖南省": "43", "广东省": "44", "广西壮族自治区": "45", "海南省": "46",
    "重庆市": "50", "四川省": "51", "贵州省": "52", "云南省": "53",
    "西藏自治区": "54", "陕西省": "61", "甘肃省": "62", "青海省": "63",
    "宁夏回族自治区": "64", "新疆维吾尔自治区": "65"
}

# 全局单位换算映射表
TO_SECONDS = {
    "毫秒": 0.001,
    "秒": 1,
    "分钟": 60,
    "小时": 3600,
    "天": 86400,
    "周": 604800,
    "月": 2592000,
    "年": 31536000
}

# === 常量定义 === #
RANDOM_STRING_TYPES = ["小写字母", "大写字母", "数字", "特殊字符"]
PASSWORD_OPTIONS = ["包含小写字母", "包含大写字母", "包含数字", "包含特殊字符"]
DOMAINS_PRESET = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "163.com", "qq.com"]
PHONE_TYPES = ["手机号", "座机", "国际号码"]
GENDERS = ["随机", "男", "女"]

# 工具类别定义

TOOL_CATEGORIES = {
    "数据生成工具": {
        "icon": "🎲",
        "description": "生成测试数据、随机内容、模拟用户信息",
        "color": "#667eea"
    },
    "字数统计工具": {
        "icon": "📊",
        "description": "文本分析、字符统计、频率分析",
        "color": "#48bb78"
    },
    "文本对比工具": {
        "icon": "🔍",
        "description": "文本差异比较、版本对比分析",
        "color": "#ed8936"
    },
    "正则表达式测试工具": {
        "icon": "⚡",
        "description": "正则测试、模式匹配、替换操作",
        "color": "#9f7aea"
    },
    "JSON数据对比工具": {
        "icon": "📝",
        "description": "JSON格式验证、差异比较、格式化",
        "color": "#f56565"
    },
    "日志分析工具": {
        "icon": "📋",
        "description": "日志解析、级别统计、模式识别",
        "color": "#4299e1"
    },
    "时间处理工具": {
        "icon": "⏰",
        "description": "时间戳转换、日期计算、时区处理",
        "color": "#38b2ac"
    },
    "IP/域名查询工具": {
        "icon": "🌐",
        "description": "IP定位、域名解析、网络信息查询",
        "color": "#ed64a6"
    }
}

# # CSS样式
CSS_STYLES = """
<style>
    /* 全局样式 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .main-header {
        font-size: 3rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        text-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 1rem;
    }

    .sub-header {
        font-size: 1.5rem;
        color: #2d3748;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }

    /* 工具卡片网格布局 */
    .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .tool-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    /* 选中的卡片样式 */
    .tool-card.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #4c51bf;
        transform: scale(1.02);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }

    .tool-card.selected .tool-icon {
        color: white;
    }

    .tool-card.selected .tool-title {
        color: white;
    }

    .tool-card.selected .tool-desc {
        color: rgba(255, 255, 255, 0.9);
    }

    .tool-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: #667eea;
    }

    .tool-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }

    .tool-desc {
        color: #718096;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* 功能区域样式 */
    .section-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }

    .category-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* 按钮样式 */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }

    .copy-btn {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
        margin: 5px;
    }

    .copy-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(72, 187, 120, 0.3);
    }

    /* 结果框样式 */
    .result-box {
        background: #f8fafc;
        border: 2px dashed #cbd5e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
        font-size: 0.9rem;
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #f7fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f7fafc;
        border-radius: 8px 8px 0px 0px;
        gap: 1rem;
        padding: 0 1.5rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
    }

    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }

    /* 指标卡片 */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid #667eea;
    }

    /* 响应式调整 */
    @media (max-width: 768px) {
        .tools-grid {
            grid-template-columns: 1fr;
        }

        .main-header {
            font-size: 2rem;
        }
    }

    /* 卡片按钮样式 */
    .card-button {
        background: white !important;
        color: #2d3748 !important;
        border: 1px solid #e2e8f0 !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: auto !important;
        min-height: 180px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    }

    .card-button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
        border-color: #667eea !important;
        background: white !important;
        color: #2d3748 !important;
    }

    /* 选中状态的卡片按钮 */
    .selected-card-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 2px solid #4c51bf !important;
        transform: scale(1.02) !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4) !important;
    }

    .selected-card-button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
        color: white !important;
        transform: scale(1.02) !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4) !important;
    }
</style>
"""
# 顶部标题区域
HEADLINE_STYLES = """
<div style="text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 0 0 20px 20px; margin: -1rem -1rem 2rem -1rem;">
    <h1 class="main-header">🔧 测试工程师常用工具集</h1>
    <p style="color: white; font-size: 1.2rem; opacity: 0.9; max-width: 600px; margin: 0 auto;">
        一站式测试数据生成、分析和处理平台
    </p>
</div>
"""

# 导出所有常量
__all__ = ['PROVINCES', 'COUNTRIES', 'CATEGORIES', 'PROVINCE_MAP', 'TO_SECONDS', 'RANDOM_STRING_TYPES',
           'PASSWORD_OPTIONS',
           'DOMAINS_PRESET', 'PHONE_TYPES', 'GENDERS', 'TOOL_CATEGORIES', 'CSS_STYLES', 'HEADLINE_STYLES']
