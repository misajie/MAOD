# MapAgents: Compiling City-Conditioned OSM Feature Programs with Gated Multi-Agent Tool Use for Origin–Destination Generation

**Venue.** AAMAS 2027 Main Track, area **Generative and Agentic AI (GAAI)**. Findings opt-in.  
**Deadlines.** Author accounts 17 Sep 2026; abstract 1 Oct; paper 8 Oct. Eight pages + references. Double-blind.  
**Fallback.** The Web Conference 2027 (abstract 18 Oct, paper 25 Oct), tracks Evaluation / Resources or Web Infrastructure and Agentic Systems.

**Object.** An \(N\times N\) commuting-count matrix on one named tessellation per study area.  
**Transfer unit.** An executable feature program \(P_s\), not a weight vector \(\theta\).  
**Acceptance.** Common part of commuters (CPC) on spatially held-out origins, under production-constrained emission.

---

## Abstract

Deep Gravity replaced population-and-distance attractiveness with one frozen OpenStreetMap (OSM) feature table. That table is identical for a university city, a polycentric industrial belt, and a sparsely tagged peri-urban county. We treat the table as a *program* \(P_s\) that must be compiled from a city scene, executed against a typed OSM API, and rewritten when a few target edges become visible.

MapAgents is a three-agent system. Surveyor emits a structured scene card (urban form, dominant commute attractors, OSM coverage holes, banned keys). Cartographer may call only a frozen organisation API: typed predicates, zone-level aggregators, and coverage reports. An institutional gate rejects queries that leave the dictionary, mix tessellation scales, or double-count population as a destination attractor. Adapter rewrites the program text under a \(1\%\) or \(10\%\) edge budget on training-block origins; it does not retrain the flow backbone. Destination probabilities still come from a production-constrained generator
\[
\widehat{T}_{ij}=O_i\,p_{j\mid i}\bigl(x_i^{P_s},x_j^{P_s},d_{ij}\bigr).
\]
The score is the common part of commuters
\[
\mathrm{CPC}(A,B)=\frac{2\sum_{ij}\min(A_{ij},B_{ij})}{\sum_{ij}A_{ij}+\sum_{ij}B_{ij}},
\]
with Pearson correlation on log flows, NRMSE, and Jensen–Shannon divergence as companions.

Experiments use the three public Deep Gravity geographies—England census commuting, Italy ISTAT commuting, New York State tract flows—plus one fully open LEHD LODES metro clip. Protocol baselines are single-agent ReAct on the same API, tool-free role play, and an ungated pipeline. Flow baselines are gravity, radiation, Deep Gravity with the published frozen OSM query, and (optional) Atwal building-type features on the same Deep Gravity backbone. Ablations remove the scene card, the gate, the few-shot rewrite, and the OSM API. Program traces—tag-set Jaccard, gate-reject codes, card–program alignment, \(\Delta\mathrm{CPC}\) by key family, CPC versus shot budget—are first-class results.

City specificity in trip distribution is a compilation problem. What transfers across cities is a gated feature program.

---

## 1. Problem

Flow generation writes a matrix \(\widehat{T}\) on a tessellation when destination choices for some or all origins are unseen. The short-run mobility literature already separates this task from next-location prediction, crowd-flow forecasting, and trajectory generation. On the law side the named models are the gravity law with power or exponential deterrence and the radiation law [1, 2]. On the learned side Deep Gravity maps origin features, destination features, and distance through a multilayer perceptron and a softmax [3]. Its geographic lift comes from one OSM inventory—land use, roads, transport, food, health, education, retail—applied everywhere.

That inventory is an implicit theory of attractiveness, and it is wrong in the same way for every city. A docklands employment core, a campus–hospital complex, and a logistics belt do not share a tag grammar. Coverage is uneven: the same key is dense in one metro and empty in the next. Copying England weights onto Italy therefore copies the wrong object. The object that should move is the query that built the table.

Scale and heterogeneity already decide which closed form wins [2]. Closed-form gravity-like expressions recovered by symbolic regression remain competitive with deep models at several scales [4]. Building-type counts from OSM predict commuting when they are fed to a graph attention network [5]. None of these lines supplies a *procedure* that writes a different legal feature program when the city, the OSM hole list, or the dominant attractor family changes.

Language models fail as world models of neighbourhood flows [21]. They succeed as compilers when the output is executable, the tool surface is typed, and acceptance is a matrix score on held-out origins. WorldCoder showed that an LLM agent can build a world model by writing code and interacting with an environment [18]. MapAgents continues that line: the model does not predict the next destination; it compiles the OSM query that feeds a named generator.

neuroGravity improves the *backbone*: a meta-Gravity module parameterises the gravitational constant and the distance-decay exponent, and a GNN refines residuals, then few-shot transfers across cities [10]. MapAgents does not touch the backbone. It changes the feature program that the backbone reads. The two moves are orthogonal. A program compiled here can in principle be fed to any production-constrained generator, including a meta-Gravity module. The transfer unit in this paper is the program text \(P_s\), not the weights \(\theta\).

**Question.** Can a constrained multi-agent system compile a city-specific OSM feature program that a named production-constrained generator uses to beat a frozen geographic table, and can a few observed edges rewrite that program without retraining the backbone?

---

## 2. Thesis and contributions

**Thesis.** Attractiveness for commuting origin–destination (OD) flows is city-conditioned and program-shaped. A Surveyor–Cartographer–Adapter loop, bound to a typed OSM API and an institutional gate, compiles that program. Few-shot adaptation acts on program text. CPC on spatially held-out origins is the test.

**C1. A grounded multi-agent compilation protocol.** Three roles, a frozen tool dictionary, a gate with typed reject codes, and a program schema
\[
P_s=\bigl\{(k_\ell,v_\ell,\mathrm{agg}_\ell,\mathrm{scale}_\ell)\bigr\}_{\ell=1}^{m}.
\]
This is the AAMAS object.

**C2. Program-level few-shot transfer.** Adapter edits \(P_s\) under budgets \(\tau\in\{0,0.01,0.10\}\) on training-block edges and a spatial block hold-out. Backbone weights stay frozen. What crosses England \(\to\) Italy / New York is the program, not \(\theta\). This is distinct from neuroGravity’s cross-city move (retrain the GNN and adapt meta-Gravity parameters). Adaptation cost drops from “refit the model” to “rewrite the query”.

**C3. Interpretability that is the artifact.** Every accepted destination feature is a tag set plus an aggregator. We report gate-reject rates, tag-set Jaccard across cities, alignment between the scene card and the compiled keys, and
\[
\Delta\mathrm{CPC}(\mathcal{F})=\mathrm{CPC}\bigl(T,\widehat{T}^{P_s}\bigr)-\mathrm{CPC}\bigl(T,\widehat{T}^{P_s\setminus\mathcal{F}}\bigr)
\]
when a key family \(\mathcal{F}\) is dropped.

**C4. A reproducible three-geography testbed.** England, Italy, New York State (Deep Gravity geographies) and one LODES metro clip. Frozen Deep Gravity query, classical laws, Atwal building-type features on the same backbone, and agent-protocol baselines on the same tessellations.

---

## 3. Related work

| # | Line | What they did | What we take | What we replace |
| --- | --- | --- | --- | --- |
| 1 | Simini et al., 2021, Deep Gravity [3] | Frozen OSM table + DG + CPC on England / Italy / NYS | Backbone, geographies, CPC, tile hold-out | The table becomes a compiled program |
| 2 | Simini et al., 2012, radiation [1] | Parameter-free population radiation | Law-side parameter-free baseline | Program features enter DG; no new closed form |
| 3 | Cabanas-Tirapu et al., 2025 [4] | Automatically learned closed-form gravity-like models remain strong | Law-side closed-form evidence | Features are compiled, not symbolically rediscovered |
| 4 | Urban-MAS (Lou, 2025) [10] | LLM agents + Nominatim / Overpass for urban prediction | MAS + OSM pattern | Executable programs + matrix GOF |
| 5 | ChatSUMO-Agent, 2026 [12] | OSM–SUMO tool loop + KPI feedback | Closed loop against an external scorer | Feature program + CPC, not signal timing |
| 6 | osmAG + LLM (Xie and Schwertfeger, 2024) [11] | LLMs read OSM-shaped text maps | Maps must be typed for models | Compilation to zone features for OD |
| 7 | MetaGPT [16] / CAMEL [17] / ReAct [15] | Role orchestration and tool cycles | Protocol baselines (Table A) | Grounding in a gated geo API |
| 8 | MALMAS, 2026 [23] | Multi-agent automated feature generation on tabular data, with memory | Iterative feature rewrite | Geospatial programs under a typed geo API, not tabular operators |
| 9 | LLMs for mobility data, 2026 [21] | Empirical reasoning bias of LLMs on travel data | Do not use the LLM as a next-location world model | LLM as compiler only |
| 10 | neuroGravity (Yang et al., 2026) [6] | Physics-informed GNN + meta-Gravity; few-shot cross-city reconstruction | Few-shot transfer motive; OSM features as inputs to a flow model | Rewrite program text \(P_s\); freeze backbone \(\theta\) |
| 11 | Atwal et al., 2025 [5] | OSM building types + GAT for commuting-flow prediction | OSM features as commuting predictors | A compiled program replaces a single building-type table; same DG backbone in B9 |
| 12 | GlODGen (Rong et al., 2025) [9] | Satellite imagery + VLM \(\to\) global commuting OD product | Public output matrices as an *output-level* reference | City-conditioned compilation vs. one global generator |

Additional citations, not rows of the contrast table:

- WorldCoder [18] anchors “LLM as compiler” in §1–§2.
- Masucci, 2013 [2] anchors scale and heterogeneity in §1.
- Rong et al., ICLR 2025 commuting-OD benchmark [8] is discussed in §5–§6 as a large-area benchmark we do not adopt wholesale, because city-conditioned compilation requires a scene card per tessellation.
- GeoColab [19] generates general geospatial code; MapAgents emits a constrained feature program.
- GeoJSON Agents [20] contrasts function calling with code generation; MapAgents takes the function-calling route.
- Physics-informed mobility networks [7] locate B8 (gravity + compiled mass) on the shallow end of that spectrum.
- Guardrail evaluations for LLM agents [22] supply precedent for the institutional gate in §4.4.
- Decoupled Intelligence [13] and Speak to Simulate [14] extend the SUMO-agent line cited with ChatSUMO-Agent.
- Truck Deep Gravity [24] shows that the DG skeleton travels outside commuting; we keep the commuting object.

Trajectory generators, proprietary CDR, and closed operator panels stay out of the main tables. GlODGen and neuroGravity stay out of Table B for the reasons in §6–§7.

---

## 4. Method

### 4.1 Object, constraints, and named backbones

One tessellation per study area. Intra-zonal cells are kept; their share
\[
h_{\mathrm{intra}}=\frac{\sum_i T_{ii}}{\sum_{ij}T_{ij}}
\]
is reported. Observed commuting matrix \(T\in\mathbb{R}^{N\times N}_{\ge 0}\), origin outflows \(O_i=\sum_j T_{ij}\), destination inflows \(D_j=\sum_i T_{ij}\). Every generator in the main tables is production-constrained:
\[
\widehat{T}_{ij}=O_i\,p_{j\mid i},\qquad \sum_j p_{j\mid i}=1,\qquad \sum_j\widehat{T}_{ij}=O_i.
\]
When outflows match, CPC equals the share of trips sent to the correct destination.

**Gravity law.** Attractiveness \(m_j\) (population, or a compiled mass in B8) and deterrence \(f\):
\[
p_{j\mid i}=\frac{m_j\,f(d_{ij})}{\sum_{k}m_k\,f(d_{ik})},\qquad
f(d)=d^{-\beta}\quad\text{or}\quad f(d)=e^{-\beta d}.
\]
\(\beta\) is estimated by maximum likelihood on training-origin destination shares of the commuting table.

**Radiation law.** Opportunity mass \(s_{ij}\) inside the closed disk of radius \(d_{ij}\) centred at \(i\), excluding \(i\) and \(j\):
\[
p_{j\mid i}=\frac{m_i m_j}{(m_i+s_{ij})(m_i+m_j+s_{ij})}.
\]
We use residential population for \(m\) unless a compiled opportunity mass is named.

**Deep Gravity.** Let \(x_i,x_j\in\mathbb{R}^{m}\) be zone feature vectors and \(d_{ij}\) Euclidean (or network; stated per table) distance. A multilayer map \(g_\theta\) produces logits
\[
s_{ij}=g_\theta(x_i,x_j,d_{ij}),\qquad
p_{j\mid i}=\frac{\exp(s_{ij})}{\sum_{k}\exp(s_{ik})}.
\]
Training minimises cross-entropy on destination shares of training origins. Architecture, candidate sampling, and epoch budget are copied from Simini et al. (2021) [3]. MapAgents changes only how \(x_i,x_j\) are built.

### 4.2 Scene card (Surveyor)

Surveyor emits a fixed JSON schema, not prose:

- `region_id`, tessellation name, \(N\)
- form: `{monocentric, polycentric, corridor, periurban}`
- dominant attractors: a subset of `{employment_core, campus, hospital, logistics, retail, port, government}`
- OSM coverage: `{dense, patchy}` plus a hole list of dictionary keys
- banned keys (religion, ethnicity, person-level amenities)
- legal scales per key: zone count, buffer ring, or network length

The card \(C_s\) is an input artifact, logged and released.

### 4.3 Typed OSM organisation API (Cartographer)

Cartographer cannot emit raw Overpass. It calls a frozen dictionary:

1. \(\texttt{count\_poi}(z,k,v,b)\) — count of key \(k\), value \(v\), inside zone \(z\) or a buffer of \(b\) metres.
2. \(\texttt{length\_network}(z,c)\) — length of highway class \(c\) in \(z\).
3. \(\texttt{area\_share}(z,u)\) — fraction of \(z\) tagged with landuse \(u\).
4. \(\texttt{access\_count}(z,t)\) — public-transport amenity count of type \(t\).
5. \(\texttt{coverage\_report}(z,k)\) — density of key \(k\); used to swap a hole for a proxy.

Legal buffers \(b\in\{0,300,800,1500\}\) m. New keys in the main tables are failures.

GeoJSON Agents contrast function calling with free code generation [20]. MapAgents is function calling against this API. GeoColab writes general geospatial scripts [19]; the output here is a feature program that the gate can type-check.

### 4.4 Institutional gate

A candidate program is accepted only if all of the following hold:

- every predicate belongs to the dictionary;
- a single tessellation; no mixing of output areas with districts, or tracts with counties;
- population appears at most once, as an origin mass or a radiation opportunity, never as a silent extra destination column stacked on itself;
- buffers lie in the legal set;
- runtime and cell caps (no city-wide raw dump);
- no banned keys.

Reject codes: `UNKNOWN_KEY`, `SCALE_MIX`, `POP_DOUBLE`, `BUFFER_ILLEGAL`, `TIMEOUT`, `BAN`. Guardrail evaluations for LLM agents supply the design precedent [22]. Gate-reject rate is a result, not a footnote.

Cartographer may repair against the reject code at most three times per compilation.

### 4.5 Feature program and execution

\[
P_s=\bigl\{(k_\ell,v_\ell,\mathrm{agg}_\ell,\mathrm{scale}_\ell)\bigr\}_{\ell=1}^{m}
\quad\longrightarrow\quad
X^{P_s}\in\mathbb{R}^{N\times m}.
\]
Row \(i\) of \(X^{P_s}\) is the origin feature \(x_i\); row \(j\) is the destination feature \(x_j\). Deep Gravity reads \((x_i,x_j,d_{ij})\). Gravity B8 reads a compiled destination mass
\[
m_j^{P_s}=\sum_{\ell\in\mathcal{A}} w_\ell\,X^{P_s}_{j\ell},
\]
where \(\mathcal{A}\) is the attractor-key subset and \(w\) is a non-negative normalisation stated in the supplement. The program *text* is the transferable object.

### 4.6 Few-shot Adapter

Let \(\mathcal{B}_{\mathrm{train}}\) be the training origin blocks and \(\mathcal{E}_{\mathrm{train}}=\{(i,j):i\in\mathcal{B}_{\mathrm{train}}\}\). Budget \(\tau\in\{0,0.01,0.10\}\) draws a subset \(E_\tau\subset\mathcal{E}_{\mathrm{train}}\) with \(|E_\tau|=\lceil\tau\,|\mathcal{E}_{\mathrm{train}}|\rceil\), three seeds. Adapter may

- add or drop a dictionary key,
- change aggregator or buffer,
- rewrite a proxy when \(\texttt{coverage\_report}\) is low.

Adapter may not touch held-out origins, change Deep Gravity hidden sizes, train longer than the frozen protocol, or invent keys. Acceptance at round \(r\) is mean CPC on held-out origin blocks. Stop at plateau of two rounds or cap \(R=5\).

Leakage check: no held-out origin identifier and no held-out edge statistic enters any prompt.

### 4.7 Orchestration

One compilation pass:
\[
C_s \;\xrightarrow{\text{Surveyor}}\;
P_s^{(0)} \;\xrightarrow{\text{gate}\le 3}\;
X^{P_s^{(0)}} \;\xrightarrow{\text{fit }\theta\text{ on }\mathcal{B}_{\mathrm{train}}}\;
\mathrm{CPC}_{\mathrm{hold}}.
\]
Adapter then iterates \(P_s^{(r)}\mapsto P_s^{(r+1)}\). Messages, tool calls, reject codes, and program diffs are stored as a trace \(\Gamma_s\).

---

## 5. Data

| Study area | Product | Tessellation | Status |
| --- | --- | --- | --- |
| England | 2011 Census commuting (WICID / UK Data Service) | Output Areas inside Deep Gravity \(25\,\mathrm{km}\) tiles |  |
| Italy | ISTAT commuting matrix | Census areas, same tile protocol |  |
| New York State | Deep Gravity tract flows + Census geometries | Census tracts |  |
| One US metro clip | LEHD LODES home–work OD, aggregated to tracts | Tracts |  |

Inclusion defaults: \(N\ge 25\), \(h_{\mathrm{intra}}\le 0.70\) on the unsliced commuting table. OSM features are rebuilt from a dated planet extract with (i) the frozen Deep Gravity query and (ii) each compiled \(P_s\). Snapshot date is recorded.

Hong Kong attribute OD, Spanish MITMA cubes, proprietary CDR used by neuroGravity, and generated global commuting products as *training* or *ground-truth* sources are out of this paper.

The ICLR 2025 commuting-OD benchmark covers \(3{,}333\) regions [8]. We do not adopt it wholesale: city-conditioned compilation needs a scene card and a legal dictionary per tessellation, which that benchmark does not supply. A later subset experiment remains possible; it is not required for the AAMAS object.

---

## 6. Evaluation protocol

**Spatial split.** Five contiguous origin blocks on the tessellation adjacency graph (queen contiguity on tiles or zones). Laws and programs are estimated on training origins. Held-out origins are generated with observed \(O_i\). Report mean \(\pm\) block standard deviation.

**Cross-city transfer.** Compile and fit on England. Zero-shot execute the England program on Italy and the US clip. Then Adapter at \(\tau=0.01\) and \(\tau=0.10\) on the target. Compare with a program compiled from scratch on the target.

**Metrics.** Primary:
\[
\mathrm{CPC}(T,\widehat{T})=\frac{2\sum_{ij}\min(T_{ij},\widehat{T}_{ij})}{\sum_{ij}T_{ij}+\sum_{ij}\widehat{T}_{ij}}.
\]
Companions, following Deep Gravity Supplementary Note 1 [3]: Pearson correlation on \(\log(1+T_{ij})\) and \(\log(1+\widehat{T}_{ij})\); NRMSE with denominator \(\sqrt{N^{-2}\sum_{ij}(T_{ij}-\bar T)^2}\); Jensen–Shannon divergence between the empirical histograms of \(\{T_{ij}\}\) and \(\{\widehat{T}_{ij}\}\).

**Shots.** Uniform draw over training-block pairs, three seeds.

**Compute.** One backbone copied from [3]. One frozen instruction model for all agents; snapshot named in the appendix. Temperature \(0\) for Cartographer and Adapter; \(0.2\) for Surveyor.

**Output-level reference (not a method baseline).** On the same held-out origins we score publicly released GlODGen predicted flows [9] against local census ground truth. GlODGen is a satellite + VLM + graph-diffusion product whose training stack is not rerunnable here. The number records consistency of that public output with local truth. It is not a same-backbone comparison. If MapAgents on the local hold-out meets or exceeds that reference, the result supports city-conditioned compilation against a single global generator.

---

## 7. Baselines

### Table A — Agent protocol

Mean hold-out CPC. Fill after the run.

| ID | System | England | Italy | NYS / LODES | Mean |
| --- | --- | --- | --- | --- | --- |
| A0 | Single-agent ReAct, same API and gate [15] |  |  |  |  |
| A1 | Three-role chat, no tools [16, 17] |  |  |  |  |
| A2 | Surveyor \(\to\) Cartographer \(\to\) Adapter, gate off |  |  |  |  |
| A3 | Frozen Deep Gravity `osm_query.yaml` [3] |  |  |  |  |
| A4 | Random dictionary subset, same cardinality as \(P_s\) |  |  |  |  |
| A5 | MapAgents (full) |  |  |  |  |

Human-written program on England only: appendix upper reference.

### Table B — Flow generators

All production-constrained, same \(O_i\), same spatial split. Primary cell is CPC; companions in the supplement.

| ID | Generator | Features | England CPC | Italy CPC | NYS / LODES CPC | Pearson | NRMSE | JSD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Gravity, power | population |  |  |  |  |  |  |
| B2 | Gravity, exponential | population |  |  |  |  |  |  |
| B3 | Radiation | population |  |  |  |  |  |  |
| B4 | Deep Gravity | frozen OSM table [3] |  |  |  |  |  |  |
| B5 | Deep Gravity | MapAgents \(P_s\), \(\tau=0\) |  |  |  |  |  |  |
| B6 | Deep Gravity | MapAgents \(P_s\), \(\tau=1\%\) |  |  |  |  |  |  |
| B7 | Deep Gravity | MapAgents \(P_s\), \(\tau=10\%\) |  |  |  |  |  |  |
| B8 | Gravity, exponential | compiled destination mass \(m_j^{P_s}\) |  |  |  |  |  |  |
| B9 | Deep Gravity | Atwal residential / non-residential building table [5] |  |  |  |  |  |  |

B8 tests whether compiled mass already lifts a shallow law (physics-informed shallow end [7]). B9 puts Atwal’s building-type extractor on the Deep Gravity MLP so the contrast is “one building-type table versus a compiled program” on the *same* backbone. neuroGravity is not a Table B row: it changes \(\theta\). GlODGen is not a Table B row: it is the output-level reference in §6.

### Table B-x — Cross-city program transfer

CPC on the target geography.

| Source \(\to\) target | \(\tau=0\) (zero-shot program) | \(\tau=1\%\) | \(\tau=10\%\) | From-scratch \(P_s\) on target |
| --- | --- | --- | --- | --- |
| England \(\to\) Italy |  |  |  |  |
| England \(\to\) NYS / LODES |  |  |  |  |

---

## 8. Ablations

### Table C — Knockouts

Hold-out CPC, England default; other geographies in the supplement.

| Knockout | Removes | CPC | \(\Delta\) vs A5 |
| --- | --- | --- | --- |
| −Surveyor | Generic “commuting city” card |  |  |
| −Gate | Institutional gate off |  |  |
| −Adapter | \(\tau=0\) only |  |  |
| −API | Population + distance |  |  |
| −Roles | Collapse to A0 ReAct |  |  |
| −Transport | Drop transport keys |  |  |
| −Education | Drop education keys |  |  |
| −Landuse | Drop land-use keys |  |  |
| −Retail | Drop retail keys |  |  |

---

## 9. Analysis of agent traces

Traces \(\Gamma_s\) are data. The LLM is not asked to explain itself in prose.

**Validity.**
\[
\mathrm{valid}=\frac{\#\{P_s:\text{executes}\}}{\#\{\text{compilation attempts}\}}.
\]
Mean repair rounds. Histogram of reject codes.

**Specificity.** For key sets \(K(P)\),
\[
J(P,P')=\frac{|K(P)\cap K(P')|}{|K(P)\cup K(P')|}.
\]
Report within-city repeats (\(n=5\)) versus across-city pairs. Low within-city \(J\) is instability. High across-city \(J\) is failed specialisation.

**Faithfulness.** Fraction of Surveyor attractors that appear in \(K(P_s)\); fraction of compiled keys absent from the card (hallucinated attractors).

**Utility.** \(\Delta\mathrm{CPC}(\mathcal{F})\) from §2 for each key family.

**Adaptation path.** For each Adapter step, edit type \(\in\{\mathrm{add},\mathrm{drop},\mathrm{buffer},\mathrm{proxy}\}\) against \(\Delta\mathrm{CPC}\). One plot of CPC versus \(\tau\).

**Leakage audit.** Automatic string check that no held-out origin id or held-out edge statistic enters a prompt.

**Human audit.** Twenty programs, two raters: executable, card-faithful, gate-legal. Cohen’s \(\kappa\) and pass rate.

### Table D — Trace diagnostics

| Geography | Valid rate | Mean repairs | Within-city \(J\) | Across-city \(J\) | Card alignment | Hallucinated keys | Human pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| England |  |  |  |  |  |  |  |
| Italy |  |  |  |  |  |  |  |
| NYS / LODES |  |  |  |  |  |  |  |

Figures: (1) hold-out CPC by generator and geography; (2) CPC versus \(\tau\); (3) tag-set Jaccard heatmap; (4) reject-code bars; (5) England versus Italy program diff, one tile.

---

## 10. Expected empirical shape

On the Deep Gravity geographies, under the same backbone and the same spatial hold-out, a compiled program beats the frozen OSM table. The lift is larger where OSM coverage and urban form depart from the implicit England-centric inventory. Zero-shot program transfer already moves CPC; \(1\%\) edges rewrite the hole list and add the missing attractor family; \(10\%\) approaches a from-scratch target program.

Single-agent ReAct issues more calls and compiles less stable tag sets. Tool-free role play does not emit a legal program. Ungated Cartographer raises `TIMEOUT` and `SCALE_MIX` and does not raise CPC. Random tag subsets of the same cardinality stay near population-only gravity. Adapter edits concentrate on coverage proxies and one or two city-dominant attractors rather than on rewriting the whole dictionary. B9 (building types only) sits between frozen DG and full \(P_s\).

City specificity in commuting OD lives in the feature program. Surveyor changes the legal key set, the gate makes the program auditable, Adapter rewrites the program faster than a backbone refit.

---

## 11. Eight-page map

| Pages | Content |
| --- | --- |
| 0.7 | Abstract, problem, thesis, WorldCoder + neuroGravity orthogonality |
| 0.9 | Related-work contrast (Table in §3 compressed to one page of prose + one small table) |
| 2.2 | Method: card, API, gate, \(P_s\), Adapter, named backbones, displayed equations |
| 0.5 | Data and split |
| 2.0 | Tables A–C, Figures 1–2 |
| 1.2 | Trace analysis, Table D, Figures 3–5, human audit |
| 0.5 | Conclusion |

Anonymous supplement: dictionary, card schema, prompts, reject codes, per-block CPC, three worked programs.

---

## 12. Reproducibility packet (anonymous at submission)

- Frozen tool dictionary and gate.
- Scene-card schema and three worked cards.
- Compiled programs for every area \(\times\,\tau\,\times\) seed.
- Feature tables and train / hold-out origin identifiers.
- Scripts that recompute CPC, Pearson, NRMSE, JSD.
- Trace logs with tool arguments.

Census flows remain behind their original licences; download scripts and hashed manifests ship. The LODES clip ships.

---

## 13. Calendar

| Window | Output |
| --- | --- |
| 13–17 Sep | OpenReview accounts. Freeze dictionary, card schema, reject codes, city list. Abstract draft. |
| 18–22 Sep | B1–B4 on England hold-out. Wire A0 and A3. |
| 23–27 Sep | Full MapAgents on England + Italy. Tables A and C. Twenty-program audit. |
| 28 Sep–1 Oct | NYS or LODES clip. Cross-city zero-shot + \(1\%/10\%\). Abstract on OpenReview. |
| 2–7 Oct | Table B, figures, leakage audit, eight-page freeze. |
| 8 Oct | Submit Main / GAAI. Findings remain on. |

---

## 14. OpenReview metadata

- **Area:** Generative and Agentic AI
- **Keywords:** multi-agent systems; tool-using agents; institutional constraints; geospatial tools; origin–destination generation; program synthesis
- **Title:** MapAgents: Compiling City-Conditioned OSM Feature Programs with Gated Multi-Agent Tool Use for Origin–Destination Generation

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
