# DC003 — Syracuse's longest street

## Scope and sources

This is a companion to DC002, using the **same September 19, 2026 snapshot**, not a new inventory download. `streets_nys_current.geojson` contains 20,652 NYS features downloaded for the envelope -76.25,42.97,-76.04,43.13. `syracuse_boundary.geojson` supplies the municipal cutoff. Copied source metadata and `nys_provenance.json` retain the original retrieval details. SHA-256 hashes in `results.json` identify the exact inputs.

Sources:

- [NYS Streets](https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS_Streets/FeatureServer/0)
- [NYS city boundaries](https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Civil_Boundaries/MapServer/4)
- [NYS 2022 aerial imagery](https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer), retrieved for candidate review; exact requests in `imagery_sources.json`.
- Cached OpenStreetMap tiles from post 2, retained with `editorial_basemap_sources.json`. Attribution: © OpenStreetMap contributors, https://www.openstreetmap.org/copyright.

Street-service metadata was also inspected during this investigation. It describes a line inventory compiled from imagery and other sources, with names and routing attributes. A CompleteStreetName value is not proof of the wording on a physical sign.

## What counts

Reuse DC002's documented selection: active, named public surface streets; jurisdiction codes 01, 02, 03, 12, 13; FCC A20–A49 plus A61/A62. Exclude route-only designations, unnamed/unknown entries, and names explicitly containing DRIVEWAY, RAMP, ENTRANCE, or EXIT. This is an inventory-based public-street definition, not an independent legal ownership determination. A name must have a qualifying positive-length city intersection and a Syracuse incorporated-municipality attribute on at least one side of a qualifying feature.

The local `street_network.py` retains the eligibility, compatible-elevation noding, and endpoint-grouping helpers from post 2's `calculate.py`. Its old shortest-ranking entrypoint was removed. The longest-street entrypoint is **`calculate.py`**, which writes this post's outputs.

Distances use NAD83 / UTM 18N (EPSG:26918), then metres / 0.3048 for feet or / 1609.344 for miles. Web Mercator is used only for aligning imagery, not for reported lengths. Exact normalized duplicate name/geometry pairs are removed. Every ranked length is clipped to Syracuse; unlike DC002's whole-street shortlist, boundary-crossing streets are eligible, but their outside portions get no credit. The 500-metre buffered input selection supports network context, not a claim about a street's complete out-of-town length.

## Three comparisons

### Individual source segment

Rank each retained source line feature by the length inside Syracuse before joining records. The winner is **Canal Street, NYSStreetID 477433624: 3,358.7905 feet (0.6361 mile)**. It is wholly inside the boundary. The next three features are Erie Boulevard West (3,025.8795 feet), Valley Drive (2,514.0526), and another Erie Boulevard West feature (2,293.6690).

The feature endpoints meet the mapped Peat Street and South Midler Avenue/Simon Drive junctions. The 2022 aerial shows the curved industrial-access alignment north of Erie Boulevard. This verifies the mapped context; it does not certify current access, ownership, or the longest conventional block. Source-feature boundaries are not a consistent physical-block definition. DC002's intersection-to-intersection measure was a different question; its longest candidate is not interchangeable with the single-feature winner here.

### Longest full name

Count alphabetic characters in CompleteStreetName, normalized only for case and whitespace. Include expanded type and directional words. Retain distinct complete names rather than combining North/South or East/West variants. There are **1,192** qualifying names.

| Literal name | Letters | Interpretation |
| --- | ---: | --- |
| East Brighton Avenue Avenue Northbound | 34 | Literal maximum. StreetName itself contains Brighton Avenue, PostType contributes Avenue again, and PostModifier contributes Northbound. Retain and flag; do not silently repair. |
| Genant to North Clinton Connector | 29 | A descriptive connector entry; not established as a posted sign name. |
| West Street Arterial Northbound | 28 | Carriageway-specific entry. |
| West Street Arterial Southbound | 28 | Carriageway-specific entry. |
| Onondaga Creek Boulevard East | 26 | Long conventional street-style entry, fifth in the literal ranking. |
| Elizabeth Blackwell Street | 24 | Selected comparison, sixth in the literal ranking. |

The longest name **field** is settled for this inventory; the longest name on a street sign is not. No sign survey was performed. The letterboard intentionally shows selected comparisons, omitting the two arterial variants, and says it is not a consecutive ranking.

### Whole street: summed geometry and a divided-road review

First union each complete name's clipped geometry and sum its length, regardless of source segmentation. Save all-name totals and the longest connected component separately. Do not silently join disconnected names into one continuous road.

The two leading sums are Erie Boulevard East **5.92760 miles**, then South Salina Street **4.65717 miles**. East Genesee is third at **4.18684 miles** summed across its disconnected components. Every other name's full sum is already below South Salina, so correcting those names' duplicate carriageways or disconnected sections cannot make one overtake it.

South Salina is one connected, unbranched line: **94 original source IDs**, no graph cycles, and an end-to-end path equal to the complete geometry sum, **24,589.8454 feet**. The graph runs from the city boundary at approximately (-76.143542, 42.984941) to the name change at (-76.152177, 43.050912).

Erie Boulevard East requires correction: the inventory has separate lines for its carriageways, confirmed in the aerial near South Midler. The A25 separated-road class accounts for about 24,861 feet of mapped line. Do **not** halve the entire road or assume every divided-road representation is symmetric. Trace the connected same-name graph from its western end at Salina Street to each eastern city-edge carriageway near Thompson Road. Baseline west-to-east paths measure **3.57139 and 3.57488 miles**. Each uses one through route, not both carriageways in series. The article uses about **3.57 miles**. Routing is undirected to compare geometry; it is not a legal driving itinerary.

The all-pairs graph diameter retained in `graph_diameter_rankings.csv` and the `graph_diameter_miles` result field is an internal diagnostic, **not a final corridor ranking**. For Erie its farthest graph nodes are on opposite carriageways near the eastern edge; joining them requires a U-shaped path of about 4.21 miles. This is why the article uses explicitly reviewed west-to-east paths rather than presenting graph diameter as road length. Only South Salina's unbranched path makes its diameter and total interchangeable.

After reviewing the sole raw-total challenger, South Salina is the longest whole named corridor **under this inventory, boundary, and full-name definition**. That does not combine North and South Salina into one road, establish the longest route outside the city, or certify survey accuracy.

## Where South Salina ends

- **North:** the NYS name changes to North Salina at Erie Boulevard, near the downtown James/West Genesee junction. This is a name boundary in the snapshot.
- **South:** the Syracuse polygon crosses South Salina about 48 metres south of its Dorwin Avenue junction. The same name and physical road continue into the Town of Onondaga. The published measurement stops at the city line, not at a dead end or the end of the road's name.

The four candidate overlays in `analysis/review/` were visually inspected: Canal's industrial alignment, Erie's separated carriageways, and both Salina endpoints. Imagery is **2022**, not a current field visit. Overlay geometry dates from the 2026 download; imagery cannot settle later changes.

## Validation and reproduction

From the post folder, using Python with `requirements.txt` installed:

```powershell
python analysis/calculate.py
python analysis/validate.py
python analysis/review_candidates.py
python analysis/make_graphics.py
```

The environment used during creation was `../2_shortest_street/analysis/.venv/Scripts/python.exe`. Scripts and inputs are local to this post; the environment can be replaced by a separate environment. Graphics use Georgia and Arial in `C:/Windows/Fonts`.

`calculate.py` asserts conservation of line length through noding. `validate.py` recomputes at zero and one-metre endpoint tolerance against the half-metre baseline, checking the name/segment winners, South Salina's connectivity and mileage, and Erie's reviewed corridor range. Zero snapping retains extra sub-metre boundary nodes. At one metre, a 0.974-metre South Salina boundary piece contracts to a graph self-loop, shortening the diagnostic path by that amount; the geometry sum stays unchanged. These effects change endpoint counts and tiny graph details, not the rounded mileage or winner. The unbranched-path interpretation is checked at zero and half-metre tolerance. Results are recorded in `validation.json`.

`graphics_audit.json` records plotted results. Five figures have full-size originals and 1400-pixel web exports; the article references the full-size originals, which the renderer makes clickable. `review_candidates.py` uses network only if an aerial is missing. `make_graphics.py` uses saved inputs and cached imagery/tiles.

## Publication state

`story/index.md` is a **draft**. A proposed date is not proof of publication. Preserve slug `syracuse-longest-street`. Remaining uncertainty about street-sign names is explicitly in the story rather than hidden or replaced with a false champion. Publication is not requested in the current task.
