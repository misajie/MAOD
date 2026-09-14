# P27 Transferable human mobility network reconstruction with neuroGravity

- **作者**：Jinming Yang, S. Huang, Z. Huang, Y. Jin, X. Yang, Marta C. González, Yang Xu（交大新闻稿作者表）
- **年份 / 阵地**：2026 / *Nature Computational Science* 6: 630–641（2026-06-12）
- **标识**：DOI 10.1038/s43588-026-01003-y；arXiv:2604.23678
- **线**：S。城市内部 OD 网络重建 + 少样本 / 零样本跨城迁移。
- **原文存档**：PDF `literature/sources/pdf/P27_neurogravity.pdf`；HTML `literature/sources/html/P27_arxiv.html`；TXT `literature/sources/txt/P27.txt`；代码 https://github.com/urbanmobility/NeuroGravity ；全球代理流 Zenodo 10.5281/zenodo.19727864

## 科学问题

全球南方往往没有完整出行调查。只用公开的设施和人口，加上**极少**观测边，能否重建整张城市流动网络，并迁到从未见过流的城市？迁移何时可信？

## RQs 与实验设计

1. 物理信息 GNN：先用经典重力给出物理初值（meta-Gravity），再用边增强 graph transformer 学对定律的偏离。
2. 少样本重建三种掩膜：完全随机边；部分节点的出/入边；只观测内部 OD。极端设定：约 10% 区域的内部流，占总 OD 对 <1%。
3. 波士顿：250 个 ZCTA 节点，51,786 条边。只观测 1% 内部对（496 条）时 \(R^2=0.77\)，对照重力 \(R^2=0.59\)。
4. 零样本：波士顿训练 → 洛杉矶 \(R^2=0.69\)、湾区 \(R^2=0.61\)，与目标城 10% 本地观测几乎持平（0.70、0.60）。新闻稿还提到波哥大、里约。
5. 迁移洞察：空间收入隔离相近，网络更好迁。作者构造隔离指数预测可迁移性。
6. 用波士顿集成模型为全球 1200+ 城生成代理流。

区域嵌入与社会经济 / 宜居指标相关，可当昂贵调查的代理。

## 评估指标

主报 **\(R^2\)**（绝对流量拟合）。预印本/新闻稿未把 CPC 当主表。这是 flow reconstruction，不是下一地点。缺 CPC 不是 Layer F 的 FAIL，但若与 Deep Gravity 并排，应补 CPC。

少样本加权（预印本式 (8)）：观测边按重力先验 \(F_{ij}\) 做 softmax 温度加权，避免稀观测被大边主导。

## 模型类别

Physics-informed GNN = 重力定律 + 图网络修正。明确 few-shot / zero-shot。Science for AI：定律先写进去，网络只学残差。

## 数据清单

- 波士顿等美国城普查/通勤流（CTPP 谱系）
- OSM 设施、人口、土地利用、路网、POI
- 收入空间分布（隔离指数）
- 产出：1200+ 城代理 OD

## 主要发现

- 1% 内部边足够把波士顿网络拟合到 \(R^2=0.77\)，明显优于闭式重力。
- 跨城零样本可行，但受空间收入隔离约束，不是“任意城都能迁”。
- 区域表征可当社会经济代理。
- 全球 1200 城产品与 WorldMove / Rong 全球通勤表同属“用富城模型填穷城”路线。

## 与本项目关联

和 Deep Gravity 最近：都是用地理特征生成/重建 OD。差别是 neuroGravity **允许极少观测边**（few-shot），Deep Gravity 的标准设定是区域内历史流不得作输入。本项目 Condition G 仍是零观测生成；若以后做“用 1% 通勤边重建其他分区”，neuroGravity 是现成架构。不要把它的 \(R^2\) 直接写进 CPC 主表。隔离指数提醒：跨城 hold-out 要报告城市结构是否可比，不能只报平均分。
