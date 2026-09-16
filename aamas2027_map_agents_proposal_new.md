# MapAgents: Evidence-Grounded Multi-Agent Discovery of Role-Aware Spatial Programs for Mobility-Flow Generation

**Target.** AAMAS 2027 Main Track, Generative and Agentic AI.  
**Revision.** 14 September 2026. Research proposal and experiment plan; empirical claims remain to be established.  
**Scope.** Three cooperating agents discover executable spatial representations for destination allocation with supplied origin outflows. Deep Gravity remains trainable. The main flow comparison is Gravity, Deep Gravity, and MapAgents.  
**Primary artifact.** A spatial program with measured evidence, separate origin and destination roles, and a trace of how its numerical contributions affect predictions.  
**Working horizon.** Four weeks, beginning with New York State and extending to public study areas whose observation support can be established.

---

## Abstract

Mobility-flow generation depends on how raw spatial information is aggregated into built-environment features. A fixed geographic feature schema can represent broad land use and facility counts while losing distinctions between facility types, neighborhood scales, and the different functions of a place as an origin and a destination. A flexible neural predictor can learn interactions among supplied variables, but it cannot recover measurements discarded during aggregation.

We propose MapAgents, a three-agent framework for discovering evidence-grounded spatial programs. Surveyor retrieves mobility knowledge and examines raw OpenStreetMap objects, existing aggregation recipes, and local geographic measurements. It develops hypotheses about source context, destination opportunities, and their directed relationships. Cartographer compiles these hypotheses into reusable numerical expressions and uses execution feedback to repair invalid or uninformative features. Adapter diagnoses validation errors, compares candidate programs after model training, and directs subsequent investigation. The resulting program augments a trainable Deep Gravity predictor through a learned additive score component, enabling exact decomposition of the program contribution.

The evaluation will distinguish destination-allocation accuracy from the value of agent collaboration. Gravity and Deep Gravity provide flow baselines; fixed feature libraries, LLM feature selection, single-agent tool use, and controlled removals of retrieval, endpoint-role reasoning, and feedback examine the proposed mechanism. CPC, RMSE, and off-diagonal performance measure prediction quality. Executed evidence links, feature interventions, and responses on diagnosed OD pairs measure explanatory fidelity. New York State provides the initial development case using GeoDS mobility flows, followed by public European study areas with census residence-to-work commuting flows. The central question is whether coordinated investigation produces useful and verifiable spatial representations beyond those obtained from fixed aggregation or a single feature-selection agent.

---

## 1. Problem and research question

We study time-aggregated, unimodal destination allocation with supplied origin outflows. The model estimates how the outflow from each origin is distributed among candidate destinations. The New York GeoDS example records mobility flows; census residence-to-work tables record commuting flows as person counts or weighted estimates. Each dataset retains its source-specific flow meaning.

Deep Gravity [3] represents each OD pair using attributes of both endpoints and their geographic distance. Its geographic feature schema combines a mass prior with land use, roads, and several facility groups. The schema is shared across places, while feature values and learned nonlinear responses can differ. The research gap is the information lost when raw geography is reduced to that schema.

Several distinctions motivate a richer representation. A hospital and a pharmacy may have different spatial roles despite sharing a health category. A campus can be described through land area, buildings, surrounding services, and access to transport. Facility counts can be interpreted relative to source movement scale or competing opportunities nearby. The same transport facility can describe departure access at one endpoint and arrival access at the other. These alternatives concern what is measured and how measurements are combined.

MapAgents treats feature construction as an investigation. An agent must identify the missing distinction, retrieve or compute relevant evidence, express it as a spatial program, and assess the resulting prediction change. Functional roles are open and potentially mixed: a zone can support residence, services, education, and transport simultaneously. A role is a hypothesis about the function of measured geography in an ordered OD relationship, not a categorical identity assigned permanently to a place.

**Research question.** Can evidence-grounded discovery of role-aware spatial programs improve time-aggregated mobility-flow generation beyond a fixed Deep Gravity geographic feature schema [3], while preserving supplied origin outflows and providing faithful, inspectable explanations of the program's numerical contribution?

The AAMAS contribution centers on cooperation among agents with different responsibilities and feedback. It does not require a new universal law of urban movement, a larger collection of city case studies, or a more complex flow backbone.

---

## 2. Intended contributions

**Evidence-grounded feature discovery.** Surveyor, Cartographer, and Adapter coordinate retrieval, numerical execution, and validation-guided revision. Their handoffs carry explicit hypotheses, measurement requests, executable expressions, and observed candidate outcomes. This structure makes it possible to examine where a proposed mechanism originated and whether it survived execution and model evaluation.

**Role-aware spatial programs.** Programs distinguish origin context from destination opportunity and express directional interactions with distance and neighborhood structure. The method moves beyond selecting columns from a fixed table by constructing measurements and compositions from available geographic layers.

**Joint prediction and explanation.** Deep Gravity and the spatial-program coefficients are trained together. The program branch provides an exact score decomposition, while fixed-model feature removal measures how that branch redistributes predicted flows. Predictive usefulness and explanatory fidelity are evaluated separately.

**A focused empirical comparison.** The study compares generated mobility flows against Gravity and a faithfully reproduced Deep Gravity baseline, then isolates the effects of LLM selection, tools, role separation, and iterative feedback. The intended evidence spans several public study areas, multiple training seeds, and automatic explanation measurements.

These are proposed contributions. Neither a performance gain nor a benefit from multiple agents is assumed in advance.

---

## 3. Research context

Research on mobility flows connects destination-allocation laws, geographic feature schemas, network reconstruction, and the recovery of time-dependent travel patterns. These studies motivate the geographic measurements used by MapAgents and clarify the relationship between its allocation task and other mobility models.

| Research line | Relevance to MapAgents | Comparison or distinction |
| --- | --- | --- |
| Gravity and radiation allocation [1, 2] | Mass, distance, and intervening opportunities organize destination choice given an origin total | Gravity provides a flow baseline; radiation offers an alternative allocation law |
| Learned gravity-like closed forms [4] | Interpretable deterrents learned from data can match complex predictors and extrapolate | Representation discovery complements the study of parsimonious mobility laws |
| Deep Gravity and OSM feature schemas [3, 5] | Fixed geographic aggregates improve allocation over mass and distance alone | MapAgents investigates finer measurements within and beyond the existing aggregates |
| Mobility-network reconstruction and transfer [6] | Facilities and population support absolute-flow reconstruction across cities | neuroGravity estimates network structure and flows; MapAgents allocates supplied origin outflows |
| Time-dependent multimodal recovery [7] | TD–OD flows describe when, where, and how travel occurs | Data fusion recovers mode- and time-specific flows; MapAgents models time-aggregated destination allocation |
| Generated and benchmark commuting resources [8, 9] | Commuting benchmarks and satellite generators support model development and geographic coverage | Observed commuting records and generated flow proxies serve different evaluation roles |
| Geospatial LLM applications [10, 11, 19, 20] | Map objects require tools and explicit spatial semantics | Geographic code generation and urban-factor analysis motivate executable raw-map measurements |
| Tool-using and program-as-action agents, 2023–2024 [15, 18, 24–28, 34] | Surveyor retrieves map objects; Cartographer compiles a hypothesis only after execution | These methods justify tools and executable repair. They do not construct reusable OD features |
| Role-specialized workflows, 2024 [16, 17, 29–32] | Surveyor, Cartographer, and Adapter separate investigation, compilation, and selection | SOP handoffs motivate typed artifacts. Software-engineering roles are not geographic roles |
| Automated workflow search, 2025–2026 [35, 36, 38, 41, 42] | Explains why a triad is a legitimate design object | MAS² and CARD search or generate graphs. The four-week study fixes three roles |
| Grounded revision and debugging, 2023 and 2026 [25, 26, 43–45] | Adapter converts residuals into the next contract | Reflection is not enough. Keep/reject requires execution reports and candidate fits |
| LLM and multi-agent feature construction [23, 33] | Closest methodological cousins | CAAFE and MALMAS search tabular transformations. MapAgents must recover raw-map measurements and directed pair terms |
| Official agent architectures and implementation guides [46–51] | Manager–specialist orchestration, structured outputs, separate evaluation, and selective context | MapAgents connects these patterns to executable measurements and numerical candidate selection |

Deep Gravity generates destination probabilities from origin outflows, distance, and a fixed geographic feature schema [3]. Each origin–destination pair is represented by log-mass at both ends, eighteen OpenStreetMap aggregates, and distance. Softmax preserves the supplied origin outflow. These built-environment features improve the Common Part of Commuters (CPC) over mass and distance alone, especially in dense tiles. Atwal et al. show that globally available OSM building types also support commuting-flow prediction and transfer [5]. Together, these results motivate geographic inputs and raise the question of which distinctions survive aggregation. A hospital and a pharmacy can share a health count; a station can describe departure access at one endpoint and arrival access at the other.

Gravity and radiation provide the allocation laws underlying this line of work. Given origin outflows, gravity allocates destinations through mass and a distance deterrent, while radiation uses intervening opportunities with little calibration [1, 2]. Their relative performance depends on scale and heterogeneity [2]. Closed-form gravity-like expressions learned from data can match complex machine-learning models and extrapolate when the covariates are mass and distance [4]. Gravity therefore provides a direct baseline for assessing the value of richer geographic representations.

neuroGravity reconstructs human mobility networks in which regions are nodes and origin–destination pairs are edges [6]. It estimates absolute mobility flows from urban facility and population distributions. A connection predictor proposes topology, a deep-parameterized meta-Gravity term supplies a physically grounded base flow, and a graph network refines it. The published setting includes reconstruction from sparse observed pairs and transfer to unobserved cities, with transferability linked to spatial income segregation [6]. Its global outputs are mobility flow proxies. This reconstruction task estimates network connectivity and flow magnitude jointly, whereas destination allocation distributes a supplied origin outflow.

Vo et al. study multiday, multimodal, time-dependent origin–destination (TD–OD) flows that describe when, where, and how urban travel occurs [7]. Their Singapore and Seoul study recovers unobserved modes by fusing household travel surveys with smart-card counts. A densely observed reference mode supplies information for recovering other modes, a different source of evidence from a mode's own forecasting history. Validation uses CPC and $R^2$ on city-scale TD–OD tensors [7]. These tensors represent variation across travel modes and time in addition to origin and destination.

Commuting benchmarks and generated products broaden geographic coverage. Rong et al. release a large U.S. commuting-flow generation benchmark [8], while satellite-semantic generators supply flow proxies for locations with limited census coverage [9]. Such resources support model development and later transfer studies. The New York, London, and Paris evaluations use the observed mobility or commuting records associated with each study area.

MapAgents follows the Deep Gravity allocation formulation. Its inputs are a study area, supplied origin outflows, a mass prior, and built-environment measurements. It produces a row-normalized flow allocation

$$
\widehat T_{ij}=O_i p_{j\mid i}
$$

and an inspectable spatial program. The origin outflow $O_i$ sets the row total, while the mass prior $M_z$ supplies an endpoint covariate. A discovered feature is a closed-form pair expression whose numerical contribution changes destination probabilities. Program transfer applies these expressions to target geography; parameter transfer adapts learned coefficients or predictor weights within the same allocation formulation.

Geospatial LLM systems provide tools for constructing these measurements. Urban-MAS extracts urban factors for perception-style prediction [10]. Map-layer agents support tool-mediated access to OSM [11], and GeoColab and GeoJSON Agents generate or call geospatial code [19, 20]. These capabilities motivate Surveyor's raw-map queries. MapAgents connects the resulting measurements to directed pair expressions and evaluates their contribution to destination allocation through CPC and an additive program head on Deep Gravity.

LLM-based agents after 2023 follow a short causal chain: first a single model learned to act and revise, then roles acquired structured handoffs, then workflows themselves became searchable, and by 2026 the open questions are verification, topology, and cost.

In 2023, a single language model learned to interleave reasoning with external actions and to revise later trials from feedback. ReAct and Toolformer established tool-conditioned investigation rather than closed-book prompting [15, 24]. Reflexion and Self-Refine established iterative repair from verbal or self-generated feedback [25, 26]. PAL and Voyager established programs as the object that is executed and repaired [27, 28]. CAMEL showed that role-play can organize a dialogue [17], but it did not yet specify what artifact one agent owes another.

In 2024, the field moved from dialogue to workflow. MetaGPT, AgentVerse, ChatDev, and AutoGen treated roles as SOP positions with different outputs—a plan, a program, a review—rather than decorative personas [16, 29–31]. Multi-agent debate added an explicit critic channel [32]. In parallel, CAAFE showed that an LLM can propose tabular features from task semantics [33], which is the closest ancestor of automated representation search, while WorldCoder and CodeAct reinforced execution-grounded program revision [18, 34].

In 2025, ADAS and AFlow asked whether the workflow graph itself should be searched in code [35, 36]. That question is real, but it multiplies candidate systems. It does not test one scientifically motivated factorization of investigation, compilation, and selection.

By 2026 the default background is no longer “multi-agent versus a single prompt.” ICLR and ICML each contain several hundred agent papers, and AAMAS added a Generative and Agentic AI area [37]. The live designs are specialized triads such as MAS²’s generator–implementer–rectifier [38]; tool-integrated and self-verifying agents [39, 40]; topology and routing as objects [41, 42]; and intervention-based debugging rather than log-only attribution [43]. At the same time, ungrounded hierarchy is no longer assumed to help. A manager who can only send work back without an external check can raise token cost and lower quality [44, 45]. MALMAS is the nearest 2026 system for multi-agent feature generation with memory and validation feedback [23], but it still operates on tabular columns rather than raw geographic measurements and directed origin–destination programs.

MapAgents sits on this chain at a specific point. It keeps the 2023 tools-and-programs lesson, the 2024 role-and-handoff lesson, and the 2026 verification-and-budget lesson. It does not claim a new coordination protocol and does not search over agent topologies.

Official engineering accounts make these architectural choices concrete. Anthropic's research system uses a lead agent to delegate investigations to specialists with separate contexts, then synthesizes their findings with source attribution [46]. Its 2026 application-development harness separates planning, generation, and evaluation, exchanges structured artifacts, and obtains evaluator feedback by exercising the running application [47]. These examples connect role specialization to the information passed between agents and to the observations used for revision.

OpenAI's current Agents SDK guidance distinguishes handoffs, which transfer control to a specialist, from agents-as-tools, which retain a manager's ownership of the workflow [48]. Agent definitions associate each specialist with its instructions, tools, and structured output type [49]. LangChain's multi-agent guide distinguishes subagents, handoffs, skills, routers, and custom workflows, with context selection as a central design decision [50]. Its Deep Agents guide further distinguishes isolated subagents from workers that inherit the parent's conversation, and supports structured results returned to the supervisor [51].

MapAgents uses a fixed sequence of investigation, compilation, and numerical selection. Surveyor passes geographic findings and measurement requests to Cartographer; executable candidates and fitted outcomes return to Adapter. The transferable design lesson from these guides is the explicit treatment of specialist inputs, output artifacts, and feedback. In MapAgents, execution reports and validation CPC supply the observations that determine whether an edit is retained.

---

## 4. Task, DGM priors, and information availability

### 4.1 Prediction support and supplied totals

For origin $i$, let $\mathcal D_i$ be the declared candidate destination set. It contains all retained zones in its DGM tile for the native New York example, or all zones in the declared study area for a complete-area task. The target is

$$
\widehat T_{ij}=O_i p_{j\mid i},\qquad
O_i=\sum_{j\in\mathcal D_i}T_{ij},\qquad
\sum_{j\in\mathcal D_i}p_{j\mid i}=1.
$$

The prediction task is destination allocation with a supplied origin outflow, as in Deep Gravity [3].

Inference evaluates and normalizes over the complete declared destination set. Computational batches do not define separate softmax denominators. Diagonal cells are retained when present in the source and are reported separately in the analysis.

The New York tile task is a collection of complete within-tile matrices. It is not a complete New York State matrix: cross-tile pairs lie outside its prediction support. A whole-area extension changes the task and receives a separate experiment label.

### 4.2 Decomposing the public DGM feature construction

The eighteen geographic variables follow the public Deep Gravity schema for New York [3]. These aggregation patterns provide a prior catalog available to all feature-discovery methods.

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

This mass variable is an origin-outflow prior constructed by the public loader [3]. It is not a census population count.

This sum is computed from the complete source flow file before within-tile filtering. Missing or zero values are replaced by $10^{-6}$ before taking the logarithm. At the destination endpoint, $M_j$ is the outgoing total of zone $j$, not its incoming total.

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

The three-agent split follows the 2024 workflow lesson and the 2026 verification lesson rather than an undifferentiated multi-agent chat [16, 29–31, 38, 43]. Each role has different evidence rights and a required output type [48–51].

Surveyor is the contractor for evidence. It may use source metadata, the DGM aggregation prior, raw OSM objects, retrieved mobility documents, directed pair profiles, and Adapter-specified diagnostic targets [15, 24, 39]. It may not inspect test residuals or edit model weights. Its output is an evidence-backed mechanism, an origin/destination role hypothesis, and an executable measurement request.

Cartographer is the contractor for programs. Following PAL, Voyager, WorldCoder, and later self-verifying code agents, a hypothesis is accepted only after it compiles, executes, and exhibits non-degenerate numerical behavior [18, 27, 28, 34, 40]. Cartographer may not invent undeclared source columns or treat a failed query as support. Its output is a typed expression $\phi\_k$, an evidence binding to a successful measurement, and a repair log.

Adapter is the manager. Like Reflexion and Self-Refine, it turns a failure signal into the next attempt [25, 26]. Unlike free-form reflection, and in line with DoVer and grounded loop-back studies, that signal is external: validation residuals and numerically fitted candidate comparisons [43–45]. Adapter may not select programs on the test set. Its output is a bounded diagnostic contract, a keep-or-reject decision, and the next measurement budget.

A round transfers four artifacts, all written to the run record: a directed `hypothesis` with `origin_role` and `destination_role`; a `measurement_request` that names tags, scale, neighborhood, and whether endpoints are reversed; a `program_edit` with its execution report; and a `candidate_outcome` containing training loss, off-diagonal CPC, the change relative to the incumbent, and the keep bit. A multi-agent dialogue that does not emit these objects is a single agent speaking in three voices.

A candidate enters the retained program if and only if four gates pass. The executor gate requires finite, non-constant, non-duplicate values and an evidence link to a successful measurement. The role gate records $\phi\_k(i,j)$ and $\phi\_k(j,i)$ for any directed claim and rejects an origin-only additive term, which is constant on a destination row and cancels under softmax. The fit gate requires that, under the same training protocol, validation off-diagonal CPC is at least that of the incumbent and at least that of continued training of the unchanged program. The budget gate requires that LLM calls, tool queries, and candidate fits remain inside the ceiling frozen before test evaluation. The system keeps expression identity and transferable coefficients, not a more fluent explanation.

The method is therefore a fixed three-node workflow, not an automatically designed MAS. MAS² and CARD show that generator–implementer–rectifier teams and conditional topologies can be searched [38, 41]; those results justify the role names, not an open search over graphs. DoVer and execution-based code agents justify intervening on failed artifacts rather than trusting a reasoning trace [40, 43]. Loop-back and grounded-reflection studies justify giving Adapter an external gate rather than a critique message [44, 45]. MALMAS and CAAFE justify language-guided feature search with validation feedback [23, 33], while leaving raw-map recovery and directed OD composition as the gap this paper tests.

A standard optimizer fits model weights. Adapter controls the prescribed search and fitting workflow; the LLM does not invent gradients or replace numerical optimization.

### 5.2 Surveyor: retrieval and local investigation

Surveyor uses two complementary evidence sources. Knowledge retrieval covers OSM tag meanings, mobility-related feature organization, and known aggregation recipes, drawing on the local `resources/LLMrag` collection. Geographic retrieval executes against the actual study-area objects and covariates. Following ReAct [15], Surveyor interleaves reasoning with tool queries and uses the returned observations to guide its investigation.

The knowledge collection has three connected layers. `handbooks/` holds source documents, while `handbooks/SOURCES.md` records their official URLs and the local acquisition date. `catalogs/` organizes the contents of six source families; `inventories/` contains tabular tag and variable descriptions. `catalog.md` and `catalog.json` index these resources, and `catalog_to_tasks.md` relates geographic covariates, spatial units, and observation types. The resulting organization lets Surveyor move from a concept to a field or tag and then to the document that defines it.

| Source family | Primary documentation in the collection | Evidence supplied to the investigation |
| --- | --- | --- |
| OpenStreetMap | Map features and Elements wiki pages [52, 53], with local tag, format, and query documentation | Tag meanings, element geometry, and object identifiers for executable map measurements |
| NHTS 2022 | NextGen user guide and V2.1 codebook [54, 55], with derived-variable and weighting documents | Trip-purpose and travel-mode definitions, record linkage, survey weights, and missing-value codes |
| LODES | LEHD dataset structure, format version 8.4 [56] | Residence and workplace block identifiers, job-count fields, and OD/RAC/WAC file semantics |
| CTPP | 2017–2021 methodology report [57], with portal and key-consideration documents | Residence, workplace, and worker-flow table definitions, geographic support, and disclosure treatment |
| ACS PUMS | Census Bureau PUMS handbook [58] | Person and housing record structure, weights, and the distinction between residence PUMA and workplace PUMA |
| WorldPop | Global 2 release statement R2025A v1 [59], with methods and training chapters | Gridded population definitions, age/sex and year codes, spatial resolution, and constrained population mapping |

The local inventories contain 1,503 OSM tag rows, 427 NHTS variable rows, and 2,718 NHTS code rows. The retrieval index represents each OSM tag as a separate record containing its key, value, group, geometry, and available wiki comment. It divides the five other catalogs into paragraph-based text blocks and indexes the task map separately. Each retrieved record carries an `id`, a relative `source` path, its text, and a retrieval score. Ranking combines BM25 and TF-IDF cosine similarity through reciprocal-rank fusion, with an additional embedding ranking when enabled. The NHTS inventories and archived PDF/HTML handbooks remain source material behind the catalog summaries; the current index reads the catalogs and OSM inventory directly.

Surveyor uses this documentation to interpret a candidate measurement. OSM definitions identify the tags and element types to query; NHTS, LODES, CTPP, and PUMS explain the meaning of movement-related variables and observations; WorldPop documents an independent population product. The New York numerical mass input remains the loader-derived outflow $M_z$ defined in §4.3. A retrieved population or commuting definition supplies semantic context, while the study-area data determine which numerical quantities are available.

The evidence record connects these semantic and numerical sources. A hypothesis carries `knowledge_ids` for retrieved definitions and `map_evidence_ids` for executed measurements. Knowledge IDs resolve to indexed text and its catalog or inventory path; the catalog source statement and `handbooks/SOURCES.md` lead to the original handbook or wiki page. Successful map records supply the measured values, which Cartographer binds to a program expression. The expression, execution report, and fitted candidate outcome then preserve the path from source definition to measurement and prediction change.

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

The executor checks syntax, units where available, source columns, numerical finiteness, variation, duplication, and evidence references. Failed requests return explicit feedback.

Executable repair is the acceptance criterion. Program-as-action agents treat compiler and environment errors as first-class feedback [18, 27, 28, 34]. The executor’s syntax, unit, finiteness, variation, and duplication checks play that role here. A feature that appears only in a reasoning trace is not part of the program [40, 43].

New feature names cannot be used as if they were raw source columns unless a documented reference-expansion mechanism exists.

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

The base score $g_\theta(x_{ij}^{\mathrm{DG}})$ is the Deep Gravity predictor [3]. The additive program branch preserves this allocator and makes the discovered terms inspectable.

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

Reflexion stores verbal lessons across trials and Self-Refine revises an output from self-feedback [25, 26]. Adapter uses a stronger oracle: training-set fitting plus off-diagonal validation CPC. Continuing the unchanged Deep Gravity program with the same extra fitting budget is required, because additional attempts alone can look like a method gain [25, 44]. Adapter may reject a worker output only when the executor or the fit gate fails; a manager who can only opine is not given loop-back authority [44, 45].

A working development budget is three rounds with two candidates per round. The final budget and stopping rule are fixed before test evaluation. Continuing DG training is an essential control, but equal continuation depth is not equal compute: the agent search evaluates additional candidate models.

The loop transfers both program information and compatible numerical parameters when useful. It does not require frozen weights or assume that changing program text is cheaper than model fitting.

---

## 6. Data and four-week scope

New York is the initial debugging and method-development area. London and Paris are the intended core external areas; Madrid and Barcelona provide additional settings once their suppression and support rules are handled. Italy remains a separately documented extension. The goal is a small set of scientifically usable settings, not a claim that a particular city count guarantees publication.

| Study area | Observation source | Unit |
| --- | --- | --- |
| New York State | GeoDS mobility observations distributed in the public DGM example | GeoDS flows |
| Greater London | 2011 Census WU03EW residence-to-work table | People |
| Paris / Ile-de-France | INSEE 2022 census residence-to-work table, with 2025 geographic codes | Weighted census counts |
| Madrid province / autonomous community | INE 2023 registered residence-to-work table | People |
| Barcelona province | INE 2023 registered residence-to-work table | People |
| Italy | ISTAT 2011 municipality residence-to-work table | People |

The geographic units are census tracts within native DGM tiles in New York, 983 MSOAs in Greater London, 1,285 communes and Paris arrondissements, 179 municipalities in Madrid, and 311 municipalities in Barcelona. The Italian data use municipalities, with the study-area subset defined before fitting.

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

CPC is the primary overlap metric used for Deep Gravity [3]. Off-diagonal CPC is reported separately on the New York matrix because of the large internal diagonal share.

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

### 8.1 Main mobility-flow generation table

The core table uses G, DG, and MapAgents. Gravity's power and exponential distance variants may be shown as two rows or selected on validation with the choice declared. Each uses the documented mass prior and the same output-total condition.

NY only, 163 test tiles, `dgm_mass` prior. CPC is internal-matrix CPC, not the original DGM evaluator (0.444 on 188 tiles). Diagonal share 0.888; off-diagonal CPC is the informative column. Audit: `runs/new_york_main_table/REPORT.md`.

| Method | Mass and geographic inputs | CPC | RMSE | Off-diagonal CPC | Off-diagonal RMSE |
| --- | --- | ---: | ---: | ---: | ---: |
| Gravity | Declared mass prior and distance; fitted deterrence parameters | 0.902 | 148.2 | 0.208 | 137.0 |
| Deep Gravity | Original `main.py`, 39-d mass+geography, last epoch | 0.911 | 121.8 | 0.431 | 114.2 |
| MapAgents + DG | Same base inputs plus discovered role-aware spatial program; joint training | 0.935* | 97.0* | 0.513* | 93.2* |

Gravity uses mass and distance [1]. Deep Gravity uses the reproduced 39-dimensional geographic input [3]. MapAgents adds the discovered program to that same base.

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

Program transfer executes source-discovered expressions on target geography. Parameter transfer adapts source-trained model weights or fits new target weights with the program fixed. Joint adaptation revises both the spatial program and its numerical parameters. Each setting retains the destination-allocation task with supplied target origin outflows.

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

The knowledge-source record includes the catalog and inventory snapshots, the source register, and the retrieval configuration used by each run. The current handbook register records acquisition on 20 August 2026; its LODES and ACS PUMS entries identify Internet Archive copies of official Census PDFs. Source-document versions and acquisition routes are retained alongside the original publisher URLs. Retrieved IDs are released with the indexed text and relative source paths, so the run's evidence links can be resolved against the same corpus snapshot. The PUMS catalog identifies the 2021 handbook as its local source; the year-specific full variable dictionary is not present in that snapshot.

The proposal's current working artifacts are `resources/priors/deepgravity.json`, `DISCOVERY.md`, and the historical New York data manifest. These identify development material; they are not evidence that the complete DG reproduction or planned ablations have been completed. Public data remain subject to their source licenses, and private API credentials are not part of the release.

---

## 14. Target metadata

- **Area:** Generative and Agentic AI.
- **Keywords:** multi-agent systems; retrieval-augmented generation; spatial program discovery; mobility-flow generation; destination allocation; role-aware representations; interpretable prediction.
- **Working title:** MapAgents: Evidence-Grounded Multi-Agent Discovery of Role-Aware Spatial Programs for Mobility-Flow Generation.
- **Central empirical question:** Does coordinated, evidence-grounded discovery of role-aware spatial programs improve mobility-flow generation beyond a fixed Deep Gravity geographic feature schema while preserving supplied origin outflows and explaining the program's numerical contribution?

---

## References

1. Simini, F., González, M. C., Maritan, A. & Barabási, A.-L. A universal model for mobility and migration patterns. *Nature* **484**, 96–100 (2012). https://doi.org/10.1038/nature10856
2. Masucci, A. P., Serras, J., Johansson, A. & Batty, M. Gravity versus radiation models: on the importance of scale and heterogeneity in commuting flows. *Phys. Rev. E* **88**, 022812 (2013). https://doi.org/10.1103/PhysRevE.88.022812
3. Simini, F., Barlacchi, G., Luca, M. & Pappalardo, L. A Deep Gravity model for mobility flows generation. *Nat. Commun.* **12**, 6576 (2021). https://doi.org/10.1038/s41467-021-26752-4
4. Cabanas-Tirapu, O., Danús, L., Moro, E., Sales-Pardo, M. & Guimerà, R. Human mobility is well described by closed-form gravity-like models learned automatically from data. *Nat. Commun.* **16**, 1515 (2025). https://doi.org/10.1038/s41467-025-56495-5
5. Atwal, K. S., Anderson, T., Pfoser, D. & Züfle, A. Commuting flow prediction using OpenStreetMap data. *Comput. Urban Sci.* **5**, 2 (2025). https://doi.org/10.1007/s43762-025-00161-5
6. Yang, J., Huang, S., Huang, Z., Jin, Y., Yang, X., González, M. C. & Xu, Y. Transferable human mobility network reconstruction with neuroGravity. *Nat. Comput. Sci.* **6**, 630–641 (2026). https://doi.org/10.1038/s43588-026-01003-y
7. Vo, K. D., Ham, S. W., Roy, M., Mishra, S. & Bansal, P. Uncovering latent urban mobility patterns via smart-card and survey data fusion. *Nat. Commun.* (2026). https://doi.org/10.1038/s41467-026-73445-x
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
24. Schick, T. et al. Toolformer: language models can teach themselves to use tools. In *NeurIPS* (2023).
25. Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K. & Yao, S. Reflexion: language agents with verbal reinforcement learning. In *NeurIPS* (2023).
26. Madaan, A. et al. Self-Refine: iterative refinement with self-feedback. In *NeurIPS* (2023).
27. Gao, L. et al. PAL: program-aided language models. In *ICML* (2023).
28. Wang, G. et al. Voyager: an open-ended embodied agent with large language models. arXiv:2305.16291 (2023).
29. Chen, W. et al. AgentVerse: facilitating multi-agent collaboration and exploring emergent behaviors. In *ICLR* (2024).
30. Qian, C. et al. ChatDev: communicative agents for software development. In *ACL* (2024).
31. Wu, Q. et al. AutoGen: enabling next-gen LLM applications via multi-agent conversation. In *COLM* (2024).
32. Du, Y., Li, S., Torralba, A., Tenenbaum, J. B. & Mordatch, I. Improving factuality and reasoning in language models through multiagent debate. In *ICML* (2024).
33. Hollmann, N., Müller, S. & Hutter, F. Large language models for automated data science: introducing CAAFE for context-aware automated feature engineering. In *NeurIPS* (2023).
34. Wang, X. et al. Executable code actions elicit better LLM agents. In *ICML* (2024).
35. Hu, S., Lu, C. & Clune, J. Automated design of agentic systems. In *ICLR* (2025).
36. Zhang, J. et al. AFlow: automating agentic workflow generation. In *ICLR* (2025).
37. Wooldridge, M. Rethinking multi-agent systems in the era of LLMs. Keynote, *AAMAS* (2026).
38. Wang, K. et al. MAS²: self-generative, self-configuring, self-rectifying multi-agent systems. In *ICLR* (2026).
39. Feng, J. et al. ReTool: reinforcement learning for strategic tool use in LLMs. In *ICLR* (2026).
40. Xia, Y. et al. SimpleTIR: end-to-end reinforcement learning for multi-turn tool-integrated reasoning. In *ICLR* (2026).
41. Wu, T. et al. CARD: towards conditional design of multi-agent topological structures. In *ICLR* (2026).
42. Nielsen, S. et al. Learning to orchestrate agents in natural language with the Conductor. In *ICLR* (2026).
43. Ma, M. et al. DoVer: intervention-driven auto debugging for LLM multi-agent systems. In *ICLR* (2026).
44. Agachan, B., van Duijn, M. & Zohrehvand, A. Loop-back authority in LLM agent teams. arXiv:2609.14767 (2026).
45. Chen, Y. et al. Bilevel coordinated reflection: a game-theoretic approach to multi-agent LLM systems. arXiv:2609.02750 (2026).
46. Anthropic. How we built our multi-agent research system. *Anthropic Engineering* (13 June 2025). https://www.anthropic.com/engineering/multi-agent-research-system
47. Rajasekaran, P. Harness design for long-running application development. *Anthropic Engineering* (24 March 2026). https://www.anthropic.com/engineering/harness-design-long-running-apps
48. OpenAI. Orchestration and handoffs. *Agents SDK documentation*. https://developers.openai.com/api/docs/guides/agents/orchestration (accessed 15 September 2026).
49. OpenAI. Agent definitions. *Agents SDK documentation*. https://developers.openai.com/api/docs/guides/agents/define-agents (accessed 15 September 2026).
50. LangChain. Multi-agent. *LangChain documentation*. https://docs.langchain.com/oss/python/langchain/multi-agent (accessed 15 September 2026).
51. LangChain. Subagents. *Deep Agents documentation*. https://docs.langchain.com/oss/python/deepagents/subagents (accessed 15 September 2026).
52. OpenStreetMap contributors. Map features. *OpenStreetMap Wiki*. https://wiki.openstreetmap.org/wiki/Map_features (local source snapshot acquired 20 August 2026).
53. OpenStreetMap contributors. Elements. *OpenStreetMap Wiki*. https://wiki.openstreetmap.org/wiki/Elements (local source snapshot acquired 20 August 2026).
54. Federal Highway Administration. 2022 NextGen NHTS User's Guide. Version 2.0.1. *National Household Travel Survey documentation*. https://nhts.ornl.gov/media/2022/doc/2022%20NextGen%20NHTS%20User's%20Guide%20V201_PubUse.pdf
55. Federal Highway Administration. 2022 NextGen NHTS codebook. Version 2.1 (April 2025). https://nhts.ornl.gov/media/2022/doc/codebook.xlsx
56. U.S. Census Bureau. LEHD Origin-Destination Employment Statistics (LODES) Dataset Structure. Format version 8.4, revision 3 December 2025. https://lehd.ces.census.gov/doc/help/onthemap/LODESTechDoc.pdf
57. Westat. CTPP Methodology Report. Report CBDRB-FY25-ACSO003-B0001 (March 2025). https://ctppdata.transportation.org/CTPP_Methodology_Report.pdf
58. U.S. Census Bureau. Understanding and Using the American Community Survey Public Use Microdata Sample Files: What Data Users Need to Know (February 2021). https://www.census.gov/content/dam/Census/library/publications/2021/acs/acs_pums_handbook_2021.pdf
59. WorldPop. Global 2 Release Statement. R2025A v1 (September 2025). https://data.worldpop.org/repo/prj/Global_2015_2030/R2025A/doc/Global2_Release_Statement_R2025A_v1.pdf
