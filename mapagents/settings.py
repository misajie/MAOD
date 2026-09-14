"""Configuration and secret loading. Secrets are never written to run artifacts."""
from __future__ import annotations
import os
from pathlib import Path
import yaml


def load_env(path: str | Path | None):
    if not path or not Path(path).exists(): return
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        key, value = line.split("=", 1)
        key = key.removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def read_config(path):
    path = Path(path).resolve()
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    project = path.parent.parent if path.parent.name == "configs" else path.parent
    cfg["project_root"] = str(project)
    for k in ("output_dir", "rag_root", "env_file"):
        if k in cfg and cfg[k] and not Path(cfg[k]).is_absolute(): cfg[k] = str(project / cfg[k])
    for k in ("source", "prepared", "osm_path"):
        if cfg.get("data", {}).get(k) and not Path(cfg["data"][k]).is_absolute():
            cfg["data"][k] = str(project / cfg["data"][k])
    load_env(cfg.get("env_file"))
    return cfg
