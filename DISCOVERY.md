# Grounded New York Development

This workflow retains the prepared public DGM New York state tract geometries,
tile supports, OD values and heldout tiles. The task is general movement,
not a commuting-only census task. The `discover` command uses individual OD
targets for training and validation and never runs heldout scoring. All map
covariates are visible. The current mass-prior protocol also supplies full-source
OD row sums for every zone, including heldout zones, exactly as the public DGM
loader does. This is an explicit aggregate prior, not a claim of zero label access.

## Agents and Evidence

The implementation borrows the map-survey and local-dossier organization from
`F:/pros/URBANSEM-v07-pure/skills`, while retaining automatic tool use and
validation-guided program search.

1. Adapter receives observed and predicted values, computed error directions,
   separate diagonal totals, destination residuals and individual OD errors.
   Its chosen diagnostic IDs are resolved against the actual validation data;
   incorrect requested directions are corrected and recorded.
2. Surveyor queries a map-only service for local OSM objects, tag hierarchies,
   geographic neighbors, numerically similar zones and executed feature probes.
   Raw queries use exact geometry intersections and preserve OSM element IDs.
   Ordered pair profiles preserve endpoint roles. Pair probes measure forward
   and reversed expressions and their variation over candidate destinations.
3. Surveyor synthesizes hypotheses from successful measured evidence. Each
   Cartographer feature must identify its hypothesis and a valid map evidence ID.
4. Cartographer emits reusable JSON spatial expressions. The compiler rejects
   malformed expressions, constant additions and duplicate numeric inputs.
5. Candidates are trained and compared with a continuation from the same parent.
   Adapter sees the actual validation changes before the next round.

Map summaries have context limits, not a closed attractor vocabulary. Raw tag
queries can inspect observed tags beyond the initial summary. Place names can
identify evidence, but the numerical DSL has no zone-ID lookup or arbitrary code.
All map covariates and the explicitly supplied DGM mass prior are available;
individual OD errors are restricted to training and validation. Standardization
of predictor inputs uses training pairs.

## DGM Aggregation Prior

`resources/priors/deepgravity.json` decomposes the public inputs into 18 geographic
aggregates: five land-use areas, three road lengths, and separate point/polygon
counts for five facility groups. These are prior recipes, not a closed vocabulary.
The second components of five polygon categories are zero placeholders and are
absent from the upstream 18-column vector. The New York pickle values match the
stored first components exactly; no additional area division occurs in the loader,
despite the README describing area normalization.

The public loader's `oa2pop[z]` is the original OD table's complete row sum before
tile filtering. Missing or zero values become `1e-6`; `main.py` prepends `log(oa2pop)`.
Thus each pair has 39 backbone inputs. Our `dgm_mass` names this quantity explicitly:
it is movement volume, not independent census population. Destination mass is the
destination zone's outgoing total, not its incoming total. It can support directed
mass/facility/distance compositions but cannot establish population demographics.
The predictor still applies this project's saved signed-log1p standardization;
this is input-semantic alignment, not a bit-for-bit reproduction of upstream
training, geometry, sampling or normalization.

```powershell
E:/conda/envs/my-neuro/python.exe -m mapagents prepare-dgm-mass --prepared data/processed/new_york --source resources/deepgravity --output data/processed/new_york_dgm_mass
E:/conda/envs/my-neuro/python.exe -u -m mapagents discover --config configs/new_york_grounded_mass.yaml
```

## Predictor and Explanation

For each OD pair, the score is

```text
score(i,j) = DG_theta(base_inputs(i,j)) + sum_k beta_k * z_k(i,j)
prediction(i,j) = given_origin_total(i) * softmax_j(score(i,j))
```

`z_k` is an executable spatial-program feature after signed log1p, training-only
standardization and clipping. All 15 DG hidden layers remain trainable. The
spatial correction coefficients have a separate learning rate and L1 penalty.
The architecture does not constrain DG to be monotone or causally interpretable.
Origin-only additive terms cancel under row softmax and are excluded from the
correction program; origin features can still participate in pair interactions.

`explanations.json` records exact, row-centered score contributions and
validation changes when an individual term is disabled at fixed model weights.
Disabling the head is not a separately trained DG baseline. Feature interventions
are model explanations, not causal changes in real travel demand.

The independent DG comparison receives the same maximum continuation depth.
Agents additionally fit multiple candidate programs and select on validation;
the report states this extra search budget rather than calling it equal compute.
Off-diagonal CPC selects checkpoints and programs. Total matrix CPC, RMSE, JSD
and native-style tile CPC remain visible in the search history. On the New York
GeoDS example the diagonal is about 89% of internal mass, so total CPC does not
decide whether a program is kept. Development numbers are not final paper results.
`runs/new_york_grounded_mass` selected on total CPC and is not a valid program search.

## Historical Map Input

The 2026 OSM extraction was stopped and is not an input to this configuration.
The released DGM OD table has no date column, so an exact OD year has not been
established. The configured 2020 annual archive is a historical development
choice, not a claim to reproduce the original DGM snapshot or an exact year match.
The downloader records the actual PBF timestamp when the header provides one and leaves OD year unknown unless
it is explicitly supported. A missing historical object file stops discovery.

```powershell
E:/conda/envs/my-neuro/python.exe scripts/download_new_york_osm.py --archive-date 200101
E:/conda/envs/my-neuro/python.exe -m mapagents extract-osm --pbf data/raw/new_york/osm/historical/new-york-200101.osm.pbf --zones data/processed/new_york/zones.parquet --output data/processed/new_york/osm_2020_objects.parquet
E:/conda/envs/my-neuro/python.exe -u -m mapagents discover --config configs/new_york_grounded.yaml
```

The reference can be prepared independently of the map download:

```powershell
E:/conda/envs/my-neuro/python.exe -u -m mapagents discover --config configs/new_york_grounded.yaml --reference-only
```

Current outputs live in `runs/new_york_grounded_mass`. The earlier no-mass attempt
is retained in `runs/new_york_grounded`. Completed checkpoints and proposal files
are reused. Change the output directory for a changed configuration. Existing
`runs/new_york_main` and city results are retained.
