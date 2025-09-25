# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: total.py
@time: 2025/2/26 15:34
"""
import pymysql
import pandas as pd
from datetime import datetime, timedelta

# 数据库连接信息
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['Songti SC']  # macOS 系统自带宋体
plt.rcParams['axes.unicode_minus'] = False
db_config = {
    'host': '10.0.3.190',
    'user': 'spider',
    'password': 'sp1der#2024f',
    'database': 'spiderflow',
    'port': 3306
}

# 域名与中文名称的映射字典
domain_to_chinese = {
    'polymerupdate.com': '聚合物更新',
    'chemanalyst.com': '化学分析',
    'bioplasticsnews.com': '生物塑料新闻',
    'icis.com': 'icis',
    'adsalecprj.com': '雅式橡塑网',
    'packaging-gateway.com': '包装门户',
    'plastikmedia.co.uk': '塑料媒体',
    'resource-recycling.com': '资源回收',
    'plastics.ru': '俄罗斯塑料工业协会',
    'plastics-technology.com': '塑料技术',
    'industrysourcing.com': '格荣工业',
    'ptonline.com': '塑料技术',
    'k-online.com': 'k塑料展',
    'plastech.biz': '普拉斯泰克',
    'canplastics.com': '加拿大塑料',
    'ambienteplastico.com': '塑料环境',
    'bpf.co.uk': '英国塑料协会',
    'nexizo.ai': 'nexizo',
    'pt-mexico.com': '墨西哥塑料技术',
    'interplasinsights.com': '塑料见解',
    'injectionmouldingworld.com': '世界注塑杂志',
    'plasticsbusinessmag.com': '塑料业务',
    'economictimes.indiatimes.com': '商业新闻',
    'chemorbis.com': '化工奥比斯',
    'replanetmagazine.it': 'replanet杂志',
    'plasticportal.sk': '塑料门户网站',
    'basf.com': '巴斯夫',
    'bioplasticsmagazine.com': '生物塑料杂志',
    'plasticsnet.com': '塑料网',
    'tecnoedizioni.com': '泰克诺艾迪逊尼',
    '3erp.com': '3erp',
    'kuraray.co.jp': '可乐丽',
    'sacmi.com': '萨克米',
    'plasticsdecorating.com': '塑料装饰',
    'chinaplasonline.com': '国际橡塑展',
    'itochu.co.jp': '伊藤忠',
    'canadianchemistry.ca': '加拿大化学工业协会',
    'dic-global.com': '迪爱生',
    'totalenergies.com': '道达尔',
    'chemeurope.com': '欧洲化学',
    'sumitomo-chem.co.jp': '住友化学',
    'terrumash.com': '特瑞达斯',
    'plasticsindustry.org': '塑料工业',
    'vnplas.com': '越南普拉斯',
    'berryglobal.com': '贝里国际',
    'clariant.com': '科莱恩',
    'spnews.com': '可持续包装新闻',
    'packworld.com': '包装世界',
    'grandviewresearch.com': '大观观察',
    'recyclingproductnews.com': '回收产品新闻',
    'ehn.org': '环境健康科学',
    'plasticportal.eu': '塑料门户网站',
    'news.oilandgaswatch.org': '石油和天然气观察',
    'insideclimatenews.org': '内部气候新闻',
    'theguardian.com': '卫报',
    'daicel.com': '大赛璐',
    'shokubai.co.jp': '日本触媒',
    'scgchemicals.com': 'scg化工',
    'spglobal.com': '标普全球',
    'plasticpollutioncoalition.org': '塑料污染联盟',
    'extrusion-world.com': '挤出世界网',
    'mgc.co.jp': '三菱瓦斯',
    'accedemold.com': 'accede模具',
    'pttgcgroup.com': 'pttgc',
    'prm-taiwan.com': '普拉米科技',
    'plasticsmachinerymanufacturing.com': '塑料机械制造',
    'vietnhatplastic.com': '越日塑料',
    'arburg.com': '阿布格',
    'bakelite.com': '贝科莱特',
    'recyclingtoday.com': '今日回收',
    'plasticsandrubberasia.com': '亚洲塑料橡胶展',
    'lyondellbasell.com': '利安得巴塞尔',
    'albemarle.com': '阿尔伯特',
    'newsroom.avantium.com': '阿凡提姆',
    'packagingnews.co.uk': '包装新闻',
    'corporate.dow.com': '陶氏',
    'abiplast.org.br': '巴西塑料工业协会',
    'elkem.com': '埃肯',
    'sabic.com': '沙特基础工业公司',
    'eastman.com': '伊士曼',
    'langboextruder.com': '朗博',
    'solvay.com': '索尔维',
    'groupmaire.com': '迈尔',
    'biesterfeld.com': '比斯特费尔德',
    'greiner.com': '格雷纳',
    'kolon.com': '科隆',
    'tosoh.co.jp': '东曹',
    'globenewswire.com': '环球新闻网',
    'trinseo.com': '盛禧奥',
    'braskem.com.br': '布拉科斯',
    'lubrizol.com': '路博润',
    'sml.at': 'sml',
    'lgchem.com': 'LG化学',
    'avient.com': '普立万',
    'daikin.com': '大金',
    'corporate.exxonmobil.com': '埃克森美孚',
    'plas.com': '普拉斯',
    'gpca.org.ae': 'gpca',
    'techbullion.com': '科技金条',
    'saint-gobain.com': '圣戈班',
    'covestro.com': '科思创',
    'ict.fraunhofer.de': '弗劳恩霍夫',
    'indoramaventures.com': '银都拉玛',
    'ineos-styrolution.com': '英力士苯领',
    'polykemi.se': '开米',
    'sibur.ru': '西布尔',
    'plasticsrecyclers.eu': '欧洲塑料回收商',
    'vinylinfo.org': '乙烯基研究所',
    'theconversation.com': '对话网',
    'polyplastics-global.com': '宝理塑料',
    'rusplast.com': '鲁普拉斯特',
    'sesotec.com': '双仕',
    'wh.group': '威德霍尔',
    'aekyungchemical.co.kr': '爱敬化学',
    'abchemicalsolutions.com': 'ab化学',
    'european-bioplastics.org': '欧洲生物塑料',
    'dows.com': '陶氏化学'
}

# 新增：爬虫编号映射（域名 -> 编号列表）
spider_id_mapping = {
    'polymerupdate.com': ['000001', '000004'],
    'chemanalyst.com': ['000002'],
    'bioplasticsnews.com': ['000003'],
    'icis.com': ['000005'],
    'adsalecprj.com': ['000006'],
    'packaging-gateway.com': ['000007'],
    'plastikmedia.co.uk': ['000008'],
    'resource-recycling.com': ['000009'],
    'plastics.ru': ['000010', '000027'],
    'plastics-technology.com': ['000011', '000016'],
    'industrysourcing.com': ['000012'],
    'ptonline.com': ['000013'],
    'k-online.com': ['000014'],
    'plastech.biz': ['000015'],
    'canplastics.com': ['000017'],
    'ambienteplastico.com': ['000018'],
    'bpf.co.uk': ['000019'],
    'nexizo.ai': ['000020'],
    'pt-mexico.com': ['000021'],
    'interplasinsights.com': ['000022'],
    'injectionmouldingworld.com': ['000023'],
    'plasticsbusinessmag.com': ['000024'],
    'economictimes.indiatimes.com': ['000025'],
    'chemorbis.com': ['000026'],
    'replanetmagazine.it': ['000028'],
    'plasticportal.sk': ['000029'],
    'basf.com': ['000030'],
    'bioplasticsmagazine.com': ['000031'],
    'plasticsnet.com': ['000032', '000104'],
    'tecnoedizioni.com': ['000033'],
    '3erp.com': ['000034'],
    'kuraray.co.jp': ['000035'],
    'sacmi.com': ['000036'],
    'plasticsdecorating.com': ['000037'],
    'chinaplasonline.com': ['000038'],
    'itochu.co.jp': ['000039', '000040'],
    'canadianchemistry.ca': ['000041'],
    'dic-global.com': ['000042'],
    'totalenergies.com': ['000043', '000044'],
    'chemeurope.com': ['000045'],
    'sumitomo-chem.co.jp': ['000046'],
    'terrumash.com': ['000047'],
    'plasticsindustry.org': ['000048', '000069', '000081'],
    'vnplas.com': ['000049'],
    'berryglobal.com': ['000050'],
    'clariant.com': ['000051'],
    'spnews.com': ['000052'],
    'packworld.com': ['000053'],
    'grandviewresearch.com': ['000054'],
    'recyclingproductnews.com': ['000055'],
    'ehn.org': ['000056'],
    'plasticportal.eu': ['000057'],
    'news.oilandgaswatch.org': ['000058', '000099'],
    'insideclimatenews.org': ['000059'],
    'theguardian.com': ['000060'],
    'daicel.com': ['000061'],
    'shokubai.co.jp': ['000062'],
    'scgchemicals.com': ['000063', '000111'],
    'spglobal.com': ['000064'],
    'plasticpollutioncoalition.org': ['000065'],
    'extrusion-world.com': ['000066', '000103'],
    'mgc.co.jp': ['000067'],
    'accedemold.com': ['000068'],
    'pttgcgroup.com': ['000070'],
    'prm-taiwan.com': ['000071', '000097'],
    'plasticsmachinerymanufacturing.com': ['000072'],
    'vietnhatplastic.com': ['000073'],
    'arburg.com': ['000074'],
    'bakelite.com': ['000075'],
    'recyclingtoday.com': ['000076'],
    'plasticsandrubberasia.com': ['000077'],
    'lyondellbasell.com': ['000078'],
    'albemarle.com': ['000079'],
    'newsroom.avantium.com': ['000080'],
    'packagingnews.co.uk': ['000082'],
    'corporate.dow.com': ['000083'],
    'abiplast.org.br': ['000084'],
    'elkem.com': ['000085'],
    'sabic.com': ['000086'],
    'eastman.com': ['000087'],
    'langboextruder.com': ['000088'],
    'solvay.com': ['000089'],
    'groupmaire.com': ['000090'],
    'biesterfeld.com': ['000091'],
    'greiner.com': ['000092'],
    'kolon.com': ['000093'],
    'tosoh.co.jp': ['000094'],
    'globenewswire.com': ['000095'],
    'trinseo.com': ['000096'],
    'braskem.com.br': ['000098'],
    'lubrizol.com': ['000100'],
    'sml.at': ['000101'],
    'lgchem.com': ['000102'],
    'avient.com': ['000105', '000129'],
    'daikin.com': ['000106'],
    'corporate.exxonmobil.com': ['000107'],
    'plas.com': ['000108'],
    'gpca.org.ae': ['000109'],
    'techbullion.com': ['000110'],
    'saint-gobain.com': ['000112'],
    'covestro.com': ['000113'],
    'ict.fraunhofer.de': ['000114'],
    'indoramaventures.com': ['000115'],
    'ineos-styrolution.com': ['000116'],
    'polykemi.se': ['000117'],
    'sibur.ru': ['000118'],
    'plasticsrecyclers.eu': ['000119'],
    'vinylinfo.org': ['000120'],
    'theconversation.com': ['000121'],
    'polyplastics-global.com': ['000122'],
    'rusplast.com': ['000123'],
    'sesotec.com': ['000124'],
    'wh.group': ['000125'],
    'aekyungchemical.co.kr': ['000126'],
    'abchemicalsolutions.com': ['000127'],
    'european-bioplastics.org': ['000128'],
    'dows.com': ['000130']
}

# 连接到数据库
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 执行 SQL 查询（保持不变）
query = """
SELECT
    REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(url, '://', -1), '/', 1), 'www.', '') AS domain,
    COUNT(*) AS domain_count,
    MAX(insert_date) AS latest_insert_date
FROM
    news
GROUP BY
    domain
ORDER BY
    domain_count DESC;
"""

cursor.execute(query)
result = cursor.fetchall()

# 关闭数据库连接
cursor.close()
conn.close()

# 转换为 DataFrame
df = pd.DataFrame(result, columns=['Domain', 'Count', 'latest_insert_date'])

# 数据处理部分（保持不变）
df['latest_insert_date'] = pd.to_datetime(df['latest_insert_date'])
current_time = datetime.now()
df['今日是否有更新'] = (current_time - df['latest_insert_date']) > timedelta(days=2)
df['今日是否有更新'] = df['今日是否有更新'].apply(lambda x: '无' if x else '')


# 新增：添加爬虫编号列（处理多编号情况）
def get_spider_ids(domain):
    ids = spider_id_mapping.get(domain, [])
    return ", ".join(ids) if ids else "未知"


df['爬虫编号'] = df['Domain'].apply(get_spider_ids)  # 新增列
df['Chinese Name'] = df['Domain'].apply(lambda x: domain_to_chinese.get(x, '未知'))

# 计算总条数并添加汇总行
total_count = df['Count'].sum()
df_total = pd.DataFrame([['Total', total_count, None, '', '总计', '']],  # 汇总行无编号
                        columns=['Domain', 'Count', 'latest_insert_date', '今日是否有更新', 'Chinese Name', '爬虫编号'])

# 合并数据并调整列顺序
df_combined = pd.concat([df, df_total], ignore_index=True)
df_combined = df_combined[['爬虫编号', 'Domain', 'Chinese Name', 'Count', 'latest_insert_date', '今日是否有更新']]
df_combined.columns = ['爬虫编号', '域名', '中文名称', '统计', '最近插入时间', '今日是否有更新']

# 新增统计项
# 网站个数
website_count = df['Domain'].nunique()

# 爬虫个数（去重）
spider_ids = set()
for ids in df['爬虫编号'].apply(lambda x: x.split(", ") if x != "未知" else []):
    spider_ids.update(ids)
spider_count = len(spider_ids)

# 网站爬取个数（爬虫编号不为空的网站个数）
website_crawled_count = df[(df['爬虫编号'] == "未知") | (df['爬虫编号'] == "")]['Domain'].nunique()


# 添加统计信息到汇总行
df_combined.loc[df_combined[
                    '域名'] == 'Total', '统计'] = f"新闻总数量: {total_count}\n网站个数: {website_count}\n爬虫个数: {spider_count}\n程序爬虫个数: {website_crawled_count}"

# 保存到 Excel（路径保持不变）
output_file = '/Users/leiyuxing/PycharmProjects/TestFramework/test/国外新闻爬虫数量统计.xlsx'
df_combined.to_excel(output_file, index=False, engine='openpyxl')


# # 生成图片的函数（添加爬虫编号列显示）
# def create_excel_style_image(df, output_path):
#     fig, ax = plt.subplots(figsize=(14, len(df) * 0.5 + 2))  # 加宽以适应新列
#     ax.axis('off')
#
#     # 表格数据调整
#     table = ax.table(
#         cellText=df.values,
#         colLabels=df.columns,
#         cellLoc='center',
#         loc='center',
#         colColours=['#f0f0f0'] * len(df.columns)
#     )
#
#     # 样式调整（列宽增加）
#     table.auto_set_font_size(False)
#     table.set_fontsize(10)
#     table.scale(1, 1.5)
#     col_widths = [0.15, 0.25, 0.25, 0.1, 0.2, 0.1]  # 调整列宽比例
#     for col, width in zip(range(len(df.columns)), col_widths):
#         table.auto_set_column_width(col=col)
#         table.get_celld()[(0, col)].width = width
#
#     # 其他样式保持不变...
#     plt.savefig(output_path, bbox_inches='tight', dpi=150)
#     plt.close()
#
#
# # 生成图片
# output_image = '/Users/leiyuxing/PycharmProjects/TestFramework/test/国外新闻爬虫数量统计.png'
# create_excel_style_image(df_combined, output_image)
