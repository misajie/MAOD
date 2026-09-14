# NHTS 2022 catalog

Source: 2022 NextGen NHTS National ABS Data User Guide V2.0.1; codebook xlsx V2.1 (April 2025).
Code lists with frequencies: `inventories/nhts_codes.csv`.

## Files

| File | Record | IDs |
|---|---|---|
| HOUSEHOLD | one household | HOUSEID |
| PERSON | one household member | HOUSEID, PERSONID |
| VEHICLE | one household vehicle (absent if none) | HOUSEID, VEHID |
| TRIP | one travel-day trip, 4:00 a.m. to next 4:00 a.m., including loop trips | HOUSEID, PERSONID, TRIPID |
| Long Distance | long-distance records in the codebook workbook | (see variables) |

Formats: CSV, SAS, SPSS. Special codes: `-1` Valid Skip / Appropriate skip, `-9` Not ascertained, `-7` Prefer not to answer, `-8` Don't know.

NextGen national passenger OD and truck OD are separate products (methodology PDFs in `handbooks/nhts/`), not columns in these five files.

## Household variables (43)

| Name | Label | Type | Length |
|---|---|---|---|
| `CDIVMSAR` | Grouping of household by combination of Census division, MSA status, and presence of rail | C | 2.0 |
| `CENSUS_D` | Census division classification for home address | C | 2.0 |
| `CENSUS_R` | Census region classification for home address | C | 2.0 |
| `CNTTDHH` | Count of household trips on travel day | N | 8.0 |
| `DRVRCNT` | Number of drivers in the household | N | 8.0 |
| `FLAG100` | All HH members completed survey? | C | 2.0 |
| `HBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the household's home location | C | 2.0 |
| `HBHUR` | Urban / Rural indicator - Block group | C | 2.0 |
| `HBPPOPDN` | Category of population density (persons per square mile) in the census block group of the household's home location | C | 2.0 |
| `HBRESDN` | Category of housing units per square mile in the census block group of the household's home location | C | 2.0 |
| `HHFAMINC` | Household income | C | 2.0 |
| `HHFAMINC_IMP` | Household income (imputed) | C | 2.0 |
| `HHRELATD` | Flag indicating at least 2 persons in HH are related | C | 2.0 |
| `HHSIZE` | Total number of people in household | N | 8.0 |
| `HHVEHCNT` | Total number of vehicles in household | N | 8.0 |
| `HH_HISP` | Hispanic status of household respondent | C | 2.0 |
| `HH_RACE` | Race of household respondent | C | 2.0 |
| `HOMEOWN` | Whether home owned or rented | C | 2.0 |
| `HOMETYPE` | Type of home | C | 2.0 |
| `HOUSEID` | Unique Identifier- Household | C | 10.0 |
| `HTEEMPDN` | Category of workers per square mile in the census tract of the household's home location | C | 2.0 |
| `HTHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the household's home location | C | 2.0 |
| `HTPPOPDN` | Category of population density (persons per square mile) in the census tract of the household's home location | C | 2.0 |
| `HTRESDN` | Category of housing units per square mile in the census tract of the household's home location | C | 2.0 |
| `LIF_CYC` | Life Cycle classification for the household | C | 2.0 |
| `MSACAT` | MSA category for the HH home address | C | 2.0 |
| `MSASIZE` | Population size category of the MSA from the five-year ACS API | C | 2.0 |
| `NUMADLT` | Count of adult household members at least 18 years old | N | 8.0 |
| `PPT517` | Count of household members 5-17 years old | N | 8.0 |
| `RAIL` | MSA heavy rail status for household | C | 2.0 |
| `RESP_CNT` | Count of responding persons in household | N | 8.0 |
| `STRATUMID` | Household Stratum ID | C | 4.0 |
| `TDAYDATE` | Date of travel day (YYYYMM) | C | 6.0 |
| `TRAVDAY` | Travel day - day of week | C | 2.0 |
| `URBAN` | Household urban area classification, based on 2020 TIGER/Line Shapefile | C | 2.0 |
| `URBANSIZE` | Urban area size where home address is located | C | 2.0 |
| `URBRUR` | Household in urban/rural area | C | 2.0 |
| `URBRUR_2010` | Household in urban/rural area based on 2010 Census | C | 2.0 |
| `WRKCOUNT` | Count of workers in household | N | 8.0 |
| `WTHHFIN` | 7-day natl household weight | N | 8.0 |
| `WTHHFIN2D` | 2-day natl household weight | N | 8.0 |
| `WTHHFIN5D` | 5-day natl household weight | N | 8.0 |
| `YOUNGCHILD` | Count of household members under 5 years old | N | 8.0 |

Code/range rows for this file: 293 (covers 43 variables). See `inventories/nhts_codes.csv`.

## Person variables (153)

| Name | Label | Type | Length |
|---|---|---|---|
| `BIKESHARE22` | Days in last 30 days bike share used | N | 8.0 |
| `BIKETRANSIT` | Days in last 30 days cycling used | N | 8.0 |
| `CDIVMSAR` | Grouping of household by combination of Census division, MSA status, and presence of rail | C | 2.0 |
| `CENSUS_D` | Census division classification for home address | C | 2.0 |
| `CENSUS_R` | Census region classification for home address | C | 2.0 |
| `CNTTDTR` | Count of person trips on travel day | N | 8.0 |
| `CONDNIGH` | Limited driving to daytime due to condition or disability | C | 2.0 |
| `CONDNONE` | Travel not affected by condition or disability | C | 2.0 |
| `CONDPUB` | Used bus or subway less frequently due to condition or disability | C | 2.0 |
| `CONDRF` | Prefer not to answer if travel is affected by condition or disability | C | 2.0 |
| `CONDRIDE` | Asked others for rides due to condition or disability | C | 2.0 |
| `CONDRIVE` | Given up driving due to condition or disability | C | 2.0 |
| `CONDSHARE` | Used rideshare due to condition or disability | C | 2.0 |
| `CONDSPEC` | Used special transportation services due to condition or disability | C | 2.0 |
| `CONDTRAV` | Reduced travel due to condition or disability | C | 2.0 |
| `COV1_OHD` | COVID impact on online purchases for home delivery | C | 2.0 |
| `COV1_PT` | COVID impact on use of public transit | C | 2.0 |
| `COV1_SCH` | COVID impact on travel to a physical school/class location | C | 2.0 |
| `COV1_WK` | COVID impact on travel to a physical work location | C | 2.0 |
| `COV2_OHD` | Home delivery changes temporary or permanent | C | 2.0 |
| `COV2_PT` | Public transit use changes temporary or permanent | C | 2.0 |
| `COV2_SCH` | School travel changes temporary or permanent | C | 2.0 |
| `COV2_WK` | Work travel changes temporary or permanent | C | 2.0 |
| `DELIVER` | Number of online purchase deliveries in past 30 days | N | 8.0 |
| `DELIV_FOOD` | Number of times food delivered in past 30 days | N | 8.0 |
| `DELIV_GOOD` | Number of times goods delivered in past 30 days | N | 8.0 |
| `DELIV_GROC` | Number of times groceries delivered in past 30 days | N | 8.0 |
| `DELIV_PERS` | Number of times services delivered in the past 30 days | N | 8.0 |
| `DRIVER` | Driver status, derived | C | 2.0 |
| `DRIVINGOCCUPATION` | Drive for work | C | 2.0 |
| `DRIVINGVEHICLE` | Vehicle driven for work | C | 2.0 |
| `DRVRCNT` | Number of drivers in the household | N | 8.0 |
| `EDUC` | Highest level of education | C | 2.0 |
| `EMPLOYMENT2` | Hours worked for pay each week | N | 8.0 |
| `EMPPASS` | Employer pays for discounted transit pass | C | 2.0 |
| `ESCOOTERUSED` | Days in last 30 days e-scooter used | N | 8.0 |
| `FRSTHM` | Started travel day at home | C | 2.0 |
| `GCDWORK` | Great circle distance (miles) between home and work | N | 8.0 |
| `HBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the household's home location | C | 2.0 |
| `HBHUR` | Urban / Rural indicator - Block group | C | 2.0 |
| `HBPPOPDN` | Category of population density (persons per square mile) in the census block group of the household's home location | C | 2.0 |
| `HBRESDN` | Category of housing units per square mile in the census block group of the household's home location | C | 2.0 |
| `HHFAMINC` | Household income | C | 2.0 |
| `HHFAMINC_IMP` | Household income (imputed) | C | 2.0 |
| `HHSIZE` | Total number of people in household | N | 8.0 |
| `HHVEHCNT` | Total number of vehicles in household | N | 8.0 |
| `HH_HISP` | Hispanic status of household respondent | C | 2.0 |
| `HH_RACE` | Race of household respondent | C | 2.0 |
| `HOMEOWN` | Whether home owned or rented | C | 2.0 |
| `HOUSEID` | Unique Identifier- Household | C | 10.0 |
| `HTEEMPDN` | Category of workers per square mile in the census tract of the household's home location | C | 2.0 |
| `HTHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the household's home location | C | 2.0 |
| `HTPPOPDN` | Category of population density (persons per square mile) in the census tract of the household's home location | C | 2.0 |
| `HTRESDN` | Category of housing units per square mile in the census tract of the household's home location | C | 2.0 |
| `LAST30_BIKE` | Used bicycle in last 30 days | C | 2.0 |
| `LAST30_BKSHR` | Used bike share in last 30 days | C | 2.0 |
| `LAST30_ESCT` | Used e-scooters in last 30 days | C | 2.0 |
| `LAST30_MTRC` | Used motorcycle in last 30 days | C | 2.0 |
| `LAST30_PT` | Used public transit in last 30 days | C | 2.0 |
| `LAST30_RDSHR` | Used rideshare in last 30 days | C | 2.0 |
| `LAST30_TAXI` | Used taxi service in last 30 days | C | 2.0 |
| `LAST30_WALK` | Walked from place to place in last 30 days | C | 2.0 |
| `LIF_CYC` | Life Cycle classification for the household | C | 2.0 |
| `MCTRANSIT` | Days in last 30 days motorcycle used | N | 8.0 |
| `MEDCOND` | Condition or disability that makes travel difficult | C | 2.0 |
| `MEDCOND6` | Length of time respondent has had condition | C | 2.0 |
| `MSACAT` | MSA category for the HH home address | C | 2.0 |
| `MSASIZE` | Population size category of the MSA from the five-year ACS API | C | 2.0 |
| `NUMADLT` | Count of adult household members at least 18 years old | N | 8.0 |
| `OUTOFTWN` | Away from home entire travel day | C | 2.0 |
| `PARK` | Paid for parking at any time during travel day | C | 2.0 |
| `PARKHOME` | Pay for home parking | C | 2.0 |
| `PARKHOMEAMT` | Whether respondent pays to park at home | C | 4.0 |
| `PARKHOMEAMT_PAMOUNT` | Cost of parking at home | N | 8.0 |
| `PARKHOMEAMT_PAYTYPE` | Duration of payment | C | 2.0 |
| `PAYPROF` | Worked for pay last week | C | 2.0 |
| `PERSONID` | Person ID within household | C | 2.0 |
| `PRMACT` | Primary activity for those who did not work for pay last week | C | 2.0 |
| `PROXY` | Survey completed by self or someone else | C | 2.0 |
| `PTUSED` | Days in last 30 days public transit used | N | 8.0 |
| `QACSLAN1` | Language other than English spoken at home | C | 2.0 |
| `QACSLAN3` | How well this person speaks English | C | 2.0 |
| `RAIL` | MSA heavy rail status for household | C | 2.0 |
| `RET_AMZ` | Number of times returned online purchase at Amazon dropoff center | N | 8.0 |
| `RET_HOME` | Number of times returned online purchase by home pickup | N | 8.0 |
| `RET_PUF` | Number of times returned online purchase to post office/UPS/Fed Ex/ similar | N | 8.0 |
| `RET_STORE` | Number of times returned online purchase by direct to store | N | 8.0 |
| `RIDESHARE22` | Days in last 30 days rideshare used | N | 8.0 |
| `R_AGE` | Respondent age | N | 8.0 |
| `R_HISP` | Person 5 or older - Hispanic or Latino | C | 2.0 |
| `R_RACE` | Respondent race | C | 2.0 |
| `R_RACE_IMP` | Respondent race (imputed) | C | 2.0 |
| `R_RELAT` | Respondent relationship to primary respondent | C | 2.0 |
| `R_SEX` | Respondent sex | C | 2.0 |
| `R_SEX_IMP` | Respondent sex (imputed) | C | 2.0 |
| `SAMEPLC` | Reason for not taking trips on travel day | C | 2.0 |
| `SBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the school's location | C | 2.0 |
| `SBHUR` | Urban / Rural indicator - School Block group | C | 2.0 |
| `SBPPOPDN` | Category of population density (persons per square mile) in the census block group of the school's location | C | 2.0 |
| `SBRESDN` | Category of housing units per square mile in the census block group of the school's location | C | 2.0 |
| `SCHOOL1` | Enrolled in school or academic program | C | 2.0 |
| `SCHOOL1C` | Type of non K-12 school enrolled in | C | 2.0 |
| `SCHTRN1` | Usual transport to school | C | 2.0 |
| `SCHTYP` | Type of K-12 school enrolled in | C | 2.0 |
| `STEEMPDN` | Category of workers per square mile in the census tract of the school's location | C | 2.0 |
| `STHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the school's location | C | 2.0 |
| `STPPOPDN` | Category of population density (persons per square mile) in the census tract of the school's location | C | 2.0 |
| `STRATUMID` | Household Stratum ID | C | 4.0 |
| `STRESDN` | Category of housing units per square mile in the census tract of the school's location | C | 2.0 |
| `STUDE` | School or academic program description | C | 2.0 |
| `TAXISERVICE` | Days in last 30 days taxi service used | N | 8.0 |
| `TDAYDATE` | Date of travel day (YYYYMM) | C | 6.0 |
| `TRAVDAY` | Travel day - day of week | C | 2.0 |
| `TRNPASS` | Discounted transit pass used in past 30 days | C | 2.0 |
| `URBAN` | Household urban area classification, based on 2020 TIGER/Line Shapefile | C | 2.0 |
| `URBANSIZE` | Urban area size where home address is located | C | 2.0 |
| `URBRUR` | Household in urban/rural area | C | 2.0 |
| `USAGE1` | Fewer trips in past 30 days | C | 2.0 |
| `USAGE2_1` | Reason fewer trips - more deliveries | C | 2.0 |
| `USAGE2_10` | Reason fewer trips - COVID 19 | C | 2.0 |
| `USAGE2_2` | Reason fewer trips - did not feel safe | C | 2.0 |
| `USAGE2_3` | Reason fewer trips - did not feel clean/healthy | C | 2.0 |
| `USAGE2_4` | Reason fewer trips - not reliable | C | 2.0 |
| `USAGE2_5` | Reason fewer trips - did not go where needed | C | 2.0 |
| `USAGE2_6` | Reason fewer trips - unaffordable | C | 2.0 |
| `USAGE2_7` | Reason fewer trips - health problems | C | 2.0 |
| `USAGE2_8` | Reason fewer trips - no time | C | 2.0 |
| `USAGE2_9` | Reason fewer trips - other | C | 2.0 |
| `USEPUBTR` | Public Transit Usage on Travel Date | C | 2.0 |
| `WALKTRANSIT` | Days in last 30 days walking used | N | 8.0 |
| `WBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the workplace's location | C | 2.0 |
| `WBHUR` | Urban / Rural indicator - Workplace Block group | C | 2.0 |
| `WBPPOPDN` | Category of population density (persons per square mile) in the census block group of the workplace's location | C | 2.0 |
| `WBRESDN` | Category of housing units per square mile in the census block group of the workplace's location | C | 2.0 |
| `WHOPROXY` | Who is completing the survey | C | 2.0 |
| `WKFMHM22` | Days per week worked from home | C | 2.0 |
| `WORKER` | Employment status of respondent | C | 2.0 |
| `WRKCOUNT` | Count of workers in household | N | 8.0 |
| `WRKLOC` | Description of work location | C | 2.0 |
| `WRKTRANS` | Usual transport to work | C | 2.0 |
| `WTEEMPDN` | Category of workers per square mile in the census tract of the workplace's location | C | 2.0 |
| `WTHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the workplace's location | C | 2.0 |
| `WTPERFIN` | 7 day National person weight | N | 8.0 |
| `WTPERFIN2D` | 2 day National person weight | N | 8.0 |
| `WTPERFIN5D` | 5 day National person weight | N | 8.0 |
| `WTPPOPDN` | Category of population density (persons per square mile) in the census tract of the workplace's location | C | 2.0 |
| `WTRESDN` | Category of housing units per square mile in the census tract of the workplace's location | C | 2.0 |
| `W_CANE` | Uses cane or walking stick | C | 2.0 |
| `W_CHAIR` | Uses manual scooter or wheel chair | C | 2.0 |
| `W_NONE` | Uses no medical device for mobility | C | 2.0 |
| `W_SCCH` | Uses motorized scooter or wheelchair | C | 2.0 |
| `W_VISIMP` | Uses devices to aid the blind or visually impaired | C | 2.0 |
| `W_WKCR` | Uses walker or crutches | C | 2.0 |

Code/range rows for this file: 888 (covers 153 variables). See `inventories/nhts_codes.csv`.

## Vehicle variables (55)

| Name | Label | Type | Length |
|---|---|---|---|
| `ANNMILES` | Self-reported annualized mile estimate | N | 8.0 |
| `CDIVMSAR` | Grouping of household by combination of Census division, MSA status, and presence of rail | C | 2.0 |
| `CENSUS_D` | Census division classification for home address | C | 2.0 |
| `CENSUS_R` | Census region classification for home address | C | 2.0 |
| `COMMERCIALFREQ` | Over past 30 days, how many days was vehicle used for business purposes? | C | 2.0 |
| `DRVRCNT` | Number of drivers in the household | N | 8.0 |
| `HBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the household's home location | C | 2.0 |
| `HBHUR` | Urban / Rural indicator - Block group | C | 2.0 |
| `HBPPOPDN` | Category of population density (persons per square mile) in the census block group of the household's home location | C | 2.0 |
| `HBRESDN` | Category of housing units per square mile in the census block group of the household's home location | C | 2.0 |
| `HHFAMINC` | Household income | C | 2.0 |
| `HHFAMINC_IMP` | Household income (imputed) | C | 2.0 |
| `HHSIZE` | Total number of people in household | N | 8.0 |
| `HHVEHCNT` | Total number of vehicles in household | N | 8.0 |
| `HHVEHUSETIME_DEL` | Over past 30 days, how many days was vehicle used for deliveries? | C | 2.0 |
| `HHVEHUSETIME_OTH` | Over past 30 days, how many days was vehicle used for other business? | C | 2.0 |
| `HHVEHUSETIME_RS` | Over past 30 days, how many days was vehicle used for rideshare? | C | 2.0 |
| `HH_HISP` | Hispanic status of household respondent | C | 2.0 |
| `HH_RACE` | Race of household respondent | C | 2.0 |
| `HOMEOWN` | Whether home owned or rented | C | 2.0 |
| `HOUSEID` | Unique Identifier- Household | C | 10.0 |
| `HTEEMPDN` | Category of workers per square mile in the census tract of the household's home location | C | 2.0 |
| `HTHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the household's home location | C | 2.0 |
| `HTPPOPDN` | Category of population density (persons per square mile) in the census tract of the household's home location | C | 2.0 |
| `HTRESDN` | Category of housing units per square mile in the census tract of the household's home location | C | 2.0 |
| `HYBRID` | Hybrid vehicle | C | 2.0 |
| `LIF_CYC` | Life Cycle classification for the household | C | 2.0 |
| `MAKE` | Vehicle make ID | C | 2.0 |
| `MSACAT` | MSA category for the HH home address | C | 2.0 |
| `MSASIZE` | Population size category of the MSA from the five-year ACS API | C | 2.0 |
| `NUMADLT` | Count of adult household members at least 18 years old | N | 8.0 |
| `RAIL` | MSA heavy rail status for household | C | 2.0 |
| `STRATUMID` | Household Stratum ID | C | 4.0 |
| `TDAYDATE` | Date of travel day (YYYYMM) | C | 6.0 |
| `TRAVDAY` | Travel day - day of week | C | 2.0 |
| `URBAN` | Household urban area classification, based on 2020 TIGER/Line Shapefile | C | 2.0 |
| `URBANSIZE` | Urban area size where home address is located | C | 2.0 |
| `URBRUR` | Household in urban/rural area | C | 2.0 |
| `VEHAGE` | Age of vehicle, based on model year | N | 8.0 |
| `VEHCASEID` | Unique vehicle identifier | C | 12.0 |
| `VEHCOMMERCIAL` | Vehicle used for business purposes | C | 2.0 |
| `VEHCOM_DEL` | Vehicle used for delivery service | C | 2.0 |
| `VEHCOM_OTH` | Vehicle used for other business purposes | C | 2.0 |
| `VEHCOM_RS` | Vehicle used for rideshare | C | 2.0 |
| `VEHFUEL` | Type of fuel vehicle runs on | C | 2.0 |
| `VEHID` | Vehicle ID within household | C | 2.0 |
| `VEHOWNED` | Vehicle owned for 1  year or more | C | 2.0 |
| `VEHOWNMO` | Vehicles owned less than 1 year - months owned | C | 2.0 |
| `VEHTYPE` | Vehicle type | C | 2.0 |
| `VEHYEAR` | Vehicle year | N | 8.0 |
| `WHOMAIN` | Main driver of vehicle | C | 2.0 |
| `WRKCOUNT` | Count of workers in household | N | 8.0 |
| `WTHHFIN` | 7-day natl household weight | N | 8.0 |
| `WTHHFIN2D` | 2-day natl household weight | N | 8.0 |
| `WTHHFIN5D` | 5-day natl household weight | N | 8.0 |

Code/range rows for this file: 382 (covers 55 variables). See `inventories/nhts_codes.csv`.

## Trip variables (102)

| Name | Label | Type | Length |
|---|---|---|---|
| `CDIVMSAR` | Grouping of household by combination of Census division, MSA status, and presence of rail | C | 2.0 |
| `CENSUS_D` | Census division classification for home address | C | 2.0 |
| `CENSUS_R` | Census region classification for home address | C | 2.0 |
| `DBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the trip destination's location | C | 2.0 |
| `DBHUR` | Urban / Rural indicator - Trip Destination Block group | C | 2.0 |
| `DBPPOPDN` | Category of population density (persons per square mile) in the census block group of the trip destination's location | C | 2.0 |
| `DBRESDN` | Category of housing units per square mile in the census block group of the trip destination's location | C | 2.0 |
| `DRIVER` | Driver status, derived | C | 2.0 |
| `DRVRCNT` | Number of drivers in the household | N | 8.0 |
| `DRVR_FLG` | Flag for driver on trip | C | 2.0 |
| `DTEEMPDN` | Category of workers per square mile in the census tract of the trip destination's location | C | 2.0 |
| `DTHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the trip destination's location | C | 2.0 |
| `DTPPOPDN` | Category of population density (persons per square mile) in the census tract of the trip destination's location | C | 2.0 |
| `DTRESDN` | Category of housing units per square mile in the census tract of the trip destination's location | C | 2.0 |
| `DWELTIME` | Time at Destination (minutes) | N | 8.0 |
| `EDUC` | Highest level of education | C | 2.0 |
| `ENDTIME` | 24 hour local end time of trip | C | 4.0 |
| `FRSTHM` | Started travel day at home | C | 2.0 |
| `GASPRICE` | Weekly regional gasoline price, in cents, during the week of the household's travel day | C | 8.0 |
| `HHACCCNT` | Number of household members on trip | C | 2.0 |
| `HHFAMINC` | Household income | C | 2.0 |
| `HHFAMINC_IMP` | Household income (imputed) | C | 2.0 |
| `HHMEMDRV` | Household member drove on trip | C | 2.0 |
| `HHSIZE` | Total number of people in household | N | 8.0 |
| `HHVEHCNT` | Total number of vehicles in household | N | 8.0 |
| `HH_HISP` | Hispanic status of household respondent | C | 2.0 |
| `HH_RACE` | Race of household respondent | C | 2.0 |
| `HOMEOWN` | Whether home owned or rented | C | 2.0 |
| `HOUSEID` | Unique Identifier- Household | C | 10.0 |
| `LIF_CYC` | Life Cycle classification for the household | C | 2.0 |
| `LOOP_TRIP` | Trip origin and destination at Identical location | C | 2.0 |
| `MSACAT` | MSA category for the HH home address | C | 2.0 |
| `MSASIZE` | Population size category of the MSA from the five-year ACS API | C | 2.0 |
| `NONHHCNT` | Number of non-household members on trip | N | 8.0 |
| `NUMADLT` | Count of adult household members at least 18 years old | N | 8.0 |
| `NUMONTRP` | Number of people on trip | N | 8.0 |
| `OBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the trip origin's location | C | 2.0 |
| `OBHUR` | Urban / Rural indicator - Trip Origin Block group | C | 2.0 |
| `OBPPOPDN` | Category of population density (persons per square mile) in the census block group of the trip origin's location | C | 2.0 |
| `OBRESDN` | Category of housing units per square mile in the census block group of the trip origin's location | C | 2.0 |
| `ONTD_P1` | Person 1  was on trip | C | 2.0 |
| `ONTD_P10` | Person 10 was on trip | C | 2.0 |
| `ONTD_P2` | Person 2 was on trip | C | 2.0 |
| `ONTD_P3` | Person 3 was on trip | C | 2.0 |
| `ONTD_P4` | Person 4 was on trip | C | 2.0 |
| `ONTD_P5` | Person 5 was on trip | C | 2.0 |
| `ONTD_P6` | Person 6 was on trip | C | 2.0 |
| `ONTD_P7` | Person 7 was on trip | C | 2.0 |
| `ONTD_P8` | Person 8 was on trip | C | 2.0 |
| `ONTD_P9` | Person 9 was on trip | C | 2.0 |
| `OTEEMPDN` | Category of workers per square mile in the census tract of the trip origin's location | C | 2.0 |
| `OTHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the trip origin's location | C | 2.0 |
| `OTPPOPDN` | Category of population density (persons per square mile) in the census tract of the trip origin's location | C | 2.0 |
| `OTRESDN` | Category of housing units per square mile in the census tract of the trip origin's location | C | 2.0 |
| `PARK` | Paid for parking at any time during travel day | C | 2.0 |
| `PARK2` | Paid for parking on this trip | C | 4.0 |
| `PARK2_PAMOUNT` | Amount paid for parking | N | 8.0 |
| `PARK2_PAYTYPE` | Periodicity of parking payment | C | 2.0 |
| `PERSONID` | Person ID within household | C | 2.0 |
| `PRMACT` | Primary activity for those who did not work for pay last week | C | 2.0 |
| `PROXY` | Survey completed by self or someone else | C | 2.0 |
| `PSGR_FLG` | Flag for passenger on trip | C | 2.0 |
| `PUBTRANS` | Used public transit on trip | C | 2.0 |
| `RAIL` | MSA heavy rail status for household | C | 2.0 |
| `R_AGE` | Respondent age | N | 8.0 |
| `R_HISP` | Person 5 or older - Hispanic or Latino | C | 2.0 |
| `R_RACE` | Respondent race | C | 2.0 |
| `R_SEX` | Respondent sex | C | 2.0 |
| `R_SEX_IMP` | Respondent sex (imputed) | C | 2.0 |
| `SEQ_TRIPID` | Renumbered sequential tripid | C | 2.0 |
| `STRATUMID` | Household Stratum ID | C | 4.0 |
| `STRTTIME` | 24 hour local start time of trip | C | 4.0 |
| `TDAYDATE` | Date of travel day (YYYYMM) | C | 6.0 |
| `TDCASEID` | Unique identifier for every trip record in the file | C | 14.0 |
| `TDWKND` | Weekend trip | C | 2.0 |
| `TRAVDAY` | Travel day - day of week | C | 2.0 |
| `TRIPID` | Trip ID for each trip a person took | C | 2.0 |
| `TRIPMODE` | General mode of transportation of trip | C | 2.0 |
| `TRIPPURP` | General purpose of trip | C | 2.0 |
| `TRPHHVEH` | Household vehicle used for trip | C | 2.0 |
| `TRPMILES` | Calculated Trip distance converted into miles | N | 8.0 |
| `TRPTRANS` | Trip mode, derived | C | 2.0 |
| `TRVLCMIN` | Trip Duration in Minutes | N | 8.0 |
| `URBAN` | Household urban area classification, based on 2020 TIGER/Line Shapefile | C | 2.0 |
| `URBANSIZE` | Urban area size where home address is located | C | 2.0 |
| `URBRUR` | Household in urban/rural area | C | 2.0 |
| `VEHCASEID` | Unique vehicle identifier | C | 12.0 |
| `VEHID` | Vehicle ID of vehicle used from household roster | C | 2.0 |
| `VEHTYPE` | Vehicle type | C | 2.0 |
| `VMT_MILE` | Calculated Trip distance (miles) for Driver Trips | N | 8.0 |
| `WALK` | Minutes walked from parking to destination | C | 2.0 |
| `WHODROVE` | Person who drove on trip | C | 2.0 |
| `WHODROVE_IMP` | Imputed person who drove on trip | C | 2.0 |
| `WHYFROM` | Reason for previous trip | C | 2.0 |
| `WHYTO` | Reason for travel to destination | C | 2.0 |
| `WHYTRP1S` | Trip purpose summary | C | 2.0 |
| `WHYTRP90` | Travel day trip purpose consistent with 1990 NPTS design | C | 2.0 |
| `WORKER` | Employment status of respondent | C | 2.0 |
| `WRKCOUNT` | Count of workers in household | N | 8.0 |
| `WTTRDFIN` | 7 day National trip weight | N | 8.0 |
| `WTTRDFIN2D` | 2 day National trip weight | N | 8.0 |
| `WTTRDFIN5D` | 5 day National trip weight | N | 8.0 |

Code/range rows for this file: 679 (covers 102 variables). See `inventories/nhts_codes.csv`.

## Long Distance variables (74)

| Name | Label | Type | Length |
|---|---|---|---|
| `AIRSIZE` | Domestic airport hub size based on FY23 NPIAS hub type status (international trips only) | C | 2.0 |
| `BEGTRIP` | Beginning date of trip (YYYYMM) | C | 6.0 |
| `CDIVMSAR` | Grouping of household by combination of Census division, MSA status, and presence of rail | C | 2.0 |
| `CENSUS_D` | Census division classification for home address | C | 2.0 |
| `CENSUS_R` | Census region classification for home address | C | 2.0 |
| `DRIVER` | Driver status, derived | C | 2.0 |
| `DRVRCNT` | Number of drivers in the household | N | 8.0 |
| `EDUC` | Highest level of education | C | 2.0 |
| `ENDTRIP` | Ending date of trip (YYYYMM) | C | 6.0 |
| `EXITCDIV` | Census division at which respondent exited the US | C | 2.0 |
| `FARCDIV` | Farthest domestic destination Census division code (domestic trips only) | C | 2.0 |
| `FARCREG` | Farthest domestic destination Census region FIPS code (domestic trips only) | C | 2.0 |
| `FARREAS` | Main reason for most recent long distance trip | C | 2.0 |
| `GCDTOT` | Great circle distance from home to farthest domestic dest (domestic trips only) | N | 8.0 |
| `GCD_FLAG` | Flag for long distance trips of 50 miles or more | C | 2.0 |
| `HBHTNRNT` | Category of the percent of renter-occupied housing in the census block group of the household's home location | C | 2.0 |
| `HBHUR` | Urban / Rural indicator - Block group | C | 2.0 |
| `HBPPOPDN` | Category of population density (persons per square mile) in the census block group of the household's home location | C | 2.0 |
| `HBRESDN` | Category of housing units per square mile in the census block group of the household's home location | C | 2.0 |
| `HHFAMINC` | Household income | C | 2.0 |
| `HHFAMINC_IMP` | Household income (imputed) | C | 2.0 |
| `HHSIZE` | Total number of people in household | N | 8.0 |
| `HHVEHCNT` | Total number of vehicles in household | N | 8.0 |
| `HH_HISP` | Hispanic status of household respondent | C | 2.0 |
| `HH_RACE` | Race of household respondent | C | 2.0 |
| `HOMEOWN` | Whether home owned or rented | C | 2.0 |
| `HOUSEID` | Unique Identifier- Household | C | 10.0 |
| `HTEEMPDN` | Category of workers per square mile in the census tract of the household's home location | C | 2.0 |
| `HTHTNRNT` | Category of the percent of renter-occupied housing in the census tract of the household's home location | C | 2.0 |
| `HTPPOPDN` | Category of population density (persons per square mile) in the census tract of the household's home location | C | 2.0 |
| `HTRESDN` | Category of housing units per square mile in the census tract of the household's home location | C | 2.0 |
| `INT_FLAG` | Farthest destination on the trip was in the US or outside US | C | 2.0 |
| `LDT_FLAG` | Source of long distance data | C | 2.0 |
| `LD_AMT` | Number of times used AMTRAK in past year | N | 8.0 |
| `LD_ICB` | Number of times used Inter-City bus in past year | N | 8.0 |
| `LD_NUMONTRP` | Number of people with respondent on long distance trip | N | 8.0 |
| `LIF_CYC` | Life Cycle classification for the household | C | 2.0 |
| `LONGDIST` | Number of long distance trips in past 30 days | N | 8.0 |
| `MAINMODE` | Mode of travel for last long distance trip | C | 2.0 |
| `MRT_DATE` | Date of most recent long distance trip (YYYYMM) | C | 6.0 |
| `MSACAT` | MSA category for the HH home address | C | 2.0 |
| `MSASIZE` | Population size category of the MSA from the five-year ACS API | C | 2.0 |
| `NTSAWAY` | Nights away on long distance trip | N | 8.0 |
| `NUMADLT` | Count of adult household members at least 18 years old | N | 8.0 |
| `ONTP_P1` | Person 1 on long distance trip | C | 2.0 |
| `ONTP_P10` | Person 10 on long distance trip | C | 2.0 |
| `ONTP_P2` | Person 2 on long distance trip | C | 2.0 |
| `ONTP_P3` | Person 3 on long distance trip | C | 2.0 |
| `ONTP_P4` | Person 4 on long distance trip | C | 2.0 |
| `ONTP_P5` | Person 5 on long distance trip | C | 2.0 |
| `ONTP_P6` | Person 6 on long distance trip | C | 2.0 |
| `ONTP_P7` | Person 7 on long distance trip | C | 2.0 |
| `ONTP_P8` | Person 8 on long distance trip | C | 2.0 |
| `ONTP_P9` | Person 9 on long distance trip | C | 2.0 |
| `PERSONID` | Person ID within household | C | 2.0 |
| `PROXY` | Survey completed by self or someone else | C | 2.0 |
| `RAIL` | MSA heavy rail status for household | C | 2.0 |
| `R_AGE` | Respondent age | N | 8.0 |
| `R_HISP` | Person 5 or older - Hispanic or Latino | C | 2.0 |
| `R_RACE` | Respondent race | C | 2.0 |
| `R_SEX` | Respondent sex | C | 2.0 |
| `R_SEX_IMP` | Respondent sex (imputed) | C | 2.0 |
| `STRATUMID` | Household Stratum ID | C | 4.0 |
| `TDAYDATE` | Date of travel day (YYYYMM) | C | 6.0 |
| `TRAVDAY` | Travel day - day of week | C | 2.0 |
| `URBAN` | Household urban area classification, based on 2020 TIGER/Line Shapefile | C | 2.0 |
| `URBANSIZE` | Urban area size where home address is located | C | 2.0 |
| `URBRUR` | Household in urban/rural area | C | 2.0 |
| `WEEKEND` | Trip includes weekend | C | 2.0 |
| `WORKER` | Employment status of respondent | C | 2.0 |
| `WRKCOUNT` | Count of workers in household | N | 8.0 |
| `WTPERFIN` | 7 day National person weight | N | 8.0 |
| `WTPERFIN2D` | 2 day National person weight | N | 8.0 |
| `WTPERFIN5D` | 5 day National person weight | N | 8.0 |

Code/range rows for this file: 476 (covers 74 variables). See `inventories/nhts_codes.csv`.

