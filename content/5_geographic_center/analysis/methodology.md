# Geographic center: evidence and method

Definition: area-weighted centroid of the complete Syracuse city polygon from the NYS Civil Boundaries Cities layer. Water inside the municipal boundary is retained. This is not a land-only center, population center, bounding-box midpoint, visual center, or survey of reader perceptions.

## Sources and reproducibility

- `syracuse_boundary.geojson`: fresh query for NAME = 'Syracuse', outSR = 4326, on September 24, 2026. Exactly one valid feature. Service metadata publication date: March 2026. Feature DATEMOD is older; publication date does not mean every feature was redrawn then. URL, download timestamp and SHA-256 are in `provenance.json`.
- `calculate.py`: project to NAD83 / UTM zone 18N (EPSG:26918), compute Shapely's area-weighted centroid, and transform back to longitude/latitude. Polygon holes contribute negative area. Independent signed-area formulas reproduce the centroid. A second projection (EPSG:5070, CONUS Albers equal-area) moves it only 0.102 metres. Projection sensitivity is not a positional confidence interval.
- Result: 43.04068526443205, -76.14373201653156. The point is inside the boundary. Polygon area in UTM is about 25.631 square miles; do not substitute the service's stored CALC_SQ_MI or Web Mercator area when reproducing this calculation.
- Street context is an extract of the NYS Streets snapshot downloaded September 19 for post 4. `results.json` records the source snapshot path and hash. `streets_context.geojson` preserves the actual context used here. The nearest NYS street segment is South McBride Street, about 21.7 metres away; Jackson Street is about 35.4 metres away. These are distances to mapped centerlines, not sidewalk or doorway measurements.
- Independent city street geometry places South McBride about 21.3 metres away and Jackson about 36.5 metres away. The extracted features and provenance are saved in `city_streets_check.geojson` and `location_review.json`.
- `center_aerial_2022.png`: dated NYS 2022 orthophoto, inspected to orient the calculation in the block north of Jackson and east of South McBride. Do not infer current buildings or construction conditions from it. No field visit or public-access check was made.

## Graphics

`make_graphics.py` draws the source polygon and road geometry, preserving aspect ratio. Web Mercator is used only for display; centroid and local ground distances are calculated separately. Both maps are north-up. Graphic scale bars account for latitude. Labels are offset and leader-linked in the article inset. No AI-generated geography is used.

## Guessing game and compass

The canonical article is `../story/index.md`. Its closed native details element contains the answer, source note and compass. Frontmatter explicitly lists the two bundled assets so preview and publication copy them. The summary and initially visible map do not name the center. A guess is held only in memory. Revealing freezes it and shows straight-line distance to the computed point. Reload or Guess again resets it. Guesses are not collected, and this app cannot establish what residents collectively think.

The original UI template is `app-template.html`; `build_app.py` extracts the compass and map controls, adds the guess/reveal behavior, and writes `../images/center-game.js` and `.css`. It embeds map vectors and the coordinate from `results.json` via `map_config.json`. There is no separate page to open.

Distance: spherical great-circle/haversine, mean Earth radius 6,371,008.8 metres. This is approximate (the sphere can differ from an ellipsoid by roughly half a percent). Direction: initial bearing clockwise from true north. Identical or near-antipodal points and an origin at the pole do not receive a misleading unique bearing. At most 30 metres from the center with adequate reported accuracy is shown as near; distance less than three times location accuracy suppresses the direction.

GPS is requested only from a button, with a 15-second timeout. Denial or failure offers a manual map point or coordinates. Old callbacks cannot overwrite a newly chosen point or clear action. No position is sent, stored, inferred from IP, or included in a map tile request. Browser/OS location services may make their own requests.

An optional handset compass accepts north-referenced readings only, rejects tilted phones and invalid reported WebKit compass accuracy, and expires stale readings. The north-up arrow remains the fallback. True/magnetic north and sensor differences make the handset arrow approximate. Logic is tested; physical iOS/Android sensor accuracy is not verified.

## Checks

Automated checks live in `tests/geographic-center.test.mjs` and `tests/center-experience.test.mjs` at the repository root. They cover numerical directions/distances, dateline and antipode edge cases, coordinate round trips, uncertainty suppression, usable headings, guess/reveal/reset, blue-marker visibility, GPS denial/timeout, stale callbacks and publication asset copying. Browser checks cover manual coordinates, map clicks, keyboard movement, zoom, accordion reveal and responsive layout. See `review-notes.md` for final review status.
