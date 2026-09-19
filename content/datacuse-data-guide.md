# DataCuse data guide

Reviewed September 18, 2026. This is a feasibility review of all 365 pitches, not a claim that the analyses have been run. Every pitch in the [idea bank](datacuse-idea-bank.md) now has its own availability, effort, first step, and limitation. Sources below distinguish inspected local files, verified public sources, and research leads. “Not found” means not found in this review, not that data cannot exist.

| Data route | Ideas |
| --- | ---: |
| Local | 107 |
| Public | 91 |
| Mixed | 35 |
| Manual | 70 |
| Research | 62 |

All **365** ideas reviewed. **63** have both Local inputs and Quick estimated effort. Across all routes: **89 Quick**, **221 Setup**, and **55 Project**. These are feasibility labels, independent of publication status.

## Reading the labels

| Availability | What it means |
| --- | --- |
| Local | The main input files and relevant fields were inspected on this computer. Cleaning, definitions, and checking are still needed. |
| Public | A public download, official listing, or documented data-access route exists. It has not necessarily been downloaded or checked for complete Syracuse coverage. |
| Mixed | Some inputs are local; other inputs, documentation, or observations must be added. |
| Manual | You need to create observations, a small verified inventory, photographs, or survey responses. No ready-made complete dataset was verified. |
| Research | An archive or documentary research route exists. A specific supporting record must still be located; this is not a ready spreadsheet. |

**Quick** means a plausible short analysis once the source is opened, not a promise of a finished post in an hour. **Setup** means joins, mapping, cleaning, or a bounded manual audit. **Project** means substantial collection, archival work, routing, software, or waiting for observations. Effort includes the core work described, not just clicking Download. These are editorial estimates.

For an easy next post, start with DC015 (street-name endings), DC031 (common tree species), DC036 (recorded trunk sizes), DC038 (planting sites), DC040 (stumps), DC063 (white Christmas), DC077 (weekend rain), DC107 (round building years), DC195 (busiest library month), or DC271 (Cityline categories). These have inspected local inputs. Check their source dates before writing a present-tense headline.

Use small, honestly bounded investigations when a complete citywide inventory does not exist. A survey of ten playgrounds can support “the ten playgrounds we checked”; it cannot support an unqualified citywide ranking. Preserve non-findings rather than forcing an interesting result.

## DC007 companion app

**Sam's requested addition:** build a web app as part of the center-of-Syracuse post. When a visitor opens it and chooses to use their location, show which direction they should face to face the center of Syracuse and how many miles away they are.

Proposed implementation brief, for later work:

- Calculate and document a fixed center coordinate first, linked to DC005. Suggested initial definition: centroid of the selected Syracuse municipal boundary. Decide explicitly whether to exclude water. A population center from DC006 could be a clearly labeled optional comparison.
- Show distance in **straight-line miles**, the compass direction, and bearing in degrees from north. Do not label it walking or driving distance.
- Offer a **Use my location** action, then calculate distance and initial bearing in the browser. If location is denied or unavailable, allow a manual map pin. Do not silently substitute an IP-based city location.
- A live “turn until you face the center” arrow additionally needs a usable north-referenced device heading. Where supported, request orientation access from a button press. Otherwise show a north-up map arrow and a textual bearing; GPS position alone does not say which direction a stationary person faces.
- Handle poor location accuracy, unavailable compass readings, desktop browsers, and a visitor effectively at the center. Do not display a falsely precise bearing when position uncertainty dominates the distance.
- Keep the location calculation on the device by default. No server-side location history is required. Any optional reader-vote feature should collect a separate perceived-center pin with a clear explanation.
- The app and the original question are related but distinct: “where am I relative to the center?” does not measure “where do residents think the center is?” To answer the original question, optionally ask for a center guess before showing the computed point and label responses as a self-selected sample.

Browser requirements checked against [MDN geolocation documentation](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API) and [orientation permission documentation](https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent/requestPermission_static): geolocation requires a secure context and user permission; orientation support and permission requirements vary. This is a saved feature brief, not an implemented app.

## DC058 migration-bird starting plan

Keep the bird topic with a measurable question: **Which birds have the shortest seasonal reporting windows in Onondaga County eBird checklists?** No local bird dataset was found in the inspected project folders.

Start at the [Onondaga County eBird bar chart](https://ebird.org/barchart?r=US-NY-067). eBird's [chart documentation](https://support.ebird.org/en/support/solutions/articles/48001255130-ebird-bar-charts-and-graphs) describes the **Download Histogram Data** option and frequencies calculated from complete checklists. Select a fixed multi-year window and download the data; a Cornell account may be needed for some views/downloads. The county chart itself was not retrievable through the research browser, so no species ranking is asserted here.

Proposed analysis: compare reporting curves, require adequate checklist effort and a nontrivial peak, and define a reporting window before ranking it. A narrow peak can suggest a seasonal visitor; it does not prove absence at other times. Show three to five supported examples rather than a sweeping biological claim. Use county geography in the title unless you obtain city-specific checklists. If ranking window lengths is too sensitive to effort, the easier version is “When are three selected migrant birds most often reported in Onondaga County?”

## Source catalog

Local paths are inspected copies, not synchronization links. Keep shared data where it is, and save the exact extract used for a post in that post's `analysis/` folder with the source URL, coverage dates, download date, definitions, and filtering rules. External links were checked at the documentation, metadata, or download level indicated below. Not every archive item or dataset row has been validated.

<a id="trees"></a>
### Tree inventory

**Local, inspected:** [Oak Street source CSV](1_oak_street_trees/analysis/Syracuse_Tree_Data_7832308158023752279.csv), 55,676 records. Fields include `SPP_COM`, `SPP_BOT`, `DBH`, `PLANTDATE`, `STREET`, `CENSUSTRAC`, and coordinates. Verified labels include 1,027 Planting site records, 1,092 Stump records, 282 Stump - Do not grind, and 5 Stump Ash; these are not living-tree species. `PLANTDATE` includes season/year strings and placeholders such as N/A and To Be Determined. Only one inventory snapshot was verified. Public starting point: [city Urban Forest Master Plan and inventory link](https://www.syr.gov/Departments/Parks-Recreation/Urban-Forest-Master-Plan). Confirm the CSV's collection date before claiming current conditions.

<a id="streets"></a>
### Street centerlines

**Local, inspected:** [city streets](C:/Users/samie/syracuse_public/data/public_raw/streets_city.geojson), 5,650 features, and [NYS Syracuse streets](C:/Users/samie/syracuse_public/data/public_raw/streets_nys_syracuse.geojson), 8,755 features. Relevant fields include `FULLNAME`, `NAME`, `TYPE`, `CITYST_ID`; NYS has `CompleteStreetName`, road class, direction and level fields. Public sources: [city Streets service](https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Streets/FeatureServer/0) and [NYS Streets and Addresses](https://gis.ny.gov/streets-addresses). A feature is usually a segment, not a whole street. Check clipping, connectivity, bridges, name normalization, and measurement projection. Raw Web Mercator lengths should not be treated as accurate local ground distances.

<a id="boundary"></a>
### Municipal boundaries and center calculations

**Public source verified; exact analysis extract still needed:** [NYS Civil Boundaries service](https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Civil_Boundaries/MapServer) has municipal polygons. Census place boundaries are another option through the [TIGER guide](https://www.census.gov/programs-surveys/geography/guidance/tiger-data-products-guide.html). Select Syracuse city, document vintage, and choose full-area versus land-only definitions. A place coordinate is not necessarily an area centroid. Border-road stories need roads on both sides of the city line.

<a id="parcels"></a>
### Parcels and recorded building ages

**Local, inspected:** [2025 Q3 parcels](C:/Users/samie/syracuse_public/data/public_raw/parcels_2025_q3.geojson), 41,263 features, with `TAX_ID`, `yr_built`, `LU_parcel`, `n_ResUnits`, `NHOOD`, geometry, and area fields. [Source layer metadata](https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Syracuse_Parcel_Map_%282025_Q3%29_view/FeatureServer/0) was verified. The property-atlas project also contains a local SQLite database, but the GeoJSON is a simpler starting point. Parcel polygons are not surveyed legal boundaries, building footprints, or complete building histories. Check missing/round years. Neighborhood labels are source-specific.

<a id="footprints"></a>
### Building footprints

**Public service verified:** [NYS Building Footprints](https://gisservices.its.ny.gov/arcgis/rest/services/BuildingFootprints/MapServer). The service identifies Onondaga coverage based on 2022 imagery; use its county-overview download field or query the footprint layer. Not downloaded for this review. Footprints indicate outlines, not floor area, entrance direction, garage use, age, or current occupancy. Join the local parcel file for candidate uses and inspect imagery for finalists.

<a id="imagery"></a>
### Aerial imagery

**Public access route verified:** [NYS ShareGIS](https://gis.ny.gov/shareGIS/) provides orthophotography and related geographic services. Select Onondaga coverage and record the acquisition date and whether imagery is leaf-on. Access to imagery does not mean tree crowns, sidewalks, parking areas, or storefronts are already digitized; manual tracing may be the actual work. Check the service's attribution and reuse terms before publishing imagery.

<a id="canopy"></a>
### Tree canopy

**Public tract data verified:** [Syracuse Canopy Cover by Census Tract](https://services.arcgis.com/uDTUpUPbk8X8mXwl/ArcGIS/rest/services/Syracuse_Canopy_Cover_by_Census_Tract/FeatureServer) returned 55 records and includes `GEOID` and `tree_canop`. Its metadata credits Google Environmental Insights Explorer 2022; the ArcGIS item owner is `CommGeog`, not the city open-data account. Confirm derivation, units, boundaries and reuse terms with the publisher before analysis: the service description mentions percentages while the layer name says area. Example values were 42.7 and 19.4, not independently validated percentages.

The [city's 2010 canopy-map metadata](https://www.arcgis.com/sharing/rest/content/items/0360b905a2754b0ca894f580564ae38e/info/metadata/metadata.xml?format=default&output=html) describes canopy and six other land-cover classes. Its map currently references a vector-tile layer; a current downloadable citywide crown-polygon layer was not verified. Use dated imagery plus a bounded manual audit for present street-side, playground, or parking-lot comparisons. Do not equate inventory tree points with canopy area or actual shade.

<a id="botany"></a>
### Species traits and native status

**Public reference route verified:** [USDA PLANTS downloads](https://plants.sc.egov.usda.gov/downloads) and [PLANTS field documentation](https://plants.usda.gov/assets/docs/PLANTS_Help_Document_2022.pdf). Start from botanical names in the local inventory. Evergreen behavior, local native range, fruit/nut traits, and cultivar ambiguity need a reviewed crosswalk; the downloadable checklist alone does not answer every trait question. Use regional botanical references to confirm central New York status. Species-level fruit traits do not establish safe harvesting at a particular site.

<a id="birds"></a>
### Bird reports and migration

**Public tools documented; no local extract inspected.** Use the DC058 plan above. For checklist-level effort, first-report work, or city-boundary filtering, consult Cornell's [eBird data access instructions](https://support.ebird.org/en/support/solutions/articles/48000838205-download-ebird-data). Full research downloads require the appropriate account/request process and can be large. The [Onondaga BirdCast dashboard](https://dashboard.birdcast.org/region/US-NY-067) is useful for radar-based migration context; it is not a substitute for a species-specific local reporting history. Observation frequency, abundance, and absence are different quantities.

<a id="weather"></a>
### Airport weather and snow

**Local, inspected:** [Hancock daily weather](C:/Users/samie/syracuse_public/data/public_raw/noaa_syracuse_hancock_daily.json), 8,249 observations from January 1, 2004 through August 1, 2026, station `USW00014771`. Includes daily maximum/minimum temperature in C, precipitation/snowfall/snow depth in mm, and quality/trace flags. The file has no wind series. For longer records or refreshes, use [NOAA GHCN Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily) and [NWS Binghamton's Syracuse climate tools](https://www.weather.gov/bgm/climateMain). Station-specific and composite Syracuse-area records are different series. All-time claims require the appropriate full record, not just this local extract.

<a id="gauges"></a>
### Nearby stations, wind and storm dates

**Public access route verified:** [NOAA daily station search](https://www.ncei.noaa.gov/cdo-web/search?datasetid=GHCND) and [NWS climate help](https://www.weather.gov/bgm/helpclimate). Select nearby stations with the needed variable and overlapping dates. Not every station measures snowfall, snow depth, or wind. Windstorm stories need actual wind records or documented storm events, not an inference from cold or rain. Record units, observation-time differences, missing days, and station moves. No new multi-station extract was downloaded in this review.

<a id="cityline"></a>
### Cityline requests

**Local, inspected:** [request CSV](C:/Users/samie/seeclickfix/data/raw/SYRCityline_Requests_%282021-Present%29.csv), 116,143 rows with creation dates June 17, 2021-February 27, 2025. Despite the filename, this is not a current extract. Fields include ID, category/type, summary/description, local created/acknowledged/closed times, minutes to close, and coordinates. Later [2026 Parquet collection files](C:/Users/samie/seeclickfix/collection-2026/data/parquet) exist, but their city filtering, completeness, and deduplication were not checked here. Refresh through the [city open-data program](https://www.syr.gov/Departments/API/API-Initiatives/Open-Data) or the project's documented pipeline. A snapshot does not provide a verified reopen log, duplicate flags, or category-administration history. Remove personal details from published examples.

<a id="cityhelp"></a>
### Cityline status meanings

**Official starting point verified:** [SYRCityline](https://www.syr.gov/cityline) links the public request system and tracking information. Inspect public issue histories for examples and locate an explicit status definition; if the meaning remains ambiguous, ask the city before asserting it. Neither a closed timestamp nor elapsed minutes proves a physical repair. This review did not establish an authoritative citywide closure-reason dictionary.

<a id="paving"></a>
### Road projects and pavement

**Local files verified:** [source inventory](C:/Users/samie/syracuse_public/modernization/source_inventory.csv) points to `data/public_raw/pavement_2020.geojson` through `pavement_2025.geojson`, road-reconstruction files for 2022-2027, and `road_resurfacing_2026.geojson`; those GeoJSON files exist. They include plans as well as dated ratings. Use the inventory's source URLs and inspect completion/status fields before counting completed work. Road-rating changes are not direct evidence of paving dates. Project count, distinct segments, lane miles, and centerline miles are different measures.

<a id="water"></a>
### Water-main breaks

**Local, inspected:** [2004-2019 break events](C:/Users/samie/syracuse_public/data/public_raw/breaks_2004_2019.geojson), 3,042 features, plus verified local 2021 and 2022 files. The [source inventory](C:/Users/samie/syracuse_public/modernization/source_inventory.csv) documents schema differences, sparse 2019 coverage, and missing complete confirmed-event layers for 2020 and 2023-2026. Distinguish confirmed breaks, customer water complaints, and service interruptions. Do not present the available years as an uninterrupted current series.

<a id="traffic"></a>
### Traffic counts

**Local file verified:** [NYSDOT Syracuse-area counts](C:/Users/samie/syracuse_public/data/public_raw/nysdot_aadt_syracuse_bbox.geojson), with [NYSDOT source service](https://gis.dot.ny.gov/hostingny/rest/services/Roadways/Traffic_Monitoring/FeatureServer/1) recorded in the local inventory. Coverage favors larger roads and years differ. Inspect count year, direction, geometry, and annual-average definitions before joining. An unmeasured residential street is not proven low-traffic. Cycling comfort also depends on speed, width, separation, and crossings.

<a id="transit"></a>
### Centro transit schedules

**Download verified:** [Centro's GTFS ZIP](https://www.centro.org/CentroGTFS/CentroGTFS.zip) was downloaded into memory and opened successfully on September 18, 2026. It contains stops, routes, trips, stop times, shapes, transfers, calendars, and exceptions. `feed_info.txt` gives September 7, 2026-February 28, 2027 as its date range. Save a fresh copy for a post; the review did not persist it. Use actual service dates and exceptions. GTFS supports scheduled service comparisons, not actual arrival reliability, ridership, shelter information, or a historical service archive.

<a id="osm"></a>
### Walking, cycling and place leads

**Public extraction route verified:** [OpenStreetMap Overpass API documentation](https://wiki.openstreetmap.org/wiki/Overpass_API). Extract Syracuse and a buffer beyond the boundary, including roads, paths, steps, crossings, barriers, and needed amenities. Save the query and extraction date. OSM is a community-maintained source, not a complete sidewalk/bench/business inventory. Untagged is unknown, not absent. Routing requires a connected, mode-appropriate graph and field verification of important gaps. Attribute OpenStreetMap contributors and follow its data terms.

<a id="terrain"></a>
### Elevation

**Public source verified:** [USGS 3D Elevation Program](https://www.usgs.gov/3d-elevation-program). Download a DEM covering the study area and note resolution and vertical units. The water-project source inventory mentions earlier street samples, but those sample CSVs were not found at their listed paths in this review; do not assume they are ready locally. Terrain rasters do not capture all bridges, stairs, tree/building obstructions, or sidewalk surfaces. Check short steep segments in the field.

<a id="parks"></a>
### Parks and recreation facilities

**Official listings verified:** [Syracuse park finder](https://www.syr.gov/Living/Our-Community/Parks-Recreation-Youth-Services/Visit-Our-Parks) and [city recreation directory](https://syracuse.recdesk.com/Community/Home). Listings provide candidate parks, activities, and some stated acreages. A consistent park-boundary/entrance dataset was not downloaded; obtain official polygons or carefully trace and validate selected sites. Include nearby county/town parks where the question needs them. Public restrooms, gates, fountains, playground equipment, and actual opening dates require separate verification.

<a id="libraries"></a>
### Library locations and hours

**Official directory verified:** [OCPL locations](https://www.onlib.org/locations), linking city and suburban branches. Compile branch addresses, entrances, posted hours, and exceptions for a specific date. A short hours comparison can be transcribed manually. A branch's location does not define its legal service area or prove who uses it. Geocode and verify entrances before routing. Do not assume all independent county libraries follow one schedule.

<a id="librarystats"></a>
### Monthly library statistics

**Local, inspected:** [for-analysis-current.csv](C:/Users/samie/Projects/ocpl_stats/summaries/data/for-analysis-current.csv), 351 rows covering January 2023-March 2026, with Year, MonthNum, Type, Branch Value, Central Value, and Total Value. Nine types include visits, physical/digital circulation, programs, attendance, reference, and computer use. These are **Central versus aggregate branches**, not one row per individual branch. `branch-stats.csv` is also aggregated. Use complete months and check metric definitions and whether a measure is system-wide. Do not claim individual-branch rankings or daily heatmaps from these files.

<a id="libraryreports"></a>
### Longer-term library reports

**Official report catalog verified:** [OCPL reports](https://www.onlib.org/learn/about-ocpl/reports) links community reports and system-report archives. A ten-year comparison requires opening the relevant reports and checking consistent definitions and library coverage; the required decade-long table was not assembled here. For a quick story, use the local 2023-onward monthly data and label that shorter period. Public aggregate reports are preferable to assuming board-related files are cleared for publication.

<a id="events"></a>
### Library event calendars

**Public starting point verified:** OCPL links its [public event calendar](https://onlib-central.libcal.com/) from its location/navigation pages. Independent libraries may use separate calendars. Your [OCPL API project's README](C:/Users/samie/Projects/ocpl_library_api/README.md) documents `/events` and `/events/sources`, but the local server and current event completeness were not tested here. Save a dated public-listing snapshot, normalize categories, and verify free/registration/age requirements. A live calendar is not a guaranteed historical attendance archive.

<a id="libraryhistory"></a>
### Library and local directory history

**Archive route verified:** OCPL's [Syracuse research guide](https://www.onlib.org/sites/default/files/LhgArticle.pdf) describes city directories and local-history holdings; the [locations directory](https://www.onlib.org/locations) links branch pages and histories. Begin with documented branch histories, then locate dated addresses in directories. Expect manual research; a complete machine-readable branch-movement or historical-lending dataset was not found.

<a id="census"></a>
### Population, housing and Census geography

**Public sources verified:** [2024 ACS five-year dataset catalog](https://api.census.gov/data/2024/acs/acs5.html), [Census table browser](https://data.census.gov/table?d=ACS+5-Year+Estimates+Data+Profiles), and [TIGER products](https://www.census.gov/programs-surveys/geography/guidance/tiger-data-products-guide.html). Use 2020 decennial block counts for small-area population allocation, ACS five-year estimates for tract characteristics, and matching boundary/relationship files for comparisons. Choose named tables and confirm their universe and variables before downloading. The API may require a Census key; browser table downloads are an alternative. City-level cached data below are not a verified tract-level dataset. Preserve margins of error, denominator counts, vintage, and geographic definitions.

<a id="peers"></a>
### Existing city/peer Census work

**Local, inspected:** [Below the Line summary](../projects/below-the-line/data/summary.json) identifies 2024 as current and 2019 as baseline. [The source project](C:/Users/samie/Projects/belowtheline/data/raw) contains cached city ACS requests across 2011-2024, including Syracuse and peer cities. Reuse only variables actually present; the cache is not every ACS table and is not tract-level coverage. For city comparisons, match vintages, definitions, and peer-selection rules. See [Census sources](#census) for missing measures.

<a id="lodes"></a>
### Jobs and commuting geography

**Public download route verified:** [Census LEHD/LODES](https://lehd.ces.census.gov/) and its [download tool](https://lehd.ces.census.gov/php/inc_lodesDownloadTool.php). Select New York and the same available year across residence, workplace, and origin-destination files; include cross-state flows if needed. No local extract was verified. These data describe covered jobs/worker locations, not all daytime inhabitants, students, shopping trips, or exact travel times. Do not join aggregate LODES distances to ACS times as though they represented the same individuals.

<a id="names"></a>
### First-name reference

**Public download verified in documentation:** [SSA name files](https://www.ssa.gov/oact/babynames/limits.html). Use an explicit year range and frequency threshold when matching local street names. Rare names may be suppressed; first-name matches do not establish the street's naming origin. Presidential surnames can be a small hand-reviewed comparison list without any new data service.

<a id="food"></a>
### Food businesses and everyday destinations

**Public dataset route verified:** [NYS Food Service Establishment: Last Inspection](https://health.data.ny.gov/Health/Food-Service-Establishment-Last-Inspection/cnih-y5dw). Filter to Onondaga County and the actual study boundary; check current status, establishment type, and duplicate inspection-related records. This is not a complete live restaurant, retail-grocery, cuisine, or opening-hours directory. Cross-check company/store websites and current menus; use OSM only as additional leads. No commercial places API or paid data is required for a bounded manually verified sample.

<a id="history"></a>
### Historical maps, directories, advertisements and records

**Primary archives verified:** [Library of Congress Sanborn map navigator](https://labs.loc.gov/work/experiments/sanborn-navigator/) and [a Syracuse Sanborn item](https://www.loc.gov/item/sanborn06296_009/); OCPL's [local research guide](https://www.onlib.org/sites/default/files/LhgArticle.pdf); and [OHA's research center](https://www.cnyhistory.org/visit/research-center/). These establish research routes, not proof that a particular vanished bridge, proposal, or address record has been found. Start with digitized dated maps and directory pages for a small area. The OHA page still displays a construction/closure notice with an expected summer-2026 completion; current access must be confirmed rather than assumed. Fees, appointments, item restrictions, and reproduction permission may apply. If one candidate has no supporting record, choose another documented example within the same pitch.

<a id="photos"></a>
### Historical photographs

**Online collection verified:** [Daily Life in 20th Century Onondaga County](https://nyheritage.org/collections/daily-life-20th-century-onondaga-county), contributed by OHA. Search for dated, located images with stable identifying landmarks; verify the item's caption and publication terms. Additional OHA materials may require staff access and permission. Oldest, unchanged, and surviving-same-tree claims require evidence beyond resemblance. Save item identifiers and exact captions with your analysis notes.

<a id="field"></a>
### Your own field observations

**Data must be created.** Use a simple dated log: location, route/sample boundary, feature counted, observation time, photograph reference, accessibility status, and uncertainty. Define categories before comparing places. A small field survey is often the easiest honest path for clocks, shade, benches, doors, crossing details, and storefronts. Start from public access and distinguish absence from inability to see. No existing complete inventory was verified for these features; do not describe a map-service search as a census.

<a id="survey"></a>
### Reader questions, perceptions and interviews

**Data must be collected.** Create a short voluntary prompt or map-pin exercise, record the question wording and collection dates, and report the number and selection of respondents. No existing representative Syracuse perception dataset was found. A reader poll is a convenience sample. For DC007, collect a perceived-center guess separately from optional geolocation; otherwise the app produces distance/bearing data but cannot answer the perception question. Do not publish precise visitor locations as a side effect of the compass feature.

## Revisions made in this review

The 365 permanent IDs are preserved. Revised pitches replace unsupported assumptions or narrow an overbroad claim. The table keeps the original wording so the change is reversible and future sources can revive it. Remaining Research/Manual ideas are intentionally retained where a bounded, documented investigation is feasible; they are not labeled easy or already available.

| ID | Original pitch | Revised pitch | Why |
| --- | --- | --- | --- |
| DC039 | Which streets gained the most recorded trees between inventory updates? | Which streets have the most trees with a recorded recent planting year? | Only one snapshot was verified; N/A and To Be Determined are not dates. |
| DC040 | Where have recorded tree losses been concentrated? | Where are stumps concentrated in the tree inventory? | Stumps are a snapshot, not a dated removal history or a rate of loss. |
| DC043 | Which residential blocks have the most canopy? | Which mapped Census tracts have the most recorded tree canopy? | This is a 2022-derived community layer, not a verified current city inventory; its metadata need reconciliation. |
| DC044 | Where does tree canopy change most abruptly across a street? | How different is tree cover on opposite sides of one Syracuse street? | A small measured comparison is feasible; a complete current citywide crown layer was not verified. |
| DC050 | Which neighborhood has the most evergreen canopy? | Where are inventoried evergreen trees concentrated? | Tree counts cannot establish evergreen canopy area; keep unknown species separate. |
| DC056 | Which publicly accessible tree appears in the oldest photograph? | Can we match a tree in one dated Syracuse photograph to the same location today? | Identity and survival need evidence; an absolute oldest-photo claim is not supportable from a partial archive. |
| DC058 | Which birds appear only briefly during migration? | Which birds have the shortest seasonal reporting windows in Onondaga County eBird checklists? | Use reporting frequency and adequate checklist effort; absence of reports is not biological absence. |
| DC059 | How does the reported first spring bird sighting vary by year? | When does spring reporting of a chosen migrant bird increase each year? | Define a sustained reporting threshold; an isolated first sighting is effort-sensitive. |
| DC089 | How much of the street network gets a recorded plow pass overnight? | What share of snow-related Cityline requests arrives overnight? | Historical plow-pass coverage was not found in the inspected files; request timing is a different measurable question. |
| DC092 | What is its narrowest buildable-looking parcel? | Which mapped Syracuse parcels are the narrowest? | Geometry alone cannot establish legal buildability. |
| DC106 | Where did construction nearly stop for an entire decade? | Which decades are least represented in the current property age records? | No complete historic construction flow was found; demolition and bad dates distort the apparent lull. |
| DC171 | Which parks are named after people most residents cannot identify? | Who were three people whose names survive in Syracuse parks? | No resident-recognition survey was found; avoid claiming what most residents know. |
| DC198 | Which branches have the most visits per open hour? | How has Central Library's share of recorded visits changed? | The inspected files aggregate branches and lack individual-branch open hours. |
| DC199 | Which branches host the most programs per open day? | How does attendance per recorded program compare between Central and the branches? | Individual branch rankings and per-open-day rates are unsupported by these summaries. |
| DC210 | What does one year of library activity look like as a calendar? | What does a year of library activity look like month by month? | The verified source is monthly; it cannot support a daily activity heatmap. |
| DC227 | What is the oldest continuously used restaurant location? | How far back can we trace restaurant use at one Syracuse address? | Continuous operation and an absolute oldest claim need records not located in this review. |
| DC256 | What was Syracuse’s busiest corner in different eras? | Which selected corners had the most listed businesses in two historical city directories? | No comparable historical footfall series found; directory businesses are not pedestrian counts. |
| DC266 | What is the oldest surviving advertisement painted on a wall? | How old is one surviving painted advertisement in Syracuse? | No complete inventory can establish the oldest surviving sign; bound the investigation. |
| DC283 | What changed when a request category was added or renamed? | When do request labels first appear or disappear in the Cityline extract? | No verified category change log was found; first observed does not mean newly created. |
| DC284 | How many requests are follow-ups or duplicates? | How many Cityline reports look like possible repeats under a stated rule? | The snapshot has no verified duplicate/follow-up flag; proximity alone is insufficient. |
| DC293 | How often are requests reopened, if the system records that? | Which Cityline categories have the largest share without a recorded closure date? | No reopen-event history was verified in the snapshot; missing closure means no recorded closure at extraction. |
| DC307 | How different are the daytime and residential populations? | Where are workplace jobs concentrated compared with resident workers? | LODES measures covered employment, not everyone present during the day. |
| DC310 | How much does the student calendar affect neighborhood population estimates? | Where do college enrollment and group quarters complicate neighborhood population comparisons? | No monthly student-population series was found; ACS cannot measure term-time changes. |
| DC320 | Where do short commute distances coexist with long commute times? | How do reported commute times differ between transit riders and drivers? | No linked distance/time microdata were verified; aggregate LODES and ACS are not the same trips. |
| DC325 | How much of Syracuse is road surface? | How many miles of mapped public streets fit inside Syracuse? | Centerlines lack dependable width; they cannot measure road-surface acreage. |

## Keeping this useful

When starting a post, open its data note, obtain the actual extract, confirm the required fields and coverage, and save the provenance in `analysis/`. Update the assessment when you discover a better source. The companion `datacuse-data-readiness.json` is a structured snapshot for future filtering or a tracker interface; it is not automatically synchronized with handwritten edits. Publication status stays in `datacuse-story-tracker.csv`. This review does not publish or unpublish any stories.
