# Evidence ledger — October 27, 2026

The [story](index.html) and [dashboard](dashboard.html) describe a saved research snapshot. This ledger identifies the evidence behind the additional findings and the limits of each inference. No city staff were contacted.

## Inventory and publishing

The [DCAT feed](https://data.syr.gov/api/feed/dcat-us/1.1.json) has 188 rows; ArcGIS item types identify 136 unique Feature Service items. Pages, maps, apps, packages, service definitions, and an inaccessible document account for the other 52. The default series uses item creation dates. Formal publication dates, when available, form a separate selectable measure. Neither reconstructs historic inventory totals.

The initial catalog snapshot is `data/snapshots/20261027T115322Z.zip`. Normalized rows and summary calculations are in `data/catalog-analysis.json`. See README for original methods and independent historical checkpoints. Fifteen 2023-created assessment final-roll items describe pre-2023 coverage; this is a backfill finding, not 15 new subject areas.

## Service directory

Source: [ArcGIS service directory](https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services?f=pjson). The directory lists 350 FeatureServer roots. Root matching decodes URL escapes, ignores case, and removes layer suffixes. It finds 132 matches and 218 without a portal dataset match; four catalog roots are elsewhere. Metadata succeeds for 349. The unavailable metadata response is not evidence of intentional withdrawal.

Directory responses are saved as `research/service-directory.json` and `research/directory-service-NNN.json` in the evidence archive. `data/service-directory.csv` preserves names, roots, item IDs, match results, layer names, access checks, and timestamps. These are service containers; views, duplicates, app layers, and nonproduction layers may be included. They cannot be added to 136 to calculate unique city datasets.

Successful count-only queries of unlinked layer 0 returned:

| Service name | Count |
|---|---:|
| 2022_Fire_data_csv | 78 |
| 2023_Fire_Data_csv | 83 |
| 2024_Fire_Data_csv | 84 |
| Certificate_of_Compliance_(Housing) | 2,491 |
| Potholes_filled_2018 | 3,462 |

The saved `extra-count-*.json` responses include the complete query URL. Counts establish nonempty queryable layers, not complete incident coverage. A query to layer 0 of `2021_Road_Rating` returned an invalid-URL response; that does not establish the service itself is unavailable.

## Record coverage and interruption notices

`research/coverage-{item_id}.json` contains aggregate count/min/max responses. No addresses, names, or individual incident records were collected for this analysis.

| Item | Reported service edit | Record evidence | Interpretation |
|---|---|---|---|
| [Permit Requests](https://data.syr.gov/datasets/cf857fb2f72a448c8ef712cc667768c4_0/about) | 2025-11-12 | 47,902 records; latest Issue_Date 2025-08-16 | Monthly declaration; description acknowledges technical interruption on 2025-11-12. |
| [2025 Crime Part 1](https://data.syr.gov/datasets/92bcecf4355140a98b9bba3cd8ecdca2_0/about) | 2025-11-17 | 33 records; DATEEND 2025-01-01 through 2025-01-05 | Description acknowledges technical interruption in a 2026-01-30 notice. |
| [SYRCityline](https://data.syr.gov/datasets/6c1981e96f1940a99b201482c3b7b6a9_0/about) | 2025-11-12 | 116,143 records; dates are strings, not independently range-validated | Title says 2021–January 2025; monthly declaration. No interruption reason in the reviewed description. Links to SeeClickFix may provide newer information. |
| [Water Main Breaks 2022](https://data.syr.gov/datasets/c8be66d9d53945edad5886e914418b68_0/about) | See inventory | 231 records; 2022-01-03 through 2022-12-18 | A historical edition. Newer water-quality reports contain different observations. |

A date-only Cityline sample request encountered an ArcGIS rate-limit response. We did not treat lexicographic string minima/maxima as chronological bounds, and did not infer a complete interval from a few sample values. A service edit date is not the latest event date.

## Columns and schema comparisons

All 136 layer schemas are retained in `data/evidence.json`; flattened definitions are in `data/schema-fields.csv`. Six reviewed pairs appear in the dashboard, with source links and cautions:

- Permits: 16 to 9 fields. Older includes valuation, payment, application date and status; newer adds owner and work description. Different scopes/workflows, both still available; not a historic version diff of one item.
- Parcels Q1/Q3/Q4 2024: 62 to 27 to 69. Ownership and assessed values disappear from the middle edition and return in the following one. No reason was found in the compared descriptions.
- Parcels Q4 2025/Q3 2026: 68 to 65. Only `OBJECTID_1`, `LATITUDE`, `LONGITUDE` omitted; polygon geometry remains.
- Parcels Q3 2017/Q3 2026: 57 to 65. Earlier `TotTaxOwed`, `TaxYrsDeli`, `OverdueWat` have no direct named counterparts in the latest schema. They may be available through other sources.
- Crime Part 1 2018/2024: 7 to 10. Explicit coordinates and LarcenyCode added; DATEEND changes from string to date. Both layers have geometry and generalized locations.

Field matching ignores case only. Renames, conceptual equivalents, workflow differences, and additional sources require human review. Counts include technical fields; no assertion about non-null completeness is made. Comparisons use separate editions retrieved now, not historic snapshots of the same service. Data dictionaries are mentioned in 131 descriptions, but this is not a count of validated, current dictionaries.

## Archived links

We queried the [Wayback CDX index](https://web.archive.org/cdx/search/cdx?url=data.syrgov.net%2Fdatasets%2F%2A&output=json&filter=statuscode%3A200&collapse=urlkey&fl=timestamp%2Coriginal%2Cmimetype&limit=3000) for successful captures under the former `/datasets/` path. The response yielded 179 URL records, including irrelevant resources and repeated item routes. Extracting 32-character item IDs and excluding current feed IDs left 75 candidates. Current item API checks return 54 permission-denied results, 16 missing-or-inaccessible results, and five public items absent from the feed. Sixty-one titles were recovered from archived page titles or current public metadata; generic portal titles are not treated as dataset titles.

Two illustrated cases are Syracuse Lead Violations (archived 2022-08-11) and Capital Project and Grant Funds (archived 2019-08-25), both now returning permission denied. Full archive URLs, current API URLs, checks, and any directory service matches are in `data/historical-items.csv`. The sample includes pages and maps; it is not 75 unique lost datasets. Capture dates are not deletion dates. Missing/inaccessible and permission denied do not prove deletion. No comprehensive retirement log was obtained.

The [Project Archive](https://www.arcgis.com/sharing/rest/content/items/422bd85665b64634ac3c91aef5b2cdab/data?f=json) explains broken links/accessibility for community projects. [Budget Archives](https://www.syr.gov/Departments/Budget/Budget-Archives) provides context for archived budget documents. Neither explanation is generalized to other missing items. “No explanation found” always refers to reviewed material, not proof no explanation exists.

## Data on syr.gov outside the portal

Searches included `site:syr.gov filetype:csv`, `site:syr.gov ".csv" download`, `site:syr.gov filetype:xlsx`, and `site:syr.gov filetype:pdf data`. No standalone city-hosted CSV was confirmed in this sample. Search engines do not exhaustively enumerate files.

Primary pages and verification limits are listed in [off-portal-resources.json](data/off-portal-resources.json). The Auditor links 2025 and 2026 XLSX budget workbooks; Water lists three report series for 2019–2025; CRB links PDF reports and ZIP data outputs, including October 2026; Budget lists newer fiscal-year material than the portal's latest titled budget; Police and SIDA maintain separate report indexes. Exact candidate URLs were checked against the full saved feed text; a lack of exact URL matches does not exclude topic overlap or links from non-dataset Hub pages.

The official pages were readable through web search/open tooling. Direct scripted requests to several city pages returned HTTP 403; these errors remain in `research/source-*.json` and do not mean the public pages are unavailable to residents. XLSX/ZIP binary contents were not inspected. Text of the [2025 water-quality report](https://www.syr.gov/files/sharedassets/public/v/1/departments/water/documents/reports/water-quality-annual-reports/quality-annual-report-2025.pdf) was inspected: the document includes measurement and sampling tables. No claim that PDF tables are equivalent to a reusable, validated dataset is made.

## AI/agent readiness

The [city's code-violations-chatbot repository](https://github.com/CityofSyracuse/code-violations-chatbot) publishes instructions and an OpenAPI 3.1 contract. Saved GitHub API blobs are `research/chatbot-schema.json` and `research/chatbot-instructions.json` (base64-encoded content, with blob hashes). Its default outFields includes `owner_name`, absent from the current Code_Violations_v2 layer. Its attribute response schema specifies strings generically, while the live layer has individual field types. This is a contract mismatch, not a tested failure of a deployed chatbot.

Readiness findings distinguish machine access from reliable interpretation: working JSON/query endpoints and dictionary links are positives; scattered discovery, inconsistent temporal meaning, unresolved contact placeholders, unstructured outage notices and replacement histories limit unattended use. Feed contact-email values use `{{orgContactEmail}}`; some descriptions contain real contact information. API clients must handle pagination, errors and rate limits. No unsupported readiness percentage or certification is assigned.

## Reproduction and future changes

The companion evidence archive preserves both current raw catalog metadata and the research responses. JSON wrappers retain source URLs, check times, HTTP status or error, and response data/text where available. Search-read city-page findings are separately documented above rather than represented as successful scripted fetches. See README for commands. The static narrative must be reviewed after any data refresh; it is intentionally dated.
