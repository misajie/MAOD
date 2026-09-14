# LODES catalog

Source: LEHD Origin-Destination Employment Statistics Dataset Structure, Format Version 8.4, Rev. 20251203. `handbooks/lodes/LODESTechDoc.pdf`.

Root: `lehd.ces.census.gov/data/lodes/LODES8/{st}/` with `od/`, `rac/`, `wac/`, `{st}_xwalk.csv.gz`, `lodes_{st}.sha256sum`, `version.txt`.

Geography: 2020 census blocks; TIGER/Line 2024. Years 2002–2023 for most states. 2022–2023: no OD/WAC for Alaska and Michigan. Federal jobs from 2010. Race/ethnicity/education/sex from 2009. Firm age/size from 2011, WAC only, JT02.

Job types in filenames: JT00 All Jobs; JT01 Primary Jobs; JT02 All Private Jobs; JT03 Private Primary Jobs; JT04 All Federal Jobs; JT05 Federal Primary Jobs.

OD `main` = workplace and residence in state; `aux` = workplace in state, residence outside.

## Origin-Destination file

Filename: `{st}_od_{main|aux}_{JTxx}_{year}.csv.gz`

| Pos | Variable | Type | Content |
|---|---|---|---|
| 1 | w_geocode | Char15 | Workplace census block |
| 2 | h_geocode | Char15 | Residence census block |
| 3 | S000 | Num | Total jobs |
| 4 | SA01 | Num | Workers age 29 or younger (2012+: ages 14–29) |
| 5 | SA02 | Num | Workers age 30–54 |
| 6 | SA03 | Num | Workers age 55 or older (2012+: 55–99) |
| 7 | SE01 | Num | Earnings $1250/month or less |
| 8 | SE02 | Num | Earnings $1251–$3333/month |
| 9 | SE03 | Num | Earnings greater than $3333/month |
| 10 | SI01 | Num | Goods producing (NAICS 11, 21, 23, 31–33) |
| 11 | SI02 | Num | Trade, transportation, and utilities (NAICS 42, 44–45, 48–49, 22) |
| 12 | SI03 | Num | All other services (remaining NAICS) |
| 13 | createdate | Char | YYYYMMDD |

## Residence Area Characteristics (RAC)

Filename: `{st}_rac_{SEG}_{JTxx}_{year}_1.csv.gz`

SEG = S000, SA01–SA03, SE01–SE03, SI01–SI03 (same segments as OD columns).

| Pos | Variable | Content |
|---|---|---|
| 1 | h_geocode | Residence census block |
| 2 | C000 | Total jobs |
| 3–5 | CA01 CA02 CA03 | Age: ≤29, 30–54, ≥55 |
| 6–8 | CE01 CE02 CE03 | Earnings bands (same cutpoints as SE*) |
| 9–28 | CNS01–CNS20 | NAICS 11, 21, 22, 23, 31–33, 42, 44–45, 48–49, 51, 52, 53, 54, 55, 56, 61, 62, 71, 72, 81, 92 |
| 29–34 | CR01 CR02 CR03 CR04 CR05 CR07 | Race: White; Black; AIAN; Asian; NHPI; Two or more |
| 35–36 | CT01 CT02 | Not Hispanic or Latino; Hispanic or Latino |
| 37–40 | CD01–CD04 | Education (workers 30+ only): <HS; HS no college; some college/Associate; Bachelor+ |
| 41–42 | CS01 CS02 | Male; Female |
| 43 | createdate | YYYYMMDD |

Race/ethnicity/education/sex columns exist in all years but are zero before 2009.

## Workplace Area Characteristics (WAC)

Filename: `{st}_wac_{SEG}_{JTxx}_{year}.csv.gz`

Same columns as RAC except:

- Pos 1 is `w_geocode` (workplace block)
- Extra firm variables (2011+, JT02 only; otherwise zero):

| Pos | Variable | Content |
|---|---|---|
| 43–47 | CFA01–CFA05 | Firm age 0–1, 2–3, 4–5, 6–10, 11+ years |
| 48–52 | CFS01–CFS05 | Firm size 0–19, 20–49, 50–249, 250–499, 500+ employees |
| 53 | createdate | YYYYMMDD |

## Geography crosswalk `{st}_xwalk.csv.gz`

Primary key `tabblk2020` links to OD/RAC/WAC geocodes. Other codes are current OnTheMap vintages.

| Pos | Variable | Type | Content |
|---|---|---|---|
| 1 | tabblk2020 | Char15 | 2020 census tabulation block |
| 2 | st | Char2 | FIPS state |
| 3 | stusps | Char2 | USPS state |
| 4 | stname | Char100 | State name |
| 5 | cty | Char5 | FIPS county |
| 6 | ctyname | Char100 | County name |
| 7 | trct | Char11 | Census tract |
| 8 | trctname | Char100 | Tract name |
| 9 | bgrp | Char12 | Block group |
| 10 | bgrpname | Char100 | Block group name |
| 11 | cbsa | Char5 | CBSA |
| 12 | cbsaname | Char100 | CBSA name |
| 13 | zcta | Char5 | ZCTA |
| 14 | zctaname | Char100 | ZCTA name |
| 15 | stplc | Char7 | State+place FIPS |
| 16 | stplcname | Char100 | Place name |
| 17 | ctycsub | Char10 | County subdivision |
| 18 | ctycsubname | Char100 | County subdivision name |
| 19 | stcd119 | Char4 | 119th congressional district |
| 20 | stcd119name | Char100 | Congressional district name |
| 21 | stsldl | Char5 | State legislative lower |
| 22 | stsldlname | Char100 | Lower chamber name |
| 23 | stsldu | Char5 | State legislative upper |
| 24 | stslduname | Char100 | Upper chamber name |
| 25 | stschool | Char7 | Unified/elementary school district |
| 26 | stschoolname | Char100 | School district name |
| 27 | stsecon | Char7 | Secondary school district |
| 28 | stseconname | Char100 | Secondary school district name |
| 29 | trib | Char5 | AIANNH area |
| 30 | tribname | Char100 | AIANNH name |
| 31 | tsub | Char7 | Tribal subdivision |
| 32 | tsubname | Char100 | Tribal subdivision name |
| 33 | stanrc | Char7 | Alaska Native Regional Corporation |
| 34 | stanrcname | Char100 | ANRC name |
| 35 | mil | Char22 | Military installation landmark |
| 36 | milname | Char100 | Military installation name |
| 37 | stwib | Char8 | Workforce Innovation Board area |
| 38 | stwibname | Char100 | WIB area name |
| 39 | blklatdd | Num | Block internal-point latitude |
| 40 | blklondd | Num | Block internal-point longitude |
| 41 | createdate | Char8 | YYYYMMDD |
