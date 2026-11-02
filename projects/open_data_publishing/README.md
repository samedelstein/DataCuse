# Syracuse open-data publishing history

Open `index.html` for the narrative story, or `dashboard.html` for the companion interactive evidence dashboard. Both work directly from disk with no external JavaScript dependencies or build step. These static pages are released through the DataCuse repository's GitHub Pages workflow. Research refreshes are manual.

The story links to the sibling Open Data Library and its AI-agent guide. To preview those links together, serve the projects directory: `python -m http.server 8768 --bind 127.0.0.1 --directory ..`, then open `http://127.0.0.1:8768/open_data_publishing/`.

The dashboard shows one topic at a time: current-entry dates, update schedules, coverage, columns, old links, services, or the full dataset list. Topic links support bookmarks and browser history. The story also covers city website downloads and AI/agent readiness. [RESEARCH.md](RESEARCH.md) documents the findings and caveats; [data/off-portal-resources.json](data/off-portal-resources.json) records website sources and what was actually inspected. [PUBLICATION.md](PUBLICATION.md) contains the prepared release details.

## Findings from the October 27, 2026 snapshot

- The public feed has **188 catalog entries**. **136** are confirmed unique Feature Service items, the consistent dataset definition used here. The other 52 include 40 pages, 4 web maps, 4 mapping applications, a web scene, a scene package, a service definition, and an inaccessible document entry (Syracuse PD Personnel Complaints 2021). The raw DCAT feed labels all of these as datasets, so counting its rows alone is misleading.
- Current dataset entries by item creation year: **2017: 11; 2018: 15; 2019: 2; 2020: 0; 2021: 1; 2022: 25; 2023: 36; 2024: 24; 2025: 14; 2026 through October 27: 8.**
- Comparing January 1–October 27 in each year gives **30 in 2023, 21 in 2024, 9 in 2025, and 8 in 2026**. These are surviving entry cohorts, not a complete count of all releases in those years. Entries were created in 11 months of 2023, 9 months of 2024, 7 months of 2025, and 5 months of 2026 so far.
- Formal metadata declares **70 not planned, 5 daily, 5 as needed, 4 annually, 2 monthly, 1 quarterly, and 11 unknown** update schedules. Another **38** have no formal schedule. These are publisher declarations, not measured intervals.
- **8** datasets have a service data-edit timestamp within the previous 30 days, **19** between 91 and 365 days, **99** over a year, and **10** lack a usable timestamp. There are none in the 31–90 day band. Of the 99 older than a year, **56 explicitly declare no planned updates**; old timestamps cannot be equated with neglect.
- All five daily-scheduled datasets report data edits on October 27. Vacant Properties and Syracuse Public Art NEW also report edits that day; the Q3 2026 parcel map reports an October 20 edit. This observation does not establish daily compliance over time or the freshness of each dataset’s records.
- **103** datasets have formal publication dates. **16** differ from the feed’s `issued` calendar date. The alternative chart follows Hub precedence (formal publication, formal creation, item creation); its yearly counts are 11, 13, 3, 0, 1, 26, 37, 23, 14, and 8 for 2017–2026.
- **131 of 136** descriptions mention a data dictionary. None of the feed contact-email values contains a usable address; the feed uses an unresolved template placeholder. This is a feed metadata issue, not evidence that the city has no contact information.

All quantitative findings above are calculated from the saved API responses, preserved in `data/snapshots/20261027T115322Z.zip`. Normalized rows are in `data/datasets.csv` and `data/catalog-analysis.json`.

## What can we say about growth?

The city’s program has expanded since its [July 26, 2017 launch](https://www.innovatesyracuse.com/blog/datacuse). Its [2018 annual report](https://www.syr.gov/Government/City-Reports/2018-Annual-Report/2018-Engagement-Response) describes expansion into spending, procurement, capital projects, and the proposed budget. On [March 3, 2023](https://www.syr.gov/News/City-News/City-2023/2023-03-03-City-News-1130), the city reported 29 additions during 2022 and 2023 to date. A [spring 2024 interview](https://www.hks.harvard.edu/faculty-research/policy-topics/cities-communities/nicolas-diaz-mpp-2020-creating-better-access-data) described over 100 datasets, while its [2024 Maker Faire listing](https://makerfaire.com/yearbook/projects/cityofsyracuseopendataportal-2024/) described nearly 120.

These checkpoints suggest growth but are not an apples-to-apples count series. We cannot subtract them from 136 to measure exact net additions. Nor can we call the 2023 creation peak a peak in entirely new subject areas: annual releases, backfills, hosted views, and replacement services are separate items. The current catalog has eight 2026 entries, six of which are explicitly titled as annual or quarterly editions, alongside two boundary datasets.

**A cumulative curve made from today’s item dates is a history of surviving entries, not the historical size of the catalog.** Removed and formerly private items are not recoverable from this snapshot. A zero in 2020 does not prove that no datasets were published that year. For defensible past inventory totals, obtain archived catalogs, former data.syrgov.net snapshots, or the city’s publication/retirement records. This research has not recovered a complete archived inventory series.

## Sources and fields

1. [Public catalog feed](https://data.syr.gov/api/feed/dcat-us/1.1.json): title, identifier, issued, modified, keywords, publisher, contact, distributions, license, theme, spatial extent.
2. ArcGIS item metadata: `https://www.arcgis.com/sharing/rest/content/items/{item_id}?f=json`. Type, created, modified, owner, service URL. Item IDs are retained in the downloads.
3. Formal metadata XML: `https://www.arcgis.com/sharing/rest/content/items/{item_id}/info/metadata/metadata.xml`. Publication/creation dates and `MaintFreqCd` maintenance declarations. [EPA’s metadata specification](https://www.epa.gov/geospatial/epa-metadata-technical-specification) documents the frequency field; [NOAA’s ISO workbook](https://www.ncei.noaa.gov/sites/default/files/2020-04/ISO%2019115-2%20Workbook_Part%20II%20Extentions%20for%20imagery%20and%20Gridded%20Data.pdf) documents the numeric frequency codes.
4. Catalog-linked feature layer metadata: `editingInfo.dataLastEditDate`, `lastEditDate`, and `schemaLastEditDate`. These are kept separate. All 136 service requests succeeded; 10 data-edit timestamps are zero or unusable.
5. [Esri’s date and frequency documentation](https://doc.esri.com/en/arcgis-hub/latest/build/manage-content-items.html) and [catalog feed mappings](https://doc.esri.com/en/arcgis-hub/latest/build/federate-data.html) explain why these date fields can disagree.

Item timestamps are grouped in UTC. Formal dates without timezones retain their written calendar date. The same-period comparison includes the entire October 27 calendar date in earlier years; the current snapshot was fetched at 11:51 UTC. Dates in titles describe coverage, not publication. Data-edit age measures time since a reported service edit, not the latest event date in the records. A single edit timestamp cannot reveal actual refresh frequency.

## Refresh

Python 3.11 or later; standard library only:

```powershell
python scripts/collect_metadata.py
python scripts/build_data.py
```

The first command requires network access and performs public, read-only requests. It downloads the current feed, public homepage, item metadata, formal XML, and service metadata, then creates a timestamped ZIP snapshot. Raw working responses are ignored by Git; snapshots and normalized outputs are retained. The second command is offline and regenerates the JSON, CSV, and local browser data script. Historical prose in this README describes the first snapshot and is not automatically rewritten.

For future monitoring, compare successive snapshots by item ID and service URL to measure observed additions, removals, reappearances, and timestamp changes. Keep first-seen dates distinct from publisher-supplied publication dates. Polling observes changes between checks and does not recover every intervening update. No recurring job has been created.

## Validation

No package install or build step is needed. Run `node scripts/check_site.mjs` for inventory reconciliation, script initialization, chart controls, searches, schema comparisons, deep links, and local link checks. It uses a small DOM adapter and does not validate browser layout. Syntax checks cover all three page scripts and the Python collectors/builders. The October 27 snapshot passed these checks.

The October 28 editorial review checked the story and dashboard in Edge at desktop and phone widths. Checks covered topic navigation, schema deep links, the 27-to-69 parcel recovery, unmatched-service search, and metadata/cumulative chart controls. No console errors were captured. Phone-width checks found no document-level horizontal overflow in the reviewed story and schema views; wide tables scroll within their containers. Screenshots are saved under `screenshots/`. This was not a formal accessibility audit.

## Expanded evidence and offline reproduction

`data/snapshots/evidence-20261027.zip` preserves 1,068 raw responses and a SHA-256 manifest, including the working catalog metadata used by the final analysis and additional archive/service/API research. Unzip it into `data/` to restore `raw/` and `research/`, then run:

```powershell
python scripts/build_data.py
python scripts/build_evidence.py
node scripts/check_site.mjs
```

These builders are offline. The first snapshot ZIP is retained separately. The pages load generated `catalog-data.js` and `evidence-data.js`, so they work over `file://` as well as HTTP. For local HTTP preview, run `python -m http.server 8765 --bind 127.0.0.1` here and open `http://127.0.0.1:8765/`.

To repeat expanded network research after collecting a new catalog, run `python scripts/research_evidence.py`, then the same command with `--history`, `--captures`, `--directory`, `--followups`, and `--chatbot`, in that order. The `--sources` mode records scripted city-page retrieval attempts; these returned 403 in this run, and the source pages were instead inspected with web tooling. Capture retries are optional and should be used sparingly. Requests are read-only and save source URLs, timestamps, and errors. `python scripts/package_evidence.py` writes the dated evidence ZIP; change its filename for a future edition rather than overwriting this historical record.

The 75 archived links are a partial supplement to the initial catalog analysis, not a complete historic inventory. The story's counts, prose, date labels, and editorial comparisons are curated for October 27, 2026: review and update them deliberately after refreshing data. Running collectors alone will not update the narrative or schedule future monitoring.
