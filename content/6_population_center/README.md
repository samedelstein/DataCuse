# Syracuse population center - DC006

Unpublished draft, expanded to compare age, race and Hispanic/Latino ethnicity. Canonical article: `story/index.md`. Evidence, downloads, reproducible scripts and limitations: `analysis/methodology.md`. Four final graphics are in `images/`.

Overall estimate: near Sarah Loguen/Harrison, roughly a quarter-mile northeast of the geographic center. 2020 Census total: 148,620. All demographic group totals reconcile to published city counts.

From the repository root:

```powershell
npm.cmd test
npm.cmd run build:stories
npm.cmd run story:preview -- 6_population_center
python -m http.server 8015 --bind 127.0.0.1 --directory _preview
```

Preview: http://127.0.0.1:8015/stories/population-center/

Keep `status: draft` until publication is requested. `stories/` deliberately does not contain this draft; `_preview/stories/population-center/` is the generated review copy. No app changes or new dependencies were needed.
