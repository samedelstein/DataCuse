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
$env:VISION_PROVIDER="gemini"
$env:VISION_FALLBACK_PROVIDER="ollama"
$env:GEMINI_API_KEY="..."
$env:GEMINI_VISION_MODEL="gemini-2.5-flash"
$env:OLLAMA_VISION_MODEL="llava:latest" # local fallback
$env:OLLAMA_TIMEOUT_SECONDS="600"
python scripts\property_atlas.py run-once
```

Run `python scripts\property_atlas.py --help` for commands.

For a fully free local run, leave `PROPERTY_IMAGE_PROVIDER` unset and install a local vision-capable Ollama model. Image analysis will run only when an image source is available.

For hosted vision, set `VISION_PROVIDER=gemini`. If `VISION_FALLBACK_PROVIDER=ollama` is also set, the script tries Gemini first and falls back to local Ollama if Gemini fails.

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
