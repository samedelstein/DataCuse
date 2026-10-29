# Syracuse, Parcel by Parcel

A static, story-led exploration of thirteen local Syracuse parcel snapshots (2017–2026). No API keys, external map tiles, CDN dependencies, framework install, or runtime server are required in production.

## Run locally

Requires Node 20+ and Python 3.10+.

```powershell
npm run dev
# Open http://127.0.0.1:4173
```

Generated `data/` is ready to serve. To rebuild it from the thirteen original `.geojson` files in this directory:

```powershell
npm run build:data
npm run lint
npm test
npm run build
npm run preview
```

`build` assembles the standalone site in `dist/`. Both the project directory and `dist/` work at a nested URL such as `/projects/parcel_map/`. The existing DataCuse Pages workflow already copies static project files. Commit the HTML, CSS, JavaScript and generated `data/` to publish through that workflow; no root workflow edits are necessary. The public address is https://www.datacuse.com/projects/parcel_map/.

Raw `.geojson` files are intentionally ignored locally: together they are about 965 MB. `data/sources/` contains deterministic gzip copies of the exact bytes; source downloads and the SHA-256 manifest keep the original evidence available without deploying uncompressed duplicates. The pipeline requires the original files for a rebuild. It never modifies them.

## Experience

- Editorial introduction and continuity/age charts.
- Pan/zoom canvas map with address and tax-ID search, date-pair selection, neighborhood filters, and four comparison lenses.
- Keyboard map navigation, zoom buttons, and a paginated parcel list that provides an alternative to map selection.
- Full parcel timelines, source fields, compressed original downloads, and shareable `?parcel=TAX_ID` links.
- Vacancy-to-use paths and prominent persistent-vacancy cards: 3,257 vacant-land parcels and 291 parcels with positive vacant-building flags in all 12 usable snapshots. Both filters are also available above the map and work with neighborhood selections.
- Three property biographies with actual parcel outlines.
- Neighborhood profiles and parcel patterns, tax-block and street-address grouping, and similar-block suggestions weighted equally by land-use and building-age shares.

Neighborhood cards and vacancy stories use the fixed 2017–2026 comparison. Explorer controls affect the explorer only. Geometry and property histories load by tax-section shard as needed; the opening illustration is a small SVG generated from the actual parcel locations.

## Data contract and interpretation

`data/manifest.json` records source labels, exact filenames, checksums, original field aliases, coverage flags, duplicate IDs, dictionaries, and summary denominators. Snapshot dates are file labels, not event dates.

- `index.json`: rows `[taxId, address, neighborhoodIndex, x, y, taxBlock, streetGroup, lastSnapshotIndex]`. IDs stay strings. Positions are locally projected integer coordinates for display, not an area-measurement system.
- `snapshots/{snapshotId}.json` (manifest version 2): rows `[indexPosition, useCode, assessedValue, reliableUnits, ownerLiteral, ownerTokens, ownerCoreTokens, ownerConfirmed]`. `-1` is unknown use; other missing values are null. The four owner fingerprints distinguish literal names, sorted name tokens, possible legal-qualifier variants, and parcel-specific reviewed aliases. Original names remain in the histories.
- `histories/{taxSection}.json`: tax ID to 13 observations. Each observation preserves original values in manifest field order: use, assessment, units, owner, construction year, building-vacancy field, neighborhood, address. A null observation means unavailable or excluded duplicate; the manifest distinguishes these cases. Normalized display values are derived without overwriting originals.
- `geometry/{taxSection}.json`: tax ID to rings from its latest available geometry. Rings preserve holes/parts. They are rounded for rendering and do not establish historical boundary continuity.
- `blocks.json`: latest tax-block totals, land-use counts, age bins, and neighborhood label used for similar-block suggestions.
- `manifest.persistentVacancy`: precomputed index positions and eligible snapshot indices for the separate land-use and vacant-building cohorts. A parcel must be present and positively meet the criterion in every eligible snapshot; blank flags, missing observations, and interrupted histories do not qualify. These flags cannot establish uninterrupted vacancy between snapshot dates.

### Owner-name comparisons

Owner-name changes are not confirmed sales or ownership transfers. Case and whitespace are normalized for literal matches. The same alphanumeric name tokens in a different order or punctuation form a separate `name-format` category; these are not counted under different names or silently merged into the same-owner group. Apostrophes are removed before tokenization. If tokens differ only by a legal qualifier (TRUST, LLC, INC, CORP, CORPORATION, LTD, INCORPORATED, LLP, LP, CO, COMPANY), with at least two remaining tokens, the pair is labeled `possible-name`. These are candidates for review, not established matches.

`scripts/owner_aliases.json` records explicit reviewed matches scoped to a tax ID and exact normalized names. For 1315 Cumberland Ave, the site owner confirmed that MEDICIS LIVING TRUST and LIVING MEDICIS refer to the same owner on October 28, 2026. This user-confirmed match is disclosed in the timeline and is not represented as deed verification. Other names or parcels do not inherit it; a missing observation remains unknown. Run `npm run build:data` after changing this review file.

For August 2017–October 2026, the revised comparison separates 16,047 reordered/reformatted names and 125 possible qualifier matches from 19,576 different-name records. There are 4,000 identical-name or explicitly reviewed matches. All groups are based on parcel records, not a count of home sales.

### Housing-unit date selection

Selecting housing units with unusable dates visibly switches the comparison to Q1 2024–October 2026, the consistent `n_ResUnits` series. The affected early/absent-field dates are disabled while this lens is active. Already valid selections are preserved, including Q1 2020 with a note about its older `Units` field. The default usable comparison has 296 parcels with changed counts and 40,220 with unchanged counts; it is not a count of buildings constructed or demolished. Unit totals use only the same comparable parcel cohort. A view with no usable pairs says “No comparable data,” rather than reporting misleading zero-change metrics.

Comparisons require a unique tax ID in each snapshot and nonmissing values for the selected lens. Duplicate IDs are excluded entirely in their affected snapshot. Counts for earlier-only, later-only and unknown observations are separate from comparable counts. No split/merge inference is made.

The latest neighborhood attribute is held fixed for matched parcel comparisons; historical-only IDs use their last recorded neighborhood. Blank latest labels stay unassigned. Two spelling aliases (Hawley Green / Hawley-Green and Park Ave / Park Ave.) are normalized for grouping; the original spellings remain in histories. Neighborhood panels count latest records only. Construction-year zero is unknown. Unit counts from all four 2017–2019 files are excluded because of contradictions with use classifications; absent unit fields in other exports are also unknown. Zero units on a residential-classified parcel are excluded per record, including in later files. August 2024 has no use/assessment/owner comparison fields.

Unchanged use does not imply unchanged residents or condition. Changes can reflect recoding (for example, schools to community services). Assessed values are nominal assessments, not prices. Name changes are not verified sales. Blank vacant-building fields do not establish occupancy. Longitudinal vacancy paths concern **vacant land**, not vacant buildings. No causal or demographic claims are inferred.

## Verification

`npm test` covers missing values versus zero, each comparison lens, geographic cohorts, duplicate exclusions, geometry parts, source integrity, all snapshot/index alignment, neighborhood denominators, and the actual featured-property transitions. Browser review should cover address selection, all four lenses, the August 2024 missing-data case, source disclosure, vacancy filters, block suggestions, pagination, keyboard controls, responsive layout and deep-link reloads.

Optional ownership-network reporting, parcel genealogy, causal reporting, and external photographs remain outside this first release.
