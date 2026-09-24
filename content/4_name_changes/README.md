# Street names without a turn — DC004

Canonical draft: [story/index.md](story/index.md). Three straightness graphics used in the revised article, plus three supporting continuation graphics: [images](images/). Evidence and exact definitions: [analysis/methodology.md](analysis/methodology.md).

Result: among 218 defined name-sequence windows, a whole-path straightness test finds at most two name changes. Monticello South → Monticello North → Springbrook is the better corroborated example: 686.8 m, 0.20% extra distance, 7.1 m maximum deviation. Tennyson → Burnet Park Drive → Tennyson ties in state data but disagrees with the older city map. The test allows ≤10 m deviation and ≤1% extra distance, with 50 m before/after the name-change sequence. The original continuous-chain leaders have four changes but fail this global straightness test. These are bounded geometric comparisons, not verified driving itineraries or an exhaustive search of all possible routes.

Reproduce from this post folder using Python with `analysis/requirements.txt` installed:

```powershell
python analysis/calculate.py
python analysis/validate.py
python analysis/review_candidates.py
python analysis/make_graphics.py
python analysis/straightness.py
python analysis/validate_straight.py
python analysis/review_straight.py
python analysis/make_straight_graphics.py
```

The creation environment was `../2_shortest_street/analysis/.venv/Scripts/python.exe`. All calculation inputs and the city comparison source are saved within this post; the environment can be replaced. The two aerial review scripts need network access only when imagery is absent. Georgia and Arial are loaded from Windows fonts.

From the repository root:

```powershell
npm test
npm run story:preview -- 4_name_changes
python -m http.server 8000 --bind 127.0.0.1 --directory _preview
```

Preview URL: http://127.0.0.1:8000/stories/syracuse-street-name-changes/

Status: draft, unpublished. Slug: `syracuse-street-name-changes`. Source snapshot: September 19, 2026. Proposed publication date: September 20, 2026. No commit, push or public deployment is part of this draft task.
