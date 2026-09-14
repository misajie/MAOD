# MapAgents

MapAgents uses retrieved map/mobility knowledge, executable spatial feature
programs, and validation residuals to adapt a Deep Gravity OD predictor. The
predictor has 15 hidden layers and all of its parameters remain trainable.

The first supplied configuration runs on the **public New York movement example
in `resources/deepgravity`**. That example is derived from GeoDS COVID-19 data;
it is not presented here as a census commuting dataset. This configuration uses
the supplied named geographic aggregates. Raw OSM and new OD datasets have
separate import interfaces.

The acquired London, Paris, Madrid, Barcelona and Italy raw OD/boundary/OSM files are
documented in [data/raw/README.md](data/raw/README.md), with a common path and
schema index in `data/raw/catalog.json`. These are raw aligned datasets without
spatial splits. Their source years and suppression rules are preserved; current
OSM snapshots are explicitly distinguished from the historical OD years.
Optional historical OSM files are retained separately. Italy has official 2011
municipal OD plus the 402,678 original census-section boundaries; the paper's
exact section-level OD has not been recovered from the discontinued ISTAT portal.
See [the DGM data alignment note](data/raw/DGM_DATA_ALIGNMENT.md).

## Run on the configured GPU environment

From this directory:

```powershell
conda run --no-capture-output -n my-neuro python -u -m mapagents run --config configs/new_york.yaml
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

`configs/new_york.yaml` reads the user-provided `.env.example`. The environment
variables used are:

```text
DEEPSEEK_BASE_URL
DEEPSEEK_MODEL
DEEPSEEK_API_KEY
QWEN_BASE_URL
QWEN_EMBEDDING_MODEL
QWEN_API_KEY
```

DeepSeek supplies the three LLM roles. Qwen supplies retrieval embeddings;
BM25, TF-IDF and dense rankings are combined with reciprocal-rank fusion.
The keys themselves are not copied into configurations or run artifacts.
Change `env_file` to use a different environment file. Existing environment
variables take precedence. Do not commit a file containing real keys.

The selected `my-neuro` environment already provides CUDA PyTorch and the core
dependencies. If packaging is desired without replacing its GPU installation:

```powershell
conda run -n my-neuro python -m pip install -e . --no-deps
```

Optional PBF ingestion needs `osmium`:

```powershell
conda run -n my-neuro python -m pip install osmium
```

## What the main command does

1. Reads public JSON/CSV and original geometries without executing upstream
   preprocessing or deserializing its pickle files.
2. Recomputes projected zone area and WGS84 centroids. Preserves the original
   test tile assignments and draws independent validation tiles from training.
3. Retains internal-region OD edges and complete destination supports, including
   self cells and destinations with zero outflow. Observed row totals are used
   only when scaling predicted destination probabilities into counts.
4. Trains a reference predictor on the supplied numeric geographic features for
   20 epochs. The named JSON expands to 23 components; this reference is not an
   exact reproduction of the paper's 18-column/population configuration.
5. Surveyor retrieves evidence and proposes geographic mechanisms. Cartographer
   emits edits that compile into complete spatial programs. Adapter reads
   validation residual summaries and directs subsequent retrieval and edits.
6. Expands/reorders the model input by semantic feature identity, initializes new
   input weights to zero, and fine-tunes all weights. Every search round also
   includes a weight-only continuation from the same parent.
7. Selects programs with validation CPC. Only after selection, predicts every
   destination for every held-out origin and exports the OD matrices.

The configuration uses one initial program proposal, two feedback rounds, two
LLM candidates per feedback round, and five epochs per candidate. Source
features are transformed with signed log1p and training-only standardization.
Transform parameters are reused for common columns during model adaptation.

Training samples up to 512 destinations uniformly per origin. This follows the
available loader's sampling behavior; it does not guarantee inclusion of every
positive destination. The loss is sampled count-weighted cross entropy,
normalized by sampled batch flow for numerical scale. Inference normalizes over
**all** destinations in each region, never separately over destination chunks.

## Artifacts and restart

Outputs are written to `runs/new_york_main/`:

| Artifact | Content |
|---|---|
| `result.json` | Selected checkpoint, validation and held-out metrics, input mode |
| `selected_program.json` | Complete selected executable program |
| `selected_feature_report.json` | Semantic columns and observed feature summaries |
| `agents/agent_trace.jsonl` | Role inputs/outputs, retrieved evidence, usage and timing |
| `agents/rag_cache/document_embeddings.npz` | Cached corpus embeddings |
| `reference/` | Reference checkpoint and training/validation records |
| `round_*/` | Candidate programs, checkpoints, diagnostics and selection |
| `predictions/region_*.npz` | Full OD arrays and explicit origin/destination IDs |
| `predictions/region_metrics.csv` | Per-region metrics |
| `predictions/metrics.json` | Equal-region metric aggregation |
| `search_history.json` | Program and parameter continuation comparisons |

Repeat the same command to resume. Completed checkpoints and proposed programs
are reused. A completed result is returned without retraining or reevaluating.
Choose a new output directory for a changed configuration. A failure during an
epoch restarts that candidate from its parent; a finished candidate is retained.

The data package lives at `data/processed/new_york/` and contains zones,
base features, sparse internal flows, region splits, and provenance metadata.
The metadata explicitly records excluded cross-region flow and uncertain
upstream feature units. Correcting zone area does not reconstruct incorrectly
measured upstream OSM aggregates.

## Spatial program format

```json
{
  "version": 1,
  "name": "retail_neighborhood_and_distance",
  "features": [
    {
      "name": "nearby_retail",
      "scope": "destination",
      "expression": {
        "op": "neighborhood",
        "arg": {"op": "source", "column": "retail_point"},
        "radius_km": 2,
        "aggregation": "sum"
      },
      "mechanism": "Hypothesized nearby service concentration",
      "evidence": ["dataset:retail_point"]
    },
    {
      "name": "destination_retail_distance_interaction",
      "scope": "pair",
      "expression": {
        "op": "multiply",
        "left": {"op": "destination", "arg": {"op": "source", "column": "retail_point"}},
        "right": {"op": "exp_decay", "arg": {"op": "distance"}, "scale": 5}
      },
      "mechanism": "Hypothesized distance-modulated destination attraction",
      "evidence": ["dataset:retail_point"]
    }
  ]
}
```

Implemented operators are documented in `mapagents/programs.py::OPERATORS`:
source columns, zone area, arithmetic, signed log1p, square root, clipping,
distance decay, spatial neighborhood sum/mean/decay, raw OSM count/area/length/
numeric-tag aggregation, and origin/destination pair composition.

Programs are expression trees; arbitrary Python/SQL is not evaluated. Redundant
scope wrappers and duplicate columns are canonicalized without changing their
meaning. Invalid additions trigger repair feedback; additions still ill-typed
after three attempts are explicitly rejected and recorded in
`agents/compiler_repairs.jsonl` and the program's `compiler_rejections` field.
The compiler does not guess the endpoint of ambiguous pair expressions.
Mechanism names are open vocabulary. Raw OSM predicates accept observed
tags beyond the initial documentation catalog. The initial profile shows a
bounded number of frequent tags for context size, not a legal-tag whitelist.

Network routing, travel-time estimation, and physical-facility deduplication
across different OSM elements are not implemented operators. Raw counts refer
to OSM elements; polygon area and line length are clipped to the query geometry.
The parser merges duplicate representations of the same element ID, not two
different elements that happen to describe the same real-world facility.

## Add raw OSM

Supply a dated regional PBF, then:

```powershell
conda run --no-capture-output -n my-neuro python -m mapagents extract-osm `
  --pbf data/raw/new-york.osm.pbf `
  --zones data/processed/new_york/zones.parquet `
  --output data/raw/new_york_objects.parquet
```

Set `data.osm_path` to that output in a new config and use a new output directory.
The PBF reader streams all tagged object types within the study bounding box
and halo. The compiler performs exact zone/buffer intersection in a projected
CRS. An existing GeoParquet/GeoJSON with geometry, CRS, and a `tags` JSON mapping
can also be used. Date and original source should be recorded with the dataset.

## Add your datasets

The generic data interface accepts:

- Zones: `zone_id, region_id, longitude, latitude, area_km2` as CSV/parquet,
  or polygon GeoJSON/GPKG with `zone_id, region_id` and CRS.
- Flows: `origin, destination, flow` as CSV/parquet. Each included origin row
  must be completely observed; omitted internal cells mean zero, not unknown.
- Features: `zone_id` plus named numeric covariates, as CSV/parquet.
- Splits: optional JSON lists `train`, `validation`, `test` containing disjoint
  region IDs. Automatic splitting requires at least three regions.

```powershell
conda run -n my-neuro python -m mapagents prepare-generic `
  --zones data/raw/zones.geojson --flows data/raw/flows.parquet `
  --features data/raw/features.parquet --splits data/raw/splits.json `
  --output data/processed/custom
```

Point a copied config to the prepared directory, set `data.format: generic`,
describe the actual flow semantics in `task`, and choose a new output directory.
Each region defines an entire candidate destination set. To predict a complete
metropolitan matrix, use one metro as a region and its tracts as zones.
For a single new target city, add `--target-only` during preparation, then use
`predict` or `adapt` with a source checkpoint. Training/validation rows for
adaptation are drawn from its explicitly budgeted target support.

## Few-origin adaptation

Adapt a source checkpoint to a budget of complete observed rows from the target
regions (the supplied test regions by default):

```powershell
conda run --no-capture-output -n my-neuro python -m mapagents adapt `
  --config configs/new_york.yaml --source-run runs/new_york_main `
  --budget 0.1 --output runs/new_york_adapt_10pct
```

The budget is a fraction of positive target origins. It includes both target
training and target validation rows. Remaining target rows are held out.
`row_splits.json` and the result's budget record report exact origin, edge and
cell counts. At least two visible positive origins are required. Observed row
totals remain available for production-constrained output scaling. Arbitrary
partially observed edges are not silently converted into complete rows.

Adaptation evaluates fewer rows than the original source run. Compare it with
the source checkpoint on the same `row_splits.json`, rather than comparing the
two runs' headline CPC directly. The `predict` command accepts `--row-splits`
for this purpose.

For another target dataset, use its prepared-data config. The source program's
base covariate names and meanings must be available on that dataset; column
names alone cannot repair incompatible measurement units or definitions.

## Import baseline predictions

Each exported NPZ contains `observed`, `predicted`, `origin_ids`, and
`destination_ids`. Another model may use its own architecture and optimizer.
Export its prediction with matching IDs and evaluate it without implicit
renormalization:

```powershell
conda run -n my-neuro python -m mapagents score `
  --observed runs/new_york_main/predictions/region_10.npz `
  --predicted data/baseline/region_10.npz --output runs/baseline_10.json
```

Use an existing region filename from the output directory. The scorer checks
ordered IDs and uses the standard symmetric CPC denominator. Other metrics
include log-flow Pearson, NRMSE, mean origin-distribution JSD, destination-flow
error, distance error, and row-conservation error. Undefined metrics are null.
Means are region-weighted, not silently pooled across all travelers.

## Implementation status

The public-data run exercises preparation, real retrieval/LLM roles, spatial
program construction, CUDA training, parameter transfer, validation selection,
and full held-out matrix export. Results document this dataset and configuration;
they do not establish commuting performance, causal mechanisms, or a benchmark
improvement over the original published model. Additional datasets and baseline
implementations are intended to enter through the interfaces above.

No test suite is included or run, following the user's instruction. Training
and OD evaluation are the requested end-to-end workload.
