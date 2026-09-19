# DataCuse editorial workspace

This is the home for the [idea bank](datacuse-idea-bank.md), [editorial playbook](datacuse-editorial-playbook.md), [progress tracker](datacuse-story-tracker.csv), the [data availability guide](datacuse-data-guide.md), and the full working material for every post.

```text
1_oak_street_trees/
  analysis/       Notebook, source data, scripts, audits, cached map tiles
  images/         Final graphics and working artwork
  story/
    index.md      The article to edit
2_next_post_name/
  analysis/
  images/
  story/index.md
```

From the DataCuse repository root:

```powershell
npm run story:new -- 2_next_post_name
npm run story:preview -- 1_oak_street_trees
npm run build:stories
```

Use the next unused positive number with lowercase underscore-separated words. Numbers organize post folders; `ideaId` connects each article to its idea-bank ID. Preserve the article's `slug` after publication so its URL stays stable. Do not create competing copies back in `sam_content`.

Write in `story/index.md` and link graphics as `![Description](../images/filename.png)`. The build reads posts here directly and copies only referenced images. The entire `content/` directory is excluded from the deployed website, while source files committed to a public repository remain accessible there.

Oak Street's [article](1_oak_street_trees/story/index.md) is published. Its notebook is now [analysis/trees.ipynb](1_oak_street_trees/analysis/trees.ipynb). The earlier prose draft is retained at `story/oak-street-blog-post.md`; edit `story/index.md` going forward.

See the [publishing guide](../docs/story-publishing.md) for preview, publication, RSS, and selective Medium imports. Update the tracker to Published only after verifying the live page.
