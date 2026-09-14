# Data catalogs

This is an inventory of **what is inside** each official dataset, taken from the local handbooks. It is not a task map.

Catalog → 任务分层： [catalog_to_tasks.md](catalog_to_tasks.md)

| Dataset | Coverage | Catalog | Machine-readable |
|---|---|---|---|
| OpenStreetMap | global | [catalogs/osm.md](catalogs/osm.md) | [inventories/osm_map_features.csv](inventories/osm_map_features.csv) (1503 tags + wiki comments) |
| WorldPop | global | [catalogs/worldpop.md](catalogs/worldpop.md) | filename schema in that file |
| NHTS 2022 | US survey | [catalogs/nhts.md](catalogs/nhts.md) | [inventories/nhts_variables.csv](inventories/nhts_variables.csv), [inventories/nhts_codes.csv](inventories/nhts_codes.csv) |
| LODES 8.4 | US jobs | [catalogs/lodes.md](catalogs/lodes.md) | OD / RAC / WAC / xwalk field lists |
| CTPP 2017–2021 | US ACS tables | [catalogs/ctpp.md](catalogs/ctpp.md) | parts, geographies, universes |
| ACS PUMS | US microdata | [catalogs/pums.md](catalogs/pums.md) | file layout; full dictionary not in the local handbook |

OSM and WorldPop are the only global layers. The other four are national statistical products.

OSM Aerialway / Aeroway / Public transport / Route / Craft / many others come from wiki Taglist widgets; those rows have values but not the long comment text (the comments live on Taginfo when JavaScript runs). Amenity, Highway, Building, Landuse, Shop, etc. come from full wikitables and include comments in the CSV.

PUMS handbook states ~250 person and ~200 housing variables; only the layout and the variables it names are inventoried here. Year-specific PUMS Data Dictionary was not on disk.
