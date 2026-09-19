# DC002: Syracuse's shortest street, three ways

Scope agreed in Sam's September 19, 2026 request. This expands idea 2 to include the shortest-name question also listed as DC017. No winners have been established yet.

## Data

- [City Streets service](https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Streets/FeatureServer/0): verified 5,650 features on September 19, 2026. Separate FULLNAME, NAME, TYPE, PREFIX and SUFFIX fields support the naming analysis. In this schema TYPE is the street type (ST, RD, etc.); do not assume the field called SUFFIX contains that type.
- Project download: `../analysis/syracuse_streets_shapefile.zip`, with the five constituent files in `../analysis/syracuse_streets/`. This is a conversion from the city's service, retaining selected street attributes. The full original attribute set is in `../analysis/streets_city.geojson`; provenance and service metadata are saved beside it. Reproduce using `python analysis/prepare_streets.py` from the project root (requires pyshp).
- The export retains the full service extent with no public-road, name, or municipal-boundary filter. It is an input dataset, not the final eligible-street inventory.
- [NYS Streets and Addresses](https://gis.ny.gov/streets-addresses) provides a [statewide street shapefile ZIP](https://gisdata.ny.gov/GISData/State/Streets/Streets.shp.zip) and a [filterable street layer](https://data.gis.ny.gov/datasets/nys-streets/explore). Use the regular Streets dataset, not the simplified labeling version. The page lists July 2026 downloadable files and describes a twice-monthly service update schedule. The county download table higher on that page is for address points, not streets.
- NYS is the preferred current cross-check: the city layer's published metadata shows a data-last-edit date of March 29, 2023. A fresh download does not make those streets current. Check changes, closures and names against NYS, current imagery and signs before publication.
- Existing comparison extract: `C:/Users/samie/syracuse_public/data/public_raw/streets_nys_syracuse.geojson`. Its spatial selection and vintage still need auditing.

## 1. Shortest name

Updated per Sam's clarification during drafting: the primary measure is **total letters in the full, spelled-out street name**, including directional words and street type. Exclude spaces and punctuation; do not compare abbreviations such as ST and BLVD. Report all ties. Keep base-name letter count as a secondary descriptive column for the suffix comparison. No eligible full names in the analyzed snapshot contain digits.

Side question: where is the street type longer than the base name? Expand TYPE with a documented crosswalk (ST -> STREET, RD -> ROAD, AVE -> AVENUE, BLVD -> BOULEVARD). Compare expanded type character count to base-name character count. Report the difference and optionally the ratio. Oak Street illustrates the rule: OAK has 3 letters and STREET has 6; this is an illustration, not a claim that Oak wins.

Count each unique complete street name once, not once per GIS segment. Keep Oak Street distinct from Oak Avenue, and preserve directional qualifiers in the identity. Blank/unnamed records and unresolved abbreviations require separate review. Check full spelling against NYS because the city's NAME field allows only 20 characters.

## 2. Shortest block

Measure along the street centerline between two real, at-grade intersections. Reconstruct blocks by merging artificial feature splits and splitting at genuine intersections missing from the source segmentation. Geometry vertices are not intersections. A GIS row can be a block, part of one, or several blocks.

Keep intersection-to-dead-end stretches as a separately labeled category because Sam's primary definition is block to block. Avoid treating bridges, boundary clips, median connectors, ramps and divided carriageways as tiny winning blocks. Verify the shortest candidates on a map and document both endpoint streets.

## 3. Shortest whole connected street

Group segments by normalized complete name, including directional qualifiers and street type. Within each name, find connected components using endpoint geometry and grade/level information where available. Sum the unique centerline length of all constituent blocks in each component. Do not use straight-line distance between its endpoints.

Thus Oak Street's short individual blocks become one longer connected street. Disconnected pieces with the same name remain separate components; also report their combined length and component count as a secondary name-level measure. If a name has multiple components, label a winner as a connected section and show the other pieces rather than implying it is the entire named street. Review branches and divided roads to avoid counting both carriageways as twice the street's length.

## Common geographic and measurement rules

Recommended primary scope: named public streets within Syracuse city limits. Use a documented current municipal boundary. Compute connectivity on roads extending beyond the boundary before clipping and retain a boundary-crossing flag. Exclude artificial city-line fragments from the shortest-block competition. For the whole-street table, label boundary-crossing totals as length inside Syracuse and show wholly contained streets separately.

The supplied shapefile is WGS84 (EPSG:4326), in degrees. Reproject to a suitable local system such as NAD83 / UTM zone 18N (EPSG:26918, metres), or calculate ellipsoidal lengths. Convert metres to feet for display. Do not rank using raw Web Mercator Shape__Length or the legacy LENGTH field without verifying units and meaning.

Set and record any endpoint snapping tolerance; inspect candidate connectivity at exact, 0.5-metre and 1-metre tolerances so a tiny gap or aggressive snap does not determine the winner. Grade-separated crossings must remain disconnected. Source node IDs may help but need verification against geometry.

## Planned outputs

1. Unique-name table with base/full name counts, expanded street type, suffix-minus-name count and ties.
2. Verified block table with length, endpoint streets and constituent source feature IDs.
3. Connected-street table with total length, component count, block count and boundary flags.
4. A map showing the leading candidates for each physical-length definition, plus a review log explaining exclusions.

Calculation completed September 19, 2026: see `../analysis/methodology.md`, the CSV rankings and `shortest_street_draft.md`. Fay Road and Lea Lane tie at seven total letters. Spring Lane leads the qualified whole-street data ranking. The shortest mapped junction link is not a verified conventional block; the methodology documents that unresolved distinction.
