# Syracuse Pickup

A small DataCuse tool at `/projects/pickup/`: enter a Syracuse address, confirm its match, and see the next published trash and recycling dates. Includes Week A/B, set-out dates, calendar export, opt-in browser-only address memory, and direct official links. The DataCuse homepage links here.

## Run locally

Node 20+; no packages or API keys needed.

```sh
npm start
# http://127.0.0.1:8767/
npm run lint
npm test
npm run build
```

`npm start` serves both the page and the read-only JSON API. `HOST` defaults to `127.0.0.1`, `PORT` to `8767`. Use `HOST=0.0.0.0` explicitly when deploying the server behind your hosting provider's HTTPS proxy. The API has bounded inputs, fixed upstream URLs, 12-second timeouts, and no request logging, storage, credentials, or write endpoints. Add infrastructure-level rate limits before exposing it at scale.

The browser directly calls the public city and Esri APIs using the same `lib.mjs` as the Node service. This keeps the browser tool compatible with the existing DataCuse GitHub Pages workflow. The source directory is directly deployable, or use `dist/` from `npm run build`. **GitHub Pages does not run the Node API.** API documentation is in `openapi.json`; a static deployment does not imply a hosted API.

## Routes (Node service only)

| Route | Result |
| --- | --- |
| `/api/health` | Process health, not an upstream availability check |
| `/api/search?q=105%20Victoria%20Pl` | Address candidates requiring confirmation |
| `/api/lookup?lat=43.0408654&lon=-76.1186858` | Zone, regular weekday, Week A/B, actual upcoming dates, source and retrieval time |
| `/api/calendar.ics?lat=43.0408654&lon=-76.1186858` | Explicit dates as an all-day calendar snapshot |
| `/api/openapi.json` | OpenAPI description |

## Provenance and behavior

On November 10, 2026 the city recycling page embedded ArcGIS app `73be90dd8f2f47b1b85a1b2e01db72a7`. Its configuration referenced webmap `7477c6a3ce444b9ab9bbb7949f3081d9`, whose Sanitation Day layer is `Recycling_Biweekly_and_Day/FeatureServer/22`. See `sources.json` for exact URLs and field meanings. We use that map's current layer, not similarly named older datasets in the open data catalog. The other map layer (sanitation quadrants) is not part of this first version.

- `Sanitation` and `RecyclingW` provide regular weekday and week A/B.
- `TrSchedule` and `Schedule` contain comma-separated explicit dates, including holiday shifts. Only valid ISO dates are shown. No every-two-weeks recurrence is invented.
- Next means the first published date on or after today's Eastern date. A same-day result is scheduled collection, not a claim that the truck has yet to arrive.
- The first review found ten zones; recycling dates ran through late December 2026 or January 2, 2027, depending on zone. The app fetches live records for each lookup and states the coverage returned at that time.
- Exact spatial intersections only. Multiple zones, no zone, invalid schemas, exhausted schedules, and upstream outages have separate states.
- Only street/point/subaddress candidates in Syracuse with an Esri score >=80 are offered; all candidates require user confirmation. Browser location worse than 100m accuracy is rejected in favor of an address.
- Map coverage does not establish residential service eligibility or override temporary city notices.
- Calendar downloads contain explicit dates and stable event UIDs. They do not update automatically or repeat past published coverage.
- Optional memory stores only the user's typed query locally, not returned geocoder data or coordinates. No automatic location permission, analytics, or address in share URLs. Location is sent only after the user's browser permission.

Tests cover Eastern time boundaries, holiday shifts, expired and malformed dates, match ambiguity, upstream failure, geocoder filtering, calendar boundaries, HTTP validation, and static route restrictions. Live upstream and browser verification must be reported separately from these deterministic tests.

The GitHub Pages workflow checks and builds this project, then publishes browser assets and the AI guide from `dist/` at `/projects/pickup/`. Tests, scripts, and the Node server stay out of the published directory. No deployment is performed by building locally; deploy the Node entry point separately if a hosted JSON API is wanted.

## AI access

- `/for-ai/`: readable instructions, a copyable starter prompt, and a public live example.
- `/for-ai.json`: access manifest with exact upstream request parameters, field definitions, date rules, and answer requirements.
- `/llms.txt`: plain-text agent instructions and failure/privacy handling.
- `/upstream-openapi.json`: OpenAPI 3.1 describing the live city and Esri endpoints, with operation-level servers. This is distinct from the self-hosted Node API's `openapi.json`.
- **Copy schedule for AI**: copies the current result's dates, source, coverage and timestamp, omitting address and coordinates. A visible text field supports browsers without clipboard access. The result remains a snapshot and includes its zone ID.

These resources do not install a chatbot or MCP connector. An assistant needs HTTP access, or a user-pasted schedule. The next architectural step would be a hosted shared API for agent tools and a messaging bot. A Telegram interface can use deterministic lookup commands without an LLM; a model is only needed if richer language interpretation is wanted. No messaging service, recipient storage, or recurring reminder has been enabled.

## Verification — November 11, 2026

All 11 deterministic tests, syntax/DOM checks, and the static build passed. A separate headless Chromium session verified live address confirmation, the matched Wednesday / Week B zone for the public Petit Branch Library address (105 Victoria Pl), desktop and 390px mobile layouts without horizontal overflow, a 12-event calendar download, saved-address reload and removal, the outside-coverage message for City Hall, and recovery after an upstream request failure. No browser JavaScript errors occurred. Live Node lookup and calendar endpoints also passed. Screenshots and the local browser check script are in the ignored `_preview/pickup-qa/` and `_preview/pickup-qa.mjs` paths at the repository root.
