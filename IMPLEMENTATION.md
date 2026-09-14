# Implementation contracts

This file describes the initial implementation interfaces. It is not a paper
result or an experiment report. The upstream resource directories are read-only.

- Python package: `mapagents`; shared dataclasses: `mapagents/contracts.py`.
- Runtime for GPU work: the local Conda `my-neuro` environment (Python 3.11,
  PyTorch CUDA 12.4, RTX 4070 SUPER). No test suites are to be written or run.
- `data.py`: prepare_deepgravity(source, output, seed=1234,
  validation_fraction=.2) -> ODData; load_dataset(root) -> ODData.
- `metrics.py`: matrix_metrics(observed, predicted, distances_km=None) -> dict;
  aggregate_metrics(records) -> dict.
- `programs.py`: SpatialCompiler(data, osm_path=None, cache_dir=None),
  `.compile(program: dict) -> FeatureBundle`, `.catalog() -> list[dict]`,
  `.profile() -> dict`; module function
  `pair_features(bundle, origins, destinations, distances_km) -> np.ndarray`
  with integer global-zone indices, broadcast origin/destination arrays and an
  output last axis equal to len(bundle.pair_ids). `default_program(data)` returns
  a valid program using public supplied features. Stable semantic IDs are based
  on expressions, not user-chosen display names.
- Program JSON: {"version":1,"name":str,"features":[{"name":str,
  "scope":"both|origin|destination|pair", "expression":{...},
  "evidence":[str],"mechanism":str}]}. Expression schema is defined in
  `program_schema.json` by the compiler owner. Operators include source columns,
  OSM aggregations, spatial neighborhood aggregates, algebraic composition and
  pairwise feature combinations. All actual implementations must be documented.
- `osm.py`: extract_pbf(pbf_path, zones_path, output_path, buffer_m=3000),
  read GeoParquet/GeoJSON, write projected/identified raw OSM objects for the
  compiler. Optional raw OSM; supplied public features remain a clearly named
  input mode, never represented as raw map reconstruction.
- `agents.py`: AgentSystem(config: dict, rag_root: Path, output_dir: Path),
  `.initial_program(catalog, profile, current_program, task) -> dict`,
  `.propose(catalog, profile, current_program, diagnostics, history, task,
  count=2) -> list[dict]`. Each real role uses configured OpenAI-compatible
  endpoint. No silent heuristic substitute for an LLM. Backend=offline is an
  explicitly labeled deterministic development mode if implemented.
- Model/training/orchestration/CLI/config/docs belong to the root agent.
- Full-region inference uses all destination logits in one softmax; training
  sampling must not turn unobserved labels into observed zeros. Program search
  uses validation only; final held-out matrices are evaluated after selection.
