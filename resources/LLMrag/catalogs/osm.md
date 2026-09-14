# OpenStreetMap catalog

Source: OSM wiki Map features, Elements, Tags. Local copy: `handbooks/osm/`.
Complete tag rows: `inventories/osm_map_features.csv` (includes wiki comments).

## Data model

| Element | What it is |
|---|---|
| node | Point. WGS84 lat/lon. Standalone POI or vertex of a way. |
| way | Ordered list of 1–2000 nodes. Open polyline or closed area. |
| relation | Ordered members (nodes, ways, relations) with optional roles. Routes, turn restrictions, multipolygons. |
| tag | `key=value` on any element. Keys unique per element. Unicode, max 255 characters. |

Common attributes on every element: `id` (separate id space per type), `version`, `timestamp`, `changeset`, `uid`, `user`, `visible`.

License: ODbL. Delivery: planet PBF/XML, Geofabrik extracts, Overpass.

## Map features (1503 tags extracted from the wiki page)

Wiki Taglist blocks (Aerialway, Aeroway, Public transport, Route, etc.) have values but not the full comment text; comments for those say so in the CSV.

### Aerialway (14)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `aerialway` | `cable_car` |  |
|  | `aerialway` | `gondola` |  |
|  | `aerialway` | `mixed_lift` |  |
|  | `aerialway` | `chair_lift` |  |
|  | `aerialway` | `drag_lift` |  |
|  | `aerialway` | `t-bar` |  |
|  | `aerialway` | `j-bar` |  |
|  | `aerialway` | `platter` |  |
|  | `aerialway` | `rope_tow` |  |
|  | `aerialway` | `magic_carpet` |  |
|  | `aerialway` | `zip_line` |  |
|  | `aerialway` | `goods` |  |
|  | `aerialway` | `pylon` |  |
|  | `aerialway` | `station` |  |

### Aeroway (13)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `aeroway` | `aerodrome` |  |
|  | `aeroway` | `aircraft_crossing` |  |
|  | `aeroway` | `apron` |  |
|  | `aeroway` | `gate` |  |
|  | `aeroway` | `hangar` |  |
|  | `aeroway` | `helipad` |  |
|  | `aeroway` | `heliport` |  |
|  | `aeroway` | `navigationaid` |  |
|  | `aeroway` | `runway` |  |
|  | `aeroway` | `spaceport` |  |
|  | `aeroway` | `taxiway` |  |
|  | `aeroway` | `terminal` |  |
|  | `aeroway` | `windsock` |  |

### Amenity (140)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Sustenance | `amenity` | `bar` | node area |
| Sustenance | `amenity` | `biergarten` | node area |
| Sustenance | `amenity` | `cafe` | node area |
| Sustenance | `amenity` | `fast_food` | node area |
| Sustenance | `amenity` | `food_court` | node area |
| Sustenance | `amenity` | `ice_cream` | node area |
| Sustenance | `amenity` | `pub` | node area |
| Sustenance | `amenity` | `restaurant` | node area |
| Education | `amenity` | `college` | node area |
| Education | `amenity` | `dancing_school` | node area |
| Education | `amenity` | `driving_school` | node area |
| Education | `amenity` | `first_aid_school` | node area |
| Education | `amenity` | `kindergarten` | node area |
| Education | `amenity` | `language_school` | node area |
| Education | `amenity` | `library` | node area |
| Education | `amenity` | `surf_school` | node area |
| Education | `amenity` | `toy_library` | node area |
| Education | `amenity` | `research_institute` | node area |
| Education | `amenity` | `training` | node area |
| Education | `amenity` | `music_school` | node area |
| Education | `amenity` | `school` | node area |
| Education | `amenity` | `traffic_park` | node area |
| Education | `amenity` | `university` | node area |
| Transportation | `amenity` | `bicycle_parking` | node area |
| Transportation | `amenity` | `bicycle_repair_station` | node area |
| Transportation | `amenity` | `bicycle_rental` | node area |
| Transportation | `amenity` | `bicycle_wash` | node area |
| Transportation | `amenity` | `boat_rental` | node area |
| Transportation | `amenity` | `boat_storage` | node area |
| Transportation | `amenity` | `boat_sharing` | node area |
| Transportation | `amenity` | `bus_station` | node area |
| Transportation | `amenity` | `car_rental` | node area |
| Transportation | `amenity` | `car_sharing` | node area |
| Transportation | `amenity` | `car_wash` | node area |
| Transportation | `amenity` | `compressed_air` | node area |
| Transportation | `amenity` | `vehicle_inspection` | node area |
| Transportation | `amenity` | `charging_station` | node |
| Transportation | `amenity` | `driver_training` | node area |
| Transportation | `amenity` | `ferry_terminal` | node area |
| Transportation | `amenity` | `fuel` | node area |
| Transportation | `amenity` | `grit_bin` | node |
| Transportation | `amenity` | `motorcycle_parking` | node area |
| Transportation | `amenity` | `parking` | node area |
| Transportation | `amenity` | `parking_entrance` | node |
| Transportation | `amenity` | `parking_space` | node area |
| Transportation | `amenity` | `taxi` | node area |
| Transportation | `amenity` | `weighbridge` | node area |
| Financial | `amenity` | `atm` | node |
| Financial | `amenity` | `payment_terminal` | node |
| Financial | `amenity` | `bank` | node area |
| Financial | `amenity` | `bureau_de_change` | node area |
| Financial | `amenity` | `money_transfer` | node area |
| Financial | `amenity` | `payment_centre` | node area |
| Healthcare | `amenity` | `baby_hatch` | node area |
| Healthcare | `amenity` | `clinic` | node area |
| Healthcare | `amenity` | `dentist` | node area |
| Healthcare | `amenity` | `doctors` | node area |
| Healthcare | `amenity` | `hospital` | node area |
| Healthcare | `amenity` | `nursing_home` | node area |
| Healthcare | `amenity` | `pharmacy` | node area |
| Healthcare | `amenity` | `social_facility` | node area |
| Healthcare | `amenity` | `veterinary` | node area |
| Entertainment, Arts & Culture | `amenity` | `arts_centre` | node area |
| Entertainment, Arts & Culture | `amenity` | `brothel` | node area |
| Entertainment, Arts & Culture | `amenity` | `casino` | node area |
| Entertainment, Arts & Culture | `amenity` | `cinema` | node area |
| Entertainment, Arts & Culture | `amenity` | `community_centre` | node area |
| Entertainment, Arts & Culture | `amenity` | `conference_centre` | node area |
| Entertainment, Arts & Culture | `amenity` | `events_venue` | node area |
| Entertainment, Arts & Culture | `amenity` | `exhibition_centre` | node area |
| Entertainment, Arts & Culture | `amenity` | `fountain` | node area |
| Entertainment, Arts & Culture | `amenity` | `gambling` | node area |
| Entertainment, Arts & Culture | `amenity` | `love_hotel` | node area |
| Entertainment, Arts & Culture | `amenity` | `music_venue` | node area |
| Entertainment, Arts & Culture | `amenity` | `nightclub` | node area |
| Entertainment, Arts & Culture | `amenity` | `planetarium` | node area |
| Entertainment, Arts & Culture | `amenity` | `public_bookcase` | node area |
| Entertainment, Arts & Culture | `amenity` | `social_centre` | node area |
| Entertainment, Arts & Culture | `amenity` | `stage` | node area |
| Entertainment, Arts & Culture | `amenity` | `stripclub` | node |
| Entertainment, Arts & Culture | `amenity` | `studio` | node area |
| Entertainment, Arts & Culture | `amenity` | `swingerclub` | node area |
| Entertainment, Arts & Culture | `amenity` | `theatre` | node area |
| Public Service | `amenity` | `courthouse` | node area |
| Public Service | `amenity` | `fire_station` | node area |
| Public Service | `amenity` | `police` | node area |
| Public Service | `amenity` | `post_box` | node |
| Public Service | `amenity` | `post_depot` | node area |
| Public Service | `amenity` | `post_office` | node area |
| Public Service | `amenity` | `prison` | node area |
| Public Service | `amenity` | `ranger_station` | node area |
| Public Service | `amenity` | `townhall` | node area |
| Facilities | `amenity` | `bbq` | node |
| Facilities | `amenity` | `bench` | node way |
| Facilities | `amenity` | `check_in` | node way area |
| Facilities | `amenity` | `dog_toilet` | node area |
| Facilities | `amenity` | `dressing_room` | node area |
| Facilities | `amenity` | `drinking_water` | node |
| Facilities | `amenity` | `give_box` | node area |
| Facilities | `amenity` | `lounge` | node area |
| Facilities | `amenity` | `mailroom` | node area |
| Facilities | `amenity` | `parcel_locker` | node area |
| Facilities | `amenity` | `shelter` | node area |
| Facilities | `amenity` | `shower` | node area |
| Facilities | `amenity` | `telephone` | node |
| Facilities | `amenity` | `toilets` | node area |
| Facilities | `amenity` | `water_point` | node |
| Facilities | `amenity` | `watering_place` | node |
| Waste Management | `amenity` | `sanitary_dump_station` | node area |
| Waste Management | `amenity` | `recycling` | node area |
| Waste Management | `amenity` | `waste_basket` | node |
| Waste Management | `amenity` | `waste_disposal` | node |
| Waste Management | `amenity` | `waste_transfer_station` | node area |
| Others | `amenity` | `animal_boarding` | node area |
| Others | `amenity` | `animal_breeding` | node area relation |
| Others | `amenity` | `animal_shelter` | node area |
| Others | `amenity` | `animal_training` | node area |
| Others | `amenity` | `baking_oven` | node |
| Others | `amenity` | `clock` | node |
| Others | `amenity` | `crematorium` | node area |
| Others | `amenity` | `dive_centre` | node area |
| Others | `amenity` | `funeral_hall` | node area |
| Others | `amenity` | `grave_yard` | node area |
| Others | `amenity` | `hunting_stand` | node area |
| Others | `amenity` | `internet_cafe` | node area |
| Others | `amenity` | `kitchen` | node area |
| Others | `amenity` | `kneipp_water_cure` | node area |
| Others | `amenity` | `lounger` | node |
| Others | `amenity` | `marketplace` | node area |
| Others | `amenity` | `monastery` | node area |
| Others | `amenity` | `mortuary` | node area |
| Others | `amenity` | `photo_booth` | node |
| Others | `amenity` | `place_of_mourning` | node area |
| Others | `amenity` | `place_of_worship` | node area |
| Others | `amenity` | `public_bath` | node area |
| Others | `amenity` | `public_building` | node area |
| Others | `amenity` | `refugee_site` | node area |
| Others | `amenity` | `vending_machine` | node |
| Others | `amenity` | `hydrant` | node |
| Others | `amenity` | `user defined` | node area |

### Barrier (39)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Linear barriers | `barrier` | `cable_barrier` |  |
| Linear barriers | `barrier` | `city_wall` |  |
| Linear barriers | `barrier` | `ditch` |  |
| Linear barriers | `barrier` | `fence` |  |
| Linear barriers | `barrier` | `guard_rail` |  |
| Linear barriers | `barrier` | `handrail` |  |
| Linear barriers | `barrier` | `hedge` |  |
| Linear barriers | `barrier` | `kerb` |  |
| Linear barriers | `barrier` | `retaining_wall` |  |
| Linear barriers | `barrier` | `wall` |  |
| Access control on highways | `barrier` | `block` |  |
| Access control on highways | `barrier` | `bollard` |  |
| Access control on highways | `barrier` | `border_control` |  |
| Access control on highways | `barrier` | `bump_gate` |  |
| Access control on highways | `barrier` | `bus_trap` |  |
| Access control on highways | `barrier` | `cattle_grid` |  |
| Access control on highways | `barrier` | `chain` |  |
| Access control on highways | `barrier` | `cycle_barrier` |  |
| Access control on highways | `barrier` | `debris` |  |
| Access control on highways | `barrier` | `entrance` |  |
| Access control on highways | `barrier` | `full-height_turnstile` |  |
| Access control on highways | `barrier` | `gate` |  |
| Access control on highways | `barrier` | `hampshire_gate` |  |
| Access control on highways | `barrier` | `height_restrictor` |  |
| Access control on highways | `barrier` | `horse_stile` |  |
| Access control on highways | `barrier` | `jersey_barrier` |  |
| Access control on highways | `barrier` | `kissing_gate` |  |
| Access control on highways | `barrier` | `lift_gate` |  |
| Access control on highways | `barrier` | `log` |  |
| Access control on highways | `barrier` | `motorcycle_barrier` |  |
| Access control on highways | `barrier` | `rope` |  |
| Access control on highways | `barrier` | `sally_port` |  |
| Access control on highways | `barrier` | `spikes` |  |
| Access control on highways | `barrier` | `stile` |  |
| Access control on highways | `barrier` | `sump_buster` |  |
| Access control on highways | `barrier` | `swing_gate` |  |
| Access control on highways | `barrier` | `toll_booth` |  |
| Access control on highways | `barrier` | `turnstile` |  |
| Access control on highways | `barrier` | `yes` |  |

### Boundary (30)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Boundary types | `boundary` | `aboriginal_lands` | area relation |
| Boundary types | `boundary` | `administrative` | area |
| Boundary types | `boundary` | `border_zone` | area relation |
| Boundary types | `boundary` | `census` | area relation |
| Boundary types | `boundary` | `forest` | area relation |
| Boundary types | `boundary` | `forest_compartment` | area relation |
| Boundary types | `boundary` | `hazard` | area |
| Boundary types | `boundary` | `health` | area relation |
| Boundary types | `boundary` | `historic` | area relation |
| Boundary types | `boundary` | `limited_traffic_zone` | area relation |
| Boundary types | `boundary` | `local_authority` | relation |
| Boundary types | `boundary` | `low_emission_zone` | area relation |
| Boundary types | `boundary` | `maritime` | area |
| Boundary types | `boundary` | `marker` | node |
| Boundary types | `boundary` | `national_park` | area |
| Boundary types | `boundary` | `place` | way relation |
| Boundary types | `boundary` | `political` | area |
| Boundary types | `boundary` | `postal_code` | relation |
| Boundary types | `boundary` | `protected_area` | area |
| Boundary types | `boundary` | `religious_administration` | relation |
| Boundary types | `boundary` | `special_economic_zone` | area |
| Boundary types | `boundary` | `statistical` | area relation |
| Boundary types | `boundary` | `disputed` | area relation |
| Boundary types | `boundary` | `timezone` | relation |
| Boundary types | `boundary` | `public_transport` | area relation |
| Boundary types | `boundary` | `user defined` | node way |
| Attributes | `admin_level` | `(number)` | area |
| Attributes | `religious_level` | `(number)` | relation |
| Attributes | `border_type` | `*` | way area |
| Attributes | `start_date` | `(date)` | area |

### Building (120)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Accommodation | `building` | `apartments` |  |
| Accommodation | `building` | `barracks` |  |
| Accommodation | `building` | `bungalow` |  |
| Accommodation | `building` | `cabin` |  |
| Accommodation | `building` | `detached` |  |
| Accommodation | `building` | `annexe` |  |
| Accommodation | `building` | `dormitory` |  |
| Accommodation | `building` | `farm` |  |
| Accommodation | `building` | `ger` |  |
| Accommodation | `building` | `hotel` |  |
| Accommodation | `building` | `house` |  |
| Accommodation | `building` | `houseboat` |  |
| Accommodation | `building` | `residential` |  |
| Accommodation | `building` | `semidetached_house` |  |
| Accommodation | `building` | `static_caravan` |  |
| Accommodation | `building` | `stilt_house` |  |
| Accommodation | `building` | `terrace` |  |
| Accommodation | `building` | `tree_house` |  |
| Accommodation | `building` | `trullo` |  |
| Commercial | `building` | `commercial` |  |
| Commercial | `building` | `industrial` |  |
| Commercial | `building` | `kiosk` |  |
| Commercial | `building` | `office` |  |
| Commercial | `building` | `retail` |  |
| Commercial | `building` | `supermarket` |  |
| Commercial | `building` | `warehouse` |  |
| Religious | `building` | `religious` |  |
| Religious | `building` | `cathedral` |  |
| Religious | `building` | `chapel` |  |
| Religious | `building` | `church` |  |
| Religious | `building` | `kingdom_hall` |  |
| Religious | `building` | `monastery` | [W] |
| Religious | `building` | `mosque` |  |
| Religious | `building` | `presbytery` |  |
| Religious | `building` | `shrine` |  |
| Religious | `building` | `synagogue` |  |
| Religious | `building` | `temple` |  |
| Civic/amenity | `building` | `bakehouse` |  |
| Civic/amenity | `building` | `bridge` |  |
| Civic/amenity | `building` | `civic` |  |
| Civic/amenity | `building` | `clock_tower` |  |
| Civic/amenity | `building` | `college` |  |
| Civic/amenity | `building` | `fire_station` |  |
| Civic/amenity | `building` | `government` |  |
| Civic/amenity | `building` | `gatehouse` |  |
| Civic/amenity | `building` | `hospital` |  |
| Civic/amenity | `building` | `kindergarten` |  |
| Civic/amenity | `building` | `museum` |  |
| Civic/amenity | `building` | `public` |  |
| Civic/amenity | `building` | `school` |  |
| Civic/amenity | `building` | `toilets` |  |
| Civic/amenity | `building` | `train_station` |  |
| Civic/amenity | `building` | `transportation` |  |
| Civic/amenity | `building` | `university` |  |
| Agricultural/plant production | `building` | `barn` |  |
| Agricultural/plant production | `building` | `conservatory` |  |
| Agricultural/plant production | `building` | `cowshed` |  |
| Agricultural/plant production | `building` | `farm_auxiliary` |  |
| Agricultural/plant production | `building` | `greenhouse` |  |
| Agricultural/plant production | `building` | `slurry_tank` |  |
| Agricultural/plant production | `building` | `stable` |  |
| Agricultural/plant production | `building` | `sty` |  |
| Agricultural/plant production | `building` | `livestock` |  |
| Sports | `building` | `grandstand` |  |
| Sports | `building` | `pavilion` | [W] |
| Sports | `building` | `riding_hall` |  |
| Sports | `building` | `sports_hall` |  |
| Sports | `building` | `sports_centre` |  |
| Sports | `building` | `stadium` |  |
| Storage | `building` | `allotment_house` |  |
| Storage | `building` | `boathouse` |  |
| Storage | `building` | `hangar` |  |
| Storage | `building` | `hut` |  |
| Storage | `building` | `shed` |  |
| Cars | `building` | `carport` |  |
| Cars | `building` | `garage` |  |
| Cars | `building` | `garages` |  |
| Cars | `building` | `parking` |  |
| Power/technical buildings | `building` | `digester` |  |
| Power/technical buildings | `building` | `service` |  |
| Power/technical buildings | `building` | `tech_cab` | a question mark |
| Power/technical buildings | `building` | `transformer_tower` |  |
| Power/technical buildings | `building` | `water_tower` |  |
| Power/technical buildings | `building` | `storage_tank` |  |
| Power/technical buildings | `building` | `silo` |  |
| Other buildings | `building` | `beach_hut` |  |
| Other buildings | `building` | `bunker` |  |
| Other buildings | `building` | `castle` |  |
| Other buildings | `building` | `construction` |  |
| Other buildings | `building` | `container` |  |
| Other buildings | `building` | `guardhouse` |  |
| Other buildings | `building` | `military` |  |
| Other buildings | `building` | `outbuilding` |  |
| Other buildings | `building` | `pagoda` |  |
| Other buildings | `building` | `quonset_hut` |  |
| Other buildings | `building` | `roof` |  |
| Other buildings | `building` | `ruins` |  |
| Other buildings | `building` | `ship` |  |
| Other buildings | `building` | `tent` |  |
| Other buildings | `building` | `tower` |  |
| Other buildings | `building` | `triumphal_arch` |  |
| Other buildings | `building` | `windmill` |  |
| Other buildings | `building` | `[[ Too many Data Items entities accessed. \| yes ]]` |  |
| Other buildings | `building` | `user defined` |  |
| Additional attributes | `building:architecture` | `< architectural style >` | node area |
| Additional attributes | `building:colour` | `< RGB hex triplet > \| < W3C colour name >` | area |
| Additional attributes | `building:fireproof` | `yes \| no` | node area |
| Additional attributes | `building:flats` | `< number >` | node area |
| Additional attributes | `building:levels` | `< number >` | node area |
| Additional attributes | `building:material` | `< material type >` | area |
| Additional attributes | `building:min_level` | `< number >` | area |
| Additional attributes | `building:part` | `As building` | area |
| Additional attributes | `building:soft_storey` | `yes \| no \| reinforced` | node area |
| Additional attributes | `construction_date` | `< date >` | node area |
| Additional attributes | `entrance` | `yes \| main \| exit \| service \| emergency` | node |
| Additional attributes | `height` | `< number >` | node area |
| Additional attributes | `max_level` | `< number >` | area |
| Additional attributes | `min_level` | `< number >` | area |
| Additional attributes | `non_existent_levels` | `< number >` | area |
| Additional attributes | `start_date` | `< date >` | node area |

### Craft (101)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `craft` | `agricultural_engines` |  |
|  | `craft` | `atelier` |  |
|  | `craft` | `bag_repair` |  |
|  | `craft` | `bakery` |  |
|  | `craft` | `basket_maker` |  |
|  | `craft` | `beekeeper` |  |
|  | `craft` | `blacksmith` |  |
|  | `craft` | `boatbuilder` |  |
|  | `craft` | `bookbinder` |  |
|  | `craft` | `brewery` |  |
|  | `craft` | `builder` |  |
|  | `craft` | `cabinet_maker` |  |
|  | `craft` | `candlemaker` |  |
|  | `craft` | `car_painter` |  |
|  | `craft` | `carpenter` |  |
|  | `craft` | `carpet_cleaner` |  |
|  | `craft` | `carpet_layer` |  |
|  | `craft` | `caterer` |  |
|  | `craft` | `chimney_sweeper` |  |
|  | `craft` | `cleaning` |  |
|  | `craft` | `clockmaker` |  |
|  | `craft` | `clothes_mending` |  |
|  | `craft` | `confectionery` |  |
|  | `craft` | `cooper` |  |
|  | `craft` | `dental_technician` |  |
|  | `craft` | `distillery` |  |
|  | `craft` | `door_construction` |  |
|  | `craft` | `dressmaker` |  |
|  | `craft` | `electrician` |  |
|  | `craft` | `electronics_repair` |  |
|  | `craft` | `elevator` |  |
|  | `craft` | `embroiderer` |  |
|  | `craft` | `engraver` |  |
|  | `craft` | `fence_maker` |  |
|  | `craft` | `floorer` |  |
|  | `craft` | `gardener` |  |
|  | `craft` | `glassblower` |  |
|  | `craft` | `glaziery` |  |
|  | `craft` | `goldsmith` |  |
|  | `craft` | `grinding_mill` |  |
|  | `craft` | `gunsmith` |  |
|  | `craft` | `handicraft` |  |
|  | `craft` | `hvac` |  |
|  | `craft` | `insulation` |  |
|  | `craft` | `interior_decorator` |  |
|  | `craft` | `interior_work` |  |
|  | `craft` | `jeweller` |  |
|  | `craft` | `joiner` |  |
|  | `craft` | `key_cutter` |  |
|  | `craft` | `laboratory` |  |
|  | `craft` | `lapidary` |  |
|  | `craft` | `leather` |  |
|  | `craft` | `locksmith` |  |
|  | `craft` | `luthier` |  |
|  | `craft` | `metal_construction` |  |
|  | `craft` | `mint` |  |
|  | `craft` | `musical_instrument` |  |
|  | `craft` | `oil_mill` |  |
|  | `craft` | `optician` |  |
|  | `craft` | `organ_builder` |  |
|  | `craft` | `painter` |  |
|  | `craft` | `paperhanger` |  |
|  | `craft` | `parquet_layer` |  |
|  | `craft` | `paver` |  |
|  | `craft` | `pest_control` |  |
|  | `craft` | `photographer` |  |
|  | `craft` | `photographic_laboratory` |  |
|  | `craft` | `photovoltaic` |  |
|  | `craft` | `piano_tuner` |  |
|  | `craft` | `plasterer` |  |
|  | `craft` | `plumber` |  |
|  | `craft` | `pottery` |  |
|  | `craft` | `printer` |  |
|  | `craft` | `printmaker` |  |
|  | `craft` | `restoration` |  |
|  | `craft` | `rigger` |  |
|  | `craft` | `roofer` |  |
|  | `craft` | `saddler` |  |
|  | `craft` | `sailmaker` |  |
|  | `craft` | `sawmill` |  |
|  | `craft` | `scaffolder` |  |
|  | `craft` | `sculptor` |  |
|  | `craft` | `shoemaker` |  |
|  | `craft` | `signmaker` |  |
|  | `craft` | `stand_builder` |  |
|  | `craft` | `stonemason` |  |
|  | `craft` | `stove_fitter` |  |
|  | `craft` | `sun_protection` |  |
|  | `craft` | `tailor` |  |
|  | `craft` | `tatami` |  |
|  | `craft` | `tiler` |  |
|  | `craft` | `tinsmith` |  |
|  | `craft` | `toolmaker` |  |
|  | `craft` | `turner` |  |
|  | `craft` | `upholsterer` |  |
|  | `craft` | `watchmaker` |  |
|  | `craft` | `water_well_drilling` |  |
|  | `craft` | `weaver` |  |
|  | `craft` | `welder` |  |
|  | `craft` | `window_construction` |  |
|  | `craft` | `winery` |  |

### Emergency (19)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Medical rescue | `emergency` | `ambulance_station` |  |
| Medical rescue | `emergency` | `defibrillator` |  |
| Medical rescue | `emergency` | `landing_site` |  |
| Medical rescue | `emergency` | `emergency_ward_entrance` |  |
| Firefighters | `emergency` | `fire_service_inlet` |  |
| Firefighters | `emergency` | `fire_alarm_box` |  |
| Firefighters | `emergency` | `fire_extinguisher` |  |
| Firefighters | `emergency` | `fire_hose` |  |
| Firefighters | `emergency` | `fire_hydrant` |  |
| Firefighters | `emergency` | `water_tank` |  |
| Firefighters | `emergency` | `suction_point` |  |
| Lifeguards | `emergency` | `lifeguard` |  |
| Lifeguards | `emergency` | `life_ring` |  |
| Lifeguards | `lifeguard` | `tower` |  |
| Assembly point | `emergency` | `assembly_point` |  |
| Other structure | `emergency` | `angela` |  |
| Other structure | `emergency` | `phone` |  |
| Other structure | `emergency` | `siren` |  |
| Other structure | `emergency` | `drinking_water` |  |

### Geological (23)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `geological` | `moraine` |  |
|  | `geological` | `outcrop` |  |
|  | `geological` | `volcanic_caldera_rim` |  |
|  | `geological` | `fault` |  |
|  | `geological` | `fold` |  |
|  | `geological` | `palaeontological_site` |  |
|  | `geological` | `volcanic_lava_field` |  |
|  | `geological` | `volcanic_vent` |  |
|  | `geological` | `glacial_erratic` |  |
|  | `geological` | `rock_glacier` |  |
|  | `geological` | `giants_kettle` |  |
|  | `geological` | `meteor_crater` |  |
|  | `geological` | `hoodoo` |  |
|  | `geological` | `columnar_jointing` |  |
|  | `geological` | `dyke` |  |
|  | `geological` | `monocline` |  |
|  | `geological` | `tor` |  |
|  | `geological` | `unconformity` |  |
|  | `geological` | `cone` |  |
|  | `geological` | `sinkhole` |  |
|  | `geological` | `pingo` |  |
|  | `geological` | `inselberg` |  |
|  | `geological` | `limestone_pavement` |  |

### Highway (120)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Roads | `highway` | `motorway` | way |
| Roads | `highway` | `trunk` | way |
| Roads | `highway` | `primary` | way |
| Roads | `highway` | `secondary` | way |
| Roads | `highway` | `tertiary` | way |
| Roads | `highway` | `unclassified` | way |
| Roads | `highway` | `residential` | way |
| Link roads | `highway` | `motorway_link` | way |
| Link roads | `highway` | `trunk_link` | way |
| Link roads | `highway` | `primary_link` | way |
| Link roads | `highway` | `secondary_link` | way |
| Link roads | `highway` | `tertiary_link` | way |
| Special road types | `highway` | `living_street` | way |
| Special road types | `highway` | `service` | way area |
| Special road types | `highway` | `pedestrian` | way area |
| Special road types | `highway` | `track` | way |
| Special road types | `highway` | `bus_guideway` | way |
| Special road types | `highway` | `escape` | way |
| Special road types | `highway` | `raceway` | way |
| Special road types | `highway` | `road` | way |
| Special road types | `highway` | `busway` | way |
| Paths | `highway` | `footway` | way area |
| Paths | `highway` | `bridleway` | way |
| Paths | `highway` | `steps` | way |
| Paths | `highway` | `corridor` | way |
| Paths | `highway` | `path` | way |
| Paths | `highway` | `via_ferrata` | way |
| When sidewalk/crosswalk is tagged as a separate way | `footway` | `sidewalk` | way |
| When sidewalk/crosswalk is tagged as a separate way | `footway` | `crossing` | way |
| When sidewalk/crosswalk is tagged as a separate way | `footway` | `traffic_island` | way |
| When sidewalk (or pavement) is tagged on the main roadway (see Sidewalks ) | `sidewalk` | `both \| left \| right \| no` | way |
| When cycleway is drawn as its own way (see Bicycle ) | `highway` | `cycleway` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `lane` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `opposite` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `opposite_lane` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `track` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `opposite_track` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `share_busway` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `opposite_share_busway` | way |
| Cycleway tagged on the main roadway or lane (see Bicycle ) | `cycleway` | `shared_lane` | way |
| Busways tagged on the main roadway or lane (see Bus lanes ) | `busway` | `lane` | way |
| Busways tagged on the main roadway or lane (see Bus lanes ) | `busway` | `opposite` | way |
| Busways tagged on the main roadway or lane (see Bus lanes ) | `busway` | `opposite_lane` | way |
| Street parking tagged on the main roadway (see Street parking ) | `parking :left / :right / :both (hereafter: parking: side )` | `lane \| street_side \| on_kerb \| half_on_kerb \| shoulder \| no \| separate \| yes` | way |
| Street parking tagged on the main roadway (see Street parking ) | `parking: side orientation =*` | `parallel \| diagonal \| perpendicular` | way |
| Lifecycle (see also lifecycle prefixes ) | `highway` | `proposed` | way |
| Lifecycle (see also lifecycle prefixes ) | `highway` | `construction` | way |
| Attributes | `abutters` | `commercial \| industrial \| mixed \| residential \| retail etc.` | way |
| Attributes | `bicycle_road` | `yes` | way |
| Attributes | `bus_bay` | `both \| left \| right` | way |
| Attributes | `change` | `yes \| no \| not_right \| not_left \| only_right \| only_left` | way |
| Attributes | `destination` | `<place name of destination>` | way |
| Attributes | `embankment` | `yes \| dyke` | way |
| Attributes | `embedded_rails` | `yes \| <type of railway>` | way |
| Attributes | `ford` | `yes` | node way |
| Attributes | `frontage_road` | `yes` | way |
| Attributes | `ice_road` | `yes` | way |
| Attributes | `incline` | `Number % \| ° \| up \| down` | node way |
| Attributes | `junction` | `roundabout` | way closed way |
| Attributes | `lanes` | `<number>` | way |
| Attributes | `lane_markings` | `yes \| no` | way |
| Attributes | `lit` | `yes \| no` | node way area |
| Attributes | `maxspeed` | `<number>` | way |
| Attributes | `motorroad` | `yes \| no` | way node |
| Attributes | `mountain_pass` | `yes` | node |
| Attributes | `mtb:scale` | `0-6` | way |
| Attributes | `mtb:scale :uphill` | `0-5` | way |
| Attributes | `mtb:scale :imba` | `0-4` | way |
| Attributes | `mtb:description` | `Text` | way |
| Attributes | `oneway` | `yes \| no \| reversible` | way |
| Attributes | `oneway:bicycle` | `yes \| no \|` | way |
| Attributes | `overtaking` | `yes \| no \| caution \| both \| forward \| backward` | way |
| Attributes | `parking:lane` | `parallel \| diagonal \| perpendicular \| marked \| no_parking \| no_stopping \| fire_lane.` | way |
| Attributes | `parking:condition` | `free \| ticket \| disc \| residents \| customers \| private` | way |
| Attributes | `passing_places` | `yes` | way |
| Attributes | `priority` | `forward \| backward` | way |
| Attributes | `priority_road` | `designated \| yes_unposted \| end` | way |
| Attributes | `sac_scale` | `strolling \| hiking \| mountain_hiking \| demanding_mountain_hiking \| alpine_hiking \| demanding_alpine_hiking \| difficult_alpine_hiking` | way |
| Attributes | `service` | `alley \| driveway \| parking_aisle etc.` | way |
| Attributes | `shoulder` | `no \| yes \| right \| both \| left` | way |
| Attributes | `side_road` | `yes` | way |
| Attributes | `smoothness` | `excellent \| good \| intermediate \| bad \| very_bad \| horrible \| very_horrible \| impassable` | way area |
| Attributes | `surface` | `paved \| unpaved \| asphalt \| concrete \| paving_stones \| sett \| cobblestone \| metal \| wood \| compacted \| fine_gravel \| gravel \| pebblestone \| plastic \| grass_paver \| grass \| dirt \| earth \| mud \| sand \| ground` | way |
| Attributes | `tactile_paving` | `yes \| no` | node way area |
| Attributes | `tracktype` | `grade1 \| grade2 \| grade3 \| grade4 \| grade5` | way |
| Attributes | `traffic_calming` | `bump \| hump \| table \| island \| cushion \| yes \| etc.` | node way |
| Attributes | `trail_visibility` | `excellent \| good \| intermediate \| bad \| horrible \| no` | way |
| Attributes | `trailblazed` | `yes \| no \| poles \| cairns \| symbols` | way |
| Attributes | `trailblazed:visibility` | `excellent \| good \| intermediate \| bad \| horrible \| no` | way |
| Attributes | `turn` | `left \| slight_left \| through \| right \| slight_right \| merge_to_left \| merge_to_right \| reverse` | way |
| Attributes | `width` | `<number>` | way |
| Attributes | `winter_road` | `yes` | way |
| Other highway features | `highway` | `bus_stop` | node |
| Other highway features | `highway` | `crossing` | node |
| Other highway features | `highway` | `cyclist_waiting_aid` | node |
| Other highway features | `highway` | `elevator` | node way |
| Other highway features | `highway` | `emergency_bay` | node way |
| Other highway features | `highway` | `emergency_access_point` | node |
| Other highway features | `highway` | `give_way` | node |
| Other highway features | `emergency` | `phone` | node |
| Other highway features | `highway` | `hitchhiking` | node |
| Other highway features | `highway` | `ladder` | node way |
| Other highway features | `highway` | `milestone` | node |
| Other highway features | `highway` | `mini_roundabout` | node |
| Other highway features | `highway` | `motorway_junction` | node |
| Other highway features | `highway` | `passing_place` | node |
| Other highway features | `highway` | `platform` | node way area |
| Other highway features | `highway` | `rest_area` | node area |
| Other highway features | `highway` | `services` | node area |
| Other highway features | `highway` | `speed_camera` | node |
| Other highway features | `highway` | `speed_display` | node |
| Other highway features | `highway` | `stop` | node |
| Other highway features | `highway` | `street_lamp` | node |
| Other highway features | `highway` | `toll_gantry` | node |
| Other highway features | `highway` | `traffic_mirror` | node |
| Other highway features | `highway` | `traffic_signals` | node |
| Other highway features | `highway` | `trailhead` | node |
| Other highway features | `highway` | `turning_circle` | node |
| Other highway features | `highway` | `turning_loop` | node |
| Other highway features | `highway` | `User Defined` | node way |

### Historic (63)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `historic` | `aircraft` |  |
|  | `historic` | `anchor` |  |
|  | `historic` | `aqueduct` |  |
|  | `historic` | `archaeological_site` |  |
|  | `historic` | `battlefield` |  |
|  | `historic` | `bomb_crater` |  |
|  | `historic` | `boundary_stone` |  |
|  | `historic` | `building` |  |
|  | `historic` | `bullaun_stone` |  |
|  | `historic` | `cannon` |  |
|  | `historic` | `caravanserai` |  |
|  | `historic` | `castle` |  |
|  | `historic` | `castle_wall` |  |
|  | `historic` | `cattle_crush` |  |
|  | `historic` | `charcoal_pile` |  |
|  | `historic` | `church` |  |
|  | `historic` | `city_gate` |  |
|  | `historic` | `citywalls` |  |
|  | `historic` | `creamery` |  |
|  | `historic` | `district` |  |
|  | `historic` | `epigraph` |  |
|  | `historic` | `farm` |  |
|  | `historic` | `fort` |  |
|  | `historic` | `gallows` |  |
|  | `historic` | `house` |  |
|  | `historic` | `high_cross` |  |
|  | `historic` | `highwater_mark` |  |
|  | `historic` | `lavoir` |  |
|  | `historic` | `lime_kiln` |  |
|  | `historic` | `locomotive` |  |
|  | `historic` | `machine` |  |
|  | `historic` | `manor` |  |
|  | `historic` | `memorial` |  |
|  | `historic` | `milestone` |  |
|  | `historic` | `millstone` |  |
|  | `historic` | `mine` |  |
|  | `historic` | `minecart` |  |
|  | `historic` | `monastery` |  |
|  | `historic` | `monument` |  |
|  | `historic` | `mosque` |  |
|  | `historic` | `ogham_stone` |  |
|  | `historic` | `optical_telegraph` |  |
|  | `historic` | `pillory` |  |
|  | `historic` | `pound` |  |
|  | `historic` | `railway_car` |  |
|  | `historic` | `road` |  |
|  | `historic` | `round_tower` |  |
|  | `historic` | `ruins` |  |
|  | `historic` | `rune_stone` |  |
|  | `historic` | `shieling` |  |
|  | `historic` | `ship` |  |
|  | `historic` | `stećak` |  |
|  | `historic` | `stone` |  |
|  | `historic` | `tank` |  |
|  | `historic` | `temple` |  |
|  | `historic` | `tomb` |  |
|  | `historic` | `tower` |  |
|  | `historic` | `vehicle` |  |
|  | `historic` | `wayside_cross` |  |
|  | `historic` | `wayside_shrine` |  |
|  | `historic` | `wreck` |  |
|  | `historic` | `warehouse` |  |
|  | `historic` | `yes` |  |

### Landuse (43)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Common landuse key values - developed land | `landuse` | `commercial` | node area |
| Common landuse key values - developed land | `landuse` | `construction` | node area |
| Common landuse key values - developed land | `landuse` | `education` | node area |
| Common landuse key values - developed land | `landuse` | `fairground` | node area |
| Common landuse key values - developed land | `landuse` | `industrial` | node area |
| Common landuse key values - developed land | `landuse` | `residential` | node area |
| Common landuse key values - developed land | `landuse` | `retail` | node area |
| Common landuse key values - developed land | `landuse` | `institutional` | node area |
| Common landuse key values - rural and agricultural land | `landuse` | `aquaculture` | node area |
| Common landuse key values - rural and agricultural land | `landuse` | `allotments` | node area |
| Common landuse key values - rural and agricultural land | `landuse` | `farmland` | area |
| Common landuse key values - rural and agricultural land | `landuse` | `farmyard` | area |
| Common landuse key values - rural and agricultural land | `landuse` | `animal_keeping` | area |
| Common landuse key values - rural and agricultural land | `landuse` | `flowerbed` | area |
| Common landuse key values - rural and agricultural land | `landuse` | `forest` | node area |
| Common landuse key values - rural and agricultural land | `landuse` | `logging` | area |
| Common landuse key values - rural and agricultural land | `landuse` | `greenhouse_horticulture` | area |
| Common landuse key values - rural and agricultural land | `landuse` | `meadow` | node area |
| Common landuse key values - rural and agricultural land | `landuse` | `orchard` | node area |
| Common landuse key values - rural and agricultural land | `landuse` | `plant_nursery` | area |
| Common landuse key values - rural and agricultural land | `landuse` | `vineyard` | node area |
| Common landuse key values - traffic and transportation | `landuse` | `depot` | area |
| Common landuse key values - traffic and transportation | `landuse` | `garages` | area |
| Common landuse key values - traffic and transportation | `landuse` | `highway` | area |
| Common landuse key values - traffic and transportation | `landuse` | `port` | area |
| Common landuse key values - traffic and transportation | `landuse` | `railway` | area |
| Common landuse key values - waterbody | `landuse` | `basin` | node area |
| Common landuse key values - waterbody | `landuse` | `reservoir` | node area |
| Common landuse key values - waterbody | `landuse` | `salt_pond` | area |
| Other landuse key values | `landuse` | `brownfield` | node area |
| Other landuse key values | `landuse` | `cemetery` | node area |
| Other landuse key values | `landuse` | `conservation` | area |
| Other landuse key values | `landuse` | `grass` | node area |
| Other landuse key values | `landuse` | `greenfield` | node area |
| Other landuse key values | `landuse` | `landfill` | node area |
| Other landuse key values | `landuse` | `military` | node area |
| Other landuse key values | `landuse` | `quarry` | node area |
| Other landuse key values | `landuse` | `recreation_ground` | node area |
| Other landuse key values | `landuse` | `religious` | node area |
| Other landuse key values | `landuse` | `village_green` | node area |
| Other landuse key values | `landuse` | `greenery` | area |
| Other landuse key values | `landuse` | `winter_sports` | node area |
| Other landuse key values | `landuse` | `user defined` | node area |

### Leisure (34)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `leisure` | `adult_gaming_centre` | node area |
|  | `leisure` | `amusement_arcade` | node area |
|  | `leisure` | `beach_resort` | node area |
|  | `leisure` | `bandstand` | node area |
|  | `leisure` | `bird_hide` | node area |
|  | `leisure` | `common` | node area |
|  | `leisure` | `dance` | node area |
|  | `leisure` | `disc_golf_course` | node area |
|  | `leisure` | `dog_park` | node area |
|  | `leisure` | `escape_game` | node area |
|  | `leisure` | `firepit` | node area |
|  | `leisure` | `fishing` | node area |
|  | `leisure` | `fitness_centre` | node area |
|  | `leisure` | `fitness_station` | node area |
|  | `leisure` | `garden` | node area |
|  | `leisure` | `hackerspace` | node area |
|  | `leisure` | `horse_riding` | node area |
|  | `leisure` | `ice_rink` | node area |
|  | `leisure` | `marina` | node area |
|  | `leisure` | `miniature_golf` | node area |
|  | `leisure` | `nature_reserve` | node area |
|  | `leisure` | `paddling_pool [en]` | node area |
|  | `leisure` | `park` | node area |
|  | `leisure` | `picnic_table` | node area |
|  | `leisure` | `pitch` | node area |
|  | `leisure` | `playground` | node area |
|  | `leisure` | `slipway` | node area |
|  | `leisure` | `sports_centre` | node area |
|  | `leisure` | `stadium` | node area |
|  | `leisure` | `summer_camp` | node area |
|  | `leisure` | `swimming_area` | node area |
|  | `leisure` | `swimming_pool` | node area |
|  | `leisure` | `track` | node area |
|  | `leisure` | `water_park` | node area |

### Man made (58)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `man_made` | `adit` |  |
|  | `man_made` | `beacon` |  |
|  | `man_made` | `breakwater` |  |
|  | `man_made` | `bridge` |  |
|  | `man_made` | `bunker_silo` |  |
|  | `man_made` | `carpet_hanger` |  |
|  | `man_made` | `chimney` |  |
|  | `man_made` | `column` |  |
|  | `man_made` | `communications_tower` |  |
|  | `man_made` | `crane` |  |
|  | `man_made` | `cross` |  |
|  | `man_made` | `cutline` |  |
|  | `man_made` | `clearcut` |  |
|  | `man_made` | `dovecote` |  |
|  | `man_made` | `dyke` |  |
|  | `man_made` | `embankment` |  |
|  | `man_made` | `flagpole` |  |
|  | `man_made` | `gasometer` |  |
|  | `man_made` | `goods_conveyor` |  |
|  | `man_made` | `groyne` |  |
|  | `man_made` | `guard_stone` |  |
|  | `man_made` | `kiln` |  |
|  | `man_made` | `lighthouse` |  |
|  | `man_made` | `mast` |  |
|  | `man_made` | `mineshaft` |  |
|  | `man_made` | `monitoring_station` |  |
|  | `man_made` | `obelisk` |  |
|  | `man_made` | `observatory` |  |
|  | `man_made` | `offshore_platform` |  |
|  | `man_made` | `petroleum_well` |  |
|  | `man_made` | `pier` |  |
|  | `man_made` | `pipeline` |  |
|  | `man_made` | `pump` |  |
|  | `man_made` | `pumping_station` |  |
|  | `man_made` | `reservoir_covered` |  |
|  | `man_made` | `sewer_vent` |  |
|  | `man_made` | `silo` |  |
|  | `man_made` | `snow_fence` |  |
|  | `man_made` | `snow_net` |  |
|  | `man_made` | `storage_tank` |  |
|  | `man_made` | `street_cabinet` |  |
|  | `man_made` | `stupa` |  |
|  | `man_made` | `surveillance` |  |
|  | `man_made` | `survey_point` |  |
|  | `man_made` | `tailings_pond` |  |
|  | `man_made` | `telescope` |  |
|  | `man_made` | `tower` |  |
|  | `man_made` | `video_wall` |  |
|  | `man_made` | `wastewater_plant` |  |
|  | `man_made` | `watermill` |  |
|  | `man_made` | `water_tower` |  |
|  | `man_made` | `water_well` |  |
|  | `man_made` | `water_tap` |  |
|  | `man_made` | `water_works` |  |
|  | `man_made` | `wildlife_crossing` |  |
|  | `man_made` | `windmill` |  |
|  | `man_made` | `works` |  |
|  | `man_made` | `yes` |  |

### Military (14)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `military` | `academy` |  |
|  | `military` | `airfield` |  |
|  | `military` | `base` |  |
|  | `military` | `bunker` |  |
|  | `military` | `barracks` |  |
|  | `military` | `checkpoint` |  |
|  | `military` | `danger_area` |  |
|  | `military` | `nuclear_explosion_site` |  |
|  | `military` | `obstacle_course` |  |
|  | `military` | `office` |  |
|  | `military` | `range` |  |
|  | `military` | `school` |  |
|  | `military` | `training_area` |  |
|  | `military` | `trench` |  |

### Natural (49)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Vegetation | `natural` | `fell` |  |
| Vegetation | `natural` | `grassland` |  |
| Vegetation | `natural` | `heath` |  |
| Vegetation | `natural` | `moor` |  |
| Vegetation | `natural` | `scrub` |  |
| Vegetation | `natural` | `shrubbery` |  |
| Vegetation | `natural` | `tree` |  |
| Vegetation | `natural` | `tree_row` |  |
| Vegetation | `natural` | `tundra` |  |
| Vegetation | `natural` | `wood` |  |
| Water related | `natural` | `bay` |  |
| Water related | `natural` | `beach` |  |
| Water related | `natural` | `blowhole` |  |
| Water related | `natural` | `cape` |  |
| Water related | `natural` | `coastline` |  |
| Water related | `natural` | `crevasse` |  |
| Water related | `natural` | `geyser` |  |
| Water related | `natural` | `glacier` |  |
| Water related | `natural` | `hot_spring` |  |
| Water related | `natural` | `isthmus` |  |
| Water related | `natural` | `mud` |  |
| Water related | `natural` | `peninsula` |  |
| Water related | `natural` | `reef` |  |
| Water related | `natural` | `shingle` |  |
| Water related | `natural` | `shoal` |  |
| Water related | `natural` | `spring` |  |
| Water related | `natural` | `strait` |  |
| Water related | `natural` | `water` |  |
| Water related | `natural` | `wetland` |  |
| Geology related | `natural` | `arch` |  |
| Geology related | `natural` | `arete` |  |
| Geology related | `natural` | `bare_rock` |  |
| Geology related | `natural` | `blockfield` |  |
| Geology related | `natural` | `cave_entrance` |  |
| Geology related | `natural` | `cliff` |  |
| Geology related | `natural` | `dune` |  |
| Geology related | `natural` | `earth_bank` |  |
| Geology related | `natural` | `fumarole` |  |
| Geology related | `natural` | `hill` |  |
| Geology related | `natural` | `peak` |  |
| Geology related | `natural` | `ridge` |  |
| Geology related | `natural` | `rock` |  |
| Geology related | `natural` | `saddle` |  |
| Geology related | `natural` | `sand` |  |
| Geology related | `natural` | `scree` |  |
| Geology related | `natural` | `sinkhole` |  |
| Geology related | `natural` | `stone` |  |
| Geology related | `natural` | `valley` |  |
| Geology related | `natural` | `volcano` |  |

### Office (58)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `office` | `accountant` |  |
|  | `office` | `advertising_agency` |  |
|  | `office` | `airline` |  |
|  | `office` | `architect` |  |
|  | `office` | `association` |  |
|  | `office` | `broadcaster` |  |
|  | `office` | `chamber` |  |
|  | `office` | `charity` |  |
|  | `office` | `company` |  |
|  | `office` | `construction_company` |  |
|  | `office` | `consulting` |  |
|  | `office` | `courier` |  |
|  | `office` | `coworking` |  |
|  | `office` | `diplomatic` |  |
|  | `office` | `educational_institution` |  |
|  | `office` | `employment_agency` |  |
|  | `office` | `energy_supplier` |  |
|  | `office` | `engineer` |  |
|  | `office` | `estate_agent` |  |
|  | `office` | `event_management` |  |
|  | `office` | `financial` |  |
|  | `office` | `financial_advisor` |  |
|  | `office` | `forestry` |  |
|  | `office` | `foundation` |  |
|  | `office` | `geodesist` |  |
|  | `office` | `gongo` |  |
|  | `office` | `government` |  |
|  | `office` | `graphic_design` |  |
|  | `office` | `guide` |  |
|  | `office` | `harbour_master` |  |
|  | `office` | `insurance` |  |
|  | `office` | `it` |  |
|  | `office` | `lawyer` |  |
|  | `office` | `logistics` |  |
|  | `office` | `moving_company` |  |
|  | `office` | `newspaper` |  |
|  | `office` | `ngo` |  |
|  | `office` | `notary` |  |
|  | `office` | `politician` |  |
|  | `office` | `political_party` |  |
|  | `office` | `property_management` |  |
|  | `office` | `publisher` |  |
|  | `office` | `quango` |  |
|  | `office` | `religion` |  |
|  | `office` | `research` |  |
|  | `office` | `school` |  |
|  | `office` | `security` |  |
|  | `office` | `surveyor` |  |
|  | `office` | `tax_advisor` |  |
|  | `office` | `telecommunication` |  |
|  | `office` | `transport` |  |
|  | `office` | `travel_agent` |  |
|  | `office` | `tutoring` |  |
|  | `office` | `union` |  |
|  | `office` | `university` |  |
|  | `office` | `visa` |  |
|  | `office` | `water_utility` |  |
|  | `office` | `yes` |  |

### Place (33)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Administratively declared places | `place` | `country` |  |
| Administratively declared places | `place` | `state` |  |
| Administratively declared places | `place` | `region` |  |
| Administratively declared places | `place` | `province` |  |
| Administratively declared places | `place` | `district` |  |
| Administratively declared places | `place` | `county` |  |
| Administratively declared places | `place` | `subdistrict` |  |
| Administratively declared places | `place` | `municipality` |  |
| Populated settlements, urban | `place` | `city` |  |
| Populated settlements, urban | `place` | `borough` |  |
| Populated settlements, urban | `place` | `suburb` |  |
| Populated settlements, urban | `place` | `quarter` |  |
| Populated settlements, urban | `place` | `neighbourhood` |  |
| Populated settlements, urban | `place` | `city_block` |  |
| Populated settlements, urban | `place` | `plot` |  |
| Populated settlements, urban and rural | `place` | `city` |  |
| Populated settlements, urban and rural | `place` | `town` |  |
| Populated settlements, urban and rural | `place` | `village` |  |
| Populated settlements, urban and rural | `place` | `hamlet` |  |
| Populated settlements, urban and rural | `place` | `isolated_dwelling` |  |
| Populated settlements, urban and rural | `place` | `farm` |  |
| Populated settlements, urban and rural | `place` | `allotments` |  |
| Other places | `place` | `continent` |  |
| Other places | `place` | `archipelago` |  |
| Other places | `place` | `island` |  |
| Other places | `place` | `islet` |  |
| Other places | `place` | `square` |  |
| Other places | `place` | `locality` |  |
| Other places | `place` | `polder` |  |
| Other places | `place` | `sea` |  |
| Other places | `place` | `ocean` |  |
| Additional attributes | `population` | `*` |  |
| Additional attributes | `population` | `is_in=*` |  |

### Power (22)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `power` | `cable` |  |
|  | `power` | `catenary_mast` |  |
|  | `power` | `compensator` |  |
|  | `power` | `connection` |  |
|  | `power` | `converter` |  |
|  | `power` | `generator` |  |
|  | `power` | `heliostat` |  |
|  | `power` | `insulator` |  |
|  | `power` | `inverter` |  |
|  | `power` | `line` |  |
|  | `power` | `line=busbar` |  |
|  | `power` | `bay` |  |
|  | `power` | `power=minor_line` |  |
|  | `power` | `plant` |  |
|  | `power` | `pole` |  |
|  | `power` | `portal` |  |
|  | `power` | `substation` |  |
|  | `power` | `switch` |  |
|  | `power` | `switchgear` |  |
|  | `power` | `terminal` |  |
|  | `power` | `tower` |  |
|  | `power` | `transformer` |  |

### Public transport (5)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `public_transport` | `stop_position` |  |
|  | `public_transport` | `platform` |  |
|  | `public_transport` | `station` |  |
|  | `public_transport` | `stop_area` |  |
|  | `public_transport` | `stop_area_group` |  |

### Railway (55)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Tracks | `railway` | `abandoned` | way |
| Tracks | `railway` | `construction` | way |
| Tracks | `railway` | `proposed` | way |
| Tracks | `railway` | `disused` | way |
| Tracks | `railway` | `funicular` | way |
| Tracks | `railway` | `light_rail` | way |
| Tracks | `railway` | `miniature` | way |
| Tracks | `railway` | `monorail` | way |
| Tracks | `railway` | `narrow_gauge` | way |
| Tracks | `railway` | `preserved` | way |
| Tracks | `railway` | `rail` | way |
| Tracks | `railway` | `subway` | way |
| Tracks | `railway` | `tram` | way |
| Additional track features or attributes | `bridge` | `yes` | way |
| Additional track features or attributes | `cutting` | `yes` | way |
| Additional track features or attributes | `electrified` | `contact_line rail yes no` | way |
| Additional track features or attributes | `embankment` | `yes` | way |
| Additional track features or attributes | `embedded_rails` | `yes / <type of railway>` | way |
| Additional track features or attributes | `frequency` | `< number > [Hz]` | way |
| Additional track features or attributes | `passenger_lines` | `< number >` | way |
| Additional track features or attributes | `railway:track_ref` | `< number >` | way |
| Additional track features or attributes | `service` | `crossover` | way |
| Additional track features or attributes | `service` | `siding` | way |
| Additional track features or attributes | `service` | `spur` | way |
| Additional track features or attributes | `service` | `yard` | way |
| Additional track features or attributes | `tunnel` | `yes` | way |
| Additional track features or attributes | `tracks` | `< number >` | way |
| Additional track features or attributes | `usage` | `main branch industrial military tourism scientific test` | way |
| Additional track features or attributes | `voltage` | `< number >` | way |
| Stations and stops | `railway` | `halt` | node |
| Stations and stops | `public_transport` | `stop_position` | node |
| Stations and stops | `public_transport` | `platform` | node way area |
| Stations and stops | `railway` | `platform` | way area |
| Stations and stops | `public_transport` | `station` | node area |
| Stations and stops | `railway` | `station` | node area |
| Stations and stops | `railway` | `stop` | node |
| Stations and stops | `railway` | `subway_entrance` | node |
| Stations and stops | `railway` | `tram_stop` | node |
| Infrastructure | `landuse` | `railway` | area |
| Infrastructure | `railway` | `buffer_stop` | node |
| Infrastructure | `railway` | `crossing` | node |
| Infrastructure | `railway` | `derail` | node |
| Infrastructure | `railway` | `level_crossing` | node |
| Infrastructure | `railway` | `railway_crossing` | node |
| Infrastructure | `railway` | `roundhouse` | area |
| Infrastructure | `railway` | `signal` | node |
| Infrastructure | `railway` | `switch` | node |
| Infrastructure | `railway` | `tram_level_crossing` | node |
| Infrastructure | `railway` | `traverser` | node area |
| Infrastructure | `railway` | `turntable` | node area |
| Infrastructure | `railway` | `ventilation_shaft` | node way |
| Infrastructure | `railway` | `wash` | node area |
| Infrastructure | `railway` | `water_crane` | node |
| Infrastructure | `railway` | `workshop` | area |
| Infrastructure | `railway` | `user defined` | node way |

### Route (24)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `route` | `bicycle` | relation |
|  | `route` | `bus` | relation |
|  | `route` | `canoe` | relation |
|  | `route` | `detour` | relation |
|  | `route` | `ferry` | way relation |
|  | `route` | `fitness_trail` | relation |
|  | `route` | `foot` | relation |
|  | `route` | `funicular` | relation |
|  | `route` | `hiking` | relation |
|  | `route` | `horse` | relation |
|  | `route` | `inline_skates` | relation |
|  | `route` | `light_rail` | relation |
|  | `route` | `mtb` | relation |
|  | `route` | `piste` | way relation |
|  | `route` | `railway` | relation |
|  | `route` | `road` | relation |
|  | `route` | `running` | relation |
|  | `route` | `ski` | relation |
|  | `route` | `subway` | relation |
|  | `route` | `train` | relation |
|  | `route` | `tracks` | relation |
|  | `route` | `tram` | relation |
|  | `route` | `trolleybus` | relation |
|  | `route` | `User defined` | relation |

### Shop (182)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Food, beverages | `shop` | `alcohol` |  |
| Food, beverages | `shop` | `bakery` |  |
| Food, beverages | `shop` | `beverages` |  |
| Food, beverages | `shop` | `brewing_supplies` |  |
| Food, beverages | `shop` | `butcher` |  |
| Food, beverages | `shop` | `cheese` |  |
| Food, beverages | `shop` | `chocolate` |  |
| Food, beverages | `shop` | `coffee` |  |
| Food, beverages | `shop` | `confectionery` |  |
| Food, beverages | `shop` | `convenience` |  |
| Food, beverages | `shop` | `dairy` |  |
| Food, beverages | `shop` | `deli` |  |
| Food, beverages | `shop` | `farm` |  |
| Food, beverages | `shop` | `food` |  |
| Food, beverages | `shop` | `frozen_food` |  |
| Food, beverages | `shop` | `greengrocer` |  |
| Food, beverages | `shop` | `health_food` |  |
| Food, beverages | `shop` | `ice_cream` |  |
| Food, beverages | `shop` | `nuts` |  |
| Food, beverages | `shop` | `pasta` |  |
| Food, beverages | `shop` | `pastry` |  |
| Food, beverages | `shop` | `seafood` |  |
| Food, beverages | `shop` | `spices` |  |
| Food, beverages | `shop` | `tea` |  |
| Food, beverages | `shop` | `tortilla` |  |
| Food, beverages | `shop` | `water` |  |
| Food, beverages | `shop` | `wine` |  |
| General store, department store, mall | `shop` | `department_store` |  |
| General store, department store, mall | `shop` | `general` |  |
| General store, department store, mall | `shop` | `kiosk` |  |
| General store, department store, mall | `shop` | `mall` |  |
| General store, department store, mall | `shop` | `supermarket` |  |
| General store, department store, mall | `shop` | `wholesale` |  |
| Clothing, shoes, accessories | `shop` | `baby_goods` |  |
| Clothing, shoes, accessories | `shop` | `bag` |  |
| Clothing, shoes, accessories | `shop` | `boutique` |  |
| Clothing, shoes, accessories | `shop` | `clothes` |  |
| Clothing, shoes, accessories | `shop` | `fabric` |  |
| Clothing, shoes, accessories | `shop` | `fashion` |  |
| Clothing, shoes, accessories | `shop` | `fashion_accessories` |  |
| Clothing, shoes, accessories | `shop` | `jewelry` |  |
| Clothing, shoes, accessories | `shop` | `leather` |  |
| Clothing, shoes, accessories | `shop` | `sewing` |  |
| Clothing, shoes, accessories | `shop` | `shoes` |  |
| Clothing, shoes, accessories | `shop` | `shoe_repair` |  |
| Clothing, shoes, accessories | `shop` | `tailor` |  |
| Clothing, shoes, accessories | `shop` | `watches` |  |
| Clothing, shoes, accessories | `shop` | `wool` |  |
| Discount store, charity | `shop` | `charity` |  |
| Discount store, charity | `shop` | `second_hand` |  |
| Discount store, charity | `shop` | `variety_store` |  |
| Health and beauty | `shop` | `beauty` |  |
| Health and beauty | `shop` | `chemist` |  |
| Health and beauty | `shop` | `cosmetics` |  |
| Health and beauty | `shop` | `erotic` |  |
| Health and beauty | `shop` | `hairdresser` |  |
| Health and beauty | `shop` | `hairdresser_supply` |  |
| Health and beauty | `shop` | `hearing_aids` |  |
| Health and beauty | `shop` | `herbalist` |  |
| Health and beauty | `shop` | `massage` |  |
| Health and beauty | `shop` | `medical_supply` |  |
| Health and beauty | `shop` | `nutrition_supplements` |  |
| Health and beauty | `shop` | `optician` |  |
| Health and beauty | `shop` | `perfumery` |  |
| Health and beauty | `shop` | `piercing` |  |
| Health and beauty | `shop` | `tattoo` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `agrarian` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `appliance` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `bathroom_furnishing` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `country_store` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `doityourself` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `electrical` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `energy` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `fireplace` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `florist` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `garden_centre` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `garden_furniture` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `gas` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `glaziery` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `groundskeeping` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `hardware` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `houseware` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `locksmith` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `paint` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `pottery` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `security` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `tool_hire` |  |
| Do-it-yourself, household, building materials, gardening | `shop` | `trade` |  |
| Furniture and interior | `shop` | `antiques` |  |
| Furniture and interior | `shop` | `bed` |  |
| Furniture and interior | `shop` | `candles` |  |
| Furniture and interior | `shop` | `carpet` |  |
| Furniture and interior | `shop` | `curtain` |  |
| Furniture and interior | `shop` | `doors` |  |
| Furniture and interior | `shop` | `flooring` |  |
| Furniture and interior | `shop` | `furniture` |  |
| Furniture and interior | `shop` | `household_linen` |  |
| Furniture and interior | `shop` | `interior_decoration` |  |
| Furniture and interior | `shop` | `kitchen` |  |
| Furniture and interior | `shop` | `lighting` |  |
| Furniture and interior | `shop` | `tiles` |  |
| Furniture and interior | `shop` | `window_blind` |  |
| Electronics | `shop` | `computer` |  |
| Electronics | `shop` | `electronics` |  |
| Electronics | `shop` | `hifi` |  |
| Electronics | `shop` | `mobile_phone` |  |
| Electronics | `shop` | `printer_ink` |  |
| Electronics | `shop` | `radiotechnics` |  |
| Electronics | `shop` | `telecommunication` |  |
| Electronics | `shop` | `vacuum_cleaner` |  |
| Outdoors and sport, vehicles | `shop` | `[[ Too many Data Items entities accessed. \| atv ]]` |  |
| Outdoors and sport, vehicles | `shop` | `aviation` |  |
| Outdoors and sport, vehicles | `shop` | `bicycle` |  |
| Outdoors and sport, vehicles | `shop` | `boat` |  |
| Outdoors and sport, vehicles | `shop` | `car` |  |
| Outdoors and sport, vehicles | `shop` | `car_parts` |  |
| Outdoors and sport, vehicles | `shop` | `car_repair` |  |
| Outdoors and sport, vehicles | `shop` | `caravan` |  |
| Outdoors and sport, vehicles | `shop` | `fishing` |  |
| Outdoors and sport, vehicles | `shop` | `fuel` |  |
| Outdoors and sport, vehicles | `shop` | `golf` |  |
| Outdoors and sport, vehicles | `shop` | `hunting` |  |
| Outdoors and sport, vehicles | `shop` | `military_surplus` |  |
| Outdoors and sport, vehicles | `shop` | `motorcycle` |  |
| Outdoors and sport, vehicles | `shop` | `motorcycle_repair` |  |
| Outdoors and sport, vehicles | `shop` | `outdoor` |  |
| Outdoors and sport, vehicles | `shop` | `scooter` |  |
| Outdoors and sport, vehicles | `shop` | `scuba_diving` |  |
| Outdoors and sport, vehicles | `shop` | `ski` |  |
| Outdoors and sport, vehicles | `shop` | `snowmobile` |  |
| Outdoors and sport, vehicles | `shop` | `sports` |  |
| Outdoors and sport, vehicles | `shop` | `surf` |  |
| Outdoors and sport, vehicles | `shop` | `swimming_pool` |  |
| Outdoors and sport, vehicles | `shop` | `trailer` |  |
| Outdoors and sport, vehicles | `shop` | `truck` |  |
| Outdoors and sport, vehicles | `shop` | `tyres` |  |
| Art, music, hobbies | `shop` | `art` |  |
| Art, music, hobbies | `shop` | `camera` |  |
| Art, music, hobbies | `shop` | `collector` |  |
| Art, music, hobbies | `shop` | `craft` |  |
| Art, music, hobbies | `shop` | `frame` |  |
| Art, music, hobbies | `shop` | `games` |  |
| Art, music, hobbies | `shop` | `model` |  |
| Art, music, hobbies | `shop` | `music` |  |
| Art, music, hobbies | `shop` | `musical_instrument` |  |
| Art, music, hobbies | `shop` | `photo` |  |
| Art, music, hobbies | `shop` | `trophy` |  |
| Art, music, hobbies | `shop` | `video` |  |
| Art, music, hobbies | `shop` | `video_games` |  |
| Stationery, gifts, books, newspapers | `shop` | `anime` |  |
| Stationery, gifts, books, newspapers | `shop` | `books` |  |
| Stationery, gifts, books, newspapers | `shop` | `gift` |  |
| Stationery, gifts, books, newspapers | `shop` | `lottery` |  |
| Stationery, gifts, books, newspapers | `shop` | `newsagent` |  |
| Stationery, gifts, books, newspapers | `shop` | `stationery` |  |
| Stationery, gifts, books, newspapers | `shop` | `ticket` |  |
| Others | `shop` | `bookmaker` |  |
| Others | `shop` | `cannabis` |  |
| Others | `shop` | `copyshop` |  |
| Others | `shop` | `dry_cleaning` |  |
| Others | `shop` | `e-cigarette` |  |
| Others | `shop` | `funeral_directors` |  |
| Others | `shop` | `laundry` |  |
| Others | `shop` | `money_lender` |  |
| Others | `shop` | `outpost` |  |
| Others | `shop` | `party` |  |
| Others | `shop` | `pawnbroker` |  |
| Others | `shop` | `pest_control` |  |
| Others | `shop` | `pet` |  |
| Others | `shop` | `pet_grooming` |  |
| Others | `shop` | `pyrotechnics` |  |
| Others | `shop` | `religion` |  |
| Others | `shop` | `rental` |  |
| Others | `shop` | `storage_rental` |  |
| Others | `shop` | `tobacco` |  |
| Others | `shop` | `toys` |  |
| Others | `shop` | `travel_agency` |  |
| Others | `shop` | `vacant` |  |
| Others | `shop` | `vending_machine` |  |
| Others | `shop` | `weapons` |  |
| Others | `shop` | `yes` |  |
| Others | `shop` | `user defined` |  |

### Telecom (7)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `telecom` | `exchange` |  |
|  | `telecom` | `connection_point` |  |
|  | `telecom` | `distribution_point` |  |
|  | `telecom` | `service_device` |  |
|  | `telecom` | `data_center` |  |
|  | `telecom` | `line` |  |
|  | `telecom` | `cable_landing_station` |  |

### Tourism (22)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `tourism` | `alpine_hut` |  |
|  | `tourism` | `apartment` |  |
|  | `tourism` | `aquarium` |  |
|  | `tourism` | `artwork` |  |
|  | `tourism` | `attraction` |  |
|  | `tourism` | `camp_pitch` |  |
|  | `tourism` | `camp_site` |  |
|  | `tourism` | `caravan_site` |  |
|  | `tourism` | `chalet` |  |
|  | `tourism` | `gallery` |  |
|  | `tourism` | `guest_house` |  |
|  | `tourism` | `hostel` |  |
|  | `tourism` | `hotel` |  |
|  | `tourism` | `information` |  |
|  | `tourism` | `motel` |  |
|  | `tourism` | `museum` |  |
|  | `tourism` | `picnic_site` |  |
|  | `tourism` | `theme_park` |  |
|  | `tourism` | `viewpoint` |  |
|  | `tourism` | `wilderness_hut` |  |
|  | `tourism` | `zoo` |  |
|  | `tourism` | `yes` |  |

### Water (15)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `water` | `river` |  |
|  | `water` | `oxbow` |  |
|  | `water` | `canal` |  |
|  | `water` | `ditch` |  |
|  | `water` | `lock` |  |
|  | `water` | `fish_pass` |  |
|  | `water` | `lake` |  |
|  | `water` | `reservoir` |  |
|  | `water` | `pond` |  |
|  | `water` | `basin` |  |
|  | `water` | `lagoon` |  |
|  | `water` | `stream_pool` |  |
|  | `water` | `reflecting_pool` |  |
|  | `water` | `moat` |  |
|  | `water` | `wastewater` |  |

### Waterway (19)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Natural watercourses | `waterway` | `river` |  |
| Natural watercourses | `waterway` | `riverbank` |  |
| Natural watercourses | `waterway` | `stream` |  |
| Natural watercourses | `waterway` | `tidal_channel` |  |
| Man-made waterways | `waterway` | `canal` |  |
| Man-made waterways | `waterway` | `drain` |  |
| Man-made waterways | `waterway` | `ditch` |  |
| Man-made waterways | `waterway` | `pressurised` |  |
| Man-made waterways | `waterway` | `fairway` |  |
| Facilities | `waterway` | `dock` |  |
| Facilities | `waterway` | `boatyard` |  |
| Barriers on waterways | `waterway` | `dam` |  |
| Barriers on waterways | `waterway` | `weir` |  |
| Barriers on waterways | `waterway` | `waterfall` |  |
| Barriers on waterways | `waterway` | `lock_gate` |  |
| Other features on waterways | `waterway` | `soakhole` |  |
| Other features on waterways | `waterway` | `turning_point` |  |
| Other features on waterways | `waterway` | `water_point` |  |
| Other features on waterways | `waterway` | `fuel` |  |

### Addresses (21)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
| Tags for individual houses | `addr:housenumber` | `user defined` | node area |
| Tags for individual houses | `addr:housename` | `user defined` | node area |
| Tags for individual houses | `addr:flats` | `user defined` | node |
| Tags for individual houses | `addr:conscriptionnumber` | `user defined` | node area |
| Tags for individual houses | `addr:street` | `user defined` | node area |
| Tags for individual houses | `addr:place` | `user defined` | node area |
| Tags for individual houses | `addr:postcode` | `user defined` | node area |
| Tags for individual houses | `addr:city` | `user defined` | node area |
| Tags for individual houses | `addr:country` | `user defined` | node area |
| Tags for individual houses | `addr:postbox` | `user defined` | node area |
| Tags for individual houses | `addr:full` | `user defined` | node area |
| For countries using hamlet, subdistrict, district, province, state, county | `addr:hamlet` | `user defined` | node area |
| For countries using hamlet, subdistrict, district, province, state, county | `addr:suburb` | `user defined` | node area |
| For countries using hamlet, subdistrict, district, province, state, county | `addr:subdistrict` | `user defined` | node area |
| For countries using hamlet, subdistrict, district, province, state, county | `addr:district` | `user defined` | node area |
| For countries using hamlet, subdistrict, district, province, state, county | `addr:province` | `user defined` | node area |
| For countries using hamlet, subdistrict, district, province, state, county | `addr:state` | `user defined` | node area |
| For countries using hamlet, subdistrict, district, province, state, county | `addr:county` | `user defined` | node area |
| Tags for interpolation ways | `addr:interpolation` | `all/even/odd/ alphabetic` | way |
| Tags for interpolation ways | `addr:interpolation` | `Number n` | way |
| Tags for interpolation ways | `addr:inclusion` | `actual/estimate/potential` | way |

### Annotations (28)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `comment` | `*` |  |
|  | `comment` | `contact:email=*` |  |
|  | `comment` | `contact:fax=*` |  |
|  | `comment` | `contact:phone=*` |  |
|  | `comment` | `contact:sms=*` |  |
|  | `comment` | `contact:website=*` |  |
|  | `comment` | `delivery:*=*` |  |
|  | `comment` | `description=*` |  |
|  | `comment` | `drive_through:*=*` |  |
|  | `comment` | `email=*` |  |
|  | `comment` | `fax=*` |  |
|  | `comment` | `fixme=*` |  |
|  | `comment` | `image=*` |  |
|  | `comment` | `note=*` |  |
|  | `comment` | `phone=*` |  |
|  | `comment` | `source=*` |  |
|  | `comment` | `source=extrapolation` |  |
|  | `comment` | `source=historical` |  |
|  | `comment` | `source=image` |  |
|  | `comment` | `source=knowledge` |  |
|  | `comment` | `source=survey` |  |
|  | `comment` | `source=voice` |  |
|  | `comment` | `source:geometry=*` |  |
|  | `comment` | `source:name=*` |  |
|  | `comment` | `source:ref=*` |  |
|  | `comment` | `source_ref=*` |  |
|  | `comment` | `takeaway:*=*` |  |
|  | `comment` | `wikipedia=*` |  |

### Properties (56)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `area` | `yes` | area |
|  | `brand` | `user defined` | node area |
|  | `bridge` | `yes / aqueduct / viaduct / cantilever / movable / covered / …` | way |
|  | `capacity` | `amount` |  |
|  | `charge` | `amount` |  |
|  | `clothes` | `see key's page` |  |
|  | `covered` | `yes` |  |
|  | `crossing` | `no / traffic_signals / uncontrolled / island / unmarked` |  |
|  | `crossing:island` | `yes / no` |  |
|  | `cutting` | `yes / left / right` |  |
|  | `disused` | `yes` |  |
|  | `drinking_water` | `yes / no` |  |
|  | `drive_through` | `yes / no` |  |
|  | `drive_in` | `yes / no` |  |
|  | `electrified` | `contact_line / rail` |  |
|  | `ele` | `Number` |  |
|  | `embankment` | `yes` |  |
|  | `end_date` | `Date` |  |
|  | `energy_class [en]` | `code` |  |
|  | `est_width` | `Number` |  |
|  | `fee` | `yes / no` |  |
|  | `fire_object:type` | `poo / szo` |  |
|  | `fire_operator` | `Name` |  |
|  | `fire_rank` | `1bis / 2 to 5` | area |
|  | `frequency` | `Number` |  |
|  | `gutter [en]` | `yes/no` |  |
|  | `hazard` | `see hazard` |  |
|  | `hot_water` | `yes / no` |  |
|  | `inscription` | `User Defined` |  |
|  | `internet_access` | `yes / wired / wlan / terminal / no` |  |
|  | `layer` | `-5 to 5` |  |
|  | `leaf_cycle` | `evergreen / deciduous / semi_evergreen / semi_deciduous / mixed` |  |
|  | `leaf_type` | `broadleaved / needleleaved / mixed / leafless` | area |
|  | `location` | `underground / overground / underwater / roof / indoor` |  |
|  | `narrow` | `yes` |  |
|  | `nudism` | `yes / obligatory / designated / no / customary / permissive` |  |
|  | `opening_hours` | `24/7 or mo md hh:mm-hh:mm. (read described syntax)` |  |
|  | `opening_hours:drive_through` | `24/7 or mo md hh:mm-hh:mm. (read described syntax)` |  |
|  | `operator` | `User Defined` |  |
|  | `power_supply` | `yes / no` |  |
|  | `produce` | `User Defined` | relation |
|  | `rental` | `see key's page` |  |
|  | `sauna` | `yes / no` |  |
|  | `service_times` | `see opening_hours` |  |
|  | `shower` | `yes / no` |  |
|  | `sport` | `soccer / tennis / basketball / baseball / multi / ...` |  |
|  | `start_date` | `Date` | relation |
|  | `tactile_paving` | `yes /no` |  |
|  | `tidal` | `yes` | area |
|  | `toilets` | `yes / no` |  |
|  | `topless` | `yes / no` |  |
|  | `tunnel` | `yes` | way |
|  | `toilets:wheelchair` | `yes / no` |  |
|  | `wheelchair` | `yes / no / limited` |  |
|  | `width` | `Number` |  |
|  | `wood` | `coniferous / deciduous / mixed` |  |

### References (14)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `iata` | `*` |  |
|  | `iata` | `icao=*` |  |
|  | `iata` | `int_ref=*` |  |
|  | `iata` | `lcn_ref=*` |  |
|  | `iata` | `loc_ref=*` |  |
|  | `iata` | `local_ref=*` |  |
|  | `iata` | `nat_ref=*` |  |
|  | `iata` | `ncn_ref=*` |  |
|  | `iata` | `old_ref=*` |  |
|  | `iata` | `rcn_ref=*` |  |
|  | `iata` | `ref=*` |  |
|  | `iata` | `reg_ref=*` |  |
|  | `iata` | `route_ref=*` |  |
|  | `iata` | `source_ref=*` |  |

### Restrictions (62)

| Subgroup | Key | Value | Elements |
|---|---|---|---|
|  | `access` | `agricultural delivery designated destination forestry no official permissive private yes` | way |
|  | `agricultural` | `yes / no` | way |
|  | `atv` | `For values see access above` | way |
|  | `bdouble` | `For values see access above` | way area |
|  | `bicycle` | `For values see access above + dismount` | way |
|  | `boat` | `For values see access above` | way area |
|  | `bus` | `For values see access above` | way area |
|  | `carriage` | `For values see access above` | way area |
|  | `cycle_rickshaw` | `For values see access above` | way area |
|  | `electric_bicycle` | `For values see access above` | way node area |
|  | `emergency` | `yes` | way |
|  | `foot` | `For values see access above` | way |
|  | `forestry` | `yes / no` | way |
|  | `golf_cart` | `For values see access above` | way |
|  | `goods` | `For values see access above` | way |
|  | `hand_cart` | `For values see access above` | way area |
|  | `hazmat` | `For values see access above` | way |
|  | `hgv` | `For values see access above` | way |
|  | `horse` | `For values see access above` | way |
|  | `hov` | `For values see access above` | way |
|  | `inline_skates` | `yes / no` | way node area |
|  | `lhv` | `For values see access above` | way |
|  | `mofa` | `For values see access above` | way |
|  | `moped` | `For values see access above` | way |
|  | `motorboat` | `For values see access above` | way area |
|  | `motorcar` | `For values see access above` | way |
|  | `motorcycle` | `For values see access above` | way |
|  | `motor_vehicle` | `For values see access above` | way |
|  | `psv` | `For values see access above` | way |
|  | `roadtrain` | `For values see access above` | way area |
|  | `ski` | `For values see access above` | way area |
|  | `speed_pedelec` | `For values see access above` | way node area |
|  | `tank` | `For values see access above` | way area |
|  | `taxi` | `For values see access above` | way |
|  | `trailer` | `For values see access above` | way area |
|  | `tourist_bus` | `For values see access above` | way area |
|  | `vehicle` | `For values see access above` | way |
|  | `4wd_only` | `yes` | way |
|  | `alcohol` | `yes / no` | node area |
|  | `dog` | `yes / no` | node way area relation |
|  | `drinking_water:legal` | `yes / no` | node area |
|  | `female` | `yes` | node area |
|  | `gender_segregated` | `yes/no` | node area |
|  | `male` | `yes` | node area |
|  | `max_age` | `age` | node area |
|  | `maxaxleload` | `Weight` | way |
|  | `maxheight` | `Height` | way |
|  | `maxlength` | `Length` | way |
|  | `maxspeed` | `Speed` | way |
|  | `maxstay` | `Duration` | way |
|  | `maxweight` | `Weight` | way |
|  | `maxwidth` | `Width` | way |
|  | `min_age` | `age` | node area |
|  | `minspeed` | `Speed` | way |
|  | `noexit` | `yes` | node way |
|  | `oneway` | `yes / no / -1` | way |
|  | `openfire` | `yes / no` | node area relation |
|  | `Relation:restriction` | `nan` | relation |
|  | `smoking` | `yes / no` | node area relation |
|  | `toll` | `yes` | node |
|  | `traffic_sign` | `city_limit` | node |
|  | `unisex` | `yes` | node area |

