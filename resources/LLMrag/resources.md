**Complete Official Overview of Key Spatial Demographic and Urban Population Mobility Datasets**

This is a fully organized compilation of official introductions to WorldPop, OpenStreetMap (OSM), NHTS, PUMS, and other highly recognized statistical datasets related to urban population distribution and mobility/flows. Information is based on official sources as of mid-2026.

### 1. WorldPop

**Overview**  
WorldPop is an interdisciplinary research group based at the University of Southampton (UK). Its mission is to ensure that everyone, everywhere is counted in decision-making by producing high-resolution, open-access spatial demographic datasets. It was initiated in 2013 by unifying earlier regional projects (AfriPop, AsiaPop, AmeriPop).

**Key Data Products**  
- **Global 2** (latest major release, launched 2025): Annual high-resolution gridded population estimates for 2015–2030 covering 242 countries and territories. Available at 100 m × 100 m and 1 km resolution, with age and sex breakdowns.  
- Incorporates 2010 and 2020 census rounds, enhanced settlement data (GHSL, World Settlement Footprint), building footprints, satellite imagery, nighttime lights, and other covariates.  
- Uses top-down random forest dasymetric modelling.  
- Additional products: country-specific (bespoke) estimates (often co-produced with governments/UN agencies), population density, development indicators (poverty, literacy, vaccination coverage), population dynamics, migration flows, and degree-of-urbanisation maps.  
- Earlier Global 1 series (approx. 2000–2020) remains archived.

**Uses**  
Default subnational population data for UN agencies; supports DHIS2 health systems (covering billions of people), disaster response, vaccination campaigns, SDG monitoring, and urban planning.

**Access**  
- Official website: https://www.worldpop.org/  
- Data Hub/Catalog: https://hub.worldpop.org/  
- Country-specific (WOPR): https://wopr.worldpop.org/  
- Formats: primarily GeoTIFF; also available via HDX and APIs.  
- Free and open; citation required (www.worldpop.org + dataset-specific DOI).

### 2. OpenStreetMap (OSM)

**Overview**  
OpenStreetMap is a free, editable map of the entire world created and maintained by a global community of volunteers. Founded in 2004 by Steve Coast in the UK due to the lack of freely usable map data. It is governed by the OpenStreetMap Foundation and often described as the “Wikipedia of maps.”

**Data Content**  
- Roads, buildings, addresses, points of interest (shops, cafés, stations), railways, trails, transit, land use, natural features, and more.  
- Data model: **Nodes** (points), **Ways** (lines/polygons), and **Relations** (complex features), all described by free-form tags (key-value pairs).  
- Continuously updated by nearly 5 million registered users and over 1 million active contributors using GPS, aerial imagery, and local knowledge.

**License**  
Open Database License (ODbL). Free to use for any purpose with attribution to OpenStreetMap and its contributors. Share-alike applies to derived databases.

**Access**  
- Main site: https://www.openstreetmap.org/  
- Full planet dump (weekly): https://planet.openstreetmap.org/ (PBF or compressed XML; ~80–160+ GB compressed).  
- Regional extracts: Geofabrik (https://download.geofabrik.de/), BBBike, etc.  
- APIs: Overpass API for custom queries; editing tools available.  
- About page: https://www.openstreetmap.org/about

**Uses**  
Navigation apps, humanitarian mapping (HOT), government planning, research, commercial services (used by major tech companies), and as base layers for population mobility analysis when combined with demographic data.

### 3. National Household Travel Survey (NHTS)

**Overview**  
The NHTS is the primary source of information on how people in the United States travel. Conducted by the Federal Highway Administration (FHWA), U.S. Department of Transportation. It serves as the nation’s inventory of daily personal travel. Historical series began in 1969 (as NPTS); modern NHTS years include 2001, 2009, 2017, and 2022.

**Key Features (NextGen NHTS)**  
- Collects data on trip purpose, mode of transportation, travel time, distance, time of day/day of week, for all household members.  
- 2022 survey: ~7,893 households (mail/push-to-web design).  
- NextGen redesign: more frequent (biennial) surveys with smaller samples (~7,500 households), focused questions, plus annual passive national Origin-Destination (OD) products for passengers and trucks (2020–2024 available).  
- 2024/2025 survey data collection ran from November 2024 through November 2025.

**Uses**  
Quantify travel behaviour, analyse trends over time, study demographic-travel relationships, assess emerging mobility services, and support transportation planning and policy.

**Access**  
- Main site: https://nhts.ornl.gov/  
- FHWA page: https://www.fhwa.dot.gov/policyinformation/nhts.cfm  
- Passive OD data: https://nhts.ornl.gov/od/  
- Free download in multiple formats (CSV, SAS, SPSS, etc.).

### 4. Public Use Microdata Sample (PUMS)

**Overview**  
PUMS files are anonymized individual-level records from the American Community Survey (ACS) produced by the U.S. Census Bureau. They allow users to create custom tabulations not available in standard ACS summary tables while protecting confidentiality.

**Key Features**  
- 1-year and 5-year files.  
- Includes housing and person records with variables on demographics, socioeconomic status, commuting (mode, travel time, workplace), vehicles, etc.  
- Smallest geography: Public Use Microdata Areas (PUMAs) of approximately 100,000 people.  
- Sample is roughly 1% (1-year) or larger for multi-year files.

**Uses**  
Custom analysis of commuting patterns, residential mobility, and demographic characteristics at sub-state levels; complementary to aggregated ACS and CTPP data.

**Access**  
- Official page: https://www.census.gov/programs-surveys/acs/microdata.html  
- Tools: data.census.gov Microdata Access Tool and FTP site.  
- Comprehensive documentation, data dictionaries, and user guides available.

### 5. Other Highly Recognized Datasets for Urban Population Mobility

**5.1 Census Transportation Planning Products (CTPP)**  
- Special tabulations of ACS data focused on transportation, funded by state DOTs via AASHTO’s Census Transportation Solutions (ACTS) program.  
- Three parts: residence-based characteristics, workplace-based characteristics, and home-to-work flow matrices (including mode of travel).  
- Supports Traffic Analysis Zones (TAZs) and other planning geographies.  
- Latest major release: 2017–2021 data on the new portal.  
- Official access: https://ctppdata.transportation.org/ (or https://ctpp.transportation.org/).  
- Primary uses: travel demand modelling, transit planning, and policy analysis.

**5.2 LEHD Origin-Destination Employment Statistics (LODES)**  
- Produced by the U.S. Census Bureau’s Longitudinal Employer-Household Dynamics (LEHD) program under the Local Employment Dynamics partnership.  
- Detailed census-block-level data on jobs, worker residence locations, and origin-destination commuting flows.  
- Variables include age, earnings, industry, race, ethnicity, sex, etc.  
- Coverage: 2002–2023 (2023 data released in late 2025; note limited coverage for Alaska and Michigan in 2023).  
- File types: Origin-Destination (OD), Residence Area Characteristics (RAC), Workplace Area Characteristics (WAC).  
- Companion tool: OnTheMap (interactive mapping and reporting).  
- Access: https://lehd.ces.census.gov/ and https://onthemap.ces.census.gov/.  
- Extremely valuable for fine-grained urban commuting and labour-market analysis.
