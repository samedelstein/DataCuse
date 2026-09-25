# Syracuse population center: scope and method

## Definition and vintage

A population-weighted mean of geometric block polygon centroids for Syracuse city, New York (place 3673000), using April 1, 2020 Census population and matching January 1, 2020 Census boundaries. This is a DataCuse calculation, not a published Census official Syracuse center. It is a mean balance point, not a median center, an optimal travel destination, or the most densely populated location.

The total includes group quarters under Census residence rules. Race and age comparisons are separate complete partitions, not race-by-age intersections. Race uses DHC P3 single-race-alone categories and Two or More Races. Ethnicity uses P4, independently of race. P12 male and female age cells are summed into under 18, 18–34, 35–64 and 65+; every age belongs to exactly one band.

## Inputs and reproduction

`download.py` downloads the Census2020 TIGERweb layer 26 Syracuse polygon and layer 10 candidate blocks using its bounding box. `provenance.json` holds exact URLs, UTC timestamps and SHA-256 hashes. `calculate.py` projects polygons into NAD83 UTM zone 18N (EPSG:26918), selects blocks whose representative points are covered by the city, confirms each selected block lies entirely inside it, and places each block's population at its polygon's area centroid. Sum(population * x) / sum(population), and similarly y, gives the mean.

`download_demographics.py` reads the official New York `ny2020.dhc.zip` using HTTP byte ranges. The geography member plus segments 5 (P1, P3, P4) and 6 (P12) are decompressed and checked against ZIP CRC32 and size. The large complete state members are cached only in the system temp folder `datacuse-dhc`, not committed. The official XLSX layouts determine field order, not guessed column offsets. Full geography rows and full segment rows for 2,109 matching blocks and the separate city total are retained here, along with the extracted analysis CSV, API variable metadata, field layouts, ZIP directory and SHA-256 provenance. Geography uses summary level 100 for blocks and 160 for the city, geographic component 00; GEOID and city PLACE codes are checked.

Run from the repository root:

```powershell
python content/6_population_center/analysis/download.py
& C:/Users/samie/syracuse_public/.venv-modern/Scripts/python.exe content/6_population_center/analysis/calculate.py
python content/6_population_center/analysis/download_demographics.py
& C:/Users/samie/syracuse_public/.venv-modern/Scripts/python.exe content/6_population_center/analysis/calculate_demographics.py
python content/6_population_center/analysis/review_location.py
python content/6_population_center/analysis/make_group_graphics.py
```

The calculation interpreter has Shapely 2.1.1 and pyproj 3.7.1. The standard `python` used for graphics has Pillow; downloads use only Python's standard library. Graphics read saved results. `make_group_graphics.py` also regenerates both overview graphics. Age and race maps share an identical extent and north-up orientation; proportional circles in the overview map encode population by area. Group-center symbols have equal size, with population printed separately.

## Results and checks

- Exactly 2,109 blocks tile the place polygon; the union's symmetric-difference area is zero. 1,614 blocks have population; 495 have zero population. No partially overlapping blocks. One invalid candidate polygon was repaired with a negligible area change; repair details are retained in results.json.
- 148,620 residents exactly match the Census place population. The DHC and TIGERweb population match for every block, including zeros.
- All race, age and ethnicity partitions sum to the population of each block. Each group's summed block counts separately match its published city total. Recombining each partition's centers with group population weights reproduces the overall center to less than 0.000001 metre.
- Overall result: 43.0437419656 N, -76.1409864534 W. These digits support reproduction, not a claim of street-address accuracy.
- Distance from post 5's municipal-area centroid: 406.65 metres (0.25268 mile), bearing 33.38 degrees. Using this matching 2020 Census boundary changes the area centroid by only 0.79 metre versus post 5.
- Independent local-origin accumulation reproduces the overall mean. Using EPSG:5070 equal-area polygon centroids shifts it 0.08 metre; Census internal points shift it 0.88 metre. Group internal-point shifts range up to 8.35 metres. These checks are not confidence intervals and do not measure Census disclosure-avoidance error.
- All group coordinates, fields, counts, distances and sensitivity checks are saved in `group_results.json`. The 67-person Native Hawaiian and Other Pacific Islander alone category is especially sensitive; one block contains 20 of its published residents. It is disclosed rather than silently omitted or treated as equally stable.

## Location check

NYS street geometry places the overall point about 38 metres from Sarah Loguen Street and 53 metres from Harrison Street. The independent city street layer agrees on the corridor, though the older city data labels the Sarah Loguen segment CD RD. An [Upstate source](https://www.upstate.edu/news/articles/2004/04-centro-bus-service-be-rerouted-harrison-street.php) names the Sarah Loguen/Harrison junction. Official NYS 2022 aerial imagery was inspected and saved with its bounding box, URL and hash. The point appears on a large roof southwest of that junction; the story makes no building-identity, current-condition, public-access or visitor-destination claim.

## Interpretation limits

Every resident of a block is approximated at the same block centroid, regardless of within-block age or race distribution. Seventeen populated blocks have a geometric centroid outside their own concave polygon. The total calculation's conservative weighted maximum block-radius bound is about 202 metres under an assumption that everyone is inside their recorded block; it is not an expected error or confidence interval and does not include disclosure-avoidance uncertainty.

The Census modifies public counts to protect confidentiality. Small populations and detailed local counts warrant particular caution; no error bars or statistical significance claims are available for these derived centers. See the [DHC technical documentation](https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf), chapter 4. Group population sizes are shown, no small group is ranked as a more important population, and geographic displacement is not presented as a measure of segregation. Similar centers can hide very different spatial distributions. No causal explanations of race or age geography are inferred from a point.

This analysis is a 2020 snapshot, not a current estimate or a historical change comparison. The broad age bands were chosen before inspecting results. The exact locations of individuals are neither available nor inferred.
