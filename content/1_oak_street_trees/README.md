# Oak Street trees — post 1, idea DC001

- Edit [story/index.md](story/index.md) for the DataCuse article.
- Use [analysis/trees.ipynb](analysis/trees.ipynb) for the notebook. CSVs, scripts, audits, the interactive analysis chart, and cached map tiles are also in `analysis/`.
- Final maps, icons, working artwork, and art prompts are in `images/`.
- The earlier prose draft is retained at `story/oak-street-blog-post.md`.

The article is still a draft. Its date is a proposed publication date, not a claim that it is live. The public URL slug is fixed as `oak-street-trees`.

From the repository root:

```powershell
npm run build:stories
npm run story:preview -- 1_oak_street_trees
python -m http.server 8000 --bind 127.0.0.1 --directory _preview
```

Open `http://127.0.0.1:8000/stories/oak-street-trees/`. Previewing does not publish or change draft status.

To regenerate graphics, run `python content/1_oak_street_trees/analysis/make_lost_trees_graphic.py` from the repository root. It reads data and cached tiles from `analysis/`, and writes PNGs into `images/`. There is no image-copy or import step: the next preview/build reads the referenced files directly. See [graphics notes](analysis/blog-graphics-notes.md) for methods and dependencies.

When ready, set `status: published` and the intended publication date in `story/index.md`, then test, build, review, and deploy through the normal GitHub Pages workflow. Keep its slug unchanged. Mark DC001 Published in the tracker only after verifying the live page.
