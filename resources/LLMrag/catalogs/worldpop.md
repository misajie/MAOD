# WorldPop catalog

Source: Global Demographic Data public release R2025A V1 (September 2025); Book of Methods; methods pages. `handbooks/worldpop/`.

## Global 2 gridded demographic rasters (R2025A)

- 242 countries/territories; annual 2015–2030
- Age and sex structure
- Constrained top-down random forest dasymetric (`popRF`)
- Grid: 3 arc-seconds (~100 m at equator); 1 km mosaics also described on methods pages
- National totals aligned to UN WPP 2024, 1 January
- Alpha public release; mastergrid is not aligned with Global 1 (2000–2020)

Filename: `{iso}_{gender}_{age}_{year}_{type}_{resolution}_{release}_{version}.tif`

| Field | Values in the release note |
|---|---|
| iso | ISO-3 |
| gender | `m` male, `f` female, `t` both |
| age | `00` ages 0–12 months; `01` ages 1–4; `05` ages 5–9; … ; `90` ages 90+ |
| year | 2015–2030 |
| type | `CN` constrained |
| resolution | e.g. `100m` |
| release / version | `R2025A` `v1` |

Example: `afg_f_00_2016_CN_100m_R2025A_v1.tif`.

Not modelled (uninhabited or static): ATF, BVT, CPT, HMD, IOT, SGS, SPR, UMI, VAT.

Companion tables on WorldPop FTP `Global_2015_2030/R2025A/doc/`:

- `global2_census_data_sources_R2025A_v1.xlsx`
- `global2_covariates_metadata_R2025A_v1.xlsx`

## Other WorldPop product families (Book of Methods / methods pages)

| Family | What it contains |
|---|---|
| Top-down unconstrained | Population in every land cell (Global 1-style and unconstrained top-down pages) |
| Top-down constrained | Population only in mapped built/residential cells (Global 2 `CN`) |
| Bottom-up / WOPR | Country-specific estimates from surveys, with uncertainty |
| Peanut butter | People-per-building mapped onto footprints |
| Covariate library | Global rasters used in RF (elevation, slope, climate, night lights, land cover, distance to roads/water/protected areas, settlement layers) |
| Built settlement time series | Annual 100 m built mask from GHSL BUILT-S/V, Google Open Buildings, Microsoft footprints, WSF |
| Age-sex / births / pregnancies / urban change / development indicators | Additional Hub/FTP layers; not all are Global 2 |

Access: hub.worldpop.org, FTP, REST API, `wpgpDownloadR`, `wpgpDownloadPy`, QGIS/ArcGIS plugins, WOPR.
