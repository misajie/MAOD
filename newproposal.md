以下是整合所有新增 baseline 后的完整 AAMAS 版本。

---

# MapAgents: Evidence-Grounded Multi-Agent Discovery of Role-Aware Spatial Programs for Origin-Destination Prediction

**Target.** AAMAS 2027 Main Track, Generative and Agentic AI (GAAI).
**Revision.** 14 September 2026. AAMAS-adapted proposal with expanded baseline matrix. Native Deep Gravity on the public New York example has been executed from the original repository (`runs/dgm_native_new_york`; tile CPC 0.4437). Main-table comparisons remain unfilled until Gravity, Radiation, and MapAgents use that checkpoint. Development CPC numbers from `mapagents/training.py` are not paper results.
**Scope.** Three cooperating agents discover executable spatial representations for OD prediction. Deep Gravity remains trainable. The main flow comparison includes Gravity, Radiation, Deep Gravity, MLP on raw OSM, and MapAgents. The agent-mechanism comparison includes LLM feature selection, single-agent (ReAct-style), MALMAS-style multi-agent, and MapAgents.
**Primary artifact.** A spatial program with measured evidence, separate origin and destination roles, and a trace of how its numerical contributions affect predictions.
**Working horizon.** One week for core experiments; two weeks for manuscript.

---

## Abstract

Geographic OD models depend on how raw spatial information is aggregated before prediction. Deep Gravity's 18-variable schema is a consumption-city atlas: it sees restaurants, clinics, schools, and shops, but it does not see warehouses, logistics corridors, industrial employment centers, or cross-barrier commuting structure. When a model built on this atlas systematically underpredicts flows to peripheral industrial zones and overpredicts flows to amenity-dense cores, the error is not statistical noise—it is a labor market that has been written in the wrong vocabulary. A flexible neural predictor can learn interactions among supplied variables, but it cannot recover measurements discarded during aggregation.

We propose MapAgents, a three-agent framework that treats feature construction as an investigation. Surveyor retrieves mobility knowledge and examines raw OpenStreetMap objects, existing aggregation recipes, and local geographic measurements, developing hypotheses about source context, destination opportunities, and their directed relationships. Cartographer compiles these hypotheses into reusable numerical expressions and uses execution feedback to repair invalid or uninformative features. Adapter diagnoses validation errors, compares candidate programs after model training, and directs subsequent investigation. The agent boundary between Surveyor and Cartographer creates a rejection mechanism: invalid hypotheses are caught by a separate agent with different tools, reducing the self-confirmation bias inherent in a single agent that both generates and validates its own proposals. The resulting program augments a trainable Deep Gravity predictor through a learned additive score component, enabling exact decomposition of the program contribution.

The evaluation distinguishes final OD accuracy from the value of agent cooperation. Gravity, Radiation, and Deep Gravity provide flow baselines; an MLP on raw OSM features tests whether brute-force feature availability is sufficient. Fixed feature libraries, non-LLM feature search, LLM feature selection, a single-agent ReAct-style tool loop, and a MALMAS-style multi-agent system without rejection handoffs or role awareness provide progressively richer agent-mechanism controls. Controlled removals of retrieval, endpoint-role reasoning, and feedback examine individual components. New York State provides the initial development case, followed by public European study areas. The central question is whether structured cooperation among agents with different tools and responsibilities produces spatial representations that neither a fixed schema, nor brute-force features, nor a single agent, nor a multi-agent system without rejection handoffs can discover.

**The AAMAS contribution centers on multi-agent cooperation with structured handoffs and feedback. It does not require a new universal law of urban movement, a larger collection of city case studies, or a more complex flow backbone.**

---

## 1. Problem and Research Question

### 1.1 The consumption-city atlas and the employment-city reality

OD prediction estimates how flow from an origin is allocated among candidate destinations. Deep Gravity [3] represents each OD pair using attributes of both endpoints and their geographic distance. Its feature schema covers population, land use, roads, and several facility groups—five land-use areas, three road lengths, and ten facility counts grouped into health, education, food, retail, and transport.

This schema is not neutral. It is an implicit urban economic theory that defines attractiveness through **visible consumption and public service nodes**. This vocabulary works adequately for central districts where retail density, healthcare access, and educational amenity correlate with employment density. It fails systematically for logistics corridors and warehousing districts, where the largest employers carry no POI tag more specific than "industrial"; for campus complexes, where a university represented as a POI count loses its function as a large employer and transit generation source; for cross-barrier commuting belts, where a river or railway severs an employment community that straight-line distance treats as contiguous; and for peripheral industrial zones, where employment growth is real but retail amenity is sparse.

The problem is not that feature values vary across cities. The problem is that **the schema pre-decides which economic activities deserve to be seen**. A downstream neural network can reweight supplied variables, but it cannot recover measurements discarded during aggregation. A hospital and a pharmacy merged into one health count cannot be separated by any nonlinear layer. A logistics park and a row of small warehouses counted as the same number cannot be distinguished by any attention mechanism. The information is gone before the model sees it.

### 1.2 What existing approaches change and what they leave unchanged

The OD prediction landscape has produced several strong but differently-focused advances. Deep Gravity [3] (Nat. Commun.) introduces a neural predictor over geographic features but keeps the fixed 18-variable schema. NeuroGravity [6] (Nat. Comput. Sci.) performs few-shot GNN reconstruction of complete OD matrices from partial observations but uses the same fixed facility/population inputs. GlODGen [9] (Rong et al., Tsinghua FIB-Lab) generates OD flows for global cities from satellite imagery via graph diffusion models but replaces geographic features with satellite pixels, not producing inspectable feature programs. The LODES Benchmark [8] (Rong et al., ICLR 2025) provides a 3,333-area benchmark but benchmarks existing feature schemas rather than questioning what the schema should contain. UrbanGPT (KDD 2024) uses an LLM as a spatio-temporal predictor from fixed features, not as a feature discoverer. LLM mobility simulators (TrajLLM, MobiVerse, LLM-PDM) generate synthetic trajectories or persona-driven mobility, not features for OD allocation models. PI-MPN [7] (IEEE T-ITS) introduces physics-informed neural diffusion for OD flow prediction but augments the predictor, not the representation.

Each of these works changes the **predictor** (neural network, GNN, diffusion model, LLM) or the **data source** (satellite imagery, partial observations, synthetic personas). None changes the **representation**: what geographic measurements are computed, how they are combined, and whose economic activity they make visible. MapAgents targets exactly this layer.

**Why not compare against NeuroGravity, GlODGen, or PI-MPN as flow baselines?** These methods solve different tasks under different setups. NeuroGravity reconstructs a complete OD matrix from partial observations via GNN transfer—it does not discover geographic features. GlODGen generates OD flows from satellite imagery via graph diffusion—it replaces the geographic input modality entirely, making feature-level comparison impossible. PI-MPN augments the predictor with physics-informed diffusion but operates on the same fixed features. Including them as flow baselines would conflate representation discovery with matrix reconstruction, modality substitution, or predictor augmentation—three distinct research questions. The appropriate baselines for representation discovery are methods that operate on the same geographic data and the same prediction task: Gravity, Radiation, Deep Gravity, and brute-force feature expansion. The appropriate baselines for agent-mechanism comparison are methods that use LLM agents for feature generation: MALMAS-style multi-agent, single-agent ReAct-style, and LLM feature selection.

### 1.3 Research question and AAMAS positioning

**Can a multi-agent investigation of geographic evidence and prediction errors discover directed spatial programs that improve OD allocation and provide faithful, inspectable explanations of their numerical contribution?**

This paper targets the multi-agent contribution: how structured cooperation among agents with different tools and responsibilities produces spatial representations that neither a fixed schema, nor brute-force features, nor a single agent, nor a multi-agent system without rejection handoffs can discover. The agents are the mechanism; the program is the artifact; the socioeconomic visibility of labor-market geography is the stake.

---

## 2. Intended Contributions

### Contribution 1: Multi-agent feature discovery with structured rejection

Surveyor, Cartographer, and Adapter coordinate retrieval, numerical execution, and validation-guided revision. Their handoffs carry explicit hypotheses, measurement requests, executable expressions, and observed candidate outcomes. The agent boundary between Surveyor (hypothesis generation) and Cartographer (typed expression compilation with execution feedback) creates a rejection mechanism: invalid hypotheses are caught by a separate agent with different tools, reducing self-confirmation bias. This structure makes it possible to examine where a proposed mechanism originated and whether it survived execution and model evaluation.

### Contribution 2: Role-aware spatial programs

Programs distinguish origin context from destination opportunity and express directional interactions with distance and neighborhood structure. The method moves beyond selecting columns from a fixed table by constructing measurements and compositions from available geographic layers. Cross-barrier terms encode the fact that rivers, railways, and enclosed campuses sever employment communities within a single metropolitan area.

### Contribution 3: Joint prediction and explanation

Deep Gravity and the spatial-program coefficients are trained together. The program branch provides an exact score decomposition, while fixed-model feature removal measures how that branch redistributes predicted flows. Predictive usefulness and explanatory fidelity are evaluated separately.

### Contribution 4: Rewriting the employment-city atlas

The fixed DGM schema is a consumption-city inventory. MapAgents discovers features that make warehouses, industrial corridors, campus employment capacity, and cross-barrier labor-market structure computationally visible. This is not "richer input"—it is a different economic theory of what constitutes destination attractiveness, grounded in measurable geographic evidence.

### Contribution 5: A focused empirical comparison with a graduated baseline matrix

The study compares final OD predictions against Gravity, Radiation, and a faithfully reproduced Deep Gravity baseline, plus an MLP on raw OSM features to test brute-force feature availability. It then isolates the effects of agent design through a graduated matrix: LLM feature selection → single-agent ReAct-style → MALMAS-style multi-agent → MapAgents. Each step adds exactly one design element (agent tool use, multi-agent coordination, rejection handoffs + role awareness). Controlled removals of retrieval, endpoint-role reasoning, and feedback examine individual components. If the thesis is correct—that the consumption-city schema systematically discards employment-relevant geography—then the largest MapAgents improvements should appear on off-diagonal and long-distance flows, where industrial, logistics, and cross-barrier commuting are most relevant.

These are proposed contributions. Neither a performance gain nor a benefit from multiple agents is assumed in advance. But the prior is strong: if the information loss is structural, recovering it should produce measurable, non-trivial improvements.

---

## 3. Research Context

### 3.1 OD prediction landscape

| Research line | Key works | What they change | What they leave unchanged | MapAgents' distinction |
| --- | --- | --- | --- | --- |
| Gravity and radiation [1-4] | Simini et al. (Nature, 2012); Cabanas-Tirapu et al. (Nat. Commun., 2025) | Mass and distance organize OD allocation | The feature schema | Discovers the schema itself |
| Deep Gravity [3, 5, 24] | Simini et al. (Nat. Commun., 2021) | Neural predictor over geographic features | The 18-variable schema and its consumption-city bias | Augments and revises the schema through evidence-grounded discovery |
| Few-shot OD reconstruction [6] | NeuroGravity (Nat. Comput. Sci., 2026) | GNN reconstruction from partial observations | The fixed facility/population input schema | Discovers better geographic programs, not reconstructs from partial OD |
| Large-scale OD generation [8, 9] | Rong et al. (ICLR 2025; 2025) | 3,333-area benchmark; satellite-to-OD via graph diffusion | What geographic features matter | Asks what the schema should measure |
| Physics-informed OD models [7] | PI-MPN (IEEE T-ITS, 2025) | Physics-informed neural diffusion | The representation layer | Changes representation, not just the predictor |

### 3.2 LLM and agent landscape: why MapAgents' cooperation is different

Several multi-agent frameworks establish the value of role separation. MetaGPT [16] assigns software-engineering roles (product manager, architect, engineer) along a production pipeline. CAMEL [17] uses role-playing for task completion. ReAct [15] interleaves reasoning and acting in a single agent. WorldCoder [18] builds world models by writing code. KnowFeat [29] uses knowledge-guided LLM agents for feature engineering. MALMAS [23] (ACL 2026) is the closest in mechanism: a memory-augmented multi-agent system for automated feature generation on tabular data.

MapAgents' cooperation differs from these in three ways:

1. **Rejection-based handoff, not pipeline handoff.** MetaGPT's architect hands off to the engineer, who implements; the handoff is sequential production. MapAgents' Surveyor hands off a hypothesis to Cartographer, who independently checks whether it compiles, executes, and produces non-degenerate numerical behavior. The handoff carries a rejection opportunity: Cartographer can refuse the hypothesis with explicit execution feedback. This rejection mechanism is absent in pipeline-style cooperation. MALMAS uses multiple agents with shared memory, but its agents do not exercise independent rejection authority over each other's outputs—a memory-augmented agent can propose and self-check a feature within the same role.

2. **Residual-driven search control, not task completion.** CAMEL and ReAct complete a fixed task. Adapter in MapAgents does not complete a fixed task—it diagnoses validation residuals, proposes competing measurable explanations, and allocates search budget. The search is open-ended: the number of rounds and the direction of investigation are determined by observed prediction errors, not by a predefined task decomposition.

3. **Geographic semantics, not tabular generality.** MALMAS and KnowFeat operate on generic tabular data. MapAgents' operators are geographic: tag predicates, point/line/polygon aggregation, buffers, centroid neighborhoods, cross-layer proximity, and distance functions. The role-aware construction is specific to ordered OD relationships, not to arbitrary feature columns.

**MALMAS as an experimental baseline.** Because MALMAS [23] is the closest published multi-agent feature-generation system, it is implemented as a baseline in the agent-mechanism comparison (§8.2). The MALMAS-style baseline uses multiple LLM agents with shared memory to generate features from the same expanded feature library and numerical summaries available to MapAgents. It differs from MapAgents in two controlled ways: (1) no rejection-based handoff—agents can propose and self-check features within the same role, as in the original MALMAS design; (2) no role-aware constraints—features are generated as undirected tabular columns, not as directed OD pair expressions. This isolation ensures that any performance difference between MALMAS-style and MapAgents is attributable to the rejection mechanism and role-aware construction, not to the number of agents or the availability of tools.

### 3.3 What is deliberately excluded

NeuroGravity [6] is outside the main experiment: it solves a different problem (matrix reconstruction from partial observations via GNN transfer). Reproducing its architecture would conflate two distinct tasks. Public model-generated OD products (e.g., GlODGen [9]) are not used as ground truth; satellite-derived features are a different input modality. Deep Gravity already separates origin and destination inputs at the concatenation level; the proposed role-aware contribution requires evidence-conditioned directed feature construction and corresponding ablations.

---

## 4. Task and DGM Priors *(Main text: compressed; details in Supplement A)*

### 4.1 Prediction support and supplied totals

For origin $i$, let $\mathcal{D}_i$ be the declared candidate destination set. The target is

$$\hat{T}_{ij} = O_i \, p_{j|i}, \quad O_i = \sum_{j \in \mathcal{D}_i} T_{ij}, \quad \sum_{j \in \mathcal{D}_i} p_{j|i} = 1.$$

The supplied origin total $O_i$ has institutional meaning: LODES residence-to-work matrices record where people live and where they earn wages, not traffic volume. Predicting destination allocation given $O_i$ is predicting job-market access. The study does not predict $\hat{O}_i$; it explains **job spatial choice under known labor supply**.

### 4.2 The consumption-city atlas

The public New York model uses 18 geographic variables per zone. The OD vector is

$$x_{ij}^{\text{DG}} = \text{concat}\left[\log M_i, \, G_i^{18}, \, \log M_j, \, G_j^{18}, \, d_{ij}\right], \quad \dim = 39.$$

The seven geographic families (land use, roads, transport, food, health, education, retail) are a consumption-city inventory. Health collapses regional medical centers and community pharmacies into one count. Education reduces universities to POI counts. Industrial land use records area but not building mass or employment capacity. *(Full decomposition table with "what it collapses" and "what a program could recover" columns: Supplement A.)*

### 4.3 Mass prior and information contract

The public loader constructs mass as $M_z = \sum_{u \in \mathcal{D}_{\text{raw}}} F^{\text{raw}}_{zu}$ from the complete source flow file before within-tile filtering. G, DG, and all agent controls receive the same declared mass prior. The information contract has three parts: raw geography and supplied masses are available for all zones; training OD entries fit parameters; validation supports checkpoint selection, residual diagnosis, and program search; test entries do not guide agents or model selection. *(Full mass prior derivation, zero handling, and area normalization: Supplement A.)*

### 4.4 DG reference restoration

A matching layer count or 39-dimensional input is not sufficient to establish a DGM reproduction. The local original implementation is `resources/deepgravity`. The native reference must be obtained by **running that repository**, not by rewriting it inside `mapagents`. Three layers of the current project still differ; only the first two have been partially repaired.

**Layer 1 — input completeness (partially repaired).** The earlier public-feature loader flattened 18 geographic fields plus five constant-zero polygon placeholders (`food_poly__1`, `health_poly__1`, `retail_poly__1`, `school_poly__1`, `transport_poly__1`) and omitted both endpoint $\log(\texttt{oa2pop})$ variables. That backbone was 23 geographic columns $\times$ 2 endpoints $+$ distance $= 47$ dimensions, not 39. `prepare-dgm-mass` now keeps the 18 first-component geographic columns. The five zero placeholders are absent from the original 18-dimensional vector and must stay absent.

**Layer 2 — mass semantics (repaired only in `dgm_mass`).** DGM's `oa2pop` is not independent population. The public loader sets $M_z=\sum_u F^{\text{raw}}_{zu}$ from the complete source OD file **before** tile filtering; missing or zero values become $10^{-6}$; `main.py` prepends $\log M$ at both endpoints. Destination mass $M_j$ is zone $j$'s **outgoing** total, not its inflow. Only `data/processed/new_york_dgm_mass` restores this. `data/processed/new_york`, `runs/new_york_main`, `runs/new_york_grounded`, the New York gravity baseline, and the London/Barcelona city runs do not.

**Layer 3 — training, splits, and evaluation (not reproduced).** The 15-layer network and 39-dimensional `dgm_mass` input still use this project's trainer. They are not a line-by-line run of the original `main.py` / `data_loader.py` / `models/deepgravity.py`. Verified residual differences against the local original:

| Component | Original DGM (`resources/deepgravity`) | Current `mapagents` trainer | Paper-ready? |
| --- | --- | --- | --- |
| Geographic columns | 18 first components from `oa2features.pkl` | Restored in `dgm_mass`; old loader still has 18+5 zeros | Only `dgm_mass` |
| Mass input | $\log(\texttt{oa2pop})$ prepended in `main.py` | `log(dgm_mass)` in the default program | Only `dgm_mass` |
| Feature scaling | Raw stored values; no z-score. README area-normalization is **not** applied by the New York loader | Signed $\mathrm{log1p}$, training-set standardization, clip $\pm 20$ (this also re-logs the already-logged mass) | No |
| Centroids / distance | Pickle `oa2centroid` + `earth_distance` | Recomputed UTM centroids + haversine | No |
| Architecture | Code: 5$\times$256 + 10$\times$128, LeakyReLU; `instantiate_model` dropout $0$; class default $0.35$ unused. README "bottom six 256-wide layers" does not match the code | Same 5$\times$256+10$\times$128, dropout $0$ | Architecture matches the **code**, not the README |
| Destination sampling | `frac_true_dest=0` $\Rightarrow$ uniform up to 512 locations in the tile; zero-sum rows kept | Uniform up to 512; zero-sum sampled rows skipped | No |
| Loss | Unnormalized $-(y\log p)$ summed over the batch (`od_models.py`). Paper formula is origin-normalized; argparse `batch_size` default is 1, paper text says 64 | `count_weighted`: $-(y\log p)/\sum y$; grounded config `batch_size=32` | No |
| Splits | `train_tiles.csv` vs `test_tiles.csv` only; no validation split | 20% of usable **train** tiles held out; 29 empty train tiles and 30 empty test tiles dropped (5,279 vs 5,367 zones) | No |
| Checkpoint | Last epoch (argparse default 15; paper text 20) | Best validation **off-diagonal CPC**; up to 100 epochs, patience 30. Total matrix CPC is logged and is not the keep rule | No |
| Evaluation | Origin CPC numerator aggregated to **tile** CPC; `tot_flow` is the full-table origin sum, including out-of-tile flow. `common_part_of_commuters` has a $2\sum\hat y$ denominator when `numerator_only=False` | Region-equal matrix CPC on **internal-tile** observed+predicted cells | No |

Keep two records after the native run: (i) original evaluator output (`tile2cpc_*.csv` and the original CPC printout); (ii) common-support matrix evaluation of the **same** predicted flows. Where the source scoring convention and the matrix metric differ, report the difference rather than renaming the formula.

The development measurements CPC/RMSE $0.9105/130.01$ (`runs/new_york_grounded`, no mass, 47-d input) and $0.9285/105.14$ (`runs/new_york_grounded_mass` validation, 39-d input, `mapagents/training.py`) do not meet this requirement. They also sit in a different scoring regime from DGM Table 1 (New York DG vs G improvements of order $10^{3}\%$ on the original tile CPC).

The original repository has now been executed (`runs/dgm_native_new_york`, 14 September 2026): 20 epochs, `batch_size=1`, seed 1234, GPU, unmodified `main.py`. Native tile CPC mean is $0.4437$ (188 test tiles; original `tile2cpc_DG_new_york.csv`). The same predictions scored with this project's matrix CPC on 130 overlapping test tiles give $0.8882$ overall and $0.4311$ off-diagonal. First-layer weights are $256\times 39$. Main-table DG cells stay empty until Gravity/Radiation and MapAgents are run against this checkpoint under a frozen protocol.

---

### 4.5 Working experimental inventory (14 September 2026)

These are local development artifacts. None of them is a paper result.

| Artifact | What it actually is | Can enter the main table? |
| --- | --- | --- |
| `data/processed/new_york` | 5,279 zones, 326 tiles, 130/33/163 split; **23** geographic columns (18 + 5 zero placeholders); no `oa2pop` | No (wrong input) |
| `data/processed/new_york_dgm_mass` | Same support; 18 geographic columns + `dgm_mass`; 39-d backbone **after** origin/destination concat and distance | Input schema only; trainer still ours |
| `runs/new_york_main` | Old 47-d supplied-feature agent run; held-out tile CPC $0.9244$, off-diagonal $0.4567$ | No |
| `runs/new_york_grounded` | No-mass grounded search, stopped at round 0; validation CPC $0.9105$ | No |
| `runs/new_york_grounded_mass` | Mass-restored grounded search; **selected on total matrix CPC**. Reference validation CPC $0.9285$; off-diagonal CPC $0.473$. Rounds 0–1 proposed 16 features then reverted (`selected_epoch=0`) because total CPC did not rise. Round 2 interrupted. This keep rule is withdrawn. | No. Re-run with `selection_metric: offdiagonal_cpc` in a new output directory |
| `runs/new_york_baselines` | Gravity on the **old** no-mass New York data, not `dgm_mass` | No |
| `runs/cities_v1` | London and Barcelona, 3 seeds; G / `mapagents/training.py` DG / MapAgents. Madrid, Paris, Italy not run. DG here is not original `main.py` | No, not until NY native DG exists and the city protocol is restated |
| Historical NY OSM | Geofabrik `new-york-200101.osm.pbf` extracted to `osm_2020_objects.parquet` (3,648,510 objects). OD year remains unknown | Map input for agents; not a DGM snapshot claim |
| `runs/dgm_native_new_york` | Unmodified original `main.py`, 20 epochs, batch 1, seed 1234. Native tile CPC **0.4437**. Common-support matrix CPC 0.8882 / off-diagonal 0.4311. Input dim 39 confirmed in `linear1.weight`. | Native tile CPC is the DG reference for the original evaluator. Do not mix it with project-trainer CPC in one table without naming both formulas. |
| Radiation, MLP-on-raw-OSM, MALMAS-style, single-agent ReAct, LLM feature selection, non-LLM search | Specified in §8; **not implemented** | No |

**Gate status.** Native DGM on New York has been executed. Remaining gate work: freeze this checkpoint as the DG reference; re-fit G and Radiation on `dgm_mass`; do not describe city or agent numbers as "vs Deep Gravity" until they use this reference or an explicitly named adaptation.

---

## 5. Multi-Agent Method

### 5.1 Responsibilities and initialization

| Agent | Evidence available | Decision responsibility | Output |
| --- | --- | --- | --- |
| Surveyor | RAG knowledge, raw OSM, local profiles, declared mass covariates, directed pair profiles | Which measurement or spatial relation could distinguish competing explanations of a residual? | Evidence-backed mechanisms, endpoint-role hypotheses, executable measurement requests |
| Cartographer | Mechanisms, numerical tool results, operator definitions, current program | How should a mechanism become a reusable feature, and does it have informative numerical behavior? | Typed expressions, feature reports, repairs, evidence bindings |
| Adapter | Training/validation protocol, validation residuals, candidate outcomes, search history | Which failures deserve investigation, which edit to retain, and where to spend the next search budget? | Diagnostic targets, accepted program, training configuration, next-round requests |

A standard optimizer fits model weights. Adapter controls the search and fitting workflow; the LLM does not invent gradients or replace numerical optimization.

### 5.2 Why three agents, not one

The agent boundary creates a **rejection mechanism** that is the core multi-agent contribution of this paper. Surveyor proposes hypotheses from retrieved evidence and local dossiers. Cartographer independently checks whether those hypotheses compile, execute, and produce non-degenerate numerical behavior. This separation reduces the self-confirmation bias inherent in a single agent that both generates and validates its own proposals.

A single agent that generates a hypothesis and immediately checks it faces a conflict of interest: it is evaluating its own idea. LLMs are known to exhibit confirmation bias when asked to self-evaluate. By placing the numerical execution check in a different agent (Cartographer) with a different tool surface (the typed expression executor), MapAgents creates an asymmetric verification: Surveyor proposes without knowing whether the expression will execute; Cartographer evaluates without having generated the hypothesis. The rejection is not a disagreement about opinion—it is an execution result: syntax error, undefined column, constant value, duplicate feature, or numerical non-finiteness.

**If the single-agent control (§8.3) performs comparably**, the contribution shifts to "evidence-grounded feature discovery" as a paradigm rather than "multi-agent architecture" as a mechanism. The paper reports whichever result the data supports.

### 5.3 Agent handoff protocol

The three agents communicate through structured handoffs with typed payloads. Each handoff carries information that the receiving agent cannot generate independently.

**Surveyor → Cartographer handoff.** Payload: (1) mechanism description—a natural-language hypothesis about which measurement or spatial relation could distinguish competing explanations; (2) measurement request—a specification of the zone-level or pair-level quantity to compute; (3) evidence link—the specific OSM object IDs, tag queries, or supplied covariates that support the hypothesis; (4) endpoint-role assignment—whether the measurement is an origin-role descriptor, a destination-role descriptor, or a directed pair term; (5) expected reversal effect—the predicted direction of $\phi_k(i,j) - \phi_k(j,i)$.

**Cartographer → Adapter handoff.** Payload: (1) typed expression—the compiled spatial program term with operator type and scope; (2) feature report—distribution, redundancy, within-origin variation, and numerical finiteness statistics; (3) execution status—success, repair count, or rejection with reason; (4) evidence binding—the measurement actually computed and its source objects; (5) candidate fit result—validation off-diagonal CPC, with total CPC/RMSE recorded.

**Adapter → Surveyor handoff.** Payload: (1) diagnostic target—the OD pair or destination zone with the largest residual; (2) correction direction—underprediction or overprediction with magnitude; (3) competing explanations—two or more measurable hypotheses for the failure; (4) search budget—remaining rounds, remaining candidate fits, remaining LLM/tool budget; (5) accepted program—the current best program with its terms and coefficients.

This protocol ensures that each agent's output is inspectable and that the revision history forms a traceable record. A log of fluent LLM reasoning alone is not an explanation; the handoff payloads are the explanation.

### 5.4 Surveyor: retrieval and local investigation

Surveyor uses two complementary evidence sources. Knowledge retrieval covers OSM tag meanings, mobility-related feature organization, and known aggregation recipes. Geographic retrieval executes against the actual study-area objects and covariates.

Local dossiers contain facility tags and source object identifiers, measured counts and geometry, zone area, nearby zones, and zones with similar existing feature vectors. Similar-feature pairs reveal raw-map distinctions collapsed by the original aggregates.

**Observation sparsity and its causes.** OSM tag density follows mapping culture, middle-class interests, and platform economy activity—not employment volume. Warehouses, factories, delivery stations, and informal commerce are sparse on the map. Sparsity does not mean absence of employment; density does not mean presence of the largest employer. Surveyor records observation sparsity and its possible causes, distinguishing real industrial sparsity from mapping-class bias. The open vocabulary allows constructing features like "industrial/warehousing building area adjacent to freight-class roads"—a measurement that acknowledges employment growth where retail POI statistics are blind.

### 5.5 Perceiving distinct origin and destination roles

For a zone $z$, let $r_z^o$ and $r_z^d$ denote numerical role descriptors. A program may construct

$$\phi_k(i,j) = f_k(r_i^o, r_j^d, d_{ij}, \mathcal{N}_i, \mathcal{N}_j).$$

The origin role represents conditions that modulate destination choice: movement scale, facility composition, departure access. The destination role represents candidate opportunities and arrival context. A mixed commercial-residential zone has both roles.

**Concrete example.** If $A_j$ is a measured destination facility count:

$$\phi_{\text{mass,supply}}(i,j) = \log(1 + M_i) \cdot \frac{A_j}{1 + M_j} \cdot \exp(-d_{ij}/h).$$

Reversing endpoints exchanges source and opportunity quantities. A standalone additive term depending only on the origin is constant across its destination row and cancels under softmax; origin context must enter an interacting pair term.

**Cross-barrier terms.** A directed expression can incorporate barrier structure: rivers, railways, enclosed campuses, and limited-access highways that sever employment communities. These are not geometric decoration—they encode that a straight-line distance across a barrier is not the same labor-market distance as the same separation without the barrier.

Each feature records `origin_role`, `destination_role`, the supporting measurements, and the expected effect of swapping endpoints. A directed expression is evaluated as both $\phi_k(i,j)$ and $\phi_k(j,i)$. A nonzero difference demonstrates directional numerical behavior but does not by itself establish the role interpretation.

### 5.6 Cartographer: from hypotheses to spatial programs

A feature program consists of typed zone or pair expressions:

$$P = \{(\text{name}_k, \text{scope}_k, \phi_k, \text{hypothesis}_k, \text{evidence}_k, \text{roles}_k)\}_{k=1}^K.$$

The operator surface includes tag predicates; point/line/polygon aggregation; zone area; buffers; centroid neighborhoods and nearest neighbors; cross-layer geometry proximity; arithmetic and stabilized ratios; and distance functions. Network travel time requires an actual network measurement tool and cannot be inferred from road density.

The executor checks syntax, units, source columns, numerical finiteness, variation, duplication, and evidence references. Failed requests return explicit feedback. An evidence link must identify the specific OSM object or supplied covariate relevant to the expression. Citing a generic overview is insufficient for a new raw-map relation.

### 5.7 Trainable predictor and interpretable program branch

The main design retains the complete DG base representation and augments its score:

$$s_{ij} = g_\theta(x_{ij}^{\text{DG}}) + \sum_{k=1}^K \beta_k \, z_k(i,j), \quad \hat{T}_{ij} = O_i \frac{\exp(s_{ij})}{\sum_{u \in \mathcal{D}_i} \exp(s_{iu})}.$$

All DG parameters $\theta$ and program coefficients $\beta$ remain trainable. The additive program branch makes the program's score contribution explicit and exactly decomposable. A concatenation architecture (feeding discovered features into the DG input) is included as a supplementary comparison; if the additive branch underperforms, the paper reports the accuracy-explanation tradeoff honestly.

### 5.8 Adapter: residual-guided revision

Adapter receives observed and predicted validation values with residuals $r_j = \sum_i (T_{ij} - \hat{T}_{ij})$.

**Residuals as socioeconomic signals.** Systematic underprediction of peripheral industrial zones reads as: warehouse, manufacturing, and freight workers have been rendered invisible by the amenity grammar. Overprediction of core commercial districts reads as: consumption density has been mistaken for employment density. Distance-band residual structure carries economic meaning: short-distance misallocation reflects within-zone mixed-function miscalculation; long-distance misallocation reflects corridor and bridge commuting flattened by straight-line distance.

For each round:
1. Adapter selects a bounded set of failures and proposes competing measurable explanations.
2. Surveyor investigates the associated zones and directed relationships.
3. Cartographer produces candidate edits and responds to execution feedback.
4. Numerical training fits each candidate on training OD rows.
5. Validation scores compare candidates with the incumbent and with further training of the unchanged program.
6. Adapter retains a useful candidate or records that no edit improved the selection objective.

A working development budget is three rounds with two candidates per round. The final budget and stopping rule are fixed before test evaluation. Continuing DG training is an essential control: equal continuation depth is not equal compute, because the agent search evaluates additional candidate models.

---

## 6. Data and Splits *(Main text: compressed; details in Supplement B)*

| Study area | Source and unit | Geographic unit | Role |
| --- | --- | --- | --- |
| New York State | Public DGM example (GeoDS general movement) | Census tracts within native DGM tiles | Initial reference reproduction and agent development |
| Greater London | 2011 Census WU03EW residence-to-work counts | 983 MSOAs | Core external area |
| Paris / Île-de-France | INSEE 2022 census weighted residence-to-work counts | 1,285 communes | Core external area |

Madrid, Barcelona, and Italy are extensions whose inclusion depends on their observation contract. *(Full observation semantics, suppression rules, temporal matching, and spatial split design: Supplement B.)*

For New York, preserve the original test-tile assignment and define validation using only the original training tiles. For other areas, use a fixed spatial origin split when feasible. Training fits parameters; validation selects checkpoints and programs by **off-diagonal CPC** (the New York GeoDS internal matrix is about 89% diagonal, so total CPC does not decide keeps). Test scoring follows the frozen program and protocol and reports total CPC, off-diagonal CPC, RMSE, and off-diagonal RMSE. `runs/new_york_grounded_mass` selected on total CPC and is not a valid program search.

---

## 7. Evaluation *(Main text: compressed; details in Supplement C)*

### 7.1 Primary metrics

Primary accuracy is CPC on declared evaluation cells:

$$\text{CPC} = \frac{2 \sum_{(i,j) \in \Omega} \min(T_{ij}, \hat{T}_{ij})}{\sum_{(i,j) \in \Omega} T_{ij} + \sum_{(i,j) \in \Omega} \hat{T}_{ij}}.$$

**CPC measures matrix overlap, not individual assignment accuracy.** Better CPC means the model places more of the labor-market allocation in the correct destination zones, not that any specific worker is assigned to their actual workplace. RMSE is reported alongside. The main table includes overall and **off-diagonal CPC/RMSE**—off-diagonal metrics are the most socially meaningful, measuring cross-zone job allocation where the consumption-city bias is most damaging. *(Companion metrics, pooling strategy, and cross-area comparison design: Supplement C.)*

### 7.2 Controls summary

All methods share the same OD source, geographic unit, origin split, destination support, mass prior, and evaluation cells. LLM, prompts, and tool budgets are shared across agent controls. Three declared numerical training seeds; agent discovery repeated three times on New York and one external area. DeepSeek is the initial common LLM. *(Full control matrix, seed design, and cost reporting: Supplement C.)*

---

## 8. Main Comparisons and Ablations

### 8.1 Flow baselines (main OD prediction table)

The main table reports five flow-prediction methods. Each operates on the same OD source, geographic unit, mass prior, and evaluation cells. Gravity and Radiation are deterministic physics baselines fitted once. Deep Gravity is the faithfully reproduced neural baseline. MLP on raw OSM tests whether brute-force feature availability without adaptive selection is sufficient. MapAgents adds the discovered role-aware spatial program to Deep Gravity.

NY only, 163 test tiles, `dgm_mass` prior. **CPC below is internal-matrix CPC** (equal-tile mean). It is not the original DGM evaluator (that number for original `main.py` is 0.444 on 188 tiles). Diagonal share is 0.888, so off-diagonal CPC is the informative column. Full audit: `runs/new_york_main_table/REPORT.md`.

| Method | Type | Geographic inputs | CPC | RMSE | Off-diag CPC | Off-diag RMSE |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| Gravity [1] | Deterministic physics | Declared mass prior and distance; fitted deterrence | 0.902 | 148.2 | 0.208 | 137.0 |
| Radiation [1] | Deterministic physics | Declared mass prior and intervening mass | 0.707 | 580.9 | 0.259 | 584.2 |
| Deep Gravity [3] | Neural network | Original `main.py`, 39-d mass+geography, last epoch | 0.911 | 121.8 | 0.431 | 114.2 |
| MLP on raw OSM | Neural network | All extractable OSM tags as high-dimensional feature vector; same mass prior | — | — | — | — |
| **MapAgents + DG** | Neural + discovered program | Same DG inputs plus role-aware spatial program; joint training | 0.935* | 97.0* | 0.513* | 93.2* |

\*MapAgents currently equals `runs/new_york_grounded_mass/reference/model.pt`. That search kept programs by total matrix CPC and is withdrawn. MLP is not run. The next MapAgents run must select by off-diagonal CPC and write a new output directory.

**Gravity and Radiation** are classical physics baselines. Gravity models flow as proportional to $M_i M_j / d_{ij}^\gamma$. Radiation [1] models flow as proportional to $M_i M_j / [(M_i + s_{ij})(M_i + M_j + s_{ij})]$ where $s_{ij}$ is the population within the circle centered at $i$ with radius $d_{ij}$. Both use the same declared mass prior as all other methods. Both are fitted once (no stochastic seeds).

**MLP on raw OSM** replaces the 18-variable DGM aggregation with a high-dimensional vector of all extractable OSM tag counts and area/length measurements per zone—potentially hundreds of features, depending on the study area's OSM richness. This baseline tests whether the key limitation is the *number* of features (can a bigger feature set with a simple neural network match agent-discovered features?) or the *construction* of features (are composed, role-aware, evidence-grounded measurements necessary even when raw tags are available?). The MLP uses the same DG architecture and training protocol, with the input dimension replaced. Feature selection is not applied: the point is to give the network maximum information and see whether it can learn useful representations without adaptive construction.

**Why not include NeuroGravity [6], GlODGen [9], or PI-MPN [7] as flow baselines?** As argued in §1.2, these methods solve different tasks or use different data modalities. NeuroGravity reconstructs OD matrices from partial observations—a different prediction setup. GlODGen generates OD from satellite imagery—a different input modality that cannot be compared at the feature level. PI-MPN augments the predictor with physics-informed diffusion but operates on the same fixed features, making it a predictor-level rather than representation-level comparison. Including them would conflate representation discovery with matrix reconstruction, modality substitution, or predictor augmentation.

### 8.2 Feature-discovery and agent-mechanism controls

The agent-mechanism comparison uses a **graduated baseline matrix**: each row adds exactly one design element to the previous row, isolating the marginal contribution of each mechanism.

| Control | Agents | Handoff type | Role-aware | Residual feedback | Rejection mechanism | Question answered |
| --- | --- | --- | --- | --- | --- | --- |
| DG continuation | 0 | — | — | — | — | Does extra optimization explain the gain? |
| Fixed expanded library + DG | 0 | — | — | — | — | Is richer input sufficient without adaptive discovery? |
| Non-LLM feature search | 0 | — | — | — | — | Is language-guided selection useful beyond numerical search? |
| LLM feature selection (ReAct-style) | 1 | — | ✗ | ✗ | ✗ | Does program construction add value beyond LLM column selection from a library? |
| Single-agent tool loop (ReAct-style) | 1 | — | ✓ | ✓ | ✗ | Does separating investigative responsibilities help? |
| MALMAS-style multi-agent | 3+ | Pipeline (shared memory) | ✗ | ✓ | ✗ | Does rejection-based handoff outperform pipeline handoff? |
| **MapAgents** | **3** | **Rejection** | **✓** | **✓** | **✓** | **Does the complete cooperative workflow add value?** |

**Design of each control:**

**DG continuation.** The original 18-variable DG feature program with additional training epochs and checkpoint selection budget matching the agent search's total compute. This ensures an apparent gain is not attributed to feature discovery when it comes from more fitting.

**Fixed expanded feature library + DG.** A predeclared library of finer tags, scales, mass normalizations, and directed combinations—*including* industrial building area, freight-road adjacency, campus extent, and cross-barrier indicators. This library is constructed before the evaluated search and is available to all library-based controls. It ensures that any MapAgents gain over the fixed library comes from adaptive discovery, not from the library being consumption-biased. The library is fed directly into DG (all features concatenated), without adaptive selection.

**Non-LLM feature search.** The same expanded library is searched under the same candidate-fit allowance using genetic programming or symbolic regression (e.g., gplearn or PySR). This tests whether language-guided selection adds value beyond pure numerical optimization over the same candidate space. The search can construct arithmetic combinations of library features but cannot use retrieval or natural-language reasoning.

**LLM feature selection (ReAct-style).** A single LLM agent, following the ReAct [15] paradigm (interleaved reasoning and acting), selects features from the same expanded library and numerical summaries. The agent can retrieve knowledge, query feature distributions, and request model training, but it *cannot invent expressions outside the library* and *cannot construct directed pair terms*. This isolates the value of program construction (MapAgents' open vocabulary and expression compilation) from LLM-guided selection alone.

**Single-agent tool loop (ReAct-style).** A single LLM agent receives the same knowledge base, the same tools (RAG, map queries, expression executor, model training, validation feedback), and the same total budget (LLM calls, tool queries, candidate fits) as MapAgents. The agent performs all roles—hypothesis generation, expression compilation, execution checking, and residual-guided search—without structured handoffs or a rejection mechanism. The agent can construct directed pair terms and use the full operator surface. The only difference from MapAgents is that one agent does everything, including self-evaluating its own proposals.

**MALMAS-style multi-agent.** Three or more LLM agents with shared memory, following the design of MALMAS [23] (ACL 2026): agents generate feature expressions collaboratively, retain history of proposed features and evaluation results in a shared memory store, and iterate based on validation feedback. The key differences from MapAgents, both controlled: (1) *no rejection-based handoff*—agents can propose and self-check features within the same role, as in the original MALMAS design, rather than having an independent agent reject invalid hypotheses; (2) *no role-aware constraints*—features are generated as undirected tabular columns, not as directed OD pair expressions with origin/destination role descriptors. This baseline isolates the contribution of the rejection mechanism and role-aware construction from the contribution of multi-agent coordination itself.

**MapAgents.** Surveyor, Cartographer, and Adapter with structured rejection handoffs, role-aware directed program construction, and residual-driven search control. This is the complete proposed method.

The graduated design means that the difference between consecutive rows isolates one factor:

| Comparison | Isolated factor |
| --- | --- |
| Fixed library → LLM selection | Value of LLM-guided selection over static availability |
| LLM selection → Single-agent tool loop | Value of program construction (open vocabulary + expression compilation) over library selection |
| Single-agent → MALMAS-style | Value of multi-agent coordination over single-agent self-evaluation |
| MALMAS-style → MapAgents | Value of rejection handoffs + role-aware construction over pipeline coordination |

### 8.3 Focused component removals

| Variant | Single intended change | Evidence |
| --- | --- | --- |
| Without knowledge RAG | Keep map tools; remove retrieved mobility documents | Accuracy, useful candidates, cost |
| Without raw-map investigation | Keep supplied aggregates and mass prior; remove raw object queries | Value of recovered geographic measurements (core of the employment-city thesis) |
| Without role-aware investigation | Remove ordered dossiers, role-specific hypotheses, and reversal feedback; retain directed DG predictor and available operators | Value of explicit endpoint-role reasoning |
| Without Adapter feedback | Propose candidate batch without sequential residual/selection feedback, under same fit allowance | Value of iterative adaptation |
| **Single agent** | Preserve same information and tools; collapse responsibility separation | **Value of multi-agent cooperation (central test)** |

**The single-agent ablation is the central test of the multi-agent contribution.** If the single agent performs comparably to MapAgents, the paper honestly reports this and reframes the contribution as "evidence-grounded feature discovery" as a paradigm. If MapAgents significantly outperforms the single agent, the result supports the claim that the rejection-based handoff between Surveyor and Cartographer, combined with Adapter's residual-driven search control, produces representations that a single self-evaluating agent cannot.

**The "without raw-map investigation" ablation is the central test of the employment-city thesis.** If MapAgents improves primarily through recovered industrial, logistics, and cross-barrier geography, then removing raw-map access should eliminate most of the gain. If the gain persists without raw-map investigation, the improvement comes from adaptive composition of existing aggregates, not from recovered measurements—a different finding reported as such.

---

## 9. Explanatory Evidence and Program Analysis

### 9.1 Traceable representations and the revision log

The explanatory object links an observed map or supplied covariate, a hypothesis, an endpoint-role description, an executed expression, and a numerical model contribution. The residual-driven revision log records where the model first failed and what geographic evidence later corrected it. If the first corrections target peripheral industrial zones, cross-barrier corridors, or campus-employment areas, the log itself documents the process by which the consumption-city atlas was rewritten into something closer to an employment-city atlas.

Automatically report execution success, repair counts, successful measurement coverage for selected features, constant/duplicate rejection, selected program size, and the number of accepted edits. Failed measurements cannot support a feature simply because their request appears in a trace. The automatic artifact is `execution_report.json`.

### 9.2 Exact program contribution

For a trained program branch, report the contribution centered over the complete destination row:

$$c_k(i,j) = \beta_k \left[ z_k(i,j) - \frac{1}{|\mathcal{D}_i|} \sum_{u \in \mathcal{D}_i} z_k(i,u) \right].$$

Remove term $k$ at fixed learned weights, renormalize, and record $\Delta_k(i,j) = \hat{T}_{ij} - \hat{T}_{ij}^{(-k)}$. Report its effect on CPC, RMSE, and the originally diagnosed pairs.

A program term that improves off-diagonal allocation to industrial zones is a policy-grade finding: it says "treating logistics building area as a destination attractiveness component improves labor-market allocation prediction." This is a debatable, inspectable claim—not an opaque weight in a neural network.

### 9.3 Program transfer as labor-market structure test

If city A's discovered program $P_A$ is executed on city B's geography and retains most of its accuracy, the finding is: **two cities share a common structure in how employment geography organizes labor-market allocation.** The program encodes a hypothesis about what makes a destination attractive to workers; if that hypothesis transfers, the employment-geography vocabulary is not city-specific—it is a general feature of metropolitan labor markets that the consumption-city schema systematically omits. Conversely, if transfer fails, the paper reports which terms do not transfer and relates that to measured data without excluding the negative result.

### 9.4 Automatic analysis summary

| Analysis | Automatic output | What it supports |
| --- | --- | --- |
| Execution report | `execution_report.json`: query success, Cartographer repairs, measurement coverage, constant/duplicate rejection, selected program size, accepted edits | A feature is supported only by successful measurements, not by a failed request in the trace |
| Evidence binding | Source object, query, measured value, expression | Traceability |
| Role probes | Ordered endpoint contrasts and reversed values | Directed representation behavior |
| Additive terms | Coefficients and centered score contributions | Exact explanation of program branch |
| Fixed-model removal | Flow, CPC, RMSE changes per term | Predictive fidelity |
| Targeted revision | Requested direction, realized change, error change | Whether an edit addresses its failure |
| Repeatability and cost | Program stability, tokens, queries, fits | Reliability and effort |

No human rater study or manual program audit is included.

---

## 10. Interpretation of Outcomes

- **If MapAgents improves over DG and all controls, with gains concentrated on off-diagonal and long-distance flows:** results support the thesis that recovering employment-relevant geography produces measurable improvements, and that structured multi-agent cooperation discovers these representations better than fixed schemas, brute-force features, single agents, or multi-agent systems without rejection handoffs.
- **If DG improves only after restoring mass inputs:** that is a baseline correction, not evidence for agents.
- **If MLP on raw OSM matches MapAgents:** the gain comes from feature quantity, not from adaptive construction. The contribution shifts to "the problem is feature availability, not feature discovery."
- **If accuracy is similar but program contributions are faithful and useful:** the paper describes the measured accuracy-explanation tradeoff.
- **If MapAgents outperforms the single-agent control but not MALMAS-style:** the gain comes from multi-agent coordination in general, not from rejection handoffs specifically.
- **If MapAgents outperforms MALMAS-style:** the result supports the claim that rejection-based handoffs and role-aware construction outperform pipeline-style multi-agent coordination.
- **If MapAgents and the single-agent control perform comparably:** the contribution shifts to "evidence-grounded feature discovery" as a paradigm, and the paper reports this honestly.
- **If the program head is inactive:** do not claim an interpretable correction.
- **If cross-city program transfer is near-lossless:** report the discovery of a transferable labor-market geographic structure.

The study does not predeclare that tool-free agents fail, that every city needs different tags, or that the multi-agent system is cheaper than a single agent.

---

## 11. Work Plan

Native DGM reproduction is a **gate**, not a parallel workstream. Agent loops, city numbers, and the graduated baseline matrix that currently exist used `mapagents/training.py` and must be rerun or relabeled after the gate.

| Phase | Main output | Completion criterion |
| --- | --- | --- |
| Gate | Execute `resources/deepgravity` on the public New York example; save original `tile2cpc` plus common-support matrix scores; freeze hyperparameters actually used (paper text vs argparse defaults, documented) | **Done 14 September 2026.** Native tile CPC 0.4437 in `runs/dgm_native_new_york`. Residual vs `mapagents/training.py` tabulated in §4.4–4.5. Do not replace this with a rewritten trainer. |
| After gate, NY | Re-fit G and Radiation on `dgm_mass` with the same mass prior; DG continuation under the native protocol; only then MapAgents starting from `runs/dgm_native_new_york/model_DG_new_york.pt` | Main-table G / Radiation / DG cells can be filled; agent search may start from the native checkpoint |
| After gate, controls | Single-agent ReAct, MALMAS-style, LLM selection, MLP on raw OSM, non-LLM search, DG continuation — all unimplemented as of 14 September 2026 | Graduated matrix yields reviewable candidate outcomes on the same NY support |
| External area | London or Paris, three seeds, after NY native DG is frozen | One external area under the same information contract |
| Manuscript | Focused ablations, explanation traces, 8-page draft | Core comparisons complete; main claims map to data |
| Post-rejection fallback | If AAMAS rejects (notification 12/21), revise with reviewer feedback for KDD 2027 Cycle 2 (~Feb) | Addressed all reviewer concerns |

Priority fallback: NY MapAgents from the native DG checkpoint + G/Radiation on `dgm_mass` > one external city > additional agent controls. Do not spend further search rounds on `new_york_grounded_mass` against `mapagents/training.py`. Do not treat London/Barcelona `cities_v1` CPC as a Deep Gravity paper comparison.

---

## 12. Paper Structure (8 pages)

| Space | Content |
| --- | --- |
| 0.8 pp | Problem: consumption-city atlas, information loss, research question, AAMAS positioning |
| 0.5 pp | Related work: distinction from MetaGPT/CAMEL/ReAct/MALMAS/KnowFeat |
| 2.5 pp | Agent responsibilities, handoff protocol, rejection mechanism, directed roles, executable programs, trainable predictor |
| 0.5 pp | Data and splits (compressed; details in supplement) |
| 1.7 pp | Flow baselines (5 methods), agent controls (graduated matrix), focused ablations, expected gain pattern |
| 1.2 pp | Program effects, revision log, transfer test, cost |
| 0.3 pp | Findings, scope, conclusion |
| 0.5 pp | References (within page limit; full bibliography in supplement) |

**Supplement:** A) DGM reconstruction details and prior decomposition; B) Data sources, observation semantics, suppression rules, temporal matching, split design; C) Full control matrix, metrics, pooling, seeds, cost; D) Tool schemas, operator definitions, model settings; E) Per-area metrics, repeat runs, additional program cases; F) MLP raw-OSM feature extraction details and MALMAS-style baseline implementation details.

---

## 13. Reproducibility

Release dataset sources and observation semantics, aligned zone identifiers, destination supports, mass definitions, and split assignments. The agent record includes prompts, LLM identifiers, retrieval sources, tool arguments and responses, candidate programs, rejected edits, validation selection decisions, and actual cost. The prediction record includes complete ordered outputs, fitted feature transformations, checkpoints, and metric definitions. The MLP raw-OSM feature list and the MALMAS-style baseline configuration are released as separate reproducible configurations.

---

## 14. Target Metadata

- **Area:** Generative and Agentic AI (GAAI).
- **Keywords:** multi-agent systems; agent cooperation; rejection-based handoff; retrieval-augmented generation; spatial program discovery; origin-destination prediction; role-aware representations; interpretable prediction.
- **Working title:** MapAgents: Evidence-Grounded Multi-Agent Discovery of Role-Aware Spatial Programs for Origin-Destination Prediction.
- **Central empirical question:** Does structured cooperation among agents with different tools and responsibilities—specifically, rejection-based handoffs and residual-driven search control—produce spatial representations that neither a fixed schema, nor brute-force features, nor a single agent, nor a multi-agent system without rejection handoffs can discover?

---

## References

1. Simini, F., González, M. C., Maritan, A. & Barabási, A.-L. A universal model for mobility and migration patterns. *Nature* **484**, 96–100 (2012).
2. Masucci, A. P. et al. Gravity versus radiation models: on the importance of scale and heterogeneity in commuting flows. *Phys. Rev. E* **88**, 022812 (2013).
3. Simini, F., Barlacchi, G., Luca, M. & Pappalardo, L. A Deep Gravity model for mobility flows generation. *Nat. Commun.* **12**, 6576 (2021). | [AMiner](https://www.aminer.cn/pub/5fc774a991e0114897921269)
4. Cabanas-Tirapu, O. et al. Human mobility is well described by closed-form gravity-like models learned automatically from data. *Nat. Commun.* **16**, 1515 (2025).
5. Atwal, K. S. et al. Commuting flow prediction using OpenStreetMap data. *Comput. Urban Sci.* **5**, 2 (2025).
6. Yang, J. et al. Transferable human mobility network reconstruction with NeuroGravity. *Nat. Comput. Sci.* (2026). | [AMiner](https://www.aminer.cn/pub/69f009929be8eb7c4bdd183e)
7. Wu, X., Pan, T. & He, Z. Physics-informed mobility perception networks for origin–destination flow prediction. *IEEE Trans. Intell. Transp. Syst.* (2025). | [AMiner](https://www.aminer.cn/pub/685de465163c01c850218150)
8. Rong, C., Ding, J., Liu, Y. & Li, Y. A large-scale dataset and benchmark for commuting origin-destination flow generation. In *ICLR* (2025). | [AMiner](https://www.aminer.cn/pub/67e26889163c01c850caa086)
9. Rong, C. et al. Satellites reveal mobility: a commuting origin-destination flow generator for global cities (GlODGen) (2025). | [AMiner](https://www.aminer.cn/pub/682fd5b0163c01c85047a4ab)
10. Lou, S. Urban-MAS: human-centered urban prediction with LLM-based multi-agent system. In *ACM SIGSPATIAL UrbanAI Workshop* (2025). arXiv:2511.00096
11. Xie, F. & Schwertfeger, S. Empowering robotics with large language models: osmAG map comprehension with LLMs. arXiv:2403.08228 (2024).
12. ChatSUMO Agent: an LLM-based agent for conversational traffic simulation in SUMO. *Transp. Res. Part C* (2026).
13. Decoupled intelligence: a multi-agent LLM framework for controllable traffic scenario generation in SUMO (2026).
14. Speak to Simulate: an LLM-guided agentic framework for traffic simulation in SUMO. In *ACM SIGSPATIAL Workshop* (2025).
15. Yao, S. et al. ReAct: synergizing reasoning and acting in language models. In *ICLR* (2023).
16. Hong, S. et al. MetaGPT: meta programming for a multi-agent collaborative framework. In *ICLR* (2024).
17. Li, G. et al. CAMEL: communicative agents for "mind" exploration of large language model society. In *NeurIPS* (2023).
18. Tang, H. et al. WorldCoder, a model-based LLM agent: building world models by writing code and interacting with the environment. In *NeurIPS* (2024).
19. GeoColab: an LLM-based multi-agent collaborative framework for geospatial code generation. *Int. J. Digit. Earth* (2025).
20. GeoJSON Agents: a multi-agent LLM architecture for geospatial analysis—function calling vs code generation. *Big Earth Data* (2026). | [AMiner](https://www.aminer.cn/pub/68c37ca3163c01c85051fa0d)
21. Large language models for mobility data and transport planning. In *IEEE SDS* (2026).
22. A unified experimental evaluation of guardrail mechanisms for LLM agents. In *ICR* (2026).
23. Dong, F., Zheng, Z. et al. Memory-augmented LLM-based multi-agent system for automated feature generation on tabular data (MALMAS). *ACL* (2026). | [AMiner](https://www.aminer.cn/pub/69e96ea59be8eb7c4b5117e7)
24. Yang, Y. et al. Estimating intercity heavy truck mobility flows using the Deep Gravity framework. *Transp. Res. Part E* **169**, 102991 (2023). | [AMiner](https://www.aminer.cn/pub/6532450a939a5f408291cd59)
25. Li, Z. et al. UrbanGPT: spatio-temporal large language models. In *KDD* (2024). | [AMiner](https://www.aminer.cn/pub/65e68af113fb2c6cf6f6d7a0)
26. TrajLLM: a modular LLM-enhanced agent-based framework for realistic human trajectory simulation. In *WWW Companion* (2025). | [AMiner](https://www.aminer.cn/pub/67bfd73e163c01c8506e2b73)
27. MobiVerse: scaling urban mobility simulation with hybrid lightweight domain-specific generator and large language models. In *IEEE ITSC* (2025). | [AMiner](https://www.aminer.cn/pub/6861ef72163c01c850723fc2)
28. LLM-PDM: an LLM persona-driven method for replicating personal mobility preferences at scale. *Commun. Transp. Res.* (2026). | [AMiner](https://www.aminer.cn/pub/69e4fb879be8eb7c4bc412fa)
29. KnowFeat: knowledge-guided feature engineering via LLM agents (2026). | [AMiner](https://www.aminer.cn/pub/6a9a16b40a96f8c83cdba08f)

---

## 改动摘要（相对于上一版 AAMAS 版）

| 位置 | 上一版 | 本版 | 为什么改 |
|------|--------|------|---------|
| Abstract | "Gravity and Deep Gravity provide flow baselines" | 新增 Radiation、MLP on raw OSM、MALMAS-style、ReAct-style 的完整描述 | 审稿人第一眼看到完整的 baseline 矩阵 |
| §1.2 | 简单说明不跟 NeuroGravity/GlODGen 比 | 新增完整段落"Why not include NeuroGravity, GlODGen, or PI-MPN as flow baselines?" | 预防审稿人最常见的攻击：为什么不跟 X 比 |
| §2 贡献 5 | "focused empirical comparison" | 改为"graduated baseline matrix"，明确每步只改一个变量 | 消融设计本身成为贡献 |
| §3.2 | MALMAS 只在 related work 提及 | 新增"MALMAS as an experimental baseline"段落，说明实现方式 | 堵住"最接近竞品没比"的致命缺口 |
| §8.1 | 3 个 flow baseline（G, DG, MapAgents） | 5 个：Gravity, Radiation, DG, MLP on raw OSM, MapAgents | 从 2 个经典 + 1 个 neural 扩展到完整的 representation spectrum |
| §8.2 | 6 个 controls，无 MALMAS | 7 个 controls，新增 MALMAS-style multi-agent，且表格重构为 graduated matrix | 每 consecutive pair 只改一个变量，形成清晰的消融阶梯 |
| §8.2 | 无隔离因子表 | 新增"isolated factor"对照表 | 让审稿人一眼看到每个比较回答什么问题 |
| §8.3 | 5 个 component removals | 不变，但 single-agent 和 without-raw-map 两个消融加粗标注为"central test" | 突出两个最关键消融的地位 |
| §10 | 6 种 outcome | 扩展为 9 种，新增 MLP match、MALMAS-style outperform、MALMAS-style not outperform 三种 | 覆盖新 baseline 的所有可能结果 |
| §11 | Week 1 核心实验列表为"single-agent, LLM selection, DG continuation" | 扩展为完整列表含 MALMAS-style, MLP on raw OSM, Radiation, non-LLM search | 确保 week 1 实验计划覆盖全部 baseline |
| §12 | 实验部分 1.5pp | 扩展为 1.7pp | 5 个 flow baseline + 7 个 agent control + 5 个 removal 需要更多空间 |
| Supplement | A–E | 新增 F: MLP raw-OSM 特征提取细节 + MALMAS-style baseline 实现细节 | 新增 baseline 的可复现性保障 |

**核心变化总结：** baseline 矩阵从"2 个 flow + 6 个 agent control"升级为"5 个 flow + 7 个 agent control + 5 个 component removal"。新增的 MALMAS-style baseline 和 MLP on raw OSM 直接堵住两个最可能被审稿人攻击的缺口，而 graduated matrix 的设计让消融本身成为论文的亮点。

| 位置 | 上一版 | 本版（14 September 2026 实验同步） | 为什么改 |
|------|--------|------|---------|
| §4.4 | 一句“尚未完整复现” | 写明三层差异：47 维旧输入、`oa2pop`/`dgm_mass`、训练/划分/评价仍是项目重建版；并规定 **跑原仓库** 而不是重写 DGM | 上一轮 session 用重建训练器冒充 DGM 复现，已被叫停 |
| §4.5 | 无 | 现有 run 清单与“能否进主表” | 提案正文与磁盘上的实验进度对齐；0.9105 / 0.9285 / `cities_v1` 均不得填主表 |
| §11 | Week 1 并行做 native DG + 全部 control | native DGM 作为硬门；门未过之前不继续 `grounded_mass` 搜特征、不把城市 CPC 写成 DG 比较 | 复现未完成前，agent 数字没有对照基线 |
| §9.1 | 只有分析表，没有强制自动报告句 | 与 AAMAS 稿对齐：自动报告执行成功、修复次数、测量覆盖、恒值/重复拒绝、程序规模、接受编辑；失败测量不能因为出现在 trace 里就支撑特征。产物为 `execution_report.json` | 提案声称必须自动报告，代码与两份文稿此前没有对齐 |