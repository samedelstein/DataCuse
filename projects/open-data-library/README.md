# DataCuse Open Data Library

A static, independent catalog at `/projects/open-data-library/`. No runtime dependencies, account, model API, or database. Serve over HTTP; search uses a local JSON index.

```sh
python -m pip install -r requirements.txt
npm run lint
npm test
npm run build
npm run dev
```

Open http://127.0.0.1:8766/. Every dataset also has static HTML, Markdown and JSON. `catalog.json`, `for-ai.json`, `for-ai.txt`, and `llms.txt` serve agents the same metadata as people. `tools/download_arcgis.py` provides a bounded, read-only export with a completeness receipt.

## Evidence and extraction

`data/catalog.json` is the approved ArcGIS inventory. `data/official-catalog.json` preserves the feed used for matching. `sources/manifest.json` contains source URLs and SHA-256 checksums. Original workbooks, PDF and ZIP are retained under `sources/`. `config/reviewed-sources.json` is the extraction version gate, not a permission to publish.

```sh
python scripts/extract.py
python scripts/build.py
```

The extractor reads cached workbook values without recalculating or changing the source; exports seven fund sheets per edition; preserves field values in all 25 CRB CSVs; and extracts water-report Tables 8, 19 and 20. `City Rates` and other PDF tables remain original-only. Dataset validation reports describe the exact checks. Source arithmetic and undefined codes are not silently corrected.

## Manual refresh

```sh
python scripts/refresh.py --output candidate
```

The command writes a candidate catalog, raw metadata evidence, document downloads, extracts and `report.json`. It never replaces approved data. Failures, rate limits, changed fields, new official matches, source checksum changes and missing services are reported. A source missing from an inventory is retained with `not-listed-this-check`; inaccessible sources retain their previous metadata. Neither state establishes deletion.

Review `candidate/report.json`, any changed schemas and source documents. For a changed document, inspect and validate the new version before updating `config/reviewed-sources.json`. After review, copy candidate catalog to `data/catalog.json` and candidate official feed to `data/official-catalog.json`. Copy candidate official-report.json to data/official-reference-report.json. Copy validated extraction outputs, downloads, sources and manifest together. Rebuild and test. Keep previous approved versions in Git. Commit only approved outputs; `candidate/` is ignored. Deployment is a separate step.

The repository's manual **Check open data library** workflow runs the same collection and tests and uploads candidate artifacts. It has read-only repository permissions, no schedule, no commit/push step, and no deployment job.

## Limits

Matching uses item/layer IDs and normalized service URLs; a root link is conservatively treated as a match. Equivalent topics with different IDs can remain. The advanced directory is metadata reviewed, not a completeness certification. Service containers, layers, file tables and subject families are different units. Summary CSVs and budget editions overlap. A source edit timestamp is not its observation coverage.

The default collection includes available official portal references and selected additional sources. The City portal filter shows official references, including any unavailable ones with status labels. Additional selected sources exclude official matches. Official records remain hosted by the city; portal_url links back to data.syr.gov. Permanent detail URLs remain for provenance. Publicly readable data does not imply a blanket reuse license; source terms govern city data. Prompts require a capable assistant or uploaded downloads; this site does not host a chatbot or MCP service.

## Catalog downloads

`catalog.json` is the version 2 discovery index: concise dataset summaries and absolute `metadata_url` links. Fetch a selected dataset's metadata before relying on fields, units, missing-value conventions, provenance or query capabilities. Summaries retain source URLs, availability, catalog membership, check dates and HTML page_url fallbacks on the canonical www.datacuse.com hostname; descriptions are shortened.

`catalog-full.json` preserves the complete original catalog structure, including service inventory and full dataset metadata. `catalog-full.json.gz` contains the identical full snapshot compressed for bulk/offline download. Existing consumers that require inline `fields` or `services` should use the full export. The website's search continues to use `data/search-index.json`.
