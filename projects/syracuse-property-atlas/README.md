# Syracuse Property Atlas

An EveryLot-style DataCuse project for Syracuse parcels.

## What it does

- Seeds a local SQLite database from the Syracuse parcel map.
- Enriches parcels with Syracuse open data for vacant properties, rental registry records, unfit properties, and code violations.
- Optionally fetches a Google Street View image for one unpublished property per run.
- Optionally asks a local Ollama vision model, or OpenAI if explicitly configured, to describe visible exterior conditions.
- Adds Census/ACS tract context for each parcel.
- Adds nearby OpenStreetMap context through Overpass.
- Publishes one new static entry into `data/entries.json` and rebuilds `index.html`.

## Run

```powershell
cd C:\Users\samie\Projects\datacuse\DataCuse\projects\syracuse-property-atlas
$env:GOOGLE_STREETVIEW_API_KEY="..."
$env:PROPERTY_IMAGE_PROVIDER="google" # optional; default is no paid image provider
$env:VISION_PROVIDER_CHAIN="gemini:gemini-3.5-flash,gemini:gemini-2.5-flash,ollama:llava:latest"
$env:GEMINI_API_KEY="..."
$env:OLLAMA_TIMEOUT_SECONDS="600"
python scripts\property_atlas.py run-once
```

Run `python scripts\property_atlas.py --help` for commands.

City feeds are refreshed automatically when their last complete import is more than seven days old. Imports verify source counts and unique record IDs before replacing cached data. Limited test imports are marked incomplete and trigger a full refresh on the next normal run. Property matching uses parcel IDs and normalized property addresses; a nearby property's records are not attached by distance alone.

To refresh the feeds and repair already published entries:

```powershell
python scripts\property_atlas.py refresh-open-data
python scripts\property_atlas.py repair-entries --retry-osm
```

The repair preserves publication dates, images, and existing AI analysis. It updates city-record matches and their refresh dates, retries only failed OpenStreetMap lookups in batches of 20, and rebuilds the static pages. Completed batches are saved, so the command can be rerun after a service outage. It uses the hourly runner's lock file to avoid overlapping publication. These commands do not commit or push the site.

OpenStreetMap requests identify the project, accept JSON, and fall back from the main Overpass server to the Private.coffee instance. Responses containing an Overpass runtime error are treated as failures, including partial results. HTTP 406/429 responses trigger a 30-second pause. Configure `OVERPASS_URL` and the comma-separated `OVERPASS_FALLBACK_URLS` to select other servers. Failed lookups retain the requested radius and diagnostics, while pages show an availability message.

Run the Python regression checks (no additional packages required):

```powershell
python -m unittest discover -s scripts -p "test_*.py"
python scripts\property_atlas.py build-site
```

For a fully free local run, leave `PROPERTY_IMAGE_PROVIDER` unset and install a local vision-capable Ollama model. Image analysis will run only when an image source is available.

For hosted vision with local fallback, set `VISION_PROVIDER_CHAIN`. The recommended chain tries Gemini 3.5 Flash, then Gemini 2.5 Flash, then local Ollama.

For hourly publishing, schedule `run-once` from Windows Task Scheduler or GitHub Actions. The free pieces are parcel/open-data feeds, tract lookup, and OpenStreetMap/Overpass. Google Street View is optional and billable.

Note: the Census API key is free, but current Census API examples require a key for data calls. Without `CENSUS_API_KEY`, the atlas still records the census tract from the FCC Census Block API and skips ACS metrics.

## Hourly Publishing

Use the PowerShell runner from the DataCuse repo. It publishes one parcel, rebuilds the site, commits generated changes, and optionally pushes to GitHub Pages.

```powershell
cd C:\Users\samie\Projects\datacuse\DataCuse\projects\syracuse-property-atlas
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_hourly.ps1 -Push
```

Publish, commit, and push a specific address match:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_hourly.ps1 -Push -Address "1301-03 Spring St"
```

Or by parcel row id:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_hourly.ps1 -Push -Id 1
```

Logs are written to `logs/hourly-YYYYMMDD.log`. The runner uses a lock file under `data/` so two scheduled runs do not overlap.

Register or update the Windows Scheduled Task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_windows_task.ps1
```

The task starts a few minutes after registration and repeats hourly by default. Use `-NoPush` if you want local commits without pushing, or `-IntervalMinutes 15` for a faster temporary run.
