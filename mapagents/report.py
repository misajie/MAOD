"""Summarize saved matrices without rerunning models or querying an LLM."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .data import load_dataset
from .metrics import matrix_metrics, aggregate_metrics
from .programs import haversine
from .training import save_json


def summarize_saved(predictions: Path, data):
    records = []
    zones = data.zones.set_index("zone_id")
    for file in sorted(Path(predictions).glob("region_*.npz")):
        with np.load(file, allow_pickle=False) as saved:
            origin_ids, destination_ids = saved["origin_ids"], saved["destination_ids"]
            oz, dz = zones.loc[origin_ids], zones.loc[destination_ids]
            distances = haversine(oz.longitude.to_numpy()[:, None], oz.latitude.to_numpy()[:, None],
                                  dz.longitude.to_numpy()[None, :], dz.latitude.to_numpy()[None, :]).astype(np.float32)
            metrics = matrix_metrics(saved["observed"], saved["predicted"], distances, origin_ids, destination_ids)
        records.append({"region_id": file.stem.removeprefix("region_"), **metrics})
    if not records: raise ValueError(f"No saved region matrices in {predictions}")
    summary = aggregate_metrics(records); summary["split"] = "test"
    save_json(Path(predictions)/"metrics.json", summary)
    pd.DataFrame(records).to_csv(Path(predictions)/"region_metrics.csv", index=False)
    return summary, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/processed/new_york")
    parser.add_argument("--main-run", default="runs/new_york_main")
    parser.add_argument("--adapt-run", default="runs/new_york_adapt_10pct")
    parser.add_argument("--output", default="RUN_REPORT.md")
    args = parser.parse_args()
    data = load_dataset(Path(args.data))
    main_run, adapt_run = Path(args.main_run), Path(args.adapt_run)
    main_result = json.loads((main_run/"result.json").read_text(encoding="utf-8"))
    main_summary, records = summarize_saved(main_run/"predictions", data)
    main_result["held_out"] = main_summary
    save_json(main_run/"result.json", main_result)
    program = json.loads((main_run/"selected_program.json").read_text(encoding="utf-8"))
    m = main_summary["macro"]
    lines = [
        "# MapAgents 公开数据运行记录", "",
        "主线已完成：数据重建 → RAG → Surveyor/Cartographer/Adapter → 可变特征 Deep Gravity → 验证选择 → 完整 OD 导出。", "",
        "运行环境：本地 Conda `my-neuro`，PyTorch 2.6.0 + CUDA 12.4，NVIDIA GeForce RTX 4070 SUPER。", "",
        f"数据：Deep Gravity 仓库公开 New York movement 示例。保留 {data.metadata['n_zones']:,} 个区域、{data.metadata['n_regions']} 个 tile；训练/验证/测试为 {len(data.splits['train'])}/{len(data.splits['validation'])}/{len(data.splits['test'])} 个 tile。",
        "它来自 GeoDS COVID-19 movement 数据；本次未将其解释为人口普查通勤数据。输入使用公开聚合特征，原始 OSM 导入接口已提供，但本次没有原始 OSM 重建运行。", "",
        f"采用完整 15 层 DG 结构，基础训练 20 epochs，候选训练 5 epochs，完成初始程序生成与 2 轮残差反馈。选中程序含 {len(program['features'])} 个表达式，形成 {main_result['input_columns']} 维区域对输入。全部模型参数可训练。", "",
        "## 完整测试 tile 的矩阵结果", "",
        "| 指标 | 数值 |", "|---|---:|",
        f"| Tile 等权 CPC | {m['cpc']:.6f} |",
        f"| 非对角线 CPC（有定义的 tile） | {m['offdiagonal_cpc']:.6f} |",
        f"| NRMSE | {m['nrmse']:.6f} |",
        f"| log-flow Pearson | {m['log_pearson']:.6f} |",
        f"| 逐 origin JSD | {m['mean_row_jsd']:.6f} |",
        f"| 真实对角线占比（tile 等权） | {m['observed_diagonal_share']:.6f} |",
        f"| 所有 tile 最大行总量绝对误差 | {max(r['row_conservation_max_abs'] for r in records):.3e} |", "",
        f"已导出 {main_summary['n_regions']} 个完整矩阵，共 {int(main_summary['totals']['n_cells']):,} 个 OD 单元。每个 NPZ 含 observed、predicted、origin_ids、destination_ids。", "",
        "该数据对角线流量占比较高，因此总 CPC 和非对角线 CPC 同时报告。未计算统计显著性，也未将这些数值宣称为原论文复现或相对外部 baseline 的改进。", "",
    ]
    if (adapt_run/"result.json").exists():
        result = json.loads((adapt_run/"result.json").read_text(encoding="utf-8"))
        summary, _ = summarize_saved(adapt_run/"predictions", data)
        result["held_out"] = summary
        reference, _ = summarize_saved(adapt_run/"source_on_same_rows", data)
        result["source_on_same_held_out_rows"] = reference
        save_json(adapt_run/"result.json", result)
        b = result["row_budget"]
        lines += ["## 10% 完整 origin 行适配", "",
                  f"目标正出流 origin 共 {b['target_positive_origins']} 个；预算提供 {b['visible_origins']} 个完整 origin 行，其中 {b['fit_origins']} 个训练、{b['validation_origins']} 个验证。验证标签计入预算。",
                  f"源模型与适配模型均在相同的 {int(summary['totals']['n_origins'])} 个剩余 origin 上评价。", "",
                  "| 同一评估行 | Tile 等权 CPC |", "|---|---:|",
                  f"| 源模型 | {reference['macro']['cpc']:.6f} |",
                  f"| 10% 适配 | {summary['macro']['cpc']:.6f} |", "",
                  "这两行可直接比较；它们的评估 origin 集合不同于上面的完整测试 tile 主结果。", ""]
    lines += ["## 文件入口", "",
              "- `README.md`：环境、运行、断点续跑、原始 OSM、通用数据与 baseline 接入。",
              "- `configs/new_york.yaml`：完整运行配置；密钥由环境文件读取。",
              "- `mapagents/`：数据、特征编译、检索、agent、模型、训练、评价和 CLI。",
              f"- `{main_run.as_posix()}/selected_program.json`：实际选中程序。",
              f"- `{main_run.as_posix()}/predictions/`：完整预测矩阵与分区域指标。",
              f"- `{main_run.as_posix()}/agents/agent_trace.jsonl`：真实调用与检索记录，包括开发过程中的重试。", "",
              "复用命令：", "", "```powershell",
              "conda run --no-capture-output -n my-neuro python -u -m mapagents run --config configs/new_york.yaml",
              "```", "", "本次执行的是用户要求的数据处理、训练和 OD 评价；未创建或运行测试套件。", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__": main()
