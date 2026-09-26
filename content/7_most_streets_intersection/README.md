# Most streets at an intersection — DC008

Canonical draft: `story/index.md`. Folder 7 is the next unused post folder; the idea-bank ID is DC008. Status: draft, unpublished.

Finding: North Salina/Lodi/Kirkpatrick has six distinct approaches and three street names. The state graph's seven-line Hiawatha leader reduces to four approaches after aerial and city-map review. Distinct full names peak at four, with ties. This is a bounded map-based finding, not a field-verified universal record for all multi-junction complexes.

Three finished graphics are in `images/`. Definitions, source dates and checks: `analysis/methodology.md`. Saved results: `analysis/results.json`; independent checks: `analysis/validation.json`.

## Reproduce

Source snapshots and topology helpers are reused from `../4_name_changes/analysis/`; `analysis/provenance.json` pins their SHA-256 hashes. Do not refresh these files without rerunning the calculation and review. No duplicated statewide street download is needed.

From the repository root, using the existing GIS environment:

```powershell
$gisPython = 'content/2_shortest_street/analysis/.venv/Scripts/python.exe'
& $gisPython content/7_most_streets_intersection/analysis/calculate.py
& $gisPython content/7_most_streets_intersection/analysis/city_crosscheck.py
& $gisPython content/7_most_streets_intersection/analysis/review_candidates.py
& $gisPython content/7_most_streets_intersection/analysis/validate.py
& $gisPython content/7_most_streets_intersection/analysis/make_graphics.py
npm.cmd test
node content/7_most_streets_intersection/analysis/verify_site.mjs
npm.cmd run story:preview -- 7_most_streets_intersection
python -m http.server 8015 --bind 127.0.0.1 --directory _preview
```

`review_candidates.py` needs network access only for uncached official aerials. The GIS environment uses Shapely, pyproj, NetworkX and Pillow (see `requirements.txt`); graphics use Windows Georgia and Arial. `verify_site.mjs` runs the real site builder on a temporary copy so it does not alter other stories' generated files.

Preview: http://127.0.0.1:8015/stories/syracuse-most-streets-intersection/

Drafts appear under `_preview/`, not the public `stories/` directory. Publish only when requested, following `docs/story-publishing.md`.
