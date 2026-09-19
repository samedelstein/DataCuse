# DC002 calculation and candidate review

Calculated September 19, 2026. This is a reproducible GIS analysis and draft, not a surveyed street-length record. The conventional shortest-city-block question is **not resolved**: the shortest network link lies within an intersection area. The draft explicitly distinguishes that from a real block.

## Inputs and scope

- `streets_nys_current.geojson`: 20,652 features fetched by object ID from the [NYS Streets service](https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS_Streets/FeatureServer/0), for the envelope -76.25,42.97,-76.04,43.13. Complete expected-vs-returned object-ID equality checked. Source metadata, query and download timestamp are in `nys_metadata.json` and `nys_provenance.json`.
- `syracuse_boundary.geojson`: NAME='Syracuse' in the [NYS Cities layer](https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Civil_Boundaries/MapServer/4). Publication is March 2026; the Syracuse feature's DATEMOD is older. Boundary accuracy does not support interpreting tiny city-line slivers as streets.
- Keep active surface streets with public jurisdiction codes 01,02,03,12,13. Eligible FCCs are the A20–A49 families plus A61/A62. Exclude unnamed/unknown placeholders, route-only names, and names explicitly containing DRIVEWAY, RAMP, ENTRANCE or EXIT even if their road class is inconsistent. All exclusions are counted in `results.json`. Source attributes establish this operational public-street inventory; ownership was not independently surveyed.
- Build the network within a 500-metre city buffer, before clipping. Include a name in the city inventory only if a qualifying segment has positive length inside the boundary and at least one incorporated-municipality field says Syracuse. Clip lengths to the municipal polygon, preserve full buffered component length, and flag any outside-city portion. Buffered lengths are not the full out-of-town length of long roads.
- Wholly-contained components are the primary whole-street competition. Boundary-crossing components and their clipped lengths remain in the diagnostic CSV. This prevents fractional-foot boundary fragments from winning. Names crossing the border can still enter the name-length competition.

## Names

Sam clarified during drafting that the primary name ranking counts **total letters in the full expanded street name**, including street type and directional words. Normalize case/whitespace and count alphabetic characters, excluding spaces and punctuation. No qualifying names contain digits in this snapshot. Use separate NYS StreetName and expanded CLDXF_PostType fields only for the secondary base/suffix comparison. Unique complete names are the counting unit. Keep supplied spelling rather than attempting historical name corrections. No blanket deletion of directional words embedded in a base-name field.

- 1,192 unique qualifying complete names.
- Primary result: **Fay Road and Lea Lane**, 7 letters each in their complete expanded names; Oak Street has 9.
- Secondary base-only minimum: 3 letters, shared by 12 complete names (11 distinct base names because Oak occurs twice).
- All ties: Amy Street, Ash Street, Elk Street, Elm Street, Fay Road, Ida Avenue, Lea Lane, May Avenue, New Street, Oak Place, Oak Street, Roe Avenue.
- Shortest complete expanded names: Fay Road and Lea Lane, 7 characters excluding the space.
- 232/1,192 (19.46%) have expanded street-type text longer than the base name.
- Largest suffix-minus-base gap: Erie Boulevard East and Erie Boulevard West, 9 minus 4 = 5 letters. Directional qualifiers remain in complete-name identity, but not in the suffix/base comparison.

## Geometry and network calculation

Transform geographic coordinates to NAD83 / UTM zone 18N (EPSG:26918). Measure polylines in metres, then divide by 0.3048 for feet. Never rank by the city's legacy LENGTH or Web Mercator Shape__Length.

Remove exact normalized duplicate geometry/name pairs. Node compatible geometric crossings and endpoint-on-line contacts, respecting endpoint Z levels; interior Z is used only when both endpoint levels agree. The current eligible network has no ambiguous grade crossings flagged by this procedure. It cannot detect a wrong source elevation attribute. Splitting conserves total input length to within 1 mm across the network.

Join same-name edges through intermediate degree-two nodes when no other eligible name joins. A block candidate ends at another eligible street name, a same-name branch or a dead end; only candidates with other named streets at both distinct endpoint nodes enter the intersection-to-intersection table. This is a topological definition: it does not automatically merge a pair of offset junctions into one physical intersection, or collapse divided carriageways into a single road. Source network segments themselves are preserved separately.

Whole connected streets use same-complete-name connected components and the length of their geometric union. Exact overlaps are counted once; parallel carriageways remain separate geometry. This limitation does not affect the single-centerline Spring Lane leader. It can affect long divided streets and those secondary totals should not be treated as fully reviewed street-length measurements.

## Findings and review

| Candidate | Calculated length | Review decision |
| --- | ---: | --- |
| Spaulding Avenue, NYS ID 800049637 | 7.34 ft | Shortest eligible raw feature in the city. Not a complete intersection-to-intersection block; it disappears into a longer block when artificial splits are joined. |
| South Avenue between Hovey and Marginal, ID 800051053 | 15.71 ft | Shortest computed intersection-to-intersection link. The 2022 aerial shows staggered street approaches within one junction area. Retain as a literal mapped-link result; **do not call it a verified conventional block**. |
| Rugby Road, IDs 504326410 and 504326416 | 54.19 and 60.30 ft | Isolated named arcs around the Sedgwick Drive traffic island. Retain in the diagnostic component table; exclude from whole-street candidates after aerial review. |
| Spring Lane, ID 477429983 | 64.37 ft | Shortest remaining wholly-contained connected street candidate; one component and one source feature. Aerial shows a real short access lane/dead end off Pond Lane. Both state and city data contain this street. |
| Meade Court, ID 477437062 | 71.30 ft | Next state-data whole-street candidate. Not independently field verified. |
| Page Avenue, ID 482659670 | 75.06 ft | Third state-data whole-street candidate. |
| Oak Street | 7,578.66 ft / 1.435 mi | One connected component in the city, illustrating why short individual pieces do not imply a short whole street. |

Spring Lane is drawn at approximately 75.0 feet in the older city dataset, versus 64.4 feet in NYS. This difference is large compared with the gap to Meade Court, so **do not present the 64-foot figure or the real-world champion as settled by survey**. Spring Lane leads the NYS ranking and the eligible city names' whole-length ranking, but the inventories differ (the older city layer does not include Meade Court under that name). The draft attributes the ranking specifically to state data and states both Spring Lane measurements.

Independent existence corroboration: the [Greater Syracuse Land Bank's April 2021 sale resolution, page 5](https://syracuselandbank.org/wp-content/uploads/2021/05/2021_09.pdf) describes rear access to 620 Carbon Street via Spring Lane. This supports the lane's existence and use, not its exact legal extent, present condition, or length.

Other aerial-reviewed short links on Lemoyne Avenue, Strathmore Drive, Devine Street and West Marcellus Street also show complex junction or divided-road geometry. These checks reinforce why a conventional shortest-block winner cannot be obtained merely by discarding the single smallest row. `junction_screen.py` only prioritizes review candidates; it is not a validated final block classifier. No arbitrary minimum-length cutoff was imposed to manufacture a winner.

Review imagery and source URLs are in `../images/*_review.png` and `imagery_sources.json`. Images are **2022**, not live street observations. Source lines are overlaid for visual inspection; they do not establish pavement edges or legal right-of-way.

## Validation and reproducibility

Run using Python 3 with shapely, pyproj, networkx and matplotlib. The isolated environment is `analysis/.venv` (ignored by git). `requirements.txt` records versions.

1. `python analysis/download_nys.py` refreshes state streets and boundary (network required).
2. `python analysis/calculate.py` writes the rankings and summary.
3. `python analysis/validate.py` checks a synthetic at-grade crossing, a grade-separated crossing, split-length conservation, and real-data sensitivity at 0, 0.5 and 1 metre endpoint tolerances.
4. `python analysis/compare_city.py` applies a diagnostic comparison to the older city layer. Its unavailable elevation attributes mean it cannot validate grade-separated blocks.
5. `python analysis/junction_screen.py` prepares a manual review queue; `python analysis/review_maps.py` downloads aerial imagery for selected candidates. `python analysis/make_story_figure.py` builds the two-panel story figure from cached images.

Validation passed: all three tolerances give the same 1,192 names, 232 suffix-longer names, South Avenue 15.71-foot mapped link, and Spring Lane 64.37-foot whole-street candidate after the documented traffic-island exclusions. Detailed results: `validation.json`.

Output CSVs include `name_rankings.csv`, `suffix_longer_than_name.csv`, `raw_segment_rankings.csv`, `block_rankings.csv`, `all_block_candidates.csv`, `connected_street_rankings.csv`, `whole_street_candidates.csv`, and `whole_name_rankings.csv`. The block CSV is a **candidate** table, not a list of aerial-verified city blocks. The whole-name table additionally sums disconnected components, while the connected table keeps them separate. CSV outputs were not edited by hand.

Before a definitive “shortest street” publication: verify the legal/public extent and present endpoints of Spring Lane and Meade Court; measure the finalists. Before a “shortest conventional block” claim: define physical junction footprints and review the smaller candidate links under that rule. The current draft is publishable only as the expressly qualified map-data finding it describes.
