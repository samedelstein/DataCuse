# DataCuse
DataCuse is the public website repo for Syracuse-focused data projects and essays.
## What Lives Here
- index.html
  Main landing page for the DataCuse site.
- public/
  Shared static assets such as project screenshots.
- projects/
  Standalone project pages, apps, and long-form writeups.
- stories/
  Generated story pages, the complete archive, and the RSS feed.
- content/
  Numbered post folders (1_oak_street_trees, 2_name, etc.), the idea bank, tracker, playbook, and metadata for existing stories. Each post has analysis/, images/, and story/. Excluded from the deployed site.
- .github/workflows/
  GitHub Actions for deployment.
## Included Content
- Below the Line 2026 poverty data story
- Syracuse snow coverage map
- OCPL library census app
- OCPL library use story
- Cityline workaround app
- Cityline snow request analysis
- Syracuse performance dashboard
- Cumberland Ave Atlas
- Datacuse MCP launch article

## Public Site Focus
The deployed site is kept Syracuse-focused. Non-Syracuse experiments can remain in the repository for reference, but the Pages workflow excludes them from the public build unless they become relevant to DataCuse.
## Datacuse MCP Article
The Datacuse MCP launch article lives at:
- projects/datacuse-mcp/index.html
It explains what Datacuse MCP is, what problem it solves, and why MCP is a useful interface for local public data and library workflows.

## Writing and Publishing Stories

Run `npm ci` once at the repository root, then `npm run story:new -- 2_your_post_name`.
Write in `content/2_your_post_name/story/index.md`. Keep `status: draft` until ready.
Preview with `npm run story:preview -- 2_your_post_name`. Run `npm run build:stories` to read the numbered folders directly and generate published pages, the homepage's latest three stories, `/stories/`, and `/stories/feed.xml`. There is no import step for posts in this repository.

See [the publishing guide](docs/story-publishing.md) for images, local preview, publication, RSS, and selective Medium imports. Existing stories keep their original URLs. GitHub Pages runs the generator on deployment.
