# DC008: definitions, evidence and limits

## Question

Which Syracuse intersection has the most streets meeting at it? Two different counts are reported:

1. **Approaches (arms):** separate surface-street corridors extending away from a single junction. Opposite sides of a continuing street count separately. Split carriageways belonging to one approach are consolidated after review. An ordinary four-way crossing of two streets has four arms and two names. This is not a count of lanes, legal entry directions or turn permissions.
2. **Distinct full names:** unique normalized NYS CompleteStreetName values incident on that junction. Case and whitespace are normalized; suffixes and directional words are retained. East/West portions can therefore count as different full names. This is a literal source-name count, not a claim about how residents group streets.

The main finding is six clearly distinct arms at North Salina Street/Lodi Street/Kirkpatrick Street. It has three full names, each appearing twice. The largest full-name count in the primary scan is four, shared by five state-map nodes.

## Scope and inputs

NYS Streets and Syracuse boundary snapshots downloaded September 19, 2026, reused from post 4. The state street download contains 20,652 source features covering Syracuse and its surroundings. Input paths and SHA-256 hashes, original URLs and selection bounds are in `provenance.json`. The 5,650-feature city reference download is separately documented in post 4's `streets_provenance.json`; its reported data edit timestamp is older than the state layer. Layer edit timestamps are not dates of individual field observations.

Eligibility is inherited from the documented post 4 topology helper: active, named, documented public-jurisdiction surface streets; jurisdiction codes 01, 02, 03, 12, 13; FCC A20–A49 and A61–A62. Exclude private/undocumented jurisdiction, freeway/ramp/service/driveway/path classes, unknown names, explicit driveway/ramp/entrance/exit names, and route-only designations. Exact duplicate name/geometry pairs are removed. Roads within a 500-metre city buffer are retained before graph construction; only junction centers inside the city polygon enter the ranking. No artificial endpoints are introduced at the city boundary.

This yields 7,371 eligible input line parts, with full source properties retained by the helper. The result is about named public surface streets, not every possible access road, footpath or grade-separated highway movement.

## Graph construction and counts

Calculate in NAD83 / UTM zone 18N (EPSG:26918). Split same-level geometric intersections and compatible endpoint-on-line contacts. Preserve FromZlev and ToZlev; connections require matching levels. Interior elevation on a segment changing level is not inferred. All original source level fields are populated; eligible endpoint levels are 14,300 at level 0 and 442 at level 1. No ambiguous interior-level crossing was encountered in these runs. This still depends on source elevation attributes being correct.

Primary endpoint tolerance: 1 metre. Endpoints within tolerance and on the same level are joined using connected components. This can chain together points, so the maximum cluster diameter is recorded, not assumed equal to tolerance. Internal links whose two ends collapse into the same node are excluded from outward-arm counts. Other degree-two continuation points are not intersections. Count both outward incidents and distinct full names at each node with at least three outward incidents.

The primary scan contains 2,910 qualifying nodes. Only two have six or more mapped outward lines: the seven-line Hiawatha/North Salina/Lodi node and the six-line North Salina/Lodi/Kirkpatrick node. All five nodes with four names and both high-arm leaders were manually inspected (six distinct locations in total).

Outputs: `node_rankings.json` includes every primary qualifying node, names, arms, exact coordinates, source IDs, bearings and cluster diameter; `eligible_noded_roads.geojson` retains the corresponding graph edge geometries and IDs. `sensitivity.json` records candidate lists and count distributions for 0, 1, 3, 5, 10 and 20 metres.

## Manual review

`review_candidates.py` saves raw 2022 NYS orthophotography and annotated copies for the six locations. Exact service requests, map bounds, retrieval timestamps and hashes are in `imagery_sources.json`. The aerials establish the visible 2022 layout, not current lane operations.

- **North Salina/Lodi/Kirkpatrick:** six separate corridors visible; three names each continue through. NYS node 4826, older city node 661. The two coordinate estimates are 6.54 metres apart. Each source independently identifies six arms and the same three names. No bridge or ramp is needed to create this six-way result.
- **Hiawatha East/Hiawatha West/North Salina/Lodi:** seven state lines are 2 + 2 + 2 + 1. Review consolidates the paired carriageways/lanes for each of Hiawatha East, Hiawatha West and North Salina, giving four street approaches. City node 389 independently has four arms and four names. The nearby freeway and ramps are excluded from this surface-street count. Do not promote the state line count to a seven-way physical-junction claim.
- **Euclid/Kimber/Edgemont/Enfield:** five physical approaches; four names agree across sources.
- **Demong/Manor/Radcliffe/Salt Springs:** four physical approaches; four names agree across sources.
- **South Salina/Harrison/East Onondaga/West Onondaga:** five approaches; four full names agree across sources, counting East and West separately.
- **Seymour/Shonnard/West Adams/West Onondaga:** five state arms, four state names. The older city topology represents the immediate junction differently. The article keeps it in the literal state-data tie list and discloses the discrepancy; it is not described as independently confirmed by both maps.

## Independent and sensitivity checks

`city_crosscheck.py` independently uses the city's FNODE_/TNODE_ IDs for surface-street classes, without borrowing state nodes. It finds 2,635 city junctions with at least three arms. Its unique highest arm count is six at North Salina/Lodi/Kirkpatrick; full names peak at four. Differences in the city and state four-name leader lists show that drawing conventions and vintage can affect which physical complexes collapse into one node.

`validate.py` separately groups the original state feature endpoints by coordinates and level, with no inferred interior crossings, and confirms the two leading locations' arms and names. Its maximums are also seven mapped lines and four full names. It checks the city six-way match and the unchanged pair of leading state candidates from exact joins through 5 metres.

Increasing tolerance to 10 or 20 metres creates additional high-degree candidates around divided boulevards and close, staggered junctions. At 20 metres, some connected endpoint clusters span more than 60 metres. The 20-metre run reaches eight outward mapped lines around parts of West Street and divided Meadowbrook Drive. It is an audit of a broader merging rule, not an accepted eight-way junction finding. Those additional clusters were not all field- or aerial-adjudicated; the article does not claim a universal record across all ways of grouping junction complexes. All tested tolerances retain a maximum of four full names, but the tied locations can change.

The strongest conclusion is a clear, independently corroborated six-way junction under a single-junction definition. Current redesigns, road closures and street signs have not been field-checked. Counts do not establish traffic volume, delay, danger, or legal turning movements.

## Graphics

Three graphics use saved computed values and true projected geometry. The six-way map numbers each arm in clockwise bearing order and uses one color per name. The Hiawatha figure overlays state lines on the exact georeferenced 2022 image and shows the reviewed grouping. The two four-name examples use the same ground scale. Nearby same-name segments continue the highlights so data segmentation does not look like a street endpoint. North arrows and ground scale bars are included. `graphics_audit.json` records the chosen IDs and number-to-street mapping.

Source and reproduction links are in the article and README. Story folder 7 corresponds to idea DC008; folder number and idea number are independent.
