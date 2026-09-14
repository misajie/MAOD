# P28 Human mobility is well described by closed-form gravity-like models learned automatically from data

- **作者**：Oriol Cabanas-Tirapu, Lluís Danús, Esteban Moro, Marta Sales-Pardo, Roger Guimerà
- **年份 / 阵地**：2025 / *Nature Communications* 16:1336
- **标识**：DOI 10.1038/s41467-025-56495-5
- **线**：S / insight。对象是市镇或普查单元之间的流矩阵；结论是机制形式，不是新深度架构。
- **原文存档**：PDF `literature/sources/pdf/P28_cabanas_gravity.pdf`；TXT `literature/sources/txt/P28.txt`；远程 https://www.nature.com/articles/s41467-025-56495-5

## 科学问题

重力模型可解释但粗；特征丰富的 ML 更准但不可读、难外推。是否真的需要远比重力复杂的模型，才能抓住城市流动的本质？

## RQs 与实验设计

1. 贝叶斯符号回归（BMS）在只给起点人口、终点人口、距离的函数族里搜闭式。
2. 主数据：美国六州（纽约、马萨诸塞、加州、佛罗里达、华盛顿、得州）市镇之间的流。
3. 对照复杂 ML（多特征、成千上万参数）与经典重力。
4. 看样本内拟合与对未见区域的外推。

## 评估指标

流拟合与外推误差（与复杂 ML 持平或更好）。文中强调可迁移，而不是 Acc@k。引用具体表时打开 PDF。

## 模型类别

自动发现的闭式重力型定律。insight 论文：复杂度不是精度的必要条件。

## 数据清单

美国六州市镇流；文称在不同尺度、不同数据集上形式仍重力状。

## 主要发现

- 搜到的闭式与复杂 ML 一样准，外推更好。
- 形式仍是“质量 × 质量 / 距离类衰减”，可按重力来读。
- 暗示城市流动有可写下来的普适结构，不一定要上基础模型。

## 与本项目关联

给 Science for AI 提供 2025 年的子刊证据：定律侧基线（重力 power/exp）不是过时装饰。本项目把重力、辐射、Deep Gravity 并排放，和这篇的立场一致。它不处理属性切片；若不同目的下搜到的闭式不同，那就是 Conditon S 的机制版问题。
