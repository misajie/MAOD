# MapAgents 公开数据运行记录

主线已完成：数据重建 → RAG → Surveyor/Cartographer/Adapter → 可变特征 Deep Gravity → 验证选择 → 完整 OD 导出。

运行环境：本地 Conda `my-neuro`，PyTorch 2.6.0 + CUDA 12.4，NVIDIA GeForce RTX 4070 SUPER。

数据：Deep Gravity 仓库公开 New York movement 示例。保留 5,279 个区域、326 个 tile；训练/验证/测试为 130/33/163 个 tile。
它来自 GeoDS COVID-19 movement 数据；本次未将其解释为人口普查通勤数据。输入使用公开聚合特征，原始 OSM 导入接口已提供，但本次没有原始 OSM 重建运行。

采用完整 15 层 DG 结构，基础训练 20 epochs，候选训练 5 epochs，完成初始程序生成与 2 轮残差反馈。选中程序含 46 个表达式，形成 85 维区域对输入。全部模型参数可训练。

## 完整测试 tile 的矩阵结果

| 指标 | 数值 |
|---|---:|
| Tile 等权 CPC | 0.924370 |
| 非对角线 CPC（有定义的 tile） | 0.456716 |
| NRMSE | 0.135047 |
| log-flow Pearson | 0.805380 |
| 逐 origin JSD | 0.023065 |
| 真实对角线占比（tile 等权） | 0.888212 |
| 所有 tile 最大行总量绝对误差 | 5.457e-12 |

已导出 163 个完整矩阵，共 939,806 个 OD 单元。每个 NPZ 含 observed、predicted、origin_ids、destination_ids。

该数据对角线流量占比较高，因此总 CPC 和非对角线 CPC 同时报告。未计算统计显著性，也未将这些数值宣称为原论文复现或相对外部 baseline 的改进。

## 10% 完整 origin 行适配

目标正出流 origin 共 2306 个；预算提供 230 个完整 origin 行，其中 172 个训练、58 个验证。验证标签计入预算。
源模型与适配模型均在相同的 2566 个剩余 origin 上评价。

| 同一评估行 | Tile 等权 CPC |
|---|---:|
| 源模型 | 0.923605 |
| 10% 适配 | 0.924497 |

这两行可直接比较；它们的评估 origin 集合不同于上面的完整测试 tile 主结果。

## 文件入口

- `README.md`：环境、运行、断点续跑、原始 OSM、通用数据与 baseline 接入。
- `configs/new_york.yaml`：完整运行配置；密钥由环境文件读取。
- `mapagents/`：数据、特征编译、检索、agent、模型、训练、评价和 CLI。
- `runs/new_york_main/selected_program.json`：实际选中程序。
- `runs/new_york_main/predictions/`：完整预测矩阵与分区域指标。
- `runs/new_york_main/agents/agent_trace.jsonl`：真实调用与检索记录，包括开发过程中的重试。

复用命令：

```powershell
conda run --no-capture-output -n my-neuro python -u -m mapagents run --config configs/new_york.yaml
```

本次执行的是用户要求的数据处理、训练和 OD 评价；未创建或运行测试套件。
