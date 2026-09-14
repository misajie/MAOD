# P16 LLMs for Human Mobility: Opportunities, Challenges, and Future Directions

- **作者**：2026 年 arXiv 综述团队（见 arXiv:2603.12420 作者表）
- **年份 / 阵地**：2026 / arXiv:2603.12420
- **线**：短时移动（LLM 综述）

- **原文存档**：PDF `pdf/P16_llm_survey.pdf`；页面/文本 `html/P16_arxiv.html ；txt/P16.txt`；远程 https://arxiv.org/abs/2603.12420。总清单见 `literature/sources/SOURCES.md`。

## 科学问题

LLM 已被塞进移动性的各种任务，文献散。如何按任务把“LLM 实际在干什么”对齐到挑战和典型设计？

## RQs 与实验设计

综述而非新实验。把任务压成五类：

1. 行程规划
2. 轨迹生成
3. 移动仿真
4. 移动预测
5. 地点/活动语义理解

每一类回答：LLM 扮演什么角色、怎么和其他模块接、为什么这个角色成立。

## 评估指标

综述不提出新指标；汇总各任务常用：GEO-BLEU、Acc@k、规划约束满足率、生成分布 JS 等。

## 模型类别

覆盖：纯 prompt、SFT、工具调用 Agent、LLM 编排 + 地理编码器、与 MFM 对齐（如 MoveFM-R）。

## 数据清单

二次文献；指向 YJMob100K、GISCUP 2025 四城、各公开轨迹集。

## 主要发现

- LLM 的比较优势在意图、活动语义、约束推理，不在坐标精度。
- 可靠路线是 grounded + privacy-aware，而不是零样本当世界模型。
- 五类任务不该共用同一套评价。

## 现实意义

给 2024–2026 SIGSPATIAL/GISCUP 的 LLM 刷屏提供地图，避免把行程规划论文的指标抄到 OD 生成论文里。

## 与本项目关联

本项目评价协议与这五类都不同：是 trip-distribution GOF。综述恰好证明“缺标准政策可用性指标”——CPC 家族可以填 OD 这一格。
