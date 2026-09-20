# Draft review — September 20, 2026

## Evidence

- Reused the exact September 19 NYS input snapshot from DC002, retaining metadata and hashes.
- Checked all three rankings against saved calculations. Canal Street's single-feature length is 3,358.7905 feet; the longest literal field has 34 letters; South Salina's city-clipped union totals 4.65717 miles.
- Inspected four NYS 2022 aerial overlays: Canal's mapped segment, Erie's divided carriageways, and both South Salina endpoints.
- Reviewed the only summed-length challenger to South Salina: Erie's 5.92760-mile sum includes both carriageways; traced west-to-east paths are about 3.57 miles.
- Recomputed at 0, 0.5 and 1 metre endpoint tolerance. Winners and rounded values hold. One-metre snapping contracts a 0.974-metre boundary piece; raw geometry length is unchanged. See `validation.json`.
- Literal database names, real street-sign names, source segments, conventional blocks, and whole streets are distinguished in prose and graphics. The street-sign-name superlative remains unverified and is explicitly qualified.

## Graphics and page

- Inspected five full-size figures/web exports. Map leaders connect to actual geometry; aerial crops retain geographic aspect ratio; letter tiles retain the repeated Avenue; bar scales start at zero.
- Site tests: **9 passed**. `npm run build:stories` passed and included two published Markdown stories; DC003 remained excluded.
- `npm run story:preview -- 3_longest_street` passed. Preview carries `noindex, nofollow` and the intended stable canonical URL.
- Browser review at desktop width (1592 pixels) and mobile width (390 pixels): no horizontal overflow; all five 2000-pixel originals loaded, with alt text and responsive widths. Essential findings and caveats also appear in article text because dense image annotations require enlargement on a phone.
- Opened the hero image through its full-size link and returned successfully. Temporary mobile viewport override was reset.
- The live local preview is `http://127.0.0.1:8033/stories/syracuse-longest-street/` while the preview server is running.

## Handoff

Ready for Sam's editorial review. `story/index.md` remains **draft**; proposed date September 20, 2026. No commit, push, deployment, or Medium import was performed. No field measurement, street-sign survey, or complete out-of-city length is claimed.
