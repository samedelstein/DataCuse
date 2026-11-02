---
name: datacuse-open-data-library-refresh
description: Refresh the DataCuse Open Data Library's Syracuse source inventory and document extracts, review changes, and rebuild its static catalog. Use for this library's data maintenance, not general website research.
---

The project is `projects/open-data-library` in the DataCuse repository. On Sam's machine the default path is `C:/Users/samie/Projects/datacuse/DataCuse/projects/open-data-library`; respect an explicitly supplied checkout.

Read the project's README and run `python scripts/refresh.py --output candidate` from that directory. This reads public city sources and writes candidate results; it does not publish or replace approved files. Inspect `candidate/report.json` for source availability, fields, official-catalog matches and document checksums. A failed required inventory invalidates the scan. An inaccessible source is not evidence of deletion.

Keep service containers, individual layers/tables and unique subject areas distinct. Match by item/layer IDs and normalized URLs; review possible equivalent sources before claiming absence. Preserve permanent dataset URLs and last reviewed data when sources disappear or enter the official portal. The default collection includes available official portal references and selected additional sources. Keep portal_url links and City portal labels; underlying official records remain city-hosted. Review official-report.json for unresolved official references and non-dataset resources. Unavailable entries remain in the full directory and official filter.

For changed document hashes, inspect the actual new source before adding its hash to `config/reviewed-sources.json`. Use PDF page/table references and workbook sheet/cell references. Verify values, row counts, headings, units, missing-value markers, footnotes and reported totals. Do not silently fix source errors. Budget editions and summary tables overlap; actuals, budgets, estimates and proposals must remain separate. Files that cannot be validated remain source-only or keep their prior approved extract with an explicit stale-status note.

After reviewing candidate changes, use the README's promotion steps, run `python scripts/extract.py`, `npm run build`, `npm run lint`, and `npm test`. Check search, a changed dataset page, mobile layout and prompt copying in the browser. People and agents must receive the same metadata. Report the check date, changed-source counts, validation, and any unresolved access or extraction limits.

Refreshing files does not itself request a deployment or changes to the city's live Cody GPT. Follow the user's current publication scope. The manual GitHub workflow only uploads candidate artifacts; it has no auto-commit or deployment step.
