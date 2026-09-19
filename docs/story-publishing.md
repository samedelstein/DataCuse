# Publishing DataCuse stories and notes

All working material lives in this repository's `content/` directory. The generator reads each numbered post directly. There is no separate working copy or import step.

```text
content/
  datacuse-idea-bank.md
  datacuse-editorial-playbook.md
  datacuse-story-tracker.csv
  existing-stories.json
  1_oak_street_trees/
    analysis/
    images/
    story/index.md
  2_next_post_name/
    analysis/
    images/
    story/index.md
```

## Start the next post

From the repository root, run `npm ci` once, then:

```powershell
npm run story:new -- 2_shortest_street
```

This is an example name; the command creates the three folders, a README, and a draft Markdown article. Choose the next unused positive number and use lowercase words separated by underscores. Existing numbers cannot be reused. Do not renumber earlier posts. The number tracks the post folder; `ideaId` separately links it to the idea-bank tracker, so post 2 can explore any idea.

## Write the article

Edit `content/2_shortest_street/story/index.md`. Its header looks like this:

```yaml
---
title: "Your question or verified finding"
slug: "shortest-street"
summary: "One sentence that invites the reader into the story."
date: "2026-09-18"
category: "Streets"
status: draft
ideaId: "DC002"
---
```

Use the intended publication date. Keep the slug unchanged after publication; it defines the public URL and feed identifier. Titles, categories, and folder labels can evolve without changing a explicitly set slug. Old drafts without a slug use the folder name after the number, with underscores converted to hyphens.

The template supplies the title, date, byline, navigation, and subscription links. Write the body in Markdown, ending with the sources, data dates, and important limitations. Treat raw HTML as trusted editorial content and review it before use.

## Analysis and images

Put notebooks, source data, scripts, audits, and notes in `analysis/`. Put finished graphics and working artwork in `images/`. Reference selected images from the story using Markdown:

```markdown
![A description of what the map shows](../images/map.png)
```

Only files referenced through Markdown image or link syntax under `../images/` are copied into the public article's `assets/` folder. Unreferenced artwork stays out of the website. Use filenames without spaces. Add captions and credits in the article. Use Markdown syntax for local images rather than raw HTML image tags so the publisher can identify them.

## Preview locally

```powershell
npm run build:stories
npm run story:preview -- 1_oak_street_trees
python -m http.server 8000 --bind 127.0.0.1 --directory _preview
```

Open `http://127.0.0.1:8000/stories/oak-street-trees/`. Replace the numbered folder argument for other posts; the preview command prints the correct URL. It reads the article directly, leaves draft status unchanged, and does not add drafts to the public archive or RSS feed. `_preview/` is gitignored, excluded from deployment, and marked noindex. Stop the server with Ctrl+C when finished.

## Publish

1. Finish and verify the article and images. Set `status: published` and the intended date in `story/index.md`.
2. Run `npm test` and `npm run build:stories`.
3. Review the generated page and the repository changes. Commit the intended source and generated output, then push through the normal main-branch deployment process.
4. After GitHub Pages succeeds, verify the live page and record its URL and date in `content/datacuse-story-tracker.csv`.

The build publishes only stories dated today or earlier in America/New_York. Future-dated stories wait for a build on or after that date; no automatic scheduled deployment is configured. Drafts with unfinished image references do not block the published-site build.

Published HTML lives under `stories/`. Edit the numbered source folder, not generated HTML. The build tracks its own output files and removes stale generated pages/assets while preserving unrelated files. Homepage changes stay between the stories markers.

The deployment excludes all of `content/`, so research and unpublished drafts are not served by the website. Files committed to a public Git repository are still accessible through that repository. Do not commit secrets or confidential research. Python caches and notebook checkpoints are gitignored.

## Archive, RSS, and Medium

- Archive: `https://www.datacuse.com/stories/`
- RSS: `https://www.datacuse.com/stories/feed.xml`
- Oak Street's eventual URL: `https://www.datacuse.com/stories/oak-street-trees/`

The homepage's latest three stories, complete archive, and RSS feed all come from the same collection. RSS includes titles, summaries, categories, permanent links, and publication dates when known. Existing project stories are listed in `content/existing-stories.json` without moving their pages. A month-only historical date stays month-only and has no invented RSS day.

Publish on DataCuse first. For a selected Medium version, use Medium's **Import a story** with the individual live article URL. Review images and source links, and confirm the canonical URL points to DataCuse. Medium imports are manual and later edits do not synchronize automatically. Keep the DataCuse URL in the tracker's Published URL field and put the Medium URL in Research Notes.

Official references checked September 18, 2026: [Medium import instructions](https://help.medium.com/hc/en-us/articles/214550207-Importing-a-post-to-Medium) and [canonical-link settings](https://help.medium.com/hc/en-us/articles/360033930293-Set-a-canonical-link).
