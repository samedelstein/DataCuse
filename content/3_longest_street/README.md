# Syracuse's longest street — post 3, idea DC003

- [Draft article](story/index.md): canonical Markdown source; **not published**.
- [Methodology and candidate review](analysis/methodology.md): definitions, findings, caveats, and reproduction commands.
- [Results](analysis/results.json): all three comparisons and divided-road/endpoints audit.
- [Validation](analysis/validation.json): endpoint-tolerance sensitivity and meaningful geometry checks.
- `images/`: five editorial figures plus web-size exports. `analysis/review/`: dated aerials and candidate overlays.

Findings: Canal Street has the longest individual source feature at about 3,359 feet. The literal longest name field is East Brighton Avenue Avenue Northbound (34 letters), with the repeated Avenue explicitly flagged. South Salina's joined city portion is about 4.66 miles; Erie's apparent 5.93-mile mapped sum includes both carriageways and corresponds to about 3.57 miles along the corridor once.

All lengths stop at the Syracuse boundary. North/South and East/West name variants stay separate. No field measurement or street-sign survey is claimed.

From the repository root:

```powershell
npm run story:preview -- 3_longest_street
python -m http.server 8000 --bind 127.0.0.1 --directory _preview
```

Preview URL: `http://127.0.0.1:8000/stories/syracuse-longest-street/`. Keep `status: draft` until publication is requested; public slug is `syracuse-longest-street`.
