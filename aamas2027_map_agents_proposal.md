# MapAgents: Evidence-Grounded Multi-Agent Discovery of Role-Aware Spatial Programs for Origin-Destination Prediction

**Target.** AAMAS 2027 Main Track, Generative and Agentic AI.  
**Revision.** 14 September 2026. Research proposal and experiment plan; empirical claims remain to be established.  
**Scope.** Three cooperating agents discover executable spatial representations for OD prediction. Deep Gravity remains trainable. The main flow comparison is Gravity, Deep Gravity, and MapAgents.  
**Primary artifact.** A spatial program with measured evidence, separate origin and destination roles, and a trace of how its numerical contributions affect predictions.  
**Working horizon.** Four weeks, beginning with New York State and extending to public study areas whose observation support can be established.

---

## Abstract

Geographic OD models depend on how raw spatial information is aggregated before prediction. A fixed feature schema can represent broad land use and facility counts while losing distinctions between facility types, neighborhood scales, and the different functions of a place as an origin and a destination. A flexible neural predictor can learn interactions among supplied variables, but it cannot recover measurements discarded during aggregation.

We propose MapAgents, a three-agent framework for discovering evidence-grounded spatial programs. Surveyor retrieves mobility knowledge and examines raw OpenStreetMap objects, existing aggregation recipes, and local geographic measurements. It develops hypotheses about source context, destination opportunities, and their directed relationships. Cartographer compiles these hypotheses into reusable numerical expressions and uses execution feedback to repair invalid or uninformative features. Adapter diagnoses validation errors, compares candidate programs after model training, and directs subsequent investigation. The resulting program augments a trainable Deep Gravity predictor through a learned additive score component, enabling exact decomposition of the program contribution.

The evaluation will distinguish final OD accuracy from the value of agent collaboration. Gravity and Deep Gravity provide flow baselines; fixed feature libraries, LLM feature selection, single-agent tool use, and controlled removals of retrieval, endpoint-role reasoning, and feedback examine the proposed mechanism. CPC, RMSE, and off-diagonal performance measure prediction quality. Executed evidence links, feature interventions, and responses on diagnosed OD pairs measure explanatory fidelity. New York State provides the initial development case, followed by public European study areas with documented flow semantics. The central question is whether coordinated investigation produces useful and verifiable spatial representations beyond those obtained from fixed aggregation or a single feature-selection agent.

---

## 1. Problem and research question

OD prediction estimates how flow from an origin is allocated among candidate destinations. Depending on the source, the flow may represent general movement, commuting people, or weighted census estimates. These meanings remain explicit for each dataset. The present task supplies origin totals and predicts destination allocation; it does not introduce a separate model of total trip production.

Deep Gravity [3] represents each OD pair using attributes of both endpoints and their geographic distance. Its feature schema covers population or mass, land use, roads, and several facility groups. The schema is shared across places, while feature values and learned nonlinear responses can differ. The research gap is the information lost when raw geography is reduced to that schema.

Several distinctions motivate a richer representation. A hospital and a pharmacy may have different spatial roles despite sharing a health category. A campus can be described through land area, buildings, surrounding services, and access to transport. Facility counts can be interpreted relative to source movement scale or competing opportunities nearby. The same transport facility can describe departure access at one endpoint and arrival access at the other. These alternatives concern what is measured and how measurements are combined.

MapAgents treats feature construction as an investigation. An agent must identify the missing distinction, retrieve or compute relevant evidence, express it as a spatial program, and assess the resulting prediction change. Functional roles are open and potentially mixed: a zone can support residence, services, education, and transport simultaneously. A role is a hypothesis about the function of measured geography in an ordered OD relationship, not a categorical identity assigned permanently to a place.

**Research question.** Can a multi-agent investigation of geographic evidence and prediction errors discover directed spatial programs that improve OD allocation and provide faithful, inspectable explanations of their numerical contribution?

The AAMAS contribution centers on cooperation among agents with different responsibilities and feedback. It does not require a new universal law of urban movement, a larger collection of city case studies, or a more complex flow backbone.

---

## 2. Intended contributions

**Evidence-grounded feature discovery.** Surveyor, Cartographer, and Adapter coordinate retrieval, numerical execution, and validation-guided revision. Their handoffs carry explicit hypotheses, measurement requests, executable expressions, and observed candidate outcomes. This structure makes it possible to examine where a proposed mechanism originated and whether it survived execution and model evaluation.

**Role-aware spatial programs.** Programs distinguish origin context from destination opportunity and express directional interactions with distance and neighborhood structure. The method moves beyond selecting columns from a fixed table by constructing measurements and compositions from available geographic layers.

**Joint prediction and explanation.** Deep Gravity and the spatial-program coefficients are trained together. The program branch provides an exact score decomposition, while fixed-model feature removal measures how that branch redistributes predicted flows. Predictive usefulness and explanatory fidelity are evaluated separately.

**A focused empirical comparison.** The study compares final OD predictions against Gravity and a faithfully reproduced Deep Gravity baseline, then isolates the effects of LLM selection, tools, role separation, and iterative feedback. The intended evidence spans several public study areas, multiple training seeds, and automatic explanation measurements.

These are proposed contributions. Neither a performance gain nor a benefit from multiple agents is assumed in advance.

---

## 3. Research context

The existing references provide context for five lines of work. Their bibliography is retained in this revision without a new citation review.

| Research line | Relevance to MapAgents | Comparison or distinction |
| --- | --- | --- |
| Gravity, radiation, and learned gravity-like expressions [1-4] | Mass and distance organize OD allocation | Gravity is a main flow baseline; the proposed novelty concerns representation discovery |
| Deep Gravity and geographic flow prediction [3, 5, 24] | Geographic measurements support flexible predictors | DGM aggregation recipes are shared prior knowledge; programs can recover finer measurements |
| Tool use, role coordination, and automated feature generation [15-18, 23] | Retrieval, execution, and feedback support agent decisions | Single-agent tool use and LLM feature selection are substantive controls |
| Geospatial agents and mobility applications [10-14, 19-21] | Spatial evidence requires tools and explicit geographic semantics | MapAgents produces numerical programs linked to OD prediction and measurable feature effects |
| Cross-area reconstruction and large-scale OD resources [6, 8, 9] | Transfer and broader geographic evaluation are useful extensions | They do not determine the four-week core comparison |

NeuroGravity is outside the main experiment. Reproducing or redesigning its multi-stage model would introduce a separate architecture and task-alignment problem. The proposed study uses G and DG as its principal flow references and concentrates effort on the agents. Public model-generated OD products are not used as ground truth.

Deep Gravity already separates origin and destination inputs. The proposed role-aware contribution therefore requires evidence-conditioned directed feature construction and corresponding ablations; merely naming the two endpoints is insufficient.

---

## 4. Task, DGM priors, and information availability

### 4.1 Prediction support and supplied totals

For origin $i$, let $\mathcal D_i$ be the declared candidate destination set. It contains all retained zones in its DGM tile for the native New York example, or all zones in the declared study area for a complete-area task. The target is

$$
\widehat T_{ij}=O_i p_{j\mid i},\qquad
O_i=\sum_{j\in\mathcal D_i}T_{ij},\qquad
\sum_{j\in\mathcal D_i}p_{j\mid i}=1.
$$

Inference evaluates and normalizes over the complete declared destination set. Computational batches do not define separate softmax denominators. Diagonal cells are retained when present in the source and are reported separately in the analysis.

The New York tile task is a collection of complete within-tile matrices. It is not a complete New York State matrix: cross-tile pairs lie outside its prediction support. A whole-area extension changes the task and receives a separate experiment label.

### 4.2 Decomposing the public DGM feature construction

The public New York model uses 18 geographic variables per zone. These aggregation patterns form a prior catalog available to all feature-discovery methods.

| Family | Number per zone | Aggregation recipe | Candidate extensions |
| --- | ---: | --- | --- |
| Land use | 5 | Areas for residential, commercial, industrial, retail, and natural classes | Area fractions, mixed-use composition, neighborhood context |
| Roads | 3 | Lengths of residential, main, and other roads | Metric length density, road-class composition, measured cross-layer proximity |
| Transport | 2 | Separate point and polygon counts | Facility subtype, departure/arrival context, nearby opportunities |
| Food | 2 | Separate point and polygon counts | Finer amenity groups, scale, mass-normalized supply |
| Health | 2 | Separate point and polygon counts | Distinguish institutions and local services through observed tags |
| Education | 2 | Separate point and polygon counts | School/university distinctions, campus extent, transport relations |
| Retail | 2 | Separate point and polygon counts | Store types, commercial clusters, neighboring alternatives |
| Mass | 1 | Full-source OD row sum, then natural logarithm for the DGM input | Directed mass/facility/distance compositions |

The OD vector is

$$
x_{ij}^{\mathrm{DG}}
=\operatorname{concat}\!\left[
\log M_i,\ G_i^{18},\ \log M_j,\ G_j^{18},\ d_{ij}
\right],
\qquad \dim x_{ij}^{\mathrm{DG}}=39.
$$

The supplied New York geographic vector has been checked against the local stored representation: the 18 values in `oa2features.pkl` match the first component of the 18 named aggregates on all 5,367 shared zones. Five polygon fields also contain a second component in the JSON source; these components are constant zero and do not enter the original 18-dimensional vector.

The README describes area normalization. The public New York loader instead reads the stored vector and prepends the log-mass variable without applying an additional area division. A reproduction must follow the executed data path. Newly recomputed OSM areas and lengths use documented projected units; the unusually small stored upstream values are not silently relabeled as valid physical measurements.

These seven geographic families are starting recipes, not a closed attractor vocabulary. Surveyor may investigate any observed tag or supported spatial relationship. Operator typing controls whether an expression can execute; it does not restrict discoveries to a fixed list of semantic categories.

### 4.3 DGM mass prior

The public loader names its mass variable `oa2pop`, but constructs it as

$$
M_z=\sum_{u\in\mathcal D_{\mathrm{raw}}}F^{\mathrm{raw}}_{zu}.
$$

This sum is computed from the complete source flow file before within-tile filtering. Missing or zero values are replaced by $10^{-6}$ before taking the logarithm. At the destination endpoint, $M_j$ is the outgoing total of zone $j$, not its incoming total and not an independent census population count.

The main New York protocol will retain this definition. G, DG, and the relevant agent controls receive the same declared mass prior. $M_i$ can differ from the internal prediction total $O_i$, because their destination supports differ. An amenity-to-mass ratio is interpreted as facilities relative to recorded movement volume, not facilities per resident.

The information contract has three parts:

- Raw geography, geographic identifiers, prior recipes, and the supplied zone masses are available for all zones.
- Training OD entries fit numerical parameters. Validation OD entries support checkpoint selection, residual diagnosis, and program search.
- Final test OD entries, test residuals, and test scores do not guide agents or model selection.

The source masses include aggregate information from validation and test zones by design. This is conditional OD allocation with supplied aggregate priors, not prediction with no target-area flow information. The map tool can expose those prepared covariates without exposing the underlying OD rows. For another dataset, the mass source and its geographic support must be stated explicitly; suppressed or partial source rows cannot silently stand in for a complete total.

### 4.4 Restoring a credible DG reference

A matching layer count or 39-dimensional input is not sufficient to establish a DGM reproduction. The planned reference must resolve the following against the local original implementation before it supplies paper results.

| Component | Required agreement or explicitly named adaptation |
| --- | --- |
| Inputs | The 18 actual geographic columns, both log-mass variables, their order, zero handling, and distance |
| Preprocessing | The stored feature vector, geometry and centroid conventions, logarithms, and any scaling |
| Architecture | The full original network, activations, dropout, and parameter initialization |
| Training | Destination sampling, target construction, count-weighted objective and reduction, optimizer, epochs, and checkpoint policy |
| Splits and support | Original tile assignments for the native case; any separate validation split and exclusions documented |
| Prediction and evaluation | Native output/scoring behavior reproduced; paper matrices also scored on the explicitly declared support |

Keep two records: native DGM reproduction results, and common-support matrix evaluation of the resulting predictions. Where a source scoring convention and the matrix metric differ, report the difference rather than changing the formula under the same name. A benchmark adaptation must be identified as such.

The earlier development references, CPC/RMSE $0.9105/130.01$ and $0.9285/105.14$, do not meet this complete reproduction requirement. The second restored mass inputs and changed the input schema while retaining the project's own preprocessing and training choices. They are development validation measurements, not original DG results or evidence of an agent improvement. Main-table cells remain unfilled until the reference is rebuilt.

---

## 5. Multi-agent method

### 5.1 Responsibilities and initialization

Surveyor is the first investigative layer. The initial pass begins with source metadata, the DGM aggregation prior, raw map objects, and retrieved mobility knowledge. A separately fitted DG reference can then supply development residuals. In later rounds Adapter directs new investigations.

| Agent | Evidence available | Decision responsibility | Output |
| --- | --- | --- | --- |
| Surveyor | RAG knowledge, raw OSM, local profiles, declared mass covariates, directed pair profiles | Which measurement or spatial relation could distinguish competing explanations? | Evidence-backed mechanisms, endpoint-role hypotheses, and executable measurement requests |
| Cartographer | Mechanisms, numerical tool results, operator definitions, current program | How should a mechanism become a reusable feature, and does it have informative numerical behavior? | Typed expressions, feature reports, repairs, and evidence bindings |
| Adapter | Training/validation protocol, validation residuals, candidate outcomes, search history | Which failures deserve investigation, which edit to retain, and where to spend the next search budget? | Diagnostic targets, accepted program, training configuration, and next-round requests |

A standard optimizer fits model weights. Adapter controls the prescribed search and fitting workflow; the LLM does not invent gradients or replace numerical optimization.

### 5.2 Surveyor: retrieval and local investigation

Surveyor uses two complementary evidence sources. Knowledge retrieval covers OSM tag meanings, mobility-related feature organization, and known aggregation recipes, drawing on the local `resources/LLMrag` collection. Geographic retrieval executes against the actual study-area objects and covariates.

Local dossiers contain facility tags and source object identifiers, measured counts and geometry, zone area, nearby zones, and zones with similar existing feature vectors. Similar-feature pairs are especially useful: they can reveal raw-map distinctions collapsed by the original aggregates. Observed tag frequency describes the available map; it does not measure real-world mapping completeness.

Surveyor can request:

- zone profiles and tag-specific object retrieval;
- area, length, count, density, neighborhood, and cross-layer measurements;
- profiles that preserve the ordering of an origin-destination pair;
- feature probes that return distributions, redundancy, and within-origin variation;
- directed pair probes that evaluate the same expression before and after endpoint reversal.

The URBANSEM skill organization informs these local dossiers and cross-layer investigations. The study retains the DGM task and predictor rather than importing URBANSEM's NG-specific feature assumptions.

### 5.3 Perceiving distinct origin and destination roles

For a zone $z$, let $r_z^{o}$ and $r_z^{d}$ denote numerical role descriptors constructed by executable expressions. They can use the same raw evidence with different transformations or neighborhoods. The descriptors need not form mutually exclusive classes or sum to one.

A program may construct

$$
\phi_k(i,j)=f_k(r_i^{o},r_j^{d},d_{ij},\mathcal N_i,\mathcal N_j).
$$

The origin role represents conditions that can modulate destination choice, such as movement scale, facility composition, or departure access. The destination role represents candidate opportunities and arrival context. A mixed commercial-residential zone may have both roles, and its relationship to a neighboring center can differ from its relationship to a distant institution.

Examples of candidate forms include origin mass interacting with destination facility supply; destination supply relative to its movement mass; origin land-use composition paired with a different destination composition; and departure/arrival contexts combined with a distance basis. These are hypotheses to measure, not explanations established by their names.

For example, if $A_j$ is a measured destination facility count, a candidate can express

$$
\phi_{\mathrm{mass,supply}}(i,j)
=\log(1+M_i)\,\frac{A_j}{1+M_j}\,\exp(-d_{ij}/h).
$$

Here the origin supplies movement context, the destination supplies facility intensity relative to its movement mass, and $h$ specifies a distance scale. The unit pseudocount regularizes zero mass. The role hypothesis, denominator, and scale must be supported or selected within development; the fitted coefficient and final softmax determine the prediction effect. Reversing endpoints exchanges the source and opportunity quantities. Other role constructions remain available, and none is required to improve prediction merely because it has this form.

Each feature records `origin_role`, `destination_role`, the supporting measurements, and the expected effect of swapping endpoints. A directed expression is evaluated as both $\phi_k(i,j)$ and $\phi_k(j,i)$. A nonzero difference demonstrates directional numerical behavior, but does not by itself establish that the proposed role interpretation is correct.

A standalone additive term depending only on the origin is constant across its destination row and cancels under softmax. Origin context must therefore enter an interacting pair term if it is to affect the program branch. Symmetric relations remain valid candidates when appropriate; directionality is not enforced by arbitrary asymmetry.

### 5.4 Cartographer: from hypotheses to spatial programs

A feature program consists of typed zone or pair expressions:

$$
P=\{(\mathrm{name}_k,\mathrm{scope}_k,\phi_k,\mathrm{hypothesis}_k,
\mathrm{evidence}_k,\mathrm{roles}_k)\}_{k=1}^{K}.
$$

The operator surface includes tag predicates; point/line/polygon aggregation; zone area; buffers; centroid neighborhoods and nearest neighbors; actual geometry proximity between layers; arithmetic and stabilized ratios; and distance functions. Network travel time or centrality requires an actual network measurement tool and cannot be inferred from road density.

Semantic categories and program width are open. Execution resources are bounded: a candidate adds a small number of focused terms, and repair attempts have a fixed budget. The same program applies across the study area. Place names and zone IDs can locate evidence, but are not numerical lookup rules in the predictor.

The executor checks syntax, units where available, source columns, numerical finiteness, variation, duplication, and evidence references. Failed requests return explicit feedback. New feature names cannot be used as if they were raw source columns unless a documented reference-expansion mechanism exists.

An evidence link must identify the measurement relevant to the expression. Citing any successful overview is insufficient for a new raw-map relation. A candidate reports whether it adds a finer semantic group, a new aggregation scale, a cross-layer relation, or a composition of existing variables. These distinctions support the feature-library controls.

### 5.5 Trainable predictor and interpretable program branch

The main design retains the complete DG base representation and augments its score:

$$
s_{ij}=g_\theta(x_{ij}^{\mathrm{DG}})
+\sum_{k=1}^{K}\beta_k\,z_k(i,j),
\qquad
\widehat T_{ij}
=O_i\frac{\exp(s_{ij})}{\sum_{u\in\mathcal D_i}\exp(s_{iu})}.
$$

Here $z_k$ is a compiled feature after a documented transformation fitted on training data. All DG parameters $\theta$ and program coefficients $\beta$ remain trainable. Program changes can add or remove terms and transfer compatible parameters by expression identity. Separate learning rates and modest regularization for the program branch are development choices to fix before final evaluation.

DG itself can accept different feature dimensions. The additive program branch is the primary proposal because it makes the program's score contribution explicit. Concatenating discovered features into a flexible DG input is a possible supplementary architecture comparison, not a substitute for completing the main agent experiment.

The base inputs remain available to the predictor. Reusing mass in distinct pair compositions is permitted; a blanket rule allowing population only once would exclude legitimate nonlinear relationships. Numerical duplication and within-row degeneracy are checked at the expression level.

### 5.6 Adapter: residual-guided revision

Adapter receives observed and predicted validation values with residuals defined as $T-\widehat T$, together with computed underprediction/overprediction directions. Diagnostic targets include off-diagonal pairs, destination totals, distance bands, and self-flow allocation. Claims about a residual's direction are checked against its numerical record.

For each round:

1. Adapter selects a bounded set of failures and proposes competing measurable explanations.
2. Surveyor investigates the associated zones and directed relationships.
3. Cartographer produces candidate edits and responds to execution feedback.
4. Numerical training fits each candidate on training OD rows.
5. Validation scores compare candidates with the incumbent and with further training of the unchanged program.
6. Adapter retains a useful candidate or records that no edit improved the selection objective.

A working development budget is three rounds with two candidates per round. The final budget and stopping rule are fixed before test evaluation. Continuing DG training is an essential control, but equal continuation depth is not equal compute: the agent search evaluates additional candidate models.

The loop transfers both program information and compatible numerical parameters when useful. It does not require frozen weights or assume that changing program text is cheaper than model fitting.

---

## 6. Data and four-week scope

New York is the initial debugging and method-development area. London and Paris are the intended core external areas; Madrid and Barcelona provide additional settings once their suppression and support rules are handled. Italy remains a separately documented extension. The goal is a small set of scientifically usable settings, not a claim that a particular city count guarantees publication.

| Study area | Local source and unit | Geographic unit | Role in the plan |
| --- | --- | --- | --- |
| New York State | Public DGM example derived from GeoDS general movement; exact OD observation date unresolved | Census tracts within native DGM tiles | Initial reference reproduction and agent development |
| Greater London | 2011 Census WU03EW residence-to-work counts, in people | 983 MSOAs | Core external area after establishing missing-pair semantics |
| Paris / Ile-de-France | INSEE 2022 census reference-year weighted residence-to-work counts; 2025 geographic codes | 1,285 communes and Paris arrondissements | Core external area; retain weights and geographic version |
| Madrid province / autonomous community | INE 2023 registered residence-to-work counts | 179 municipalities | Extension with explicit suppression handling |
| Barcelona province | INE 2023 registered residence-to-work counts | 311 municipalities | Extension with explicit suppression handling |
| Italy | ISTAT 2011 municipality residence-to-work counts | Municipalities; any study-area subset declared before fitting | Optional cross-country extension, not the original DGM census-area benchmark |

The Italy municipal files do not reconstruct the original census-area OD experiment. Likewise, the London MSOA table is not a reproduction of the original England OA experiment. Neither source is described as categorically closed merely because the exact paper slice is unavailable.

The Spanish release publishes combinations with at least five employed people. Unpublished pairs cannot be turned into true zeros. If complete target totals and observation semantics cannot support the full-matrix task, those datasets receive a separate censored-observation analysis or remain outside the main accuracy table. For all sparse sources, distinguish unreported pairs, suppressed values, and documented zeros before constructing dense targets.

Internal and external flows remain separate. Internal prediction totals sum only over internal destinations. Special workplace categories without a zone geometry are not assigned artificial polygons.

New York now has a historical OSM archive with nominal date **2020-01-01**. It is a historical development choice; its exact match to the OD observation date is not established. The 2026 New York snapshot is not an input to the main workflow. Other areas require their own recorded temporal relationship between OD and map data; a current snapshot is never described as same-year data. No additional downloads are part of this document revision.

---

## 7. Evaluation and controlled variables

### 7.1 What must be shared

Flow baselines may retain their own architecture, optimizer, feature transformations, and training settings. Their comparison must nevertheless concern the same target quantities.

| Control | Flow-model comparison | Agent-mechanism comparison |
| --- | --- | --- |
| OD source, geographic unit, year, and observation mask | Same within a dataset | Same |
| Origin split and destination support | Same declared benchmark support | Same |
| Supplied totals and mass information | Same information contract; differences receive a separate label | Same |
| Raw data available | Document each model's intended inputs | Same map, prior, and retrieval access except the ablated component |
| Architecture and optimization | Native, scientifically documented settings | Same DG/program architecture and fitting protocol |
| Hyperparameter and validation access | Document each method's selection procedure | Same candidate evaluation allowance |
| LLM, prompts, and tool budgets | Not applicable to G/DG | Same base LLM and comparable total budgets, with actual costs reported |
| Prediction scoring | One evaluator on aligned matrices | Same |

A native DGM reproduction is recorded before adaptations for a common benchmark. Rebuilding the DGM aggregation prior from historical raw OSM is another identifiable feature version; it must not silently replace the original stored baseline.

### 7.2 Splits and model selection

For New York, preserve the original test-tile assignment and define validation using only the original training tiles. Any removal of invalid or empty supports is documented independently of model performance. For other areas, use a fixed spatial origin split when feasible and distinguish it from an origin-random split. An existing random split can be retained as a separately named evaluation, not relabeled as spatial generalization.

Training fits parameters; validation selects checkpoints and programs by **off-diagonal CPC**. Total matrix CPC is recorded and does not decide keeps on the New York GeoDS example (internal diagonal share about 0.89). Test scoring follows the frozen program and protocol and reports total CPC, off-diagonal CPC, RMSE, and off-diagonal RMSE. `runs/new_york_grounded_mass` selected on total CPC and is not a valid program search. A complete origin row is the preferred supervised unit under row-normalized prediction. Randomly exposing isolated positive edges does not provide an equivalent destination distribution.

The selected program can use all geographic covariates and the declared mass prior. Test geographic IDs are therefore not themselves forbidden prompt content. What remains unavailable during development is test pair-level supervision and performance feedback.

### 7.3 Prediction metrics

Primary accuracy is CPC on the declared evaluation cells $\Omega$:

$$
\mathrm{CPC}
=\frac{2\sum_{(i,j)\in\Omega}\min(T_{ij},\widehat T_{ij})}
{\sum_{(i,j)\in\Omega}T_{ij}+\sum_{(i,j)\in\Omega}\widehat T_{ij}}.
$$

When total mass is equal, CPC equals $1-\|T-\widehat T\|_1/(2\sum T)$. It measures matrix overlap, not the fraction of identified individuals sent to their actual destination.

RMSE is reported alongside CPC:

$$
\mathrm{RMSE}
=\sqrt{\frac{1}{|\Omega|}\sum_{(i,j)\in\Omega}
(T_{ij}-\widehat T_{ij})^2}.
$$

Companion metrics are NRMSE using the standard deviation of observed values on $\Omega$, Pearson correlation of `log1p` flows, and mean row-wise Jensen-Shannon divergence over positive observed rows using natural logarithms. Row-wise JSD compares destination allocations rather than a histogram of cell magnitudes. Undefined statistics are reported as such.

The main table includes overall and off-diagonal CPC/RMSE. Off-diagonal metrics use the off-diagonal cells directly without rescaling the remaining flows. Diagonal observed/predicted shares, destination-total error, and distance-band allocation provide compact diagnostics.

For multiple tiles, pooled matrix metrics and equal-tile means are different summaries. Main matrix metrics pool the declared cells; native DGM tile summaries are reported separately. Current development logs contain equal-tile means and cannot be copied into a pooled-matrix column. Scores from single-zone tiles and the fraction of self-flow are visible; regions are not removed after observing that they favor a baseline.

Cross-area summaries use dimensionless paired changes or equal-area ranks. Raw RMSE values are kept per dataset because movement counts and weighted commuting people have different scales and meanings.

### 7.4 Seeds and LLM variation

Use three declared numerical training seeds for stochastic models in the main comparison, with the data split fixed. A deterministic Gravity fit is reported once. For a fixed discovered program, the repeated runs measure fitting variability. Report mean and standard deviation without treating the runs as independent cities.

On New York and one external area, repeat the entire agent discovery three times to measure program-search variability. Reusing a single program across three model seeds is not an end-to-end multi-agent reproducibility result. Agent repeats and training repeats are reported separately rather than expanded into an unnecessary factorial experiment.

DeepSeek is the initial common LLM for all roles and LLM controls; record the exact model identifier, parameters, and run date. A second LLM on New York and one external area is a secondary portability study after the core comparisons. Full repetition of every city, seed, and LLM combination is outside the four-week core.

### 7.5 Cost and information budget

Record successful and failed LLM calls, prompt/completion tokens, retrieval calls, tool queries, rejected programs, candidate fits, training time, and end-to-end time. A multi-agent system is not credited with equal compute merely because it uses the same number of rounds as a single agent.

Within the agent table, compare under fixed candidate-fit and LLM/tool ceilings and report actual consumption. A supplementary cost-versus-quality curve can reveal whether a gain survives comparable search expenditure.

---

## 8. Main comparisons and ablations

### 8.1 Main OD prediction table

The core table uses G, DG, and MapAgents. Gravity's power and exponential distance variants may be shown as two rows or selected on validation with the choice declared. Each uses the documented mass prior and the same output-total condition.

NY only, 163 test tiles, `dgm_mass` prior. CPC is internal-matrix CPC, not the original DGM evaluator (0.444 on 188 tiles). Diagonal share 0.888; off-diagonal CPC is the informative column. Audit: `runs/new_york_main_table/REPORT.md`.

| Method | Mass and geographic inputs | CPC | RMSE | Off-diagonal CPC | Off-diagonal RMSE |
| --- | --- | ---: | ---: | ---: | ---: |
| Gravity | Declared mass prior and distance; fitted deterrence parameters | 0.902 | 148.2 | 0.208 | 137.0 |
| Deep Gravity | Original `main.py`, 39-d mass+geography, last epoch | 0.911 | 121.8 | 0.431 | 114.2 |
| MapAgents + DG | Same base inputs plus discovered role-aware spatial program; joint training | 0.935* | 97.0* | 0.513* | 93.2* |

\*Currently identical to `runs/new_york_grounded_mass/reference/model.pt`. That search kept programs by total matrix CPC and is withdrawn. The next MapAgents run must select by off-diagonal CPC and write a new output directory.

Repeat the block for each eligible dataset; display three-seed summaries. The main table does not force classical gravity through a neural architecture and does not contain a partial NeuroGravity implementation. Further training of unchanged DG is included in the agent controls so that an apparent gain is not attributed to feature discovery when it comes from more fitting.

### 8.2 Feature-discovery and agent controls

| Control | Definition | Question answered |
| --- | --- | --- |
| DG continuation | Keep the original feature program and allow additional fitting/selection budget | Does extra optimization explain the gain? |
| Fixed expanded feature library + DG | A predeclared library of finer tags, scales, mass normalizations, and directed combinations | Is richer input availability sufficient without adaptive discovery? |
| Non-LLM feature search | Search that library under the same candidate-fit allowance | Is language-guided selection useful beyond numerical search? |
| LLM feature selection | An LLM selects from the same documented library and numerical summaries; it cannot invent expressions | Does program construction add value beyond LLM column selection? |
| Single-agent tool loop | One agent receives the same knowledge, tools, feedback, and total budget | Does separating investigative responsibilities help? |
| MapAgents | Surveyor, Cartographer, and Adapter with structured handoffs | Does the complete cooperative workflow add value? |

The feature library includes direction-sensitive and mass-combination candidates, not only the original 18 aggregates. It is fixed before the evaluated search. LLM selection is a competitive baseline with retrieval and validation feedback, not a deliberately tool-free chat task.

The shared library comparison establishes the value of selection and coordination within a common candidate space. Unrestricted program discovery can additionally construct expressions outside the library; results identify that expansion instead of attributing it entirely to the number of agents.

### 8.3 Focused component removals

| Variant | Single intended change | Evidence |
| --- | --- | --- |
| Without knowledge RAG | Keep map tools; remove retrieved mobility documents | Accuracy, useful candidates, and cost |
| Without raw-map investigation | Keep the same supplied aggregates and mass prior; remove raw object queries | Value of recovered geographic measurements |
| Without role-aware investigation | Remove ordered dossiers, role-specific hypotheses, and reversal feedback; retain the directed DG predictor and available operators | Value of explicit endpoint-role reasoning |
| Without Adapter feedback | Propose the candidate batch without sequential residual/selection feedback, under the same fit allowance | Value of iterative adaptation |
| Single agent | Preserve the same information and tools; collapse responsibility separation | Value of multi-agent cooperation |

Disabling runtime type checking is not a principal scientific baseline. Executability is infrastructure; the main contribution must survive stronger information- and budget-controlled comparisons.

Fixed-weight feature removal and retrained component ablation answer different questions. Both are named explicitly when used. There is no human-written upper reference or manual audit requirement.

---

## 9. Explanatory evidence and program analysis

### 9.1 Traceable representations

The explanatory object links an observed map or supplied covariate, a hypothesis, an endpoint-role description, an executed expression, and a numerical model contribution. A log of fluent LLM reasoning alone is not an explanation of the fitted predictor.

Automatically report execution success, repair counts, successful measurement coverage for selected features, constant/duplicate rejection, selected program size, and the number of accepted edits. Failed measurements cannot support a feature simply because their request appears in a trace. The automatic artifact is `execution_report.json`.

Tag and expression similarity across repeated searches are descriptive stability measures. High cross-area overlap can reflect reusable mechanisms; low overlap can reflect either useful adaptation or unstable search. Neither is interpreted without accuracy, evidence, and feature-value context. A valid new tag absent from an initial scene summary is not automatically a hallucination.

### 9.2 Exact program contribution

For a trained program branch, report the contribution centered over the complete destination row:

$$
c_k(i,j)=\beta_k\left[
z_k(i,j)-\frac{1}{|\mathcal D_i|}
\sum_{u\in\mathcal D_i}z_k(i,u)
\right].
$$

The sum of these terms exactly describes the centered additive program score. It does not decompose the entire nonlinear DG backbone. The transformation and coefficient are part of the explanation, so a positive raw feature or coefficient alone is not interpreted as an unconditional flow increase.

Remove term $k$ at fixed learned weights, renormalize over the same destination row, and record

$$
\Delta_k(i,j)=\widehat T_{ij}-\widehat T^{(-k)}_{ij}.
$$

Report its effect on CPC, RMSE, and the originally diagnosed pairs. Disabling the program head measures the program's contribution within the fitted model; it is not a separately trained DG baseline or a causal intervention on urban behavior.

### 9.3 Does the explanation correspond to the revision?

For each diagnostic target, retain its observed value, parent prediction, requested correction direction, new prediction, and term-removal predictions. Measure both direction agreement and reduction in absolute error: moving in the requested direction can still overshoot.

For role-aware terms, retain measured forward and reverse feature values. Compare role-aware and role-ablated programs under the same fitting protocol. Reversal probes verify expression behavior; predictive comparisons determine whether that behavior is useful.

Choose illustrative cases using a declared rule, such as the largest program-induced changes within several distance and zone-size strata, and include both improvements and failures. Development targets explain the search process. Any final test case study is produced after freezing the method and does not trigger another revision.

| Analysis | Automatic output | What it supports |
| --- | --- | --- |
| Execution report | `execution_report.json`: query success, Cartographer repairs, measurement coverage, constant/duplicate rejection, selected program size, accepted edits | A feature is supported only by successful measurements, not by a failed request in the trace |
| Evidence binding | Source object or covariate, query, measured value, expression | Traceability |
| Role probes | Ordered endpoint contrasts and reversed expression values | Directed representation behavior |
| Additive terms | Coefficients and centered score contributions | Exact explanation of the program branch |
| Fixed-model removal | Flow, CPC, and RMSE changes with each term disabled | Predictive fidelity within the fitted model |
| Targeted revision | Requested direction, realized change, absolute-error change | Whether an edit addresses its stated failure |
| Repeatability and cost | Program/value stability, tokens, queries, model fits | Reliability and effort |

No human rater study, Cohen's kappa, or manual program audit is included in the four-week plan.

---

## 10. Extensions and interpretation of outcomes

The core study is feature discovery and role-aware multi-agent cooperation. Cross-city program transfer is a secondary experiment after completing the main comparisons.

A transfer study must distinguish executing a source-discovered program on target geography, fitting new target model weights with that program fixed, adapting source weights, and jointly revising the program and weights. Executing a program on a new city is not automatically zero-shot OD prediction.

If a small-label experiment is added, use complete origin-row budgets such as 1% and 10%, with validation and test access declared separately. Compare fixed-program parameter adaptation, program revision, and joint adaptation under equal target supervision. The full transfer grid is not a four-week requirement.

Interpret the empirical outcomes as follows:

- If MapAgents improves over DG and the single-agent/search controls, the results support useful cooperative representation discovery.
- If DG improves only after restoring mass inputs, that is a baseline correction and supplies no evidence for agents.
- If accuracy is similar but program contributions are faithful and useful, describe the measured accuracy-explanation tradeoff. Similar scores alone do not establish a multi-agent contribution.
- If the selected program head is inactive, do not claim that the selected predictor gained an interpretable correction.
- If several cities benefit while others do not, relate the differences to measured data and program behavior without excluding unsuccessful settings.

The study does not predeclare that tool-free agents fail, that every city needs different tags, or that the multi-agent system is cheaper than a single agent.

---

## 11. Four-week work plan

| Week | Main output | Completion criterion |
| --- | --- | --- |
| 1 | Native DG reproduction record, explicit matrix evaluator, DGM prior decomposition, New York historical-data contract | Baseline inputs, training, support, and metrics are unambiguous before comparative claims |
| 2 | New York role-aware agent loop, LLM selection and single-agent controls, automatic explanation traces | The full investigation-to-training loop yields reviewable candidate outcomes, including rejections |
| 3 | London and Paris where supervision is suitable, three numerical seeds, focused ablations | Core external comparisons use declared observation supports and information budgets |
| 4 | Cost and repeatability analysis, selected cases, manuscript and release materials | Main claims map to completed comparisons; optional cities/second LLM/transfer are included only when completed |

Madrid, Barcelona, and Italy are extensions whose inclusion depends on their observation contract, not on whether MapAgents wins. Reference reproduction, meaningful agent controls, and faithful explanations take priority over adding more cities.

The original proposal used an eight-page main-text budget and an early-October submission calendar. These remain working planning assumptions; conference deadlines and formatting are to be checked separately when preparing submission. This revision does not perform that check.

---

## 12. Paper structure

| Main-text space | Content |
| --- | --- |
| 0.8 pages | Problem, information loss, research question, and proposed contribution |
| 0.6 pages | Related work and distinction from fixed feature selection |
| 2.2 pages | Agent responsibilities, directed roles, executable programs, trainable predictor |
| 1.0 pages | Data, supplied mass protocol, splits, and baseline definition |
| 1.7 pages | Main OD table, agent controls, and focused ablations |
| 1.2 pages | Program effects, diagnosed cases, stability, and cost |
| 0.5 pages | Findings, scope, and conclusion |

The supplement contains the DGM reconstruction details, complete aggregation priors, tool schemas, model settings, per-area metrics, repeat runs, and additional program cases. The abstract and conclusion are revised around observed results after experiments, rather than retaining predicted rankings.

---

## 13. Reproducibility materials

Release the source/version and observation semantics of each dataset, aligned zone identifiers, destination supports, source mass definitions, and split assignments. Provide the original DG reference configuration separately from benchmark adaptations and from earlier development variants.

The agent record includes prompts, LLM identifiers, retrieval sources, tool arguments and responses, candidate programs, rejected edits, validation selection decisions, and actual cost. The prediction record includes complete ordered outputs, fitted feature transformations, checkpoints, and the independent metric definitions.

The proposal's current working artifacts are `resources/priors/deepgravity.json`, `DISCOVERY.md`, and the historical New York data manifest. These identify development material; they are not evidence that the complete DG reproduction or planned ablations have been completed. Public data remain subject to their source licenses, and private API credentials are not part of the release.

---

## 14. Target metadata

- **Area:** Generative and Agentic AI.
- **Keywords:** multi-agent systems; retrieval-augmented generation; spatial program discovery; origin-destination prediction; role-aware representations; interpretable prediction.
- **Working title:** MapAgents: Evidence-Grounded Multi-Agent Discovery of Role-Aware Spatial Programs for Origin-Destination Prediction.
- **Central empirical question:** Does coordinated, evidence-grounded investigation improve the usefulness and explanatory fidelity of spatial representations under a credible OD baseline and a declared search budget?

---

## References

1. Simini, F., González, M. C., Maritan, A. & Barabási, A.-L. A universal model for mobility and migration patterns. *Nature* **484**, 96–100 (2012). https://doi.org/10.1038/nature10856
2. Masucci, A. P., Serras, J., Johansson, A. & Batty, M. Gravity versus radiation models: on the importance of scale and heterogeneity in commuting flows. *Phys. Rev. E* **88**, 022812 (2013). https://doi.org/10.1103/PhysRevE.88.022812
3. Simini, F., Barlacchi, G., Luca, M. & Pappalardo, L. A Deep Gravity model for mobility flows generation. *Nat. Commun.* **12**, 6576 (2021). https://doi.org/10.1038/s41467-021-26752-4
4. Cabanas-Tirapu, O., Danús, L., Moro, E., Sales-Pardo, M. & Guimerà, R. Human mobility is well described by closed-form gravity-like models learned automatically from data. *Nat. Commun.* **16**, 1515 (2025). https://doi.org/10.1038/s41467-025-56495-5
5. Atwal, K. S., Anderson, T., Pfoser, D. & Züfle, A. Commuting flow prediction using OpenStreetMap data. *Comput. Urban Sci.* **5**, 2 (2025). https://doi.org/10.1007/s43762-025-00161-5
6. Yang, J. et al. Transferable human mobility network reconstruction with neuroGravity. *Nat. Comput. Sci.* (2026).
7. Physics-informed mobility perception networks for origin–destination flow prediction. *IEEE Trans. Intell. Transp. Syst.* (2025).
8. Rong, C., Ding, J., Liu, Y. & Li, Y. A large-scale dataset and benchmark for commuting origin-destination flow generation. In *ICLR* (2025).
9. Rong, C. et al. Satellites reveal mobility: a commuting origin-destination flow generator for global cities (GlODGen) (2025).
10. Lou, S. Urban-MAS: human-centered urban prediction with LLM-based multi-agent system. In *ACM SIGSPATIAL UrbanAI Workshop* (2025). arXiv:2511.00096
11. Xie, F. & Schwertfeger, S. Empowering robotics with large language models: osmAG map comprehension with LLMs. arXiv:2403.08228 (2024).
12. ChatSUMO Agent: an LLM-based agent for conversational traffic simulation in SUMO. *Transp. Res. Part C* (2026).
13. Decoupled intelligence: a multi-agent LLM framework for controllable traffic scenario generation in SUMO (2026).
14. Speak to Simulate: an LLM-guided agentic framework for traffic simulation in SUMO. In *ACM SIGSPATIAL Workshop* (2025).
15. Yao, S. et al. ReAct: synergizing reasoning and acting in language models. In *ICLR* (2023).
16. Hong, S. et al. MetaGPT: meta programming for a multi-agent collaborative framework. In *ICLR* (2024).
17. Li, G. et al. CAMEL: communicative agents for “mind” exploration of large language model society. In *NeurIPS* (2023).
18. Tang, H. et al. WorldCoder, a model-based LLM agent: building world models by writing code and interacting with the environment. In *NeurIPS* (2024).
19. GeoColab: an LLM-based multi-agent collaborative framework for geospatial code generation. *Int. J. Digit. Earth* (2025).
20. GeoJSON Agents: a multi-agent LLM architecture for geospatial analysis—function calling vs code generation. *Big Earth Data* (2026).
21. Large language models for mobility data and transport planning: a real-world experiment on output data, reasoning, and knowledge-conditioning. In *IEEE SDS* (2026).
22. A unified experimental evaluation of guardrail mechanisms for LLM agents. In *ICR* (2026).
23. Dong, F., Zheng, Z. et al. Memory-augmented LLM-based multi-agent system for automated feature generation on tabular data (MALMAS). arXiv:2604.20261 (2026). ACL ARR 2026.
24. Yang, Y. et al. Estimating intercity heavy truck mobility flows using the Deep Gravity framework. *Transp. Res. Part E* **169**, 102991 (2023). https://doi.org/10.1016/j.tre.2022.102991
