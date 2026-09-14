# Catalog → 任务（分层）

内容清单仍在 `catalogs/` 与 `inventories/`。本文只说明那些内容怎么接到预测任务上。

---

## 1. 三层

```
L0  全球特征     OSM Map features + WorldPop Global 2
                 任何城市都能造，也是任务 D 唯一允许的特征

L1  区划         把 L0 和 y 对到同一套空间单元
                 由任务决定，不是全球产品

L2  标签 y       只在有观测的地方存在
                 一个任务只用一张 y，不混
```

预测式：在 L1 的区 \(i,j\) 上，用 L0 得到 \(\mathbf{x}_i,\mathbf{x}_j,\mathbf{x}_{ij}\)，拟合 L2 的 \(T_{ij}\)（或行程属性）。任务 D 把这套 \(\mathbf{x}\) 迁到没有 L2 的城市。

---

## 2. 任务一览

| 任务 | y | 数据 | L1 区划 | 构造 |
|---|---|---|---|---|
| **A** | block 通勤岗位流 | LODES OD | 2020 census block（可再聚到城市区） | 居住 block → 工作 block 的岗位数 |
| **A2** | tract 通勤流 × 方式 | CTPP 2017–2021 Part 3 | tract–tract（或更粗的 Part 3 流量对） | ACS 工人 home-to-work，含方式 |
| **B** | 全目的客运 OD | NextGen NHTS 被动 OD | 该产品发布的 OD 区划 | 被动位置扩样后的客运表，不是通勤专表 |
| **C** | 调查行程目的 / 方式 | NHTS 2022 TRIP | 行程级；地理只有区分类，不是全矩阵 | 出行日一条行程一个样本 |
| **E** | PUMA 自定义 | ACS PUMS | 居住 PUMA；工作地是 POWPUMA | 微观加权后自编表或稀疏 PUMA→POWPUMA |
| **D** | 跨城迁移 | 无新的 y | 目标城市自己的 L1 | 特征只用 L0；在 A 或 B 上训练 |

层次关系（细 → 粗 / 专 → 广）：

```
A  block 通勤岗位          最细、无方式
A2 tract 通勤 × 方式       同为通勤，更粗，多方式维
E  PUMA 自定义通勤         更粗，样本微观，不是全域矩阵
B  全目的客运 OD           与通勤不是同一 y
C  行程目的/方式           不是 OD 矩阵，是属性分类/回归
D  把 L0 迁走              不新增标签
```

A 与 A2 都是通勤，不能加总成一个 y。B 是全目的。C/E 不是城市完整 \(T_{ij}\)。

---

## 3. L0：所有任务共用的特征源

详细 tag / 文件名见 `catalogs/osm.md`、`catalogs/worldpop.md`。接到任务时只做空间汇总，不改官方编码。

**WorldPop（origin mass）**

- 主用：Global 2 constrained `*_CN_100m_R2025A_v1.tif`
- 区 \(i\)：格子加总得到 \(P_i\)；可选工作年龄组（`age` 编码见 WorldPop catalog）
- 不提供工作地人口、方式、目的

**OSM（结构与网络）**

按 Map features 大类汇总到区，不另造 key：

| 汇总对象 | Catalog 大类 |
|---|---|
| 居住 | `building` 住宅类、`landuse=residential`、`place` |
| 就业 / 办事 | `office`、`amenity`（教育/医疗/公共服务/金融）、`building` 非住宅、`landuse` commercial/industrial/retail |
| 零售 / 服务 | `shop`、`amenity` 饮食、`leisure`、`tourism` |
| 交通供给 | `highway` 分级长度、`railway`、`public_transport`、`route`、`amenity` 交通子类 |
| 障碍 | `waterway`、`natural`、`barrier` |
| 区对成本 \(c_{ij}\) | `highway` / `route` 图上的距离或时间代理 |

L0 **禁止**混入：LODES RAC/WAC、CTPP 方式份额、NHTS 收入、PUMS `JWTR`。那些是 L2 或美国专有协变量，一放进 \(\mathbf{x}\) 就不能做 D。

---

## 4. 各任务

### A　block 通勤岗位流

| | |
|---|---|
| y | \(T_{ij}\) = 居住 block \(i\) 到工作 block \(j\) 的岗位数 |
| 主字段 | LODES OD：`h_geocode`、`w_geocode`、`S000` |
| 可选切片 | 同一文件的 `SA*` 年龄、`SE*` 收入、`SI*` 产业；文件名 `JT00`–`JT05` |
| 辅助（不当 y） | RAC 居住侧岗位结构；WAC 工作侧岗位结构；`{st}_xwalk.csv.gz` 把 block 聚到 tract/county/CBSA |
| L1 | 默认 2020 block；城市模型再按 xwalk 聚到分析区 |
| L0 | WorldPop → 居住区人口；OSM → 工作区吸引 + \(c_{ij}\) |
| 注意 | 2022–2023 无 AK/MI 的 OD/WAC；不要混 LODES7（2010 block） |

### A2　tract 通勤流 × 方式

| | |
|---|---|
| y | \(T_{ijm}\) = 居住 tract \(i\) 到工作 tract \(j\)、方式 \(m\) 的工人流 |
| 数据 | CTPP 2017–2021 **Part 3**；门户估计值 + MOE |
| L1 | 2017–2021 最小 **tract–tract**；无 TAZ/TAD。更粗的对：county、place、PUMA5–place 等见 CTPP catalog |
| 对照表 | Part 1 居住、Part 2 工作地（不当 y） |
| L0 | 与 A 相同，但汇总到 tract |
| 注意 | 全部表来自合成微观数据；流量对至少 3 个未加权 ACS 观测；**不要**和 2012–2016 TAZ 拼成一个 y；不要和 A 的 `S000` 加总 |

### B　全目的客运 OD

| | |
|---|---|
| y | 区对客运量（全目的，不是上班专表） |
| 数据 | NextGen NHTS **被动位置 OD**（客运方法论文档）；货运是另一张表 |
| 不是 | NHTS HOUSEHOLD/PERSON/VEHICLE/TRIP 五张核心调查文件 |
| L1 | 以该 OD 产品发布的区划为准 |
| L0 | 与 A 相同，汇总到 B 的区划 |
| 注意 | 与 A/A2 构造不同：被动扩样客运 vs 就业岗位 vs ACS 通勤 |

### C　调查行程目的 / 方式

| | |
|---|---|
| y | 行程级：目的和/或方式（不是城市 OD 矩阵） |
| 数据 | NHTS 2022 **TRIP** |
| 目的字段 | `TRIPPURP`、`WHYTO`、`WHYFROM`、`WHYTRP1S`、`WHYTRP90` |
| 方式字段 | `TRIPMODE`、`TRPTRANS`、`PUBTRANS` |
| 行程度量 | `TRPMILES`、`TRVLCMIN`、`STRTTIME`、`ENDTIME`、`LOOP_TRIP`；权重 `WTTRDFIN` / `2D` / `5D` |
| 连接 | `HOUSEID`、`PERSONID`、`TRIPID` → PERSON / HOUSEHOLD |
| L1 | 无全市区对；只有起源/目的地的密度等分类（`OB*` / `DB*`） |
| L0 | 可按行程起终点附近 OSM/WorldPop 做解释特征，不能把加权样本填成全市 \(T_{ij}\) |

### E　PUMA 自定义

| | |
|---|---|
| y | 自编：人级上班方式，或稀疏 居住 PUMA → POWPUMA 流 |
| 数据 | ACS PUMS person + housing；`SERIALNO` + `SPORDER`；必须加权 |
| 手册已点名 | `JWTR` 上班方式（非工人缺失）；`AGEP`、`SEX`、`ST` |
| L1 | 可识别地理只有 nation / region / division / state / **PUMA**。工作地是 **POWPUMA**（常比居住 PUMA 粗，代码可不对齐） |
| L0 | 汇总到 PUMA / POWPUMA |
| 注意 | 不是城市全域矩阵；估计不必等于 ACS 发表表 |

### D　跨城迁移

| | |
|---|---|
| y | 无新标签。训练用 A 或 B 的 y；目标城没有 y |
| 特征 | **只有 L0**（OSM + WorldPop） |
| L1 | 目标城官方区划 |
| 训练 | 美国有 L2 的城市：A（通勤）或 B（全目的），二选一、分开迁 |
| 不能迁 | RAC/WAC、CTPP 份额、NHTS/PUMS 微观变量 |
| 结果 | 目标城可出 \(\hat T_{ij}\)；没有当地 L2 就没有当地误差 |

---

## 5. 特征与标签：谁进 \(\mathbf{x}\)，谁进 y

| Catalog 条目 | A | A2 | B | C | E | D |
|---|---|---|---|---|---|---|
| OSM tags / 网络 | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) |
| WorldPop \(P_i\) | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) | \(\mathbf{x}\) |
| LODES OD `S000` | **y** | — | — | — | — | 仅训练时的 y |
| LODES RAC/WAC | 对照，不当 \(\mathbf{x}\)（D 禁） | — | — | — | — | 禁 |
| CTPP Part 3 | — | **y** | — | — | — | 禁当 \(\mathbf{x}\) |
| CTPP Part 1/2 | — | 对照 | — | — | — | 禁 |
| NextGen OD | — | — | **y** | — | — | 仅训练时的 y |
| NHTS TRIP 目的/方式 | — | — | — | **y** | — | 禁 |
| PUMS `JWTR` / POWPUMA | — | — | — | — | **y** | 禁 |

---

## 6. 对齐与不要做的事

| 对齐 | |
|---|---|
| 时间 | OSM 提取日、WorldPop 年、y 的年（LODES job year / CTPP 2017–2021 / NHTS 2022）说清楚 |
| 空间 | 同一任务内 L0 与 y 落到同一 L1 |
| 构造 | 上表一列一个 y |

不要：NHTS 样本当城市完整 OD；LODES+CTPP+NextGen 加总；WorldPop 当就业密度；Global 1 与 Global 2 当同一栅格；CTPP 2017–2021 tract 与 2012–2016 TAZ 混 y；L2 字段放进 D 的 \(\mathbf{x}\)。
