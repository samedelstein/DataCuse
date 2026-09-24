# DC004: continuous roads and whole-path straightness

The article now leads with the whole-path straightness investigation added at the user's request. The original continuation analysis remains reproducible below; its four-change leaders are explicitly **not** straight-line winners. See the whole-path section after the initial method.

## Scope and source

Syracuse municipal limits, active named public surface streets. Inputs are copies of the September 19, 2026 NYS Streets and boundary snapshots used in posts 2 and 3. `nys_provenance.json` preserves the original URLs, download timestamp and query envelope; `nys_metadata.json` and `boundary_metadata.json` preserve metadata. SHA-256 hashes in `results.json` identify both GeoJSON inputs. No new street download was substituted.

Sources: [NYS Streets](https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS_Streets/FeatureServer/0), [city boundaries](https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Civil_Boundaries/MapServer/4), [NYS Streets program description](https://gis.ny.gov/streets-addresses), checked September 20, 2026. The program describes centerlines compiled from imagery and attributed with names and routes. Those attributes do not establish sign wording or an intuitive straight-through route.

Eligibility uses the prior posts' helper, copied locally as `street_network.py`: public jurisdiction codes 01, 02, 03, 12, 13; FCC A20–A49 plus A61/A62; Status Active; named street rather than unknown/unnamed or route-only designation. Exclude explicit DRIVEWAY, RAMP, ENTRANCE and EXIT words. These classifications are an inventory definition, not an ownership investigation. Deduplicate identical name/geometry pairs. Normalize case and whitespace only; retain full names and directional words. No minimum name-run length is imposed. Returning to a previous name counts again.

## Reproducible continuation rule

1. Project to NAD83 / UTM zone 18N (EPSG:26918). Use 500 m of external context while finding compatible contacts, then clip geometry to the city boundary before constructing the ranked chains. Outside portions cannot connect two city fragments.
2. Split linework at geometrical intersections and endpoint-on-line contacts within 0.5 m when recorded elevations agree. Do not infer an interior elevation for a line whose endpoint Z levels differ. The baseline encountered zero ambiguous grade contacts. Endpoint grouping uses the same 0.5 m tolerance and recorded elevation.
3. For each end of a piece, take an outward vector toward the point 10 m along it, or its opposite end if shorter. For an incoming and outgoing piece, 0° is straight, 90° a right-angle turn. This chord is an approach estimate, not a steering measurement. Tiny pieces use their full length; the approach does not reach through the next piece.
4. At every graph connection, identify each piece's single straightest other piece. Join only mutual choices with deviation ≤30°. Exact angle ties within 1e-7 degrees stop the chain. Name agreement does not affect pairing. Each piece end has at most one continuation, producing unbranched chains independent of travel direction.
5. Traverse every piece once across the resulting chains. No repeated-edge wandering can inflate the count. Count transitions between consecutive full recorded names. Closed loops are saved separately, rather than getting an arbitrary starting name; the only baseline loop is Village Drive with zero changes. Rank open chains by changes. Mileage merely orders rows with equal counts; it does **not** break the reported tie.

The angle limit applies at all resulting piece joins, including degree-two connections that may just be source segmentation. It does **not** limit curvature within a piece, cumulative direction change along a road, or distance from a straight line. A road can bend considerably between joins. This makes results dependent on source segmentation as well as the explicit parameters. Mutual-straightest pairing is one defensible definition, not an exhaustive search for every route whose turns could be argued to be small. Routing is undirected: one-way restrictions, turn prohibitions and closures are not applied.

## Findings and sensitivity

Baseline: 6,224 pieces, 1,376 open chains, one excluded same-name loop. Two chains tie at four transitions:

| Full name sequence | Miles | Angles at name changes |
| --- | ---: | --- |
| Crawford Avenue → Broad Street → Berkeley Drive → Ostrom Avenue → Comstock Place | 2.90010 | 26.778°, 23.727°, 0.412°, 0.695° |
| State Fair Boulevard → Spencer Street → West Kirkpatrick Street → West Court Street → Court Street | 2.49798 | 12.998°, 16.638°, 8.483°, 0.312° |

`chain_rankings.csv` contains every baseline open chain; `results.json` contains the leading 20, transitions, IDs, locations and sensitivity winners. `top_chains.geojson` contains each of those chains' geometry with source IDs and sequence order.

| Angle / approach | Maximum | Leaders |
| --- | ---: | --- |
| 15° / 10 m | 3 | McChesney Park Drive → Pond Street → North Townsend Street → South Townsend Street; West Fayette Street → Tennyson Avenue → Burnet Park Drive → Tennyson Avenue |
| 20° / 10 m | 4 | State Fair–Court |
| 30° / 10 m | 4 | Both baseline leaders |
| 45° / 10 m | 4 | Both baseline leaders |
| 30° / 5 m | 4 | Both baseline leaders |
| 30° / 20 m | 4 | State Fair–Court |

`validate.py` independently rebuilds the graph with 0 m and 1 m tolerances. Both tied leading name sequences and the maximum of four survive. It asserts the count equals name runs minus one, all joins satisfy the threshold, and no chain repeats an edge. `validation.json` saves the full outcomes. These checks assess numerical stability under these changes; they do not prove the chosen rule is the only interpretation of straight.

Full-name choice is consequential: West Court → Court is a direction-only change. The article states this next to the chain. Alternate name normalization is not the published comparison; a different normalization would require a new ranking.

## Reality check and limits

`review_candidates.py` downloads an 800×800 north-up NYS 2022 aerial around each of the eight leading name transitions and overlays the saved chain geometry. Exact export URLs, bounds, retrieval timestamps and source IDs are in `imagery_sources.json`. All eight overlays were visually inspected on September 20, 2026; `review/all_transitions.jpg` is the contact sheet.

- Crawford → Broad: a curved residential connection; its 26.8° local join is visibly not a promise of an overall straight road.
- Broad → Berkeley: the line bends through an offset alignment. This is particularly sensitive to approach distance.
- Berkeley → Ostrom: the local continuation is almost straight at the name boundary; the road curves farther south.
- Ostrom → Comstock Place: the name transition is almost straight, then Comstock bends west **within** its piece. This distinction is explicitly in the article.
- State Fair → Spencer and Spencer → West Kirkpatrick: visible through-pavement connections at junctions; the latter changes overall heading.
- West Kirkpatrick → West Court: the name boundary lies along the curved bridge approach, not at an obvious conventional intersection. The recorded bridge elevation is retained.
- West Court → Court: the centerline continues near the highway crossing; the full-name distinction includes losing West.

The aerials support physical mapped connections in 2022. They do not verify 2026 accessibility or names on signs. No field visit, sign survey or legal driving-route validation was performed. The maxima are for the chosen inventory and continuation procedure. Short name inserts and classification errors elsewhere can influence the ranking; preserve the conditional wording.

## Graphics and review

`make_graphics.py` reads `results.json` and `top_chains.geojson`. All lines, lengths, angles and counts derive from those outputs. Background linework is NYS Streets; no generated imagery or third-party basemap tiles are used. Maps use equal horizontal and vertical projected scale and north up. Rust marks the city boundary. The comparison bars share a zero baseline and 100 pixels per change. Source notes and prose carry the caveat even at small image sizes.

The canonical article remains `status: draft`. Publication has not been requested. Reproduction commands are in the post README.

## Whole-path straightness: the second comparison

`straightness.py` rebuilds the same 30° chains, assembles ordered geometries, then assesses consecutive name-run windows **within** them. This retains one clear network-continuity definition while adding a separate, global geometric test. It does not rebrand a low junction angle as proof that the entire route is straight.

For a candidate containing two or more consecutive name runs, retain exactly 50 m of the first run before its name change, all intervening runs, and exactly 50 m of the final run beyond the last change. Reject a candidate if its first or last run is shorter than 50 m. Intermediate names have no minimum length in the baseline, and repeated names still count as new transitions. This equal lead-in/lead-out prevents shrinking the test to just the junction point. These are **defined windows**, not whole named streets or longest possible straight extents. They are not arbitrary endpoints optimized after seeing the result.

Draw the finite straight segment between each candidate's endpoints. Require:

1. Centerline length / straight endpoint distance ≤1.01: at most 1% extra distance.
2. Every centerline vertex within 10 m of the finite endpoint segment.

Checking vertices is sufficient for the continuous polyline's maximum distance to that convex segment: distance is convex along each straight polyline edge, so its maximum occurs at an endpoint. Finite-segment distance also catches excursions past an endpoint, rather than using an infinite-line measure that could reward backtracking. Report both metrics. Neither is a local steering-angle measurement; small bends within the tolerance remain possible.

Assembling source pieces includes actual sub-metre endpoint gaps as straight connectors so lengths are conserved. The two original full-chain leaders have zero such gaps. Whole-chain scores are saved for all 166 open chains with at least one name change; zero-change chains cannot contribute to the requested maximum.

### Results

There are 218 baseline 50 m windows; 95 pass both straightness limits. Of the 218, eleven have at least three name changes; none of those pass. **The maximum is two changes, with two literal NYS-data candidates tied.** Mileage or number of distinct names does not break that tie.

| Candidate | Road length | Endpoint distance | Extra distance | Maximum departure |
| --- | ---: | ---: | ---: | ---: |
| Monticello Drive South → Monticello Drive North → Springbrook Avenue | 686.803 m | 685.429 m | 0.2004% | 7.125 m |
| Tennyson Avenue → Burnet Park Drive → Tennyson Avenue | 143.872 m | 143.847 m | 0.0177% | 1.274 m |

Monticello's middle name covers 586.803 m, plus the two 50 m end pieces. Its South/North name boundary is at East Seneca Turnpike, and the Springbrook name begins at East Glen Avenue. Directions count. The Tennyson candidate has just 43.872 m carrying Burnet Park Drive in the state inventory; this candidate has two changes but only two distinct names.

The complete original Crawford–Comstock chain is 4,667.253 m along pavement versus 1,573.584 m between endpoints (2.966×). Its maximum distance from that finite endpoint segment is 1,618.279 m. State Fair–Court is 4,020.117 m versus 3,184.067 m (1.26257×), with maximum departure 1,061.125 m. Their continuity is clearly not global straightness.

### Sensitivity and search limits

`straightness_results.json` and `straightness_candidates.csv` save all 642 windows from 25, 50 and 100 m end extensions, including failures. `straightness_geometry.geojson` saves each measured polyline. The smaller/larger extension cases have 237 and 187 windows respectively. The maximum stays at two changes under all tested variations, but candidate membership changes:

- 25 m extensions, 10 m sideways limit: eight tied sequences; these include Berkeley–Ostrom–Comstock and McChesney Park–Pond–North Townsend. Their shorter endpoint pieces avoid farther curves that fail the baseline.
- 100 m extensions, 10 m sideways limit: the same two named baseline candidates still tie.
- 50 m extensions, **5 m** sideways limit: Monticello fails; only the disputed Tennyson sequence has two changes.
- 50 m extensions, **20 m** sideways limit: five candidates have two changes, including Renwick–Martin Luther King East–Martin Luther King West, the South West Street arterial sequence, and West Scott–Scott–Genesee Park.
- Requiring every name run to last at least 25 m retains both baseline candidates. Requiring 50 m removes the 43.872 m Burnet Park insert, leaving Monticello. This is a sensitivity check, **not** an excuse to erase the literal tie.

The maximum is **among windows within the mutually straightest chains**. Alternate branches discarded by the pairing rule, different source segmentation, other endpoint placements, or an optimization over all possible routes were not exhaustively searched. Extending a failed window can rotate its chord or change its distance ratio, so failure at one set of endpoints does not prove every possible extension fails. The article states the bounded search and avoids claiming a universal citywide straight-road record.

### Independent name and imagery checks

`review_straight.py` compares the two candidates with the saved City of Syracuse Streets layer from post 2, downloaded September 19, 2026. `city_name_check.json` records its source URL, full-file SHA-256, midpoint samples and nearby feature matches. `city_comparison_extract.geojson` saves all selected city features here. Distances below are from NYS run midpoints to the nearest city line; cross streets overlapping the 10 m buffer are not silently treated as through-street name matches.

- Monticello South, Monticello North and Springbrook midpoints match the corresponding city names, at 0.71, 0.67 and 0.80 m distance. City FIDs 5239, 5039 and 5296.
- The three Tennyson–Burnet–Tennyson midpoints all map to **Tennyson Avenue** in the city layer, at 0.89, 1.02 and 0.35 m. City FIDs 2250, 2388 and 3113. Burnet Park Drive has nearby entering/exiting geometry; this does not settle whether its name should temporarily replace Tennyson on the through line.

Four additional dated aerial overlays were visually inspected in `review/straight_transitions.jpg`. Monticello's two crossings show connected, approximately straight pavement. Tennyson's two inventory name boundaries lie along the same straight through pavement at the Burnet Park junction. Imagery establishes geometry, not the correct posted name. Thus **Monticello is the better corroborated example, while the state-data tie is retained and the Tennyson naming discrepancy remains unresolved**. Exact requests and imagery dates are in `straight_imagery_sources.json`.

### Validation and revised graphics

`validate_straight.py` verifies a straight line and a right-angle elbow, then independently recomputes length, finite-segment departure and distance ratio for every one of the 642 saved geographic windows using scalar vector projection, after reprojection to UTM. It checks run-length conservation, transition counts, baseline ties and sensitivity maxima. All checks pass; see `straightness_validation.json`.

`make_straight_graphics.py` adds three evidence graphics: whole continuous chains versus their endpoint chords; Monticello's true north-up geometry plus a separate offset plot; and Tennyson's state names compared with city-map midpoint checks. The offset plot explicitly exaggerates sideways variation and shows the ±10 m limit. Geographic maps retain equal coordinate scale. The revised article references these three graphics; the original three continuation graphics remain available as supporting material and are not referenced for publication.
