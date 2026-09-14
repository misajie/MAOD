# P03 A Deep Gravity model for mobility flows generation

- **作者**：Filippo Simini, Gianni Barlacchi, Massimiliano Luca, Luca Pappalardo
- **年份 / 阵地**：2021 / *Nature Communications* 12: 6576
- **标识**：DOI 10.1038/s41467-021-26752-4；PMID 34772925
- **线**：S。任务名原文是 **flow generation**：已知 tessellation、各地点流出和地理特征，生成 \(y(l_i,l_j)\)；区域内历史流不得作输入。与 flow prediction 切开。
- **原文存档**：`literature/sources/pdf/P03_deepgravity.pdf`；`literature/sources/txt/P03.txt`。代码 https://github.com/scikit-mobility/DeepGravity

## 科学问题

经典重力只用人口和距离，解释清、结构对不上。OSM 里的土地利用、POI、路网被丢掉。深度学习多用于“用历史流转未来”，几乎不碰“完全不看区域内历史流”的生成。

## 对象与符号（原文）

区域 \(R\)，tessellation \(T=\{l_i\}\)，多边形不交且覆盖 \(R\)。流 \(y(l_i,l_j)\) 为单位时间人数。总流出 \(O_i=\sum_j y(l_i,l_j)\)。例：英格兰邮编通勤 \(y(\mathrm{SW1W0NY},\mathrm{PO167GZ})\)。

## RQs 与实验设计

1. 对照：经典重力 G；多特征浅层 MFG；Deep Gravity DG。
2. OSM 特征：土地利用、路网、交通、餐饮、医疗、教育、零售。
3. 单约束重力 = 多项 logistic = 一层 softmax 线性网。DG = 加隐层的非线性多项 logistic。
4. 英格兰、意大利、纽约州。空间 hold-out（训练区与生成区不相交）。
5. 可解释 AI：总体重要性 + 单条流；三国对照。

## 评估指标

主指标 **CPC**。高密度区相对重力的 realism 提升（原文）：意大利约 +66%，英格兰约 +246%，纽约州约 +1076%。分十分位见出版 PDF Fig. 4 / Table 1。这些百分数不得填进本项目 Tables 2–8。

## 模型类别

Science for AI。定律给出非线性 \(p_{j\mid i}\)；模型是生产约束生成。

## 数据清单

英/意/纽约州通勤流 + OSM + 人口 tessellation。

## 主要发现

深度非线性 **加上** 丰富地理特征才跃升。地理不相交的 hold-out 仍可用。意/纽约以人口–距离非线性为主；英格兰是多类地理特征交织。

## 与本项目关联

**直接祖先。** Condition G 点名 gravity power / exp、radiation、Deep Gravity、从 \(R\) 出发的 IPF。评价锁定 CPC、CPL、CPCd、log-Pearson、NRMSE、JSD。
