# Publication package

Release authorized November 2, 2026. Story research snapshot: October 27. Library source checks: November 1. This is a standalone project at its existing path, outside the numbered-story generator.

## Release pages

- Story: https://www.datacuse.com/projects/open_data_publishing/
- Dashboard: https://www.datacuse.com/projects/open_data_publishing/dashboard.html
- Data library: https://www.datacuse.com/projects/open-data-library/
- AI-agent guide: https://www.datacuse.com/projects/open-data-library/for-ai/

The release includes homepage links to the write-up and library, plus a manual library-check workflow. The existing pages-projects.yml workflow publishes committed static project files on a push to main. The library-check workflow produces candidate artifacts only; it does not publish changes.

## Review

The chart counts entries still available in the October 27 snapshot by ArcGIS item creation year. Missing historical entries are excluded; creation dates can differ from first publication. Archived links establish earlier listings. Access errors do not establish deletion or retirement dates. No complete publication/removal history was recovered.

The story links to the independent library's 42 downloadable tables and AI-agent directions, and distinguishes the two snapshot dates. The compact catalog retains all 562 discovery records, with full metadata per dataset and separate complete JSON/gzip exports.

Run node scripts/check_site.mjs for the story/dashboard. Run npm run lint, npm test, and npm run build from projects/open-data-library for the library. Original city files, provenance and public metadata snapshots are included; task workspaces, local settings, candidate refreshes and the separate Cody contribution are excluded.

## Deployment verification

Verify the GitHub Pages run for the released commit, all four URLs, homepage links, cross-project links, catalog JSON and representative downloads. A local build is not proof of publication. Preserve unrelated working changes.

The Cody patch remains a separate contribution; this release does not submit that PR or update the city's live GPT.
