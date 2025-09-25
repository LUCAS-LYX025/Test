import numpy as np
import matplotlib.pyplot as plt

# 设置支持中文的字体（根据你的系统选择可用字体）
#plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统常用
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS系统常用
# plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']  # Linux系统常用
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 数据（保持不变）
labels = np.array(['故障平均定位时间', '告警误报率', '资源利用率', '标注人力成本'])
before = np.array([83, 35, 42, 15])
after = np.array([12, 6.8, 68, 2])

# 将数据转换为雷达图的角度（保持不变）
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)

# 数据闭合（保持不变）
before = np.concatenate((before, [before[0]]))
after = np.concatenate((after, [after[0]]))
angles = np.concatenate((angles, [angles[0]]))
labels = np.concatenate((labels, [labels[0]]))

# 创建雷达图（保持不变）
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# 绘图部分（保持不变）
ax.plot(angles, before, 'o-', linewidth=2, label='实施前')
ax.fill(angles, before, alpha=0.25)
ax.plot(angles, after, 'o-', linewidth=2, label='实施后')
ax.fill(angles, after, alpha=0.25)

# 设置标签和刻度（保持不变）
ax.set_thetagrids(angles * 180 / np.pi, labels)
ax.set_ylim(0, 100)

# 添加图例（保持不变）
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

plt.show()