# ACS PUMS catalog

Source: *Understanding and Using the American Community Survey Public Use Microdata Sample Files: What Data Users Need to Know*, Census Bureau, February 2021. `handbooks/pums/ACS_PUMS_Handbook_2021.pdf`.

The **full variable dictionary is not in this handbook**. Official list is the year-specific PUMS Data Dictionary on census.gov (not downloaded here). Handbook statement: about **250 person-level** and **200 housing-level** variables.

## What the files contain

| Item | Content |
|---|---|
| Person file (`p`) | One record per person in sampled housing units, plus group-quarters persons |
| Housing file (`h`) | One record per sampled housing unit, including vacant units |
| Link | `SERIALNO` (housing unit, unique nationally) and `SPORDER` (person within unit) |
| Record type | `RT` = `P` on person records |
| Weights | Population weights for people; household weights for housing units. Required |
| Sample | About two-thirds of the ACS sample. 1-year ≈ 1% of population; 5-year ≈ 5% (concatenated 1-year PUMS) |
| Formats on FTP | CSV and SAS; ZIP named by format × `h`/`p` × state abbreviation (`us` = nation, excludes PR) |
| National splits | 1-year `a`+`b`; 5-year `a`–`d` |

Housing record examples in the handbook: rooms, vacancy, internet, mortgage, household income, presence of children, vehicles available.

Person record examples in the handbook: age (`AGEP`), sex (`SEX`), marital status, educational attainment, state (`ST`), means of transportation to work (`JWTR`).

`JWTR` is missing when the person is not a worker.

## Geography that exists on the file

Only: nation, region, division, state, PUMA.

PUMA: 5-digit code, unique **within state**; use with state FIPS. Population ≥100,000 at delineation; built from counties and census tracts; does not cross state lines; redrawn each decade. Handbook figure: 2,378 PUMAs on 2010 vintage.

`POWPUMA`: primary place of work. `MIGPUMA`: residence 1 year ago. Same codes/boundaries as each other; county-based; may merge several standard PUMAs, in which case the code matches **no** standard PUMA.

Confidentiality treatments on the file: subsample only; no names/addresses; swapping with neighboring areas; top/bottom coding of selected variables; coarse geography. PUMS estimates need not match published ACS tables. Verify with “PUMS Estimates for User Verification”.

Access described in the handbook: FTP; data.census.gov Microdata Access Tool.
