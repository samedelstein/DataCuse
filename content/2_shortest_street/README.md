# Syracuse's shortest street — post 2, idea DC002

- **Article:** [story/index.md](story/index.md). This is the canonical website source, with front matter and the finished map. Status is draft; nothing has been published.
- **Finished map:** [images/shortest-streets-map-blog.png](images/shortest-streets-map-blog.png), 2400 × 2450 pixels. [1600-pixel web version](images/shortest-streets-map-web.png).
- **Four companion graphics:** [Full-name letter tiles](images/shortest-names-letterboard.png), [street-type endings](images/street-suffixes-long-way.png), [whole-street length comparison](images/short-streets-same-ruler.png), and [Oak Street's pieces versus its whole length](images/oak-street-pieces-and-whole.png). All four are embedded in the article alongside the locator map. Each has a 2000-pixel original and a 1400-pixel `-web.png` version.
- **Calculation and review notes:** [analysis/methodology.md](analysis/methodology.md).
- **Results:** [analysis/results.json](analysis/results.json) and the CSV rankings in `analysis/`.
- **Reproduction:** [analysis/calculate.py](analysis/calculate.py), [analysis/validate.py](analysis/validate.py), and [analysis/make_editorial_map.py](analysis/make_editorial_map.py).
- **Data:** full city shapefile/GeoJSON, current NYS extract, municipal boundary and source metadata are in `analysis/`. Review aerials are in `images/`.

The shortest-name definition uses **all letters in the complete, spelled-out street name**. Fay Road and Lea Lane tie at seven. The street-type-vs-base-name comparison is separate. Spring Lane leads the qualified whole-street GIS ranking; the shortest conventional city block remains unproven because the smallest network link lies inside an offset junction.

The editorial map uses the cream, dark-green serif and quiet gray-map style of the Oak Street graphics. Road-sign labels have leader lines to true geographic locations; letter tiles count actual letters. No AI-generated geography is used. OpenStreetMap attribution and the dated NYS aerial sources are printed on the image.

Regenerate companion graphics with `analysis/.venv/Scripts/python.exe analysis/make_story_charts.py`. Values come directly from the saved rankings and source geometry; selected rows and calculated measurements are recorded in `analysis/companion_graphics_audit.json`. The letter comparison shows selected examples, not a complete top-four ranking. The length comparison uses a common zero-based scale and marks the competing older Spring Lane measurement.

From the repository root, the normal preview command is:

```powershell
npm run story:preview -- 2_shortest_street
```

A self-contained project preview and publication-format check can also be generated from this folder with `node analysis/verify_post.mjs`; output is in the ignored `_preview/` folder. Keep the slug `syracuse-shortest-street` stable after publication.
