# CTPP catalog

Source: 2017–2021 Key Considerations; Methodology Report (Westat, March 2025, CBDRB-FY25-ACSO003-B0001); Data Portal User Guide; Summer 2025 Status Report. Local PDFs in `handbooks/ctpp/`.

These files describe the **table package and geography**, not a single flat codebook of every cell. Table IDs are selected in the portal (`ctppdata.transportation.org`).

## What the product is

Special ACS 5-year tabulations for transportation. Releases in the portal: 2017–2021 (March 2025), 2012–2016, 2006–2010, 2000.

Three parts:

| Part | Content |
|---|---|
| 1 Residence | Characteristics of people at residence |
| 2 Workplace | Characteristics of workers at workplace. 2017–2021 Part 2 has housing as a topic; **no PUMA geography** |
| 3 Worker flows | Home-to-work flows, including travel mode. 2017–2021 also adds Housing and Populations and People topics |

About 20 universes (total population vs population in households; about half are workers only; some include group quarters).

Versus standard ACS (Key Considerations Q3): CTPP has journey-to-work **flows**; workplace tables to tract (ACS workplace tables stop at county); 2017–2021 has 12 commute-mode crosstabs vs 5 in ACS.

## 2017–2021 geography

Smallest general unit: **census tract**. **No TAZ, no TAD.**

Part 1 / 2 summary levels listed: Nation (no PR); States; State (Part 2 includes Mexico, Canada, Other); State-County; State-County-MCD (12 MCD-strong states); State-Place; State-PUMA5 (Part 1 only); MSA–each principal city; State-County-Tract; Block groups for **3 tables only**.

Block-group tables only:

1. Total Population
2. Means of Transportation to Work
3. Time of Departure To Go To Work

Part 3 flow pairs: State–State; County–County; MCD–MCD; Place–Place; MSA–MSA; Place–County; County–Place; MCD–Place; PUMA5–Place; Tract–Tract; Tract–County; County–Tract.

## Disclosure treatments baked into the numbers

- All 2017–2021 tables come from **synthetic** ACS microdata (not a mix of unperturbed Set A / perturbed Set B).
- Target: about 50% of ACS 2017–2021 5-year records synthesized (MACH hot deck).
- All table cells rounded; flows need ≥3 unweighted ACS observations; non-residence geographies need 50 unweighted cases or they are suppressed; mean/median/aggregate need ≥3 observations.
- Tables with ≥100 cells drop small geographies unless collapsed; 100–125 cells: places ≥10,000+; >125 cells: geographies ≥100,000.
- Variable “Age of youngest person in the household” removed.
- ACS unweighted counts use differential privacy from ACS 2019 / 2015–2019 onward.

Portal download formats: CSV, XML, JSON, SHP, TAB. Default fields: estimate and MOE. API explorer on the same host.
