# Datacuse idea bank

Saved September 18, 2026. Original collection: 365 pitches in twelve topic groups.

These are questions to investigate, not established findings. Each now has a reviewed data route; some still require collection or archival research. Headlines can become more declarative once the evidence earns it. This is an idea bank, not a commitment to publish daily.

The original numbering is preserved below. Number 1 corresponds to permanent tracker ID DC001, number 365 to DC365. IDs remain stable when a pitch is refined; the data guide preserves original wording for revised pitches. Future additions begin at DC366 in a separate additions section.

See the [editorial playbook](datacuse-editorial-playbook.md) for the approach and templates, and the [story tracker](datacuse-story-tracker.csv) for progress.

## Data availability review — September 18, 2026

All 365 ideas have a data route and first step below. **Local** = main inputs inspected on this computer; **Public** = public access route verified, extraction may still be needed; **Mixed** = local inputs plus another source; **Manual** = collect observations or responses; **Research** = locate specific archival records. Effort is **Quick**, **Setup**, or **Project**, not a guaranteed completion time.

See the [data guide](datacuse-data-guide.md) for source paths, downloads, access limitations, the migration-bird plan, and Sam's center-of-Syracuse app brief. The guide also explains all 25 pitch revisions. Data readiness does not change publication status.

## Streets, names, and the small absurdities of geography

1. Does Oak Street actually have any oak trees?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Reuse the Oak Street notebook and published article; whole-word match SPP_COM against STREET.

     **Watch:** Already published; do not count planting sites or stumps as living trees.
2. What is Syracuse’s shortest named street?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Dissolve contiguous segments by complete name; rank projected lengths within a stated city extent.

     **Watch:** A tiny GIS segment is not necessarily an entire named street.
3. What is its longest street—and where does it really end?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Compare connected named-street lengths and inspect where the name or municipal coverage ends.

     **Watch:** State whether length stops at the city line; check split carriageways.
4. Which street changes names the most without making you turn?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Follow connected centerlines using a stated turn-angle threshold; count name changes.

     **Watch:** Straight-through continuity is a rule you choose, not a stored fact.
5. Where is Syracuse’s geographic center?

     **Data:** Public. **Effort:** Quick. **Sources:** [boundary](datacuse-data-guide.md#boundary).

     **Start:** Download the Syracuse municipal polygon and calculate its area-weighted centroid.

     **Watch:** Choose land-only versus full municipal area; centroid differs from visual center.
6. Where is its population center?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Weight 2020 populated Census blocks by population and calculate a center.

     **Watch:** Block-centroid approximation and decennial vintage must be stated.
7. What location do residents think is the center?

     **Data:** Manual. **Effort:** Project. **Sources:** [survey](datacuse-data-guide.md#survey), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Ask readers to place a perceived-center pin; compare with a defined geographic center. Build the requested companion app showing direction and miles to that center.

     **Watch:** The app needs a documented center coordinate; visitors' locations alone do not measure where they think the center is.

     **Sam's app idea:** Build a companion web app that uses the visitor's location to show which direction to face the center of Syracuse and how many miles away it is. [Saved feature brief](datacuse-data-guide.md#dc007-companion-app).
8. Which intersection has the most streets meeting at it?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Build an intersection graph and count distinct named arms at each node.

     **Watch:** Bridges, ramps, divided roads, and near-coincident nodes need manual review.
9. What is Syracuse’s sharpest street corner?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Measure angles between connected street approaches and inspect the smallest candidates.

     **Watch:** Define the distance over which direction is measured; exclude geometry artifacts.
10. Which street comes closest to making a complete circle?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Score closed or nearly closed named streets for circularity and compare maps.

     **Watch:** State the closure tolerance; do not silently combine differently named roads.
11. How many streets are named after trees?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets), [trees](datacuse-data-guide.md#trees).

     **Start:** Make an explicit tree-name dictionary from the inventory and count unique street names.

     **Watch:** A name match does not prove the street was named for that tree.
12. Which presidents have streets—and which got skipped?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Compare unique street names with a manually documented presidential surname list.

     **Watch:** Shared surnames are matches, not verified naming origins.
13. Which numbered streets are missing from the sequence?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Extract numbered street names, normalize ordinals, and identify gaps.

     **Watch:** Keep avenue and street sequences separate; missing numbers may never have existed.
14. How many street names are also people’s first names?

     **Data:** Mixed. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets), [names](datacuse-data-guide.md#names).

     **Start:** Match street-name tokens with the SSA first-name files using a stated frequency cutoff.

     **Watch:** Surname overlaps and omitted rare names affect the result.
15. What is the most common street-name ending: Street, Avenue, or something else?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Normalize TYPE or PostType and count unique complete street names by suffix.

     **Watch:** Report names rather than segment counts; abbreviations need a crosswalk.
16. Which street has the longest name?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Rank complete street-name character counts, then check the longest on the map.

     **Watch:** Choose whether spaces, directions, and suffixes count.
17. Which street has the shortest name?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Rank the shortest complete names using the same naming rules as DC016.

     **Watch:** Separate a short base name from a short full signed name.
18. What is the longest perfectly straight stretch of street?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Search connected paths whose headings remain within a defined tolerance.

     **Watch:** Perfectly straight is not meaningful at arbitrary GIS precision; state tolerance.
19. Which street wanders farthest from a straight line?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Compare connected street length with endpoint straight-line distance.

     **Watch:** Loops and disconnected pieces need separate treatment.
20. Where do two almost-identical street names threaten to confuse visitors?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Rank similar name pairs using spelling distance; map the nearest confusing pairs.

     **Watch:** Similarity suggests potential confusion, not evidence that visitors were confused.
21. Which named street consists of disconnected pieces?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Group by complete name and count disconnected components.

     **Watch:** Check gaps caused by clipping, bridges, and bad geometry.
22. How many dead ends does Syracuse have?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Count degree-one nodes after removing clipped boundary ends and private/service segments.

     **Watch:** The chosen public-street definition determines the count.
23. Which dead end almost connects to another street?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Find nearby dead-end endpoints, then inspect the shortest gaps.

     **Watch:** Nearby endpoints may be separated by fences, slopes, or private land.
24. Where does an ordinary street abruptly become a staircase or path?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Query mapped steps and footways connecting streets; visit a few candidates.

     **Watch:** OSM is incomplete; label the verified examples rather than a citywide census.
25. Which intersection has the biggest mismatch between its streets’ sizes?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [imagery](datacuse-data-guide.md#imagery).

     **Start:** Screen intersecting roads by class; measure widths for a small finalist set from imagery.

     **Watch:** Road classification is not measured pavement width.
26. How many city streets cross the municipal boundary?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Intersect the NYS street network with the city boundary and count unique public crossings.

     **Watch:** Use roads extending beyond the boundary, not a city-clipped extract alone.
27. Where can you leave Syracuse and reenter without turning?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Trace named connected roads that cross the boundary at least twice.

     **Watch:** Check turns and name changes; define what counts as staying on the same road.
28. Which street follows the city boundary the longest?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Measure named-street length within a fixed distance of the municipal line.

     **Watch:** Near the line is not legally on the line; disclose the buffer.
29. Are directional street names actually pointing in their advertised directions?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Compare endpoint bearings with North/South/East/West name tokens.

     **Watch:** Directions sometimes encode address systems rather than a road's physical bearing.
30. Which Syracuse street name deserves an origin story?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [streets](datacuse-data-guide.md#streets).

     **Start:** Choose one unusual name and search dated directories, maps, and naming records.

     **Watch:** No complete name-origin database found; document one supported origin.

## Trees, plants, and urban wildlife

31. What is the most common public-tree species in Syracuse?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Count cleaned SPP_COM or SPP_BOT categories among actual trees.

     **Watch:** The file also includes stumps and planting sites; exclude them.
32. Where is the rarest species in the tree inventory?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Find valid species with the fewest inventory records and map one example.

     **Watch:** Rarest in this inventory is not rarest in Syracuse or ecologically endangered.
33. Which public tree has no nearby relatives of its species?

     **Data:** Local. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Calculate each tree's nearest same-species neighbor and rank isolation.

     **Watch:** Exclude unknown species and validate coordinates; inventory coverage limits the claim.
34. Which block has the greatest variety of street trees?

     **Data:** Local. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [streets](datacuse-data-guide.md#streets).

     **Start:** Assign trees to consistently defined street blocks; count species per block.

     **Watch:** Report tree counts too; species richness rises with sample size.
35. Which block is almost entirely one tree species?

     **Data:** Local. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [streets](datacuse-data-guide.md#streets).

     **Start:** Compute the dominant species share on blocks with a minimum tree count.

     **Watch:** Do not rank a one-tree block above a meaningful monoculture.
36. Where are the largest recorded street-tree trunks?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Rank numeric DBH values after screening non-tree records and obvious errors.

     **Watch:** Confirm DBH units and field-check outliers; recorded size is not current size.
37. How much of the public-tree inventory has no identified species?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Count Unknown, unknown tree, blanks, and other unresolved species labels.

     **Watch:** Treat stumps and planting sites separately from unidentified living trees.
38. Where are there planting sites but no trees?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Filter the verified Planting site label and map recorded sites by street.

     **Watch:** An inventory planting site is not proof the space is still empty or ready today.
39. Which streets have the most trees with a recorded recent planting year?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Parse season/year strings in PLANTDATE; compare recorded planting cohorts by street.

     **Watch:** Only one snapshot was verified; N/A and To Be Determined are not dates.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
40. Where are stumps concentrated in the tree inventory?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Map SPP_COM labels Stump, Stump Ash, and Stump - Do not grind.

     **Watch:** Stumps are a snapshot, not a dated removal history or a rate of loss.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
41. Do tree-named streets have more trees than other streets?

     **Data:** Local. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [streets](datacuse-data-guide.md#streets).

     **Start:** Compare inventory trees per street mile for tree-named and other streets.

     **Watch:** Normalize by length and coverage; the association does not explain naming.
42. How green is Green Street?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees), [streets](datacuse-data-guide.md#streets).

     **Start:** Count inventory trees per mile on Green Street and compare similar streets.

     **Watch:** This measures recorded public trees, not all canopy or greenness.
43. Which mapped Census tracts have the most recorded tree canopy?

     **Data:** Public. **Effort:** Setup. **Sources:** [canopy](datacuse-data-guide.md#canopy), [census](datacuse-data-guide.md#census).

     **Start:** Use the public tract canopy layer after confirming its units and derivation; rank mapped Census tracts.

     **Watch:** This is a 2022-derived community layer, not a verified current city inventory; its metadata need reconciliation.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
44. How different is tree cover on opposite sides of one Syracuse street?

     **Data:** Manual. **Effort:** Setup. **Sources:** [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Pick two contrasting street sides; trace visible crowns in dated leaf-on imagery and verify on foot.

     **Watch:** A small measured comparison is feasible; a complete current citywide crown layer was not verified.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
45. Which bus stops have natural shade?

     **Data:** Manual. **Effort:** Setup. **Sources:** [transit](datacuse-data-guide.md#transit), [field](datacuse-data-guide.md#field).

     **Start:** Sample a defined set of bus stops and log shade at the same season and time of day.

     **Watch:** Nearby trees do not establish actual shade; repeat if comparing times.
46. Which playgrounds have shade around their equipment?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [field](datacuse-data-guide.md#field).

     **Start:** Photograph and classify shade over equipment at a small set of playgrounds.

     **Watch:** Record time and season; shaded park area is not shaded equipment.
47. How much shade surrounds Syracuse school buildings?

     **Data:** Manual. **Effort:** Setup. **Sources:** [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Trace visible tree crowns around selected school buildings and validate a sample.

     **Watch:** Use a declared buffer and image date; do not label this measured classroom cooling.
48. Which parking lots have the most tree cover?

     **Data:** Manual. **Effort:** Setup. **Sources:** [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Digitize a selected set of parking lots and crown cover using dated imagery.

     **Watch:** Sampling is easier than a complete lot inventory; distinguish lot shade from nearby trees.
49. Can you walk a mile while staying mostly under trees?

     **Data:** Manual. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Use tree locations to suggest a route, then walk it and log shaded segments.

     **Watch:** Tree points alone cannot establish continuous shade or public access.
50. Where are inventoried evergreen trees concentrated?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [botany](datacuse-data-guide.md#botany), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Classify verified species as evergreen and group inventory points by documented neighborhood geography.

     **Watch:** Tree counts cannot establish evergreen canopy area; keep unknown species separate.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
51. Where might fall color last longest, based on tree species?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [botany](datacuse-data-guide.md#botany), [field](datacuse-data-guide.md#field).

     **Start:** Create a cautious species-based fall-color route and record actual color on repeat visits.

     **Watch:** Species suggests timing; weather and individual condition prevent a firm duration prediction.
52. How many public trees produce edible fruit or nuts?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [botany](datacuse-data-guide.md#botany).

     **Start:** Join a reviewed list of fruit/nut-producing species to the tree inventory.

     **Watch:** Species traits do not establish safe edibility at a particular street location.
53. Which street trees are native to this region?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [botany](datacuse-data-guide.md#botany).

     **Start:** Match botanical names to regional native-status references, recording unresolved cultivars.

     **Watch:** Native to North America is not the same as native to central New York.
54. What would Syracuse lose if its most common tree species disappeared?

     **Data:** Local. **Effort:** Quick. **Sources:** [trees](datacuse-data-guide.md#trees).

     **Start:** Calculate the inventory share and block distribution of the most common valid species.

     **Watch:** Present a tree-count scenario; ecosystem-service dollars require additional modeling.
55. Where do large trees survive on surprisingly small parcels?

     **Data:** Local. **Effort:** Setup. **Sources:** [trees](datacuse-data-guide.md#trees), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Find large recorded DBH values near small parcels; inspect boundary placement.

     **Watch:** Street trees may lie in the right-of-way, not on the neighboring parcel.
56. Can we match a tree in one dated Syracuse photograph to the same location today?

     **Data:** Research. **Effort:** Project. **Sources:** [photos](datacuse-data-guide.md#photos), [field](datacuse-data-guide.md#field).

     **Start:** Find one dated archival view with a distinctive tree and compare the present location.

     **Watch:** Identity and survival need evidence; an absolute oldest-photo claim is not supportable from a partial archive.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
57. Where are bird sightings reported most often—and where do observers go?

     **Data:** Public. **Effort:** Setup. **Sources:** [birds](datacuse-data-guide.md#birds).

     **Start:** Compare eBird hotspot activity and reported species with complete-checklist effort where available.

     **Watch:** Observer access and popularity influence the map; it is not a bird-density map.
58. Which birds have the shortest seasonal reporting windows in Onondaga County eBird checklists?

     **Data:** Public. **Effort:** Setup. **Sources:** [birds](datacuse-data-guide.md#birds).

     **Start:** Download Onondaga County eBird histogram data and compare narrow seasonal frequency peaks.

     **Watch:** Use reporting frequency and adequate checklist effort; absence of reports is not biological absence.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
59. When does spring reporting of a chosen migrant bird increase each year?

     **Data:** Public. **Effort:** Setup. **Sources:** [birds](datacuse-data-guide.md#birds).

     **Start:** Compare one species across up to five separate years using eBird frequency charts.

     **Watch:** Define a sustained reporting threshold; an isolated first sighting is effort-sensitive.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
60. Where has pavement quietly become a garden?

     **Data:** Manual. **Effort:** Project. **Sources:** [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Find one candidate garden and compare dated imagery with a current visit and owner/organizer account.

     **Watch:** No complete conversion-history dataset found; report a verified example.

## Snow, weather, and Syracuse’s seasonal personality

61. Was last winter actually unusual?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Compare a completed winter with the 2004-2026 local station series using snowfall and temperature.

     **Watch:** The local file ends August 1, 2026; refresh before describing a newer winter.
62. What did a “normal winter” mean when you were ten?

     **Data:** Public. **Effort:** Setup. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Download the airport's longer NOAA record and define a childhood-centered comparison window.

     **Watch:** The local series begins in 2004; station history and record completeness matter.
63. How often does Syracuse have a white Christmas?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Count December 25 observations with snow depth at or above a declared threshold.

     **Watch:** Use SNWD, not snowfall on Christmas Day; report the 2004-onward period.
64. How often does Halloween come with measurable snow?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Count October 31 observations with measurable SNOW and list the years.

     **Watch:** Trace snow is flagged differently from measurable snow.
65. What is the latest recorded spring snowfall?

     **Data:** Public. **Effort:** Setup. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Use the full NOAA station record to find the latest measurable spring snow date.

     **Watch:** A local 2004-onward maximum cannot be called an all-time record.
66. What is the earliest recorded autumn snowfall?

     **Data:** Public. **Effort:** Setup. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Use the full station record to find the earliest measurable autumn snowfall.

     **Watch:** Define autumn and measurable snow; inspect quality flags and station changes.
67. What is Syracuse’s longest stretch of consecutive snowy days?

     **Data:** Public. **Effort:** Setup. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Find runs of consecutive days with measurable snowfall in the full daily series.

     **Watch:** Missing observations break runs; distinguish trace from zero.
68. How much annual snowfall comes from the five biggest days?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Calculate the five largest daily snowfall amounts as a share of each complete snow season.

     **Watch:** Define a snow season across calendar years; exclude incomplete seasons.
69. Which month delivers the most snow surprises?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Compare each month's unusually snowy days relative to its own historical distribution.

     **Watch:** Define surprise statistically before looking at the result.
70. How often does a warm day immediately precede heavy snow?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Count warm-day/heavy-next-day-snow pairs using explicit thresholds.

     **Watch:** Association and reporting-day boundaries do not prove a meteorological mechanism.
71. What is the biggest temperature swing within one day?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Rank daily TMAX_C minus TMIN_C for the local record.

     **Watch:** This is daily temperature range, not an observed hour-by-hour swing.
72. What is the biggest temperature swing between consecutive days?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Rank changes between consecutive daily mean-of-extremes temperatures.

     **Watch:** Use the same temperature metric both days; omit missing pairs.
73. How many false springs does Syracuse get in a typical year?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Define a warm spell followed by a freeze and count episodes per year.

     **Watch:** False spring is your stated operational definition, not an official weather variable.
74. When does the final freeze usually arrive?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Calculate the last spring day with TMIN at or below 0 C for each complete year.

     **Watch:** Airport air temperature is not every garden's frost exposure.
75. How much does the first freeze date vary?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Find each autumn's first TMIN at or below 0 C and show its spread.

     **Watch:** Keep season windows consistent and report incomplete years.
76. What is the longest stretch without measurable precipitation?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Find consecutive days below a measurable-precipitation threshold.

     **Watch:** Trace and missing precipitation require separate treatment.
77. Does it rain more often on weekends—or do we remember it better?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Compare rainy-day fractions for weekends and weekdays, stratified by season.

     **Watch:** Use rates, not raw counts; two weekend days cannot be compared with five weekdays directly.
78. Which calendar date has historically offered the best picnic odds?

     **Data:** Local. **Effort:** Setup. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Estimate comfortable/dry-day frequency in rolling calendar windows.

     **Watch:** One exact date has few observations; smooth and avoid promising future weather.
79. How often does the first day of summer feel like summer?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Pick a stated summer-start definition and count years meeting your warmth threshold.

     **Watch:** June 1, June 21, and the actual solstice are different questions.
80. How many days actually require a winter coat under a stated threshold?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Count days below a declared maximum-temperature threshold and compare years.

     **Watch:** A temperature threshold is a playful proxy, not a clothing or health recommendation.
81. How often does snow survive a midwinter thaw?

     **Data:** Local. **Effort:** Setup. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Track SNWD before and after above-freezing periods in complete winters.

     **Watch:** Snow-depth gaps and new snowfall can obscure survival of the old snowpack.
82. Which winters produced lots of snow but relatively few snowy days?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Plot seasonal snowfall totals against counts of measurable-snow days.

     **Watch:** Exclude partial seasons and inspect trace flags.
83. Which winters produced frequent snow without big totals?

     **Data:** Local. **Effort:** Quick. **Sources:** [weather](datacuse-data-guide.md#weather).

     **Start:** Rank winters by snow-day count relative to total snowfall.

     **Watch:** Use the same definitions as DC082 to make the two stories comparable.
84. Does snowfall at the airport represent the whole city?

     **Data:** Public. **Effort:** Setup. **Sources:** [weather](datacuse-data-guide.md#weather), [gauges](datacuse-data-guide.md#gauges).

     **Start:** Compare overlapping airport and nearby station snowfall for several storms.

     **Watch:** Multi-station observations are available, but coverage and observation times differ.
85. How different can snowfall be across nearby weather stations?

     **Data:** Public. **Effort:** Setup. **Sources:** [gauges](datacuse-data-guide.md#gauges).

     **Start:** Download nearby NOAA station snowfall and compare common reporting days.

     **Watch:** Do not treat a missing station report as zero snow.
86. When do snow-related service requests begin each season?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Find each season's first snow-category request in the verified request extract.

     **Watch:** The local CSV covers June 2021-February 2025; later collections need separate validation.
87. How long after snowfall do snow-related requests peak?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [weather](datacuse-data-guide.md#weather).

     **Start:** Align daily snow totals and snow-related requests; compare lagged counts for selected storms.

     **Watch:** Reporting delay is not the time the street became snowy or the service response time.
88. What do residents call snow problems when there is no matching request category?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Review a defined sample of snow-related summaries/descriptions outside snow categories.

     **Watch:** Redact personal details; report manual coding rules and sample size.
89. What share of snow-related Cityline requests arrives overnight?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Classify snow requests by local creation hour and compare overnight shares across storms.

     **Watch:** Historical plow-pass coverage was not found in the inspected files; request timing is a different measurable question.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
90. What does one snowstorm look like in six maps?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [weather](datacuse-data-guide.md#weather).

     **Start:** Choose one covered storm and map requests in six consecutive time windows alongside snowfall.

     **Watch:** These are complaint maps, not maps of snow depth or completed plowing.

## Buildings, parcels, and peculiar pieces of land

91. What is Syracuse’s smallest parcel?

     **Data:** Local. **Effort:** Quick. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Rank polygon areas in a projected coordinate system and inspect the smallest records.

     **Watch:** Exclude invalid geometry and document whether rights-of-way or condo records count.
92. Which mapped Syracuse parcels are the narrowest?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Rank parcel width-to-depth measures and visually verify the narrowest candidates.

     **Watch:** Geometry alone cannot establish legal buildability.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
93. Which parcel has the strangest shape?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Compare compactness, holes, and perimeter-to-area ratios; choose an interpretable outlier.

     **Watch:** Define strange shape explicitly and screen digitizing artifacts.
94. Why does this tiny triangle have its own parcel number?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [history](datacuse-data-guide.md#history).

     **Start:** Choose a tiny triangular parcel and trace its boundary in older maps or deeds.

     **Watch:** Geometry finds the triangle; the reason for a separate parcel requires records.
95. Which city block contains the most separate parcels?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [streets](datacuse-data-guide.md#streets).

     **Start:** Construct consistent city blocks and count intersecting distinct parcel IDs.

     **Watch:** Sliver intersections and parcels spanning multiple blocks need rules.
96. Which block is almost entirely one parcel?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [streets](datacuse-data-guide.md#streets).

     **Start:** Calculate the largest parcel's share of each block's area.

     **Watch:** Exclude road area consistently and inspect very small blocks.
97. Where are the deepest, narrowest residential lots?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [streets](datacuse-data-guide.md#streets).

     **Start:** Estimate frontage and depth for residential-coded parcels, then map extremes.

     **Watch:** Rotated bounding boxes are approximate lot dimensions, not surveyed frontages.
98. Which lots have frontage on three different streets?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [streets](datacuse-data-guide.md#streets).

     **Start:** Find parcels adjacent to three distinct road names and inspect the boundaries.

     **Watch:** Adjacency does not establish a legal access right or an entrance.
99. Where does a property line run through an unexpected place?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [imagery](datacuse-data-guide.md#imagery).

     **Start:** Overlay parcel lines on dated imagery and inspect surprising intersections.

     **Watch:** Map alignment errors are not property disputes; parcel GIS is not a survey.
100. Which parcels preserve the outline of a vanished street?

     **Data:** Research. **Effort:** Project. **Sources:** [parcels](datacuse-data-guide.md#parcels), [history](datacuse-data-guide.md#history).

     **Start:** Compare a selected parcel pattern with a georeferenced historical street map.

     **Watch:** Need a dated map documenting the vanished street, not just a suggestive shape.
101. What is the oldest recorded building on each neighborhood’s map?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Group valid yr_built values by NHOOD and review each neighborhood's oldest candidate.

     **Watch:** These are parcel assessment attributes, not a verified age for every building.
102. Which block has the tightest cluster of similar building ages?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [streets](datacuse-data-guide.md#streets).

     **Start:** Measure age spread among valid residential records on each defined block.

     **Watch:** Exclude missing/sentinel years and require several buildings per block.
103. Where do neighboring buildings differ most in recorded age?

     **Data:** Local. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Pair neighboring parcels and rank differences in valid yr_built.

     **Watch:** The recorded year may describe one improvement rather than every structure.
104. How many buildings are older than Syracuse’s incorporation?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [history](datacuse-data-guide.md#history).

     **Start:** Count valid assessment years before the documented incorporation year and verify candidates.

     **Watch:** Do not turn an assessment date into a claim that the original structure survives.
105. Which decade left the most surviving buildings?

     **Data:** Local. **Effort:** Quick. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Bin valid yr_built values by decade and show the surviving assessed stock.

     **Watch:** This is a survival snapshot, not total historical construction.
106. Which decades are least represented in the current property age records?

     **Data:** Local. **Effort:** Quick. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Compare counts of surviving assessed properties by recorded construction decade.

     **Watch:** No complete historic construction flow was found; demolition and bad dates distort the apparent lull.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
107. How many buildings have suspiciously round construction dates?

     **Data:** Local. **Effort:** Quick. **Sources:** [parcels](datacuse-data-guide.md#parcels).

     **Start:** Chart year frequencies and concentration at years ending in 0 or 5.

     **Watch:** Round dates suggest uncertainty but are not proof of fabricated records.
108. What does “built in 1900” really mean in property records?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [history](datacuse-data-guide.md#history).

     **Start:** Sample properties recorded as 1900 and compare dated maps or assessment documentation.

     **Watch:** Verify the source's date conventions before treating 1900 as a default code.
109. Where are the smallest residential building footprints?

     **Data:** Public. **Effort:** Setup. **Sources:** [footprints](datacuse-data-guide.md#footprints), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Download county building footprints, join residential parcels, and rank small structures.

     **Watch:** A residential parcel may contain a shed; inspect imagery before calling it a house.
110. Where are the largest buildings hiding in plain sight?

     **Data:** Public. **Effort:** Setup. **Sources:** [footprints](datacuse-data-guide.md#footprints).

     **Start:** Rank building footprint areas and map a few unexpectedly large buildings.

     **Watch:** Footprint area is not floor area; multipart structures need review.
111. Which building occupies the greatest share of its parcel?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [footprints](datacuse-data-guide.md#footprints), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Sum footprint area within each parcel and divide by parcel area.

     **Watch:** Handle shared buildings and differing map vintages; report geometry overlaps.
112. Which large parcel contains a surprisingly small building?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [footprints](datacuse-data-guide.md#footprints), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Rank large parcels with very low building coverage and inspect the leaders.

     **Watch:** Parking, parks, and utility land should not be interpreted as underused by default.
113. How much land is occupied by detached garages?

     **Data:** Manual. **Effort:** Project. **Sources:** [footprints](datacuse-data-guide.md#footprints), [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Classify detached garages in a bounded sample of blocks and sum their footprints.

     **Watch:** Unlabeled footprints do not identify garages; scope the headline to the audited sample.
114. Which blocks have the most alley-facing buildings?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [footprints](datacuse-data-guide.md#footprints), [field](datacuse-data-guide.md#field).

     **Start:** Choose mapped alleys and record buildings with verified alley-facing entrances.

     **Watch:** Footprint adjacency alone does not show which way a building faces.
115. Where do houses sit unusually close to the sidewalk?

     **Data:** Manual. **Effort:** Setup. **Sources:** [footprints](datacuse-data-guide.md#footprints), [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Measure setbacks on selected blocks from visible sidewalk edges.

     **Watch:** Road centerline distance is not a sidewalk setback.
116. Where do building setbacks abruptly change?

     **Data:** Manual. **Effort:** Setup. **Sources:** [footprints](datacuse-data-guide.md#footprints), [imagery](datacuse-data-guide.md#imagery).

     **Start:** Measure a run of building fronts on one street and locate abrupt setback changes.

     **Watch:** Use a consistent street/sidewalk reference and verify image alignment.
117. How many corner buildings have entrances facing the corner?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Photograph corner-building entrances along a defined route and code entrance direction.

     **Watch:** No complete entrance-orientation dataset found; report an observed sample.
118. Which former industrial buildings have found new uses?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [parcels](datacuse-data-guide.md#parcels), [field](datacuse-data-guide.md#field).

     **Start:** Choose a few industrial sites with documented old use and verify current use.

     **Watch:** Land-use codes alone do not establish a conversion history.
119. Can you identify a former store from its building shape?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Match one suspected storefront facade with a dated business directory or fire-insurance map.

     **Watch:** Building shape suggests a lead; archival records must confirm former use.
120. What can one block’s parcel map tell us about its history?

     **Data:** Research. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [history](datacuse-data-guide.md#history).

     **Start:** Compare one current block's lot pattern with two dated historical maps.

     **Watch:** Account for map scale, realignment, and parcel consolidation.

## Getting around, sometimes the long way

121. Where can two nearby places require a surprisingly long walk?

     **Data:** Public. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Compare walking-network distance with straight-line distance for candidate pairs.

     **Watch:** Verify paths, gates, and crossing access; routing data can be incomplete.
122. Which highway crossing creates the biggest pedestrian detour?

     **Data:** Public. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Compare nearby destinations on opposite sides of highways and calculate detour ratios.

     **Watch:** A geometric crossing may be a bridge without pedestrian access.
123. Where does a missing sidewalk interrupt an otherwise complete route?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Audit a selected corridor for sidewalk continuity using imagery and a walk.

     **Watch:** An absent OSM sidewalk tag does not prove there is no sidewalk.
124. Which intersection requires the most crossings to reach the opposite corner?

     **Data:** Manual. **Effort:** Setup. **Sources:** [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Diagram marked crossing sequences at a few complex intersections.

     **Watch:** Observe pedestrian phases and legal access; do not infer solely from road arms.
125. Where are the longest marked pedestrian crossings?

     **Data:** Manual. **Effort:** Setup. **Sources:** [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Measure visible marked crossings in a stated sample from high-resolution imagery.

     **Watch:** No complete marked-crosswalk geometry was verified; field-check finalists.
126. Which streets have sidewalks on only one side?

     **Data:** Manual. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Inventory sidewalk presence by side on a defined set of streets.

     **Watch:** Citywide claims need a complete audit; incomplete tags are only leads.
127. How many cul-de-sacs have pedestrian exits?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Find cul-de-sac candidates and verify mapped or visible pedestrian exits.

     **Watch:** Street dead ends and pedestrian dead ends are different.
128. Which pedestrian shortcut saves the most distance?

     **Data:** Public. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Compare network distances with and without selected public path connections.

     **Watch:** Verify the shortcut is publicly accessible and currently usable.
129. Where does a fence turn a short trip into a long one?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Choose a confirmed barrier and compare the legal walking route with straight-line distance.

     **Watch:** Map a real public route; do not imply permission to cross private property.
130. Which bridge serves the most potential walking routes?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [census](datacuse-data-guide.md#census).

     **Start:** Model how selected bridge closures change walking distances between populated blocks.

     **Watch:** Results depend on origins, destinations, and assumptions; these are potential routes.
131. What is the steepest street segment?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [terrain](datacuse-data-guide.md#terrain).

     **Start:** Sample elevations along street segments and rank robust grades over a minimum distance.

     **Watch:** Endpoint grade on tiny segments is noisy; bridges require special handling.
132. What is the flattest mile-long walking loop?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [terrain](datacuse-data-guide.md#terrain), [field](datacuse-data-guide.md#field).

     **Start:** Generate candidate mile loops and minimize cumulative ascent; walk the best few.

     **Watch:** DEM resolution and path access limit claims of a global minimum.
133. What is the hilliest mile-long walking loop?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [terrain](datacuse-data-guide.md#terrain), [field](datacuse-data-guide.md#field).

     **Start:** Rank candidate mile loops by cumulative ascent using the same routing rules.

     **Watch:** Keep routes legal and comparable; elevation noise can inflate ascent.
134. How much elevation do you gain walking across Syracuse?

     **Data:** Public. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [terrain](datacuse-data-guide.md#terrain).

     **Start:** Define an east-west or north-south route and plot its elevation profile.

     **Watch:** Across Syracuse is not a unique route; state endpoints and sampling interval.
135. How far can you walk without crossing a major road?

     **Data:** Public. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [streets](datacuse-data-guide.md#streets).

     **Start:** Remove major-road crossing connections and map remaining walkable components.

     **Watch:** Define major road and include only verified public pedestrian links.
136. Which neighborhood has the smallest blocks?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Polygonize street blocks, summarize their areas using documented NHOOD geography.

     **Watch:** Neighborhood labels on parcels are a source-specific definition; edge blocks need rules.
137. Which has the largest blocks?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Compare median and largest block areas by the same neighborhood definition.

     **Watch:** Large institutional sites can dominate an average.
138. Where does the street grid rotate—and why?

     **Data:** Research. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [history](datacuse-data-guide.md#history).

     **Start:** Map road headings and investigate one abrupt grid change in dated maps.

     **Watch:** Geometry detects the change; historical explanation needs a separate source.
139. How many different grid orientations does Syracuse contain?

     **Data:** Local. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Compute length-weighted bearings, folded to grid orientation, and cluster them.

     **Watch:** The number of orientations depends on your clustering tolerance.
140. Which bus stops are closest together?

     **Data:** Public. **Effort:** Quick. **Sources:** [transit](datacuse-data-guide.md#transit).

     **Start:** Download the verified Centro feed and rank stop-coordinate pairs by distance.

     **Watch:** Opposite-direction platforms and the transit hub may form trivial pairs; define exclusions.
141. Which consecutive bus stops are farthest apart?

     **Data:** Public. **Effort:** Setup. **Sources:** [transit](datacuse-data-guide.md#transit).

     **Start:** Order stops by trip sequence and compare distances along the associated route shape.

     **Watch:** Nearest geographic stops are not necessarily consecutive stops.
142. Which bus stop serves the most scheduled routes?

     **Data:** Public. **Effort:** Quick. **Sources:** [transit](datacuse-data-guide.md#transit).

     **Start:** Join stops, stop_times, trips, and routes for a chosen service date.

     **Watch:** Combine platforms consistently and count distinct routes, not trips.
143. Where do scheduled buses arrive in bunches, followed by long gaps?

     **Data:** Public. **Effort:** Setup. **Sources:** [transit](datacuse-data-guide.md#transit).

     **Start:** Build scheduled arrivals at selected stops and chart headway clusters.

     **Watch:** Schedules establish planned bunching only, not actual bus reliability.
144. How different is Sunday transit service from Tuesday service?

     **Data:** Public. **Effort:** Quick. **Sources:** [transit](datacuse-data-guide.md#transit).

     **Start:** Apply calendar and calendar_dates to comparable Tuesday and Sunday service dates.

     **Watch:** Avoid holidays unless intentional; compare departures and span, not just route counts.
145. Which trips become hardest after the evening rush?

     **Data:** Public. **Effort:** Setup. **Sources:** [transit](datacuse-data-guide.md#transit), [osm](datacuse-data-guide.md#osm).

     **Start:** Compare selected origin-destination itineraries before and after evening peak.

     **Watch:** Door-to-door difficulty needs walking and transfer assumptions, not frequency alone.
146. How many residents live within a short walk of frequent scheduled service?

     **Data:** Public. **Effort:** Project. **Sources:** [transit](datacuse-data-guide.md#transit), [census](datacuse-data-guide.md#census), [osm](datacuse-data-guide.md#osm).

     **Start:** Define frequent service, build walking catchments, and allocate block population.

     **Watch:** Population allocation and frequency threshold make this an estimate.
147. Which bus shelters face the afternoon sun?

     **Data:** Manual. **Effort:** Setup. **Sources:** [transit](datacuse-data-guide.md#transit), [field](datacuse-data-guide.md#field).

     **Start:** Inventory shelter orientation and afternoon shade at a selected stop sample.

     **Watch:** GTFS stops do not establish shelter presence, glazing, or orientation.
148. Where does a bike lane end at an especially inconvenient spot?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Find mapped bicycle-lane transitions and inspect several on the ground.

     **Watch:** OSM cycling tags may be incomplete or stale; record observation dates.
149. How much farther is the comfortable bike route than the direct route?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [traffic](datacuse-data-guide.md#traffic), [field](datacuse-data-guide.md#field).

     **Start:** Define a low-stress rule and compare selected bike routes with direct routes.

     **Watch:** Traffic counts are incomplete; comfort is an explicit model, not a measured universal fact.
150. Can you cross Syracuse using only low-traffic streets and trails?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [traffic](datacuse-data-guide.md#traffic), [field](datacuse-data-guide.md#field).

     **Start:** Search a route using trails and roads satisfying a stated traffic/stress rule.

     **Watch:** Missing traffic counts are not proof of low traffic; field-check gaps.

## Parks, public places, and nearby pleasures

151. What is Syracuse’s smallest park?

     **Data:** Public. **Effort:** Quick. **Sources:** [parks](datacuse-data-guide.md#parks).

     **Start:** Compare official listed park acreages and verify small candidates against boundaries.

     **Watch:** Some listings round acreage or combine sites; define parks versus plazas.
152. Which park has the most boundary relative to its area?

     **Data:** Public. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks).

     **Start:** Obtain or trace official park boundaries and compare perimeter-to-area ratios.

     **Watch:** Do not use an entire tax parcel when only part is parkland.
153. Which park is hardest to enter from nearby homes?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Map verified entrances and compare routes from nearby homes for selected parks.

     **Watch:** A park boundary is not an entrance; fences and hours affect access.
154. Where is the largest gap between official park boundaries and actual entrances?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [field](datacuse-data-guide.md#field).

     **Start:** Compare nearest boundary points with verified gate locations at a few parks.

     **Watch:** A citywide ranking needs a complete entrance inventory.
155. Which residential location is farthest from a public park entrance?

     **Data:** Public. **Effort:** Project. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [census](datacuse-data-guide.md#census), [field](datacuse-data-guide.md#field).

     **Start:** Build an entrance inventory, route from populated blocks, and inspect the longest trips.

     **Watch:** Requires manual entrance validation before a defensible citywide superlative.
156. How many residents can walk to more than one park?

     **Data:** Public. **Effort:** Project. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [census](datacuse-data-guide.md#census).

     **Start:** Overlay walking catchments from verified entrances and count block population with multiple options.

     **Watch:** State walking-time and block-allocation assumptions.
157. Which park serves the most people within a ten-minute walk?

     **Data:** Public. **Effort:** Project. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [census](datacuse-data-guide.md#census).

     **Start:** Estimate population in ten-minute walksheds for each verified entrance set.

     **Watch:** This measures potential access, not actual visitors or demand.
158. Where do city boundaries complicate the nearest-park question?

     **Data:** Public. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [boundary](datacuse-data-guide.md#boundary), [osm](datacuse-data-guide.md#osm).

     **Start:** Compare nearest park routes with and without parks just outside Syracuse.

     **Watch:** Include adjacent jurisdictions and check public access.
159. Which park has the most varied terrain?

     **Data:** Public. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [terrain](datacuse-data-guide.md#terrain).

     **Start:** Compare elevation range and slope distribution inside park polygons.

     **Watch:** DEM terrain does not establish trail accessibility.
160. Which park offers the flattest walking loop?

     **Data:** Public. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [terrain](datacuse-data-guide.md#terrain), [field](datacuse-data-guide.md#field).

     **Start:** Measure ascent on mapped park loops and verify a small finalist set.

     **Watch:** A mapped trail may have steps, poor surfaces, or seasonal closures.
161. Where can you watch the sunset from public land?

     **Data:** Manual. **Effort:** Setup. **Sources:** [terrain](datacuse-data-guide.md#terrain), [parks](datacuse-data-guide.md#parks), [field](datacuse-data-guide.md#field).

     **Start:** Screen west-facing public viewpoints and verify actual horizon obstruction at sunset.

     **Watch:** Terrain-only models miss buildings and foliage; specify the date/season.
162. Which public viewpoint has the widest visible horizon?

     **Data:** Manual. **Effort:** Project. **Sources:** [terrain](datacuse-data-guide.md#terrain), [field](datacuse-data-guide.md#field).

     **Start:** Compare modeled horizons at selected verified public viewpoints and photograph panoramas.

     **Watch:** Scope the claim to your candidates; vegetation and structures affect visibility.
163. Where are public benches concentrated?

     **Data:** Manual. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Use mapped benches as leads, then count every public bench in a defined study area.

     **Watch:** OSM coverage is not a complete city bench inventory.
164. What is the longest downtown walk without a public bench?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Walk and map benches along a defined downtown route network, then measure gaps.

     **Watch:** Restrict longest-gap claims to audited streets and accessible seating.
165. Where are drinking fountains—and when are they available?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Make a small fountain inventory and verify operating dates with site information or visits.

     **Watch:** Mapped locations do not establish seasonal availability or working condition.
166. How far apart are public restrooms?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Map publicly usable restrooms with verified hours and calculate route spacing.

     **Watch:** Public-looking buildings do not necessarily provide unrestricted restrooms.
167. Which playground is closest to a library?

     **Data:** Public. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [libraries](datacuse-data-guide.md#libraries), [osm](datacuse-data-guide.md#osm).

     **Start:** Compile official playground and library locations, then compare walking distances.

     **Watch:** Use playground entrances rather than park centroids.
168. Can you build a stroller-friendly park-and-library outing?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [libraries](datacuse-data-guide.md#libraries), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Plan one park-library route and audit crossings, steps, grades, and surfaces.

     **Watch:** Stroller-friendly requires observation; a router alone cannot certify it.
169. Which basketball courts are closest to one another?

     **Data:** Public. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks).

     **Start:** Compile listed public basketball-court locations and rank nearby pairs.

     **Watch:** Check multi-court facilities and school access before calling courts public.
170. How evenly are public sports facilities distributed?

     **Data:** Public. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [census](datacuse-data-guide.md#census).

     **Start:** Map official facility types and compare counts or catchments with population.

     **Watch:** Facility quality, opening hours, and accessibility are additional questions.
171. Who were three people whose names survive in Syracuse parks?

     **Data:** Research. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [history](datacuse-data-guide.md#history).

     **Start:** Choose three person-named parks and verify their namesakes in official or archival records.

     **Watch:** No resident-recognition survey was found; avoid claiming what most residents know.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
172. Which park names describe features that are gone?

     **Data:** Research. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [history](datacuse-data-guide.md#history).

     **Start:** Compare one descriptive park name with dated maps and present conditions.

     **Watch:** A suggestive name alone does not prove the former feature existed.
173. How much parkland existed in different historical decades?

     **Data:** Research. **Effort:** Project. **Sources:** [parks](datacuse-data-guide.md#parks), [history](datacuse-data-guide.md#history).

     **Start:** Digitize park areas from two comparable dated city maps.

     **Watch:** Check that each map lists all parks; do not infer complete totals from selective tourist maps.
174. Which proposed park never happened?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Find a documented park proposal with a mapped site and compare its eventual use.

     **Watch:** Locate an actual proposal first; an archive collection is only a research lead.
175. Where did a former park become something else?

     **Data:** Research. **Effort:** Project. **Sources:** [parks](datacuse-data-guide.md#parks), [history](datacuse-data-guide.md#history).

     **Start:** Trace one documented former park through dated maps and official records.

     **Watch:** Need evidence of formal park status and the later change.
176. Which overlooked public space is smaller than a house lot?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [parcels](datacuse-data-guide.md#parcels), [field](datacuse-data-guide.md#field).

     **Start:** Find and measure several small official plazas or public spaces.

     **Watch:** Public accessibility and legal ownership are separate; verify both claims.
177. Where do public stairs reveal the city’s topography?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [terrain](datacuse-data-guide.md#terrain), [field](datacuse-data-guide.md#field).

     **Start:** Map known public stairways, confirm access, and add elevation profiles.

     **Watch:** OSM steps are a starting list, not a complete stair inventory.
178. What is the longest continuous stretch of publicly accessible waterfront?

     **Data:** Manual. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [parks](datacuse-data-guide.md#parks), [field](datacuse-data-guide.md#field).

     **Start:** Trace connected public waterfront paths and verify gaps, gates, and access hours.

     **Watch:** Waterfront parcel ownership does not automatically permit public access.
179. Where can you hear traffic from almost every corner of a park?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Log audible traffic at a fixed grid of points in one park at matched times.

     **Watch:** Road proximity is only a proxy; phone sound measurements need consistent settings.
180. What would a tour of Syracuse’s tiniest public places look like?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Select verified small public spaces and build a walk between their entrances.

     **Watch:** Call it a curated tour unless the underlying inventory is complete.

## Libraries and the rhythms of community life

181. Which library is closest to the largest number of residents?

     **Data:** Public. **Effort:** Setup. **Sources:** [libraries](datacuse-data-guide.md#libraries), [census](datacuse-data-guide.md#census), [osm](datacuse-data-guide.md#osm).

     **Start:** Assign populated blocks to their nearest library by stated walking distance.

     **Watch:** This estimates nearby residents, not registered borrowers or official service areas.
182. Where is the longest walk to a library within the city?

     **Data:** Public. **Effort:** Setup. **Sources:** [libraries](datacuse-data-guide.md#libraries), [census](datacuse-data-guide.md#census), [osm](datacuse-data-guide.md#osm).

     **Start:** Route populated city blocks to library entrances and inspect the longest trips.

     **Watch:** Use actual entrances and accessible paths; block centroids approximate home locations.
183. How different are library service areas by walking, driving, and transit?

     **Data:** Public. **Effort:** Project. **Sources:** [libraries](datacuse-data-guide.md#libraries), [osm](datacuse-data-guide.md#osm), [transit](datacuse-data-guide.md#transit).

     **Start:** Compare branch catchments for walking, driving, and scheduled transit at fixed departure times.

     **Watch:** Different modes and transit departure times produce different catchments.
184. Which library can you reach from the most other branches without transferring?

     **Data:** Public. **Effort:** Setup. **Sources:** [libraries](datacuse-data-guide.md#libraries), [transit](datacuse-data-guide.md#transit), [osm](datacuse-data-guide.md#osm).

     **Start:** Join branch entrances to stops and test direct scheduled connections between branches.

     **Watch:** Define maximum walking distance at both ends; no transfer does not mean fast.
185. How much do library opening hours overlap?

     **Data:** Public. **Effort:** Quick. **Sources:** [libraries](datacuse-data-guide.md#libraries).

     **Start:** Transcribe current weekly opening hours and chart shared open intervals.

     **Watch:** Record the checking date and handle holiday or seasonal exceptions.
186. Where can you visit a library latest in the evening?

     **Data:** Public. **Effort:** Quick. **Sources:** [libraries](datacuse-data-guide.md#libraries).

     **Start:** Compare the latest posted closing time by weekday across branches.

     **Watch:** Confirm temporary changes before publication.
187. How does Saturday library access differ across the county?

     **Data:** Public. **Effort:** Quick. **Sources:** [libraries](datacuse-data-guide.md#libraries).

     **Start:** Compare Saturday hours for all listed county libraries on a chosen date.

     **Watch:** Some libraries change summer schedules; keep the comparison date explicit.
188. What is the shortest route connecting every city library?

     **Data:** Public. **Effort:** Setup. **Sources:** [libraries](datacuse-data-guide.md#libraries), [osm](datacuse-data-guide.md#osm).

     **Start:** Optimize a route visiting city-library entrances using a stated travel mode.

     **Watch:** Shortest route is different from a feasible visit while each branch is open.
189. What is the shortest route connecting every county library?

     **Data:** Public. **Effort:** Project. **Sources:** [libraries](datacuse-data-guide.md#libraries), [osm](datacuse-data-guide.md#osm).

     **Start:** Optimize a countywide branch tour and compare a practical route with the model.

     **Watch:** Choose return-to-start rules and whether time inside libraries counts.
190. Which branches have the largest nearby child populations?

     **Data:** Public. **Effort:** Setup. **Sources:** [libraries](datacuse-data-guide.md#libraries), [census](datacuse-data-guide.md#census), [osm](datacuse-data-guide.md#osm).

     **Start:** Estimate child populations in fixed library walksheds using Census age data.

     **Watch:** These are nearby residents, not children served or attending programs.
191. Which serve the largest nearby older-adult populations?

     **Data:** Public. **Effort:** Setup. **Sources:** [libraries](datacuse-data-guide.md#libraries), [census](datacuse-data-guide.md#census), [osm](datacuse-data-guide.md#osm).

     **Start:** Estimate older-adult populations using the same branch catchment method.

     **Watch:** Use age-specific Census data and disclose allocation uncertainty.
192. Which serve areas with the greatest variety of home languages?

     **Data:** Public. **Effort:** Setup. **Sources:** [libraries](datacuse-data-guide.md#libraries), [census](datacuse-data-guide.md#census).

     **Start:** Compare ACS language distributions in defined areas around branches.

     **Watch:** ACS samples and broad language groups limit precise neighborhood rankings.
193. How does library use change through the school year?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Plot monthly visits, circulation, and programs over school-year months.

     **Watch:** Local data cover Jan 2023-Mar 2026 and combine branches; calendar association is not causation.
194. Does summer bring more visits, more borrowing, or both?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Compare summer visits and physical/digital circulation with other months in complete years.

     **Watch:** Show Central and aggregate branches separately; control for partial years.
195. What is the busiest library month?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Rank complete months by visits or circulation after choosing the meaning of busiest.

     **Watch:** Different metrics produce different winners; account for open days if available.
196. Which library-use measure has changed most over a decade?

     **Data:** Public. **Effort:** Setup. **Sources:** [librarystats](datacuse-data-guide.md#librarystats), [libraryreports](datacuse-data-guide.md#libraryreports).

     **Start:** Extract comparable annual measures from public reports to extend the local 2023-onward series.

     **Watch:** Ten-year definitions and library coverage must match; PDFs may need transcription.
197. How has digital borrowing changed relative to physical borrowing?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Chart digital versus physical circulation and their shares by month.

     **Watch:** Check whether digital values are system-level before attributing them to locations.
198. How has Central Library's share of recorded visits changed?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Calculate Central Value divided by Total Value for the Visits series over time.

     **Watch:** The inspected files aggregate branches and lack individual-branch open hours.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
199. How does attendance per recorded program compare between Central and the branches?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Divide Program Attendance by Programs for Central and the aggregate branches each month.

     **Watch:** Individual branch rankings and per-open-day rates are unsupported by these summaries.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
200. Which program categories fill the calendar most often?

     **Data:** Public. **Effort:** Setup. **Sources:** [events](datacuse-data-guide.md#events).

     **Start:** Collect a defined month of public event listings and manually normalize categories.

     **Watch:** Calendars are live and categories differ by library; archive a dated snapshot.
201. How much free programming happens on an ordinary Tuesday?

     **Data:** Public. **Effort:** Quick. **Sources:** [events](datacuse-data-guide.md#events).

     **Start:** Choose one Tuesday and tally public events by time, location, and audience.

     **Watch:** Verify price, registration, and cancellation status; not all events are drop-in.
202. Can you plan an entire free Saturday from library calendars?

     **Data:** Public. **Effort:** Quick. **Sources:** [events](datacuse-data-guide.md#events), [transit](datacuse-data-guide.md#transit).

     **Start:** Choose a Saturday, verify free events, and build a realistic itinerary.

     **Watch:** Check age limits, capacity, travel time, and registration before recommending it.
203. Which library buildings were originally something else?

     **Data:** Research. **Effort:** Setup. **Sources:** [libraryhistory](datacuse-data-guide.md#libraryhistory), [history](datacuse-data-guide.md#history).

     **Start:** Choose a branch with a documented former building use and assemble before/after evidence.

     **Watch:** A suggestive building style does not establish prior use.
204. Where were Syracuse’s former library locations?

     **Data:** Research. **Effort:** Project. **Sources:** [libraryhistory](datacuse-data-guide.md#libraryhistory), [history](datacuse-data-guide.md#history).

     **Start:** Transcribe former branch addresses from dated directories and library histories.

     **Watch:** Street renumbering and name changes require address reconciliation.
205. How far have branches moved over their histories?

     **Data:** Research. **Effort:** Setup. **Sources:** [libraryhistory](datacuse-data-guide.md#libraryhistory), [history](datacuse-data-guide.md#history).

     **Start:** Pair verified historical and current branch addresses and calculate relocation distances.

     **Watch:** Use actual historical coordinates, not blindly geocoded old addresses.
206. What did the library system lend besides books in different eras?

     **Data:** Research. **Effort:** Setup. **Sources:** [libraryhistory](datacuse-data-guide.md#libraryhistory), [libraries](datacuse-data-guide.md#libraries).

     **Start:** Compare dated reports/catalogs with today's documented non-book lending.

     **Watch:** Historical availability needs a dated source; present catalogs cannot establish past practice.
207. Which library statistic would surprise someone who has not visited recently?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Pick a well-defined metric such as programs, visits, or digital circulation and chart its scale.

     **Watch:** Do not infer unique people from visits or attendance.
208. Do visits and circulation rise and fall together?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Plot monthly visits against circulation for matching months and aggregate coverage.

     **Watch:** Trends and seasonality can create correlation without a direct relationship.
209. What does an unusually busy library month look like in context?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Compare an outlier month with the same month in prior years and neighboring months.

     **Watch:** Check closures, reporting changes, and incomplete figures before explaining the outlier.
210. What does a year of library activity look like month by month?

     **Data:** Local. **Effort:** Quick. **Sources:** [librarystats](datacuse-data-guide.md#librarystats).

     **Start:** Build a 12-month visual comparing visits, programs, and borrowing for a complete year.

     **Watch:** The verified source is monthly; it cannot support a daily activity heatmap.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).

## Food, shops, and everyday errands

211. Where in Syracuse are you farthest from a Dunkin’?

     **Data:** Public. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Verify current Dunkin locations from the company's locator, then calculate distance gaps.

     **Watch:** OSM and inspection records can miss locations; include nearby shops outside the city.
212. Where are you farthest from a pizza shop?

     **Data:** Public. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Compile and verify pizza-serving businesses, then map nearest-shop distances.

     **Watch:** Define pizza shop versus any venue selling pizza and choose walking or straight-line distance.
213. Which intersection gives you the most coffee choices within a short walk?

     **Data:** Manual. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Verify coffee sellers around selected intersections and count within a walkshed.

     **Watch:** A cafe tag is incomplete and may exclude bakeries or convenience stores.
214. How many independent coffee shops fit inside one chain’s nearest-location territory?

     **Data:** Manual. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Verify independent cafes and chain locations; overlay nearest-chain territories.

     **Watch:** Define independent and use dated business checks; geometric territories are a model.
215. Where do restaurant names repeat the same favorite words?

     **Data:** Public. **Effort:** Quick. **Sources:** [food](datacuse-data-guide.md#food).

     **Start:** Filter NYS food-establishment records to local restaurants and count name words.

     **Watch:** Deduplicate inspection rows by establishment; exclude institutions and nonrestaurant facilities.
216. Which streets have the greatest variety of restaurant cuisines?

     **Data:** Manual. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [field](datacuse-data-guide.md#field).

     **Start:** Build a menu-verified cuisine classification for restaurants on selected streets.

     **Watch:** Inspection datasets do not provide reliable cuisine categories.
217. How does the restaurant map change after 10 p.m.?

     **Data:** Manual. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [field](datacuse-data-guide.md#field).

     **Start:** Verify late-night hours for a bounded restaurant list on a stated weekday.

     **Watch:** No reliable complete opening-hours dataset found; record when hours were checked.
218. Where can you get breakfast earliest?

     **Data:** Manual. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [field](datacuse-data-guide.md#field).

     **Start:** Compare verified breakfast service times among a defined set of venues.

     **Watch:** Door-opening time and breakfast-kitchen time can differ.
219. Which neighborhoods have the most Sunday-morning food options?

     **Data:** Manual. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [field](datacuse-data-guide.md#field).

     **Start:** Build a dated Sunday-morning opening-hours inventory for selected neighborhoods.

     **Watch:** Count only verified open venues; avoid citywide completeness claims from a sample.
220. Where can you complete the most ordinary errands on foot?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [food](datacuse-data-guide.md#food), [field](datacuse-data-guide.md#field).

     **Start:** Choose an explicit errands basket and test walking access to verified businesses.

     **Watch:** Different household needs change the result; OSM business coverage is incomplete.
221. Which grocery trip is short by car but awkward by bus?

     **Data:** Public. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [transit](datacuse-data-guide.md#transit), [osm](datacuse-data-guide.md#osm).

     **Start:** Choose grocery destinations and compare drive/walk/transit itineraries at fixed times.

     **Watch:** Schedule-based time excludes real-time delays and carrying groceries.
222. Where do convenience stores fill gaps between supermarkets?

     **Data:** Public. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Verify supermarkets and convenience stores and compare their catchments.

     **Watch:** Food-service inspection data do not comprehensively cover retail grocery stores.
223. Which residential areas are farthest from a laundromat?

     **Data:** Public. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Query laundromat leads, verify public self-service locations, and map gaps.

     **Watch:** Dry cleaners and apartment laundry rooms are not interchangeable with laundromats.
224. Where can you buy groceries and visit a library on one walk?

     **Data:** Public. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [libraries](datacuse-data-guide.md#libraries), [osm](datacuse-data-guide.md#osm).

     **Start:** Build a route linking verified grocery shops and library entrances.

     **Watch:** Confirm opening-hour overlap and legal walking access.
225. Which commercial block has the smallest storefronts?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [imagery](datacuse-data-guide.md#imagery), [field](datacuse-data-guide.md#field).

     **Start:** Measure storefront bay widths along selected commercial blocks.

     **Watch:** A tax parcel or whole-building footprint may contain several storefronts.
226. Which storefront has hosted the most documented business types?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Track occupants at a small set of addresses across selected directory years.

     **Watch:** Incomplete directories cannot establish an all-time citywide maximum; frame as documented candidates.
227. How far back can we trace restaurant use at one Syracuse address?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [food](datacuse-data-guide.md#food).

     **Start:** Choose one restaurant address and build a dated occupant/use timeline from directories and ads.

     **Watch:** Continuous operation and an absolute oldest claim need records not located in this review.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
228. Which business names preserve vanished neighborhood names?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [food](datacuse-data-guide.md#food).

     **Start:** Match current business names with documented historical place names.

     **Watch:** A shared word is a lead, not proof of a naming connection.
229. Where are businesses still known by a previous tenant’s name?

     **Data:** Manual. **Effort:** Project. **Sources:** [survey](datacuse-data-guide.md#survey), [history](datacuse-data-guide.md#history).

     **Start:** Collect voluntary examples of old business names still used for directions and verify former tenants.

     **Watch:** This is reader reporting, not an existing population-wide dataset.
230. How many former corner stores are visible in residential neighborhoods?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Identify corner-shop candidates on a chosen route and verify former retail use in maps/directories.

     **Watch:** Do not infer former stores from facade appearance alone.
231. Which intersections once had stores on all four corners?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Find a dated directory/map documenting businesses at all four corners of one intersection.

     **Watch:** Use one year or a narrow interval; mixed years do not prove simultaneous operation.
232. How has the geography of movie theaters changed?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Create theater locations for two or three documented years using directories and ads.

     **Watch:** Define movie theaters versus live venues and handle address changes.
233. Where did neighborhood bakeries used to cluster?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Transcribe bakery listings from selected directory years and map their distribution.

     **Watch:** An archive search is required; no clean historical bakery dataset was found.
234. What did one dollar buy in old Syracuse grocery advertisements?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Choose a dated grocery advertisement and calculate the listed basket purchasable for one dollar.

     **Watch:** This supports advertised prices, not average prices or purchasing power without more data.
235. Which foods appear most often in historical local restaurant ads?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Sample a declared newspaper/date range and code foods named in restaurant ads.

     **Watch:** OCR and newspaper selection bias the frequency; scope the headline to the sample.
236. What is the strangest product advertised as a local necessity?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Find an unusual claim in a dated local advertisement and explain its context.

     **Watch:** Strangest is editorial judgment; cite the actual ad and page.
237. How far did an ordinary grocery trip reach before supermarkets?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [osm](datacuse-data-guide.md#osm).

     **Start:** Map grocery locations in a selected historical directory and estimate neighborhood distances.

     **Watch:** No household shopping diary data found; this models proximity, not actual trips.
238. Which former shopping destination now has an entirely different purpose?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Document one former retail destination and verify its current use.

     **Watch:** Pair dated original-use evidence with current observations.
239. Can you map a day of meals using only longstanding local businesses?

     **Data:** Research. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [history](datacuse-data-guide.md#history).

     **Start:** Choose established businesses with documented founding histories and current meal hours.

     **Watch:** State what longstanding means; distinguish business age from address continuity.
240. What does the city look like if you map only ice-cream shops?

     **Data:** Public. **Effort:** Setup. **Sources:** [food](datacuse-data-guide.md#food), [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Compile and verify ice-cream shops, then make a dated map.

     **Watch:** Seasonal closures and mixed-menu shops require an inclusion rule.

## The city hiding underneath the city

241. Which current street follows an old waterway?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [streets](datacuse-data-guide.md#streets).

     **Start:** Overlay a documented historic waterway map with present roads and inspect a candidate.

     **Watch:** A curved street alone cannot establish a buried creek.
242. Where does the Erie Canal’s route remain visible in parcel boundaries?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Georeference an Erie Canal-era map and compare its corridor with current parcel edges.

     **Watch:** Account for georeferencing error; confirm dates and canal alignment changes.
243. Which modern parking lot occupies a historically surprising site?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [imagery](datacuse-data-guide.md#imagery).

     **Start:** Choose one present parking lot and identify its prior use on a dated Sanborn sheet.

     **Watch:** The source must cover that block and date; compare the exact site footprint.
244. Where did railroad tracks become ordinary-looking property lines?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Compare verified former rail alignments with current lot boundaries.

     **Watch:** Long straight lines are not proof of rail history.
245. Which old railroad curve still shapes a building or street?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [streets](datacuse-data-guide.md#streets), [footprints](datacuse-data-guide.md#footprints).

     **Start:** Overlay a documented railway curve with a present street or building.

     **Watch:** Map scale and rebuilding can weaken the apparent match.
246. What occupied the site of your favorite park a century ago?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [parks](datacuse-data-guide.md#parks).

     **Start:** Locate a century-old map or photograph covering one named park site.

     **Watch:** A map showing open land does not establish its ownership or use.
247. Which vanished bridge still has a visible approach?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Find an archival bridge location and inspect surviving approaches from public land.

     **Watch:** Need evidence that the remnant belongs to that bridge, not a later structure.
248. Where did a street get straightened?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [streets](datacuse-data-guide.md#streets).

     **Start:** Compare two dated street maps and measure a documented alignment change.

     **Watch:** Different cartographic accuracy can mimic a real street shift.
249. Which intersection used to have a completely different shape?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [streets](datacuse-data-guide.md#streets).

     **Start:** Find one intersection depicted differently in dated maps and build a before/after diagram.

     **Watch:** Corroborate major changes with photographs or engineering records.
250. Which streets were renamed, and what were they called before?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [streets](datacuse-data-guide.md#streets).

     **Start:** Transcribe old/current street-name pairs from directories, maps, or naming ordinances.

     **Watch:** Names can be reused; reconcile geography as well as spelling.
251. Which street names moved from one location to another?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Track a candidate name across multiple dated maps and directories.

     **Watch:** Need evidence of relocation of the name, not two unrelated streets with the same name.
252. Where did city boundaries sit in different decades?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Digitize municipal boundaries from selected official historical maps.

     **Watch:** Modern boundaries cannot reconstruct historic limits; document uncertain segments.
253. Which annexation most changed Syracuse’s shape?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Compare documented pre/post-annexation polygons and rank area or shape changes.

     **Watch:** Requires a consistent annexation chronology; define changed most before ranking.
254. Which neighborhood names have disappeared from maps?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Compare labels on several dated maps with a declared current neighborhood list.

     **Watch:** An absent map label does not prove residents stopped using the name.
255. Which names survived after the places they described disappeared?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [streets](datacuse-data-guide.md#streets).

     **Start:** Select a surviving place name and document the former feature it refers to.

     **Watch:** Avoid folk etymology; cite a dated primary record.
256. Which selected corners had the most listed businesses in two historical city directories?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Count listed establishments around selected intersections in two directory years.

     **Watch:** No comparable historical footfall series found; directory businesses are not pedestrian counts.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
257. Where did streetcar routes shape today’s commercial streets?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [food](datacuse-data-guide.md#food).

     **Start:** Digitize a dated streetcar map and compare former corridors with current commercial locations.

     **Watch:** Spatial overlap does not prove streetcars caused today's business pattern.
258. How far could you travel by streetcar in an hour?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Locate a period timetable and map an example one-hour itinerary.

     **Watch:** A route map lacks travel times; if no timetable is found, map route reach without a time claim.
259. Which former streetcar destination still draws crowds?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Match a documented streetcar destination with its present use and public activity.

     **Watch:** Still draws crowds needs current attendance evidence or carefully labeled observation.
260. Where were the city’s public markets?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Compile public-market locations from dated maps, directories, and city records.

     **Watch:** Distinguish municipal markets from private businesses named Market.
261. Which school building outlived the school it housed?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Choose a former school and document its school years and subsequent use.

     **Watch:** Verify current use; assessment land-use codes can lag.
262. Which firehouse became something unexpected?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Find a documented former firehouse and compare dated records with today's use.

     **Watch:** A garage-like facade is not enough to establish firehouse history.
263. Where did a church become a different kind of gathering place?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Document one former church's transition to another gathering use.

     **Watch:** Verify dates and avoid assuming the congregation ceased to exist.
264. Which building has changed addresses without moving?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Match the same structure across a documented renumbering or street rename.

     **Watch:** Historic address geocoding alone can send you to the wrong property.
265. Which building actually moved?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Find a primary account of a building move and map its origin and destination.

     **Watch:** A changed address is not proof that the building physically moved.
266. How old is one surviving painted advertisement in Syracuse?

     **Data:** Research. **Effort:** Setup. **Sources:** [photos](datacuse-data-guide.md#photos), [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Locate a visible ghost sign and date the advertised business from records.

     **Watch:** No complete inventory can establish the oldest surviving sign; bound the investigation.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
267. Which historic photograph can be matched most precisely to today’s view?

     **Data:** Research. **Effort:** Setup. **Sources:** [photos](datacuse-data-guide.md#photos), [field](datacuse-data-guide.md#field).

     **Start:** Choose an archival image with recognizable fixed landmarks and reproduce its viewpoint.

     **Watch:** Check image rights and caption/date evidence; do not overstate alignment precision.
268. Where has the skyline changed least?

     **Data:** Research. **Effort:** Setup. **Sources:** [photos](datacuse-data-guide.md#photos), [field](datacuse-data-guide.md#field).

     **Start:** Compare skyline photographs from matched viewpoints and count surviving landmarks.

     **Watch:** Scope least changed to the viewpoints compared, not every possible view.
269. Which ambitious proposed project survives only in a rendering?

     **Data:** Research. **Effort:** Project. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Find an original proposal rendering and document what happened to its site.

     **Watch:** A rendering alone does not prove formal approval or cancellation.
270. What did Syracuse once confidently predict about its own future?

     **Data:** Research. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history).

     **Start:** Select a dated plan or advertisement containing a concrete local prediction and compare outcomes.

     **Watch:** Choose the prediction before judging it; distinguish promotion from adopted policy.

## City services and how daily life shows up in records

271. What is the most common Cityline request category?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Count unique request IDs by normalized Request_type or Category.

     **Watch:** Category fields differ; identify the one used and the snapshot period.
272. Which request category has the strongest seasonal pattern?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Calculate category shares by month across complete years.

     **Watch:** New categories and partial years can mimic seasonality.
273. What day of the week gets the most requests?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Parse Created_at_local and compare requests per occurrence of each weekday.

     **Watch:** Normalize for weekday counts and incomplete months.
274. What time of day do people report problems?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Plot creation-hour distribution from local timestamps.

     **Watch:** Report entry time is not the time the problem occurred; handle daylight saving.
275. How different are weekend requests from weekday requests?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Compare per-day rates and category mixes for weekends versus weekdays.

     **Watch:** Five weekdays and two weekend days require rate normalization.
276. Which request types spike after heavy rain?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [weather](datacuse-data-guide.md#weather).

     **Start:** Define heavy rain and compare category counts before/after covered rain events.

     **Watch:** Reporting lag and seasonal confounding limit causal conclusions.
277. Which request types spike after a thaw?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [weather](datacuse-data-guide.md#weather).

     **Start:** Define thaw episodes with temperature/snow-depth data and plot request patterns.

     **Watch:** A thaw proxy is not a direct road-surface measurement.
278. How long after a windstorm do tree-related requests peak?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [weather](datacuse-data-guide.md#weather), [gauges](datacuse-data-guide.md#gauges).

     **Start:** Get verified storm dates or NOAA wind observations and align tree-request timing.

     **Watch:** The local daily weather file has no wind field; do not infer windstorms from temperature.
279. What does the annual pothole-reporting season look like?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Plot pothole requests by week or month for complete covered years.

     **Watch:** This measures reporting season, not when all potholes formed.
280. Does pothole-reporting season move around with the weather?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [weather](datacuse-data-guide.md#weather).

     **Start:** Compare annual pothole-report peaks with freeze/thaw measures.

     **Watch:** Few complete years and reporting changes limit claims about weather effects.
281. Which categories contain problems that seem to belong elsewhere?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Manually code a random sample of request summaries against assigned categories.

     **Watch:** Treat disagreement as a coding judgment; avoid exposing personal details.
282. How often do residents use “other,” and for what broad themes?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Count Other-like labels and code broad themes from a documented sample.

     **Watch:** Free text needs redaction; estimate themes only within the sampled population.
283. When do request labels first appear or disappear in the Cityline extract?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Track observed category labels and their first/last appearances in the extract.

     **Watch:** No verified category change log was found; first observed does not mean newly created.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
284. How many Cityline reports look like possible repeats under a stated rule?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Flag nearby same-category reports within a time window and manually review examples.

     **Watch:** The snapshot has no verified duplicate/follow-up flag; proximity alone is insufficient.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
285. How much does deduplication change the apparent map of problems?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Compare maps before/after grouping candidate repeat reports under several thresholds.

     **Watch:** Call this sensitivity to possible repeats, not verified duplicate removal.
286. Where do requests cluster after accounting for street length?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [streets](datacuse-data-guide.md#streets).

     **Start:** Aggregate requests to consistent areas and divide by public street length.

     **Watch:** Geocoding gaps and reporting propensity remain even after exposure adjustment.
287. How different are request counts per resident and per street mile?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [streets](datacuse-data-guide.md#streets), [census](datacuse-data-guide.md#census).

     **Start:** Compare neighborhood or tract rates using population and street length denominators.

     **Watch:** Use matching geography and dates; neither denominator measures all service need.
288. Which neighborhoods report a wider variety of issues?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Spatially join requests to documented neighborhood geography and measure category diversity.

     **Watch:** Areas with more reports tend to show more categories; adjust or show sample sizes.
289. What share of requests concern a handful of recurring locations?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Cluster repeated geocoded locations with an explicit tolerance and rank their report shares.

     **Watch:** Approximate or default coordinates can create artificial hotspots.
290. How does recorded closure time vary by request type?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Compare median and upper-percentile Minutes_to_Close for records with valid closure times.

     **Watch:** Closed records exclude still-open cases; administrative closure is not verified repair.
291. How much do a few very old requests distort average closure time?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Compare mean, median, and trimmed mean closure times by category.

     **Watch:** Do not silently drop old requests; show the effect of exclusion explicitly.
292. What does “closed” actually mean in the service-request data?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [cityhelp](datacuse-data-guide.md#cityhelp).

     **Start:** Read official status explanations and inspect a small sample of public request histories.

     **Watch:** An export's Closed_at_local does not establish whether a physical repair occurred.
293. Which Cityline categories have the largest share without a recorded closure date?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Calculate missing-closure shares by category within matched creation cohorts.

     **Watch:** No reopen-event history was verified in the snapshot; missing closure means no recorded closure at extraction.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
294. What does one ordinary day of city-service requests look like?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Choose a fully covered ordinary day and show requests by hour, type, and broad area.

     **Watch:** Avoid publishing personal descriptions or precise household details unnecessarily.
295. Which public assets generate surprisingly few reports?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline), [trees](datacuse-data-guide.md#trees), [streets](datacuse-data-guide.md#streets).

     **Start:** Compare recorded tree locations with tree-related requests by street using matching coverage.

     **Watch:** No report does not establish no defect or good service; other asset types need their own inventory.
296. How do reported streetlight problems change as nights get longer?

     **Data:** Local. **Effort:** Setup. **Sources:** [cityline](datacuse-data-guide.md#cityline).

     **Start:** Plot streetlight request counts by month and compare broad daylight-season patterns.

     **Watch:** Seasonal correlation is not proof that darkness causes failures.
297. How much street paving happens in a typical year?

     **Data:** Local. **Effort:** Setup. **Sources:** [paving](datacuse-data-guide.md#paving), [streets](datacuse-data-guide.md#streets).

     **Start:** Measure route miles in each road-project layer and distinguish completed work from plans.

     **Watch:** The verified layers include planned reconstruction; do not label all rows completed paving.
298. Where have water-main breaks recurred on the same street?

     **Data:** Local. **Effort:** Setup. **Sources:** [water](datacuse-data-guide.md#water), [streets](datacuse-data-guide.md#streets).

     **Start:** Group confirmed break events by reconciled street name or segment and map repeat locations.

     **Watch:** Available confirmed years have gaps and different schemas; reports are not confirmed breaks.
299. How does recorded water-main-break seasonality compare with temperature?

     **Data:** Local. **Effort:** Setup. **Sources:** [water](datacuse-data-guide.md#water), [weather](datacuse-data-guide.md#weather).

     **Start:** Compare break counts with daily or monthly temperature over overlapping confirmed years.

     **Watch:** Exclude incomplete years and label association; airport temperature is not pipe temperature.
300. What city work is easy to count but hard to explain?

     **Data:** Local. **Effort:** Quick. **Sources:** [cityline](datacuse-data-guide.md#cityline), [paving](datacuse-data-guide.md#paving).

     **Start:** Choose one service metric and trace the difference between record count and real-world outcome.

     **Watch:** Make the data-definition ambiguity the story rather than claiming a performance ranking.

## Numbers that challenge local intuition

301. Is Syracuse closer to New York City or another major city?

     **Data:** Public. **Effort:** Quick. **Sources:** [boundary](datacuse-data-guide.md#boundary).

     **Start:** Use documented city-center coordinates and calculate great-circle distances to selected major cities.

     **Watch:** Choose straight-line versus travel distance; do not mix center definitions.
302. How many people live within one mile of downtown?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Define downtown's center and allocate 2020 block population to a one-mile circle.

     **Watch:** Partially intersected blocks need an allocation assumption; circle is not a walkshed.
303. How many live within a mile of the city boundary?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Intersect populated blocks with an inward one-mile boundary buffer.

     **Watch:** Clarify whether residents on both sides of the boundary count.
304. Which part of Syracuse is farthest from the city limits?

     **Data:** Public. **Effort:** Setup. **Sources:** [boundary](datacuse-data-guide.md#boundary).

     **Start:** Find the point maximizing distance from the municipal boundary.

     **Watch:** Specify planar distance and whether water or inaccessible land is excluded.
305. How much of the city lies within walking distance of its boundary?

     **Data:** Public. **Effort:** Project. **Sources:** [boundary](datacuse-data-guide.md#boundary), [osm](datacuse-data-guide.md#osm), [census](datacuse-data-guide.md#census).

     **Start:** Route from populated blocks to verified public city-boundary crossings.

     **Watch:** Walking to a boundary line differs from crossing it via a legal route.
306. Which neighborhood’s population center sits somewhere unexpected?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Define neighborhood polygons and weight block locations by population.

     **Watch:** Parcel neighborhood codes require a documented boundary construction; do not mix definitions.
307. Where are workplace jobs concentrated compared with resident workers?

     **Data:** Public. **Effort:** Setup. **Sources:** [lodes](datacuse-data-guide.md#lodes), [census](datacuse-data-guide.md#census).

     **Start:** Compare LODES workplace jobs and resident-worker totals across fixed areas.

     **Watch:** LODES measures covered employment, not everyone present during the day.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
308. Where do household size and housing-unit density tell different stories?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Join household-size and housing-unit density estimates for the same tract vintage.

     **Watch:** Different denominators explain different patterns; include ACS margins of error.
309. Which areas have lots of bedrooms but relatively few children?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Compare tract bedroom distributions with child populations as separate area measures.

     **Watch:** Aggregate tables cannot establish which households have unused bedrooms.
310. Where do college enrollment and group quarters complicate neighborhood population comparisons?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Map college enrollment and group-quarters populations, then explain Census residence rules.

     **Watch:** No monthly student-population series was found; ACS cannot measure term-time changes.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
311. Where are the biggest differences between city and ZIP-code statistics?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census), [boundary](datacuse-data-guide.md#boundary).

     **Start:** Compare city estimates with overlapping ZCTAs and show their geographic mismatch.

     **Watch:** ZCTAs approximate postal geography and are not actual ZIP delivery boundaries.
312. How much does the answer change when “Syracuse” means the metro area?

     **Data:** Mixed. **Effort:** Quick. **Sources:** [census](datacuse-data-guide.md#census), [peers](datacuse-data-guide.md#peers).

     **Start:** Compare the same indicator for Syracuse city and its documented metro geography.

     **Watch:** Use the same year, measure, and universe; metro definitions may change.
313. Which Census tract changed shape enough to complicate historical comparisons?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Use Census tract relationship files and boundary overlays to identify major changes.

     **Watch:** Raw tract-code matching is insufficient for historical comparison.
314. What looks dramatic on a map but represents very few people?

     **Data:** Public. **Effort:** Quick. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Pair a tract percentage map with its denominator counts and uncertainty.

     **Watch:** Do not choose a tiny denominator just to exaggerate a contrast without explaining it.
315. Which neighborhood ranking disappears after accounting for uncertainty?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Compare tract estimates and margins of error for a chosen ranking.

     **Watch:** Overlapping intervals alone are not a formal test; use Census comparison guidance.
316. How much can a citywide average hide between neighborhoods?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Compare a citywide rate with same-definition tract rates and denominators.

     **Watch:** Weight rates correctly; a mean of tract percentages may not equal the city rate.
317. Which areas have the most residents who recently moved?

     **Data:** Public. **Effort:** Quick. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Download ACS geographic-mobility tables for city tracts and compare recent-mover shares.

     **Watch:** ACS measures specified prior-residence periods, not all residential turnover.
318. Which have the most residents living in their birth state?

     **Data:** Public. **Effort:** Quick. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Use ACS place-of-birth tables to compare residents born in their state of residence.

     **Watch:** Being born in New York does not mean someone has always lived here.
319. How has the share of households without cars changed?

     **Data:** Mixed. **Effort:** Quick. **Sources:** [peers](datacuse-data-guide.md#peers), [census](datacuse-data-guide.md#census).

     **Start:** Reuse cached city ACS data if vehicle variables exist; otherwise download matching no-vehicle tables.

     **Watch:** A city time series is available more easily than harmonized neighborhood trends.
320. How do reported commute times differ between transit riders and drivers?

     **Data:** Public. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Compare ACS travel-time distributions by commute mode for matching areas and years.

     **Watch:** No linked distance/time microdata were verified; aggregate LODES and ACS are not the same trips.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
321. How does working from home vary across the city?

     **Data:** Public. **Effort:** Quick. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Download tract work-from-home shares for one ACS five-year vintage.

     **Watch:** Five-year estimates average a period; they are not a current daily attendance survey.
322. Which occupations are unusually common here compared with the country?

     **Data:** Public. **Effort:** Quick. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Calculate occupation shares or location quotients against the national ACS distribution.

     **Watch:** Match occupation categories and working-population universes; show uncertainty.
323. How do Syracuse’s housing ages compare with those of peer cities?

     **Data:** Mixed. **Effort:** Quick. **Sources:** [peers](datacuse-data-guide.md#peers), [census](datacuse-data-guide.md#census).

     **Start:** Compare ACS year-built distributions for a clearly defined peer-city group.

     **Watch:** Cached indicators may not contain all age bins; download missing variables consistently.
324. Is Syracuse unusually compact for a city of its population?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [peers](datacuse-data-guide.md#peers), [boundary](datacuse-data-guide.md#boundary), [census](datacuse-data-guide.md#census).

     **Start:** Compare land area, population density, and a declared boundary compactness measure for peers.

     **Watch:** Administrative boundaries differ; compactness is not density or walkability.
325. How many miles of mapped public streets fit inside Syracuse?

     **Data:** Local. **Effort:** Quick. **Sources:** [streets](datacuse-data-guide.md#streets).

     **Start:** Sum cleaned public-street centerline length and compare street classes or areas.

     **Watch:** Centerlines lack dependable width; they cannot measure road-surface acreage.

     **Revised after data review.** Original wording and reason: [revision log](datacuse-data-guide.md#revisions-made-in-this-review).
326. How much of downtown is surface parking?

     **Data:** Manual. **Effort:** Setup. **Sources:** [imagery](datacuse-data-guide.md#imagery), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Define downtown, trace surface-parking polygons from dated imagery, and calculate area share.

     **Watch:** Parcel use codes do not isolate paved parking; exclude garages and roads consistently.
327. How many football fields fit inside downtown’s surface parking lots?

     **Data:** Manual. **Effort:** Quick. **Sources:** [imagery](datacuse-data-guide.md#imagery).

     **Start:** Reuse DC326's measured parking area and convert using a clearly stated football-field size.

     **Watch:** This depends on the parking audit; say whether end zones count.
328. How much land would one parking space per resident occupy?

     **Data:** Public. **Effort:** Quick. **Sources:** [census](datacuse-data-guide.md#census).

     **Start:** Multiply a population estimate by an explicit parking-space area and show several assumptions.

     **Watch:** A hypothetical scenario: stalls alone omit aisles, circulation, and access.
329. What would Syracuse look like if neighborhoods had equal populations?

     **Data:** Public. **Effort:** Project. **Sources:** [census](datacuse-data-guide.md#census), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Build a population cartogram using documented neighborhood areas and allocated block counts.

     **Watch:** A cartogram distorts geography intentionally; label estimates and boundary choices.
330. What is the most misleading technically correct statistic you can make about Syracuse?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [census](datacuse-data-guide.md#census), [cityline](datacuse-data-guide.md#cityline).

     **Start:** Show how two valid denominators or map scales tell different stories, then explain both.

     **Watch:** Keep the demonstration transparent and avoid leaving the misleading version uncorrected.

## Field trips, friendly arguments, and delightfully unnecessary investigations

331. Can you walk a route that spells “SYRACUSE”?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Design a legal walk approximating letter shapes and verify the route on foot.

     **Watch:** The spelling is a visual design choice; no existing dataset supplies the finished route.
332. What is the shortest walk that visits five neighborhoods?

     **Data:** Public. **Effort:** Project. **Sources:** [osm](datacuse-data-guide.md#osm), [parcels](datacuse-data-guide.md#parcels).

     **Start:** Use a declared neighborhood boundary set and search short walks crossing five areas.

     **Watch:** Boundary definitions drive the result; confirm every segment is public.
333. Can you visit every presidential street in chronological order?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [osm](datacuse-data-guide.md#osm).

     **Start:** Match presidential surnames, choose visit points, and route them chronologically.

     **Watch:** Name matches do not prove namesakes; verify origin if the story claims it.
334. What is the shortest route through every tree-named street?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [trees](datacuse-data-guide.md#trees), [osm](datacuse-data-guide.md#osm).

     **Start:** Reuse the tree-name dictionary, choose a point on each street, and optimize a walk.

     **Watch:** Visiting one point differs from walking every street's full length.
335. Can you walk uphill to a place whose name suggests it is downhill?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [terrain](datacuse-data-guide.md#terrain), [field](datacuse-data-guide.md#field).

     **Start:** Screen low/down/valley-like names and compare actual route elevation gains.

     **Watch:** Make a small verified example; linguistic interpretation is subjective.
336. Which “view” street names still deliver a view?

     **Data:** Manual. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [field](datacuse-data-guide.md#field).

     **Start:** Visit public viewpoints on streets containing View and photograph what is visible.

     **Watch:** Record season and viewpoint; a view from private property is not public access.
337. Which “park” street names are nowhere near a park?

     **Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [parks](datacuse-data-guide.md#parks), [osm](datacuse-data-guide.md#osm).

     **Start:** Find Park-named streets and measure distance to documented park entrances.

     **Watch:** A present-day mismatch does not establish the street's original naming intent.
338. Which “lake” or “water” names preserve a vanished feature?

     **Data:** Research. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [history](datacuse-data-guide.md#history).

     **Start:** Investigate one water-related street name against dated maps and naming records.

     **Watch:** Water in a name is not proof of a vanished water feature.
339. Where is the best public spot to photograph the most steeples?

     **Data:** Manual. **Effort:** Project. **Sources:** [terrain](datacuse-data-guide.md#terrain), [field](datacuse-data-guide.md#field).

     **Start:** Photograph panoramas from selected public viewpoints and count identifiable steeples.

     **Watch:** Best is among audited viewpoints; terrain models alone miss buildings and vegetation.
340. Which public viewpoint reveals the most different construction decades?

     **Data:** Manual. **Effort:** Project. **Sources:** [parcels](datacuse-data-guide.md#parcels), [field](datacuse-data-guide.md#field).

     **Start:** From selected viewpoints, identify visible buildings and verify recorded construction decades.

     **Watch:** Assessment dates need checking and obscured buildings cannot be counted reliably.
341. Can one photograph capture a century of building styles?

     **Data:** Manual. **Effort:** Setup. **Sources:** [history](datacuse-data-guide.md#history), [field](datacuse-data-guide.md#field).

     **Start:** Choose one public viewpoint and document the ages/styles of buildings visible together.

     **Watch:** Architectural style alone cannot establish a precise construction year.
342. What is the most colorful block, using a repeatable photo method?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Photograph selected blocks with fixed lighting/framing rules and compare color measures.

     **Watch:** Shadows, season, cameras, and parked cars affect results; state the sample.
343. How many different paving materials appear on one short walk?

     **Data:** Manual. **Effort:** Quick. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Walk a defined short route and photograph each distinct paving material.

     **Watch:** Use consistent categories and count visible surfaces only.
344. Which block has the most different fence styles?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Audit fence styles on several equal-length block faces.

     **Watch:** Most means among audited blocks unless you complete a citywide survey.
345. What is the longest row of visibly different front doors?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Photograph continuous front-door sequences on selected public streets and classify differences.

     **Watch:** Visibility, duplicates, and subjective design categories need explicit rules.
346. Where can you find the most dates carved into buildings?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Inventory visible carved dates along a defined route and map their locations.

     **Watch:** A carved date may mark a founding, renovation, or commemoration rather than construction.
347. What is the oldest date visible from a public sidewalk?

     **Data:** Manual. **Effort:** Project. **Sources:** [field](datacuse-data-guide.md#field), [history](datacuse-data-guide.md#history).

     **Start:** Collect candidate dated inscriptions and verify the oldest among those audited.

     **Watch:** A complete citywide oldest claim is not justified by a casual walk.
348. How many clocks can you see on a downtown walk?

     **Data:** Manual. **Effort:** Quick. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Walk a fixed downtown route and log visible public-facing clocks.

     **Watch:** Define clocks, visibility, and route length; record the visit date.
349. Do the public clocks agree about the time?

     **Data:** Manual. **Effort:** Quick. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Photograph the DC348 clocks against a synchronized reference time during one walk.

     **Watch:** Clocks may stop or change; this is a dated observation.
350. Which public clock is easiest to read from far away?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Compare legibility distance for a small clock sample with a consistent observer/method.

     **Watch:** Weather, vision, and display changes affect the result.
351. How many lions, eagles, and other stone animals guard Syracuse buildings?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Count stone-animal figures on a defined public walking route and make a photo map.

     **Watch:** No complete citywide sculpture inventory was verified; state the survey boundary.
352. Which block contains the most architectural faces looking back at you?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Photograph architectural faces along several equal-length blocks and compare counts.

     **Watch:** Define a face and how repeated ornament counts.
353. Where can you spot initials whose owners have been forgotten?

     **Data:** Research. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field), [history](datacuse-data-guide.md#history).

     **Start:** Find visible initials on one building and trace occupants or builders in dated records.

     **Watch:** Forgotten is not measurable; present a documented identification or unresolved lead.
354. How many historical plaques can you visit in thirty minutes?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Compile verified plaque locations and time a practical 30-minute route.

     **Watch:** Mapped plaques are incomplete; allow time to read them and cross streets.
355. What do historical plaques leave out about the surrounding block?

     **Data:** Research. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field), [history](datacuse-data-guide.md#history).

     **Start:** Transcribe a plaque and compare its account with primary records for the surrounding block.

     **Watch:** Omission is an editorial comparison, not automatically evidence of deception.
356. Which street has the strongest mismatch between its name and appearance?

     **Data:** Manual. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [field](datacuse-data-guide.md#field).

     **Start:** Choose a few literal street-name expectations and photograph the mismatch.

     **Watch:** Strongest is a playful judgment among chosen examples, not a numeric city ranking.
357. Can locals identify neighborhoods from street-grid shapes alone?

     **Data:** Manual. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets), [survey](datacuse-data-guide.md#survey).

     **Start:** Create anonymized street-grid quiz cards and collect voluntary responses.

     **Watch:** A self-selected quiz measures respondents, not all locals.
358. Can locals identify a place from one tiny map fragment?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [survey](datacuse-data-guide.md#survey).

     **Start:** Create tiny map-fragment questions and record guess accuracy and confidence.

     **Watch:** Use consistent difficulty and label the convenience sample.
359. Can locals guess which of two buildings is older?

     **Data:** Manual. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [survey](datacuse-data-guide.md#survey).

     **Start:** Select verified building-age pairs and ask readers which is older.

     **Watch:** Validate the source dates first; architectural appearance can mislead.
360. Which everyday trip do residents most overestimate in distance?

     **Data:** Manual. **Effort:** Project. **Sources:** [survey](datacuse-data-guide.md#survey), [osm](datacuse-data-guide.md#osm).

     **Start:** Ask readers to estimate selected trip distances, then compare with defined routes.

     **Watch:** No existing perception data found; avoid inferring all residents from volunteers.
361. Does “everything is twenty minutes away” survive a defined travel-time test?

     **Data:** Manual. **Effort:** Setup. **Sources:** [osm](datacuse-data-guide.md#osm), [field](datacuse-data-guide.md#field).

     **Start:** Choose destinations and measure timed trips under a stated mode/time protocol.

     **Watch:** Static road networks do not provide reliable live driving times; collect observations.
362. Where would you put a bench after walking the same route with different people?

     **Data:** Manual. **Effort:** Setup. **Sources:** [field](datacuse-data-guide.md#field), [survey](datacuse-data-guide.md#survey).

     **Start:** Walk one route with willing participants, record desired rest points, and compare.

     **Watch:** A small participatory exercise is useful but not a representative accessibility study.
363. What changes when you photograph the same corner every month?

     **Data:** Manual. **Effort:** Project. **Sources:** [field](datacuse-data-guide.md#field).

     **Start:** Start fixed-viewpoint monthly photographs and maintain a dated observation log.

     **Watch:** Requires future collection; existing imagery usually lacks monthly coverage.
364. What is one thing a longtime resident noticed that the maps missed?

     **Data:** Manual. **Effort:** Setup. **Sources:** [survey](datacuse-data-guide.md#survey), [history](datacuse-data-guide.md#history).

     **Start:** Interview a willing longtime resident about one place and verify the lead against maps/records.

     **Watch:** No existing interview dataset found; distinguish recollection from corroborated fact.
365. Which reader question seemed silly but led to the best discovery?

     **Data:** Manual. **Effort:** Project. **Sources:** [survey](datacuse-data-guide.md#survey).

     **Start:** Invite reader questions, choose one answerable with verified sources, and document the investigation.

     **Watch:** The question must first be collected; do not invent a reader contribution.

## Future additions

Add new pitches here with a permanent ID, date added, and category, and add a matching tracker row. Do not renumber the 365 IDs above. Document future pitch revisions in the data guide and update the matching tracker title.

### DC366. Which Syracuse street names rhyme?

**Added:** 2026-09-19. **Category:** Streets, names, and the small absurdities of geography.

**Data:** Mixed. **Effort:** Setup. **Sources:** [streets](datacuse-data-guide.md#streets); pronunciation references and local confirmation to collect.

**Start:** Find rhyming pairs and clusters using the name before its street-type suffix. Map the matches and see whether any rhyming streets intersect or sit near each other.

**Watch:** Shared endings such as Street or Road alone do not count. Distinguish exact rhymes from near rhymes and verify local pronunciations rather than relying on spelling.

### DC367. Which streets are named for prominent Syracuse people, including mayors?

**Added:** 2026-09-19. **Category:** Streets, names, and the small absurdities of geography.

**Data:** Research. **Effort:** Project. **Sources:** [streets](datacuse-data-guide.md#streets), [history](datacuse-data-guide.md#history).

**Start:** Build a documented list of local namesakes, starting with mayors and expanding to other notable Syracuse residents. Map their streets and compare who is commemorated and where.

**Watch:** A matching surname is a lead, not proof of the namesake. Verify naming origins in historical records and distinguish original street names from honorary designations.

**Related:** DC012, Which presidents have streets-and which got skipped?

### DC368. Can Syracuse addresses make 867-5309?

**Added:** 2026-09-19. **Category:** Streets, names, and the small absurdities of geography.

**Data:** Research. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [streets](datacuse-data-guide.md#streets); address-point source to locate.

**Start:** Look for actual house numbers 867 and 5309 on different properties, ideally on the same street. If both exist elsewhere in the city, map the closest pair. Also explore which single house number comes closest to 8675309: define a digit-similarity rule and show numeric distance separately.

**Visual:** Two address plaques joined by a map route, with a phone-keypad-style title. Possible headline: Jenny, we found your addresses.

**Watch:** Check city limits, distinguish actual addresses from street address ranges, and verify that candidate properties are houses before describing them that way. Do not assume either number exists. Keep house numbers separate from apartment numbers and ZIP codes.

**Related:** DC369.

### DC369. Where is Syracuse at its most 6-7?

**Added:** 2026-09-19. **Category:** Streets, names, and the small absurdities of geography.

**Data:** Research. **Effort:** Setup. **Sources:** [parcels](datacuse-data-guide.md#parcels), [streets](datacuse-data-guide.md#streets); address-point source to locate.

**Start:** Rank house numbers by occurrences of consecutive 67, then separately by the total digits that are 6 or 7. Find streets with the most qualifying addresses and compare their share of all addresses so longer streets do not automatically dominate. Bonus: find the nearest pair of actual house numbers 6 and 7.

**Visual:** Oversized house-number tiles with matching digits highlighted, plus a map and a street leaderboard. Possible headline: Six appeal.

**Watch:** Define whether the joke means the sequence 67 or either digit before counting; show both as distinct measures. Deduplicate addresses, exclude unit numbers and ZIP codes, report ties, and do not infer occupied houses from address records alone.

**Related:** DC368.
