# Where is Syracuse's geographic center?

Draft story and interactive guessing map for DC005, incorporating Sam's DC007 companion-app idea. Nothing has been published.

- Canonical article: [story/index.md](story/index.md)
- Calculation: [analysis/results.json](analysis/results.json)
- Method and source notes: [analysis/methodology.md](analysis/methodology.md)
- Graphic: [images/syracuse-balance-point.png](images/syracuse-balance-point.png)
- Interactive assets: `images/center-game.js` and `images/center-game.css`

Readers guess on the map before opening an accordion with their distance from the answer and the full story. The compass is a second accordion on that same page. Guesses and device location remain in browser memory; no reader-response collection is implemented.

From the repository root:

```powershell
npm.cmd test
npm.cmd run build:stories
npm.cmd run story:preview -- 5_geographic_center
python -m http.server 8015 --bind 127.0.0.1 --directory _preview
```

Open http://127.0.0.1:8015/stories/syracuse-geographic-center/ . Keep `status: draft` until publication is requested.

To regenerate the analysis, use Python with Shapely and pyproj for `analysis/calculate.py` and `analysis/review_location.py`; the existing `C:/Users/samie/syracuse_public/.venv-modern/Scripts/python.exe` has those libraries. `calculate.py` reuses the saved boundary when present. Python with Pillow is needed for `analysis/make_graphics.py`; `analysis/build_app.py` uses only the standard library. Run graphics before building the app. The street input is the saved post 4 NYS snapshot; the separate city-map check also uses post 4's dated city snapshot. Exact source hashes and downloads are preserved with the analysis.

Real handset geolocation/orientation needs a final physical-device check. The browser UI and simulated error/accuracy behavior have local checks; no personal GPS location was requested during review.
