#!/usr/bin/env python
"""Build and publish the Syracuse Property Atlas one parcel at a time."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import json
import math
import os
import re
import shutil
import sqlite3
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "property_atlas.sqlite3"
SITE_DIR = ROOT
ENTRIES_PATH = SITE_DIR / "data" / "entries.json"
PROGRESS_PATH = SITE_DIR / "data" / "progress.json"
REVIEW_PATH = SITE_DIR / "data" / "review_queue.json"
IMAGES_DIR = SITE_DIR / "images"
PROPERTIES_DIR = SITE_DIR / "properties"
TRACTS_DIR = SITE_DIR / "tracts"

PARCEL_FEED = {
    "name": "parcel_map_2025",
    "label": "2025 Syracuse parcel map",
    "url": "https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/QPD_2025_01_02_L1_ODP/FeatureServer/0/query",
}

ACS_VARIABLES = {
    "DP05_0001E": "Total population",
    "DP03_0062E": "Median household income",
    "DP03_0128PE": "Poverty rate",
    "DP04_0001E": "Housing units",
    "DP04_0003PE": "Vacancy rate",
    "DP04_0046PE": "Renter-occupied share",
    "DP04_0089E": "Median gross rent",
    "DP04_0134PE": "No vehicle available",
}

AI_ANALYSIS_SCHEMA = {
    "summary": "one cautious sentence describing the visible exterior",
    "property_type_guess": "single_family|two_family|multifamily|commercial|mixed_use|vacant_lot|unclear",
    "visible_conditions": ["specific exterior observations visible in the image"],
    "condition_scores": {
        "roof": "good|fair|poor|not_visible|unclear",
        "siding_or_facade": "good|fair|poor|not_visible|unclear",
        "windows_doors": "good|fair|poor|not_visible|unclear",
        "porch_or_entry": "good|fair|poor|not_visible|unclear",
        "yard_or_lot": "good|fair|poor|not_visible|unclear",
        "trash_debris": "none_visible|minor|major|unclear",
        "vegetation_overgrowth": "none_visible|minor|major|unclear",
    },
    "visible_flags": {
        "boarded_windows_or_doors": "yes|no|unclear",
        "fire_damage_visible": "yes|no|unclear",
        "structural_damage_visible": "yes|no|unclear",
        "vacancy_signs_visible": "yes|no|unclear",
        "active_construction_visible": "yes|no|unclear",
    },
    "possible_unrecorded_issues": ["cautious image-only flags not already reflected in known_data"],
    "image_annotations": [
        {
            "label": "short visible issue label",
            "reason": "why this area was marked",
            "bbox": {
                "x": "left position as 0-1 fraction of image width",
                "y": "top position as 0-1 fraction of image height",
                "width": "box width as 0-1 fraction of image width",
                "height": "box height as 0-1 fraction of image height",
            },
            "confidence": "high|medium|low",
        }
    ],
    "needs_human_review": "true|false",
    "confidence": "high|medium|low",
    "caveats": ["limits such as image age, obstructed view, angle, or uncertainty"],
}


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value

OPEN_DATA_FEEDS = [
    {
        "name": "vacant_properties",
        "label": "Vacant properties",
        "url": "https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/Vacant_Properties/FeatureServer/0/query",
    },
    {
        "name": "rental_registry",
        "label": "Rental registry",
        "url": "https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/Syracuse_Rental_Registry/FeatureServer/0/query",
    },
    {
        "name": "code_violations",
        "label": "Code violations",
        "url": "https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/Code_Violations_V2/FeatureServer/0/query",
    },
    {
        "name": "unfit_properties",
        "label": "Unfit properties",
        "url": "https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/Unfit_Properties/FeatureServer/0/query",
    },
]

ADDRESS_FIELDS = (
    "address",
    "site_address",
    "situs_address",
    "prop_address",
    "property_address",
    "location",
    "street_address",
    "full_address",
    "fulladdres",
    "fulladdress",
    "mailadd",
)
PARCEL_ID_FIELDS = (
    "sbl",
    "tax_id",
    "taxid",
    "parcel_id",
    "parcelid",
    "objectid",
    "swis_sbl_id",
    "print_key",
    "account",
    "printkey",
    "pnumbr",
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def request_json(url: str, params: dict[str, object] | None = None, timeout: int = 60) -> dict:
    return json.loads(request_text(url, params=params, timeout=timeout))


def request_text(url: str, params: dict[str, object] | None = None, timeout: int = 60) -> str:
    full_url = url
    if params:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "DataCusePropertyAtlas/1.0 (https://www.datacuse.com/)"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8")


def post_json(url: str, payload: dict | str, headers: dict[str, str] | None = None, timeout: int = 60, form: bool = False) -> dict:
    request_headers = {"User-Agent": "DataCusePropertyAtlas/1.0 (https://www.datacuse.com/)"}
    request_headers.update(headers or {})
    if form and isinstance(payload, dict):
        body = urllib.parse.urlencode(payload).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif isinstance(payload, str):
        body = payload.encode("utf-8")
    else:
        body = json.dumps(payload).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=request_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def request_bytes(url: str, params: dict[str, object], timeout: int = 60) -> bytes:
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "DataCusePropertyAtlas/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_arcgis_geojson(feed: dict[str, str], page_size: int = 1000, limit: int | None = None) -> list[dict]:
    features: list[dict] = []
    offset = 0
    while True:
        count = min(page_size, limit - len(features)) if limit else page_size
        if count <= 0:
            return features
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": count,
        }
        data = request_json(feed["url"], params=params)
        batch = data.get("features", [])
        features.extend(batch)
        print(f"{feed['name']}: fetched {len(features)} records", flush=True)
        if limit and len(features) >= limit:
            return features[:limit]
        if not batch:
            return features
        if len(batch) < count and not data.get("exceededTransferLimit"):
            return features
        offset += len(batch)
        time.sleep(0.15)


def fetch_arcgis_json(feed: dict[str, str], page_size: int = 1000, limit: int | None = None) -> list[dict]:
    features: list[dict] = []
    offset = 0
    while True:
        count = min(page_size, limit - len(features)) if limit else page_size
        if count <= 0:
            return features
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "returnGeometry": "true",
            "returnCentroid": "true",
            "outSR": "4326",
            "resultOffset": offset,
            "resultRecordCount": count,
        }
        data = request_json(feed["url"], params=params, timeout=180)
        batch = data.get("features", [])
        features.extend(batch)
        print(f"{feed['name']}: fetched {len(features)} records", flush=True)
        if limit and len(features) >= limit:
            return features[:limit]
        if not batch:
            return features
        if len(batch) < count and not data.get("exceededTransferLimit"):
            return features
        offset += len(batch)
        time.sleep(0.15)


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_object_id TEXT,
            parcel_key TEXT,
            address TEXT,
            lat REAL,
            lon REAL,
            properties_json TEXT NOT NULL,
            geometry_json TEXT,
            created_at TEXT NOT NULL,
            published_at TEXT
        );

        CREATE TABLE IF NOT EXISTS feed_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_name TEXT NOT NULL,
            source_object_id TEXT,
            parcel_key TEXT,
            address TEXT,
            lat REAL,
            lon REAL,
            properties_json TEXT NOT NULL,
            geometry_json TEXT,
            refreshed_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_parcels_published ON parcels(published_at, id);
        CREATE INDEX IF NOT EXISTS idx_parcels_key ON parcels(parcel_key);
        CREATE INDEX IF NOT EXISTS idx_parcels_address ON parcels(address);
        CREATE INDEX IF NOT EXISTS idx_feed_records_name_key ON feed_records(feed_name, parcel_key);
        CREATE INDEX IF NOT EXISTS idx_feed_records_name_address ON feed_records(feed_name, address);
        """
    )
    conn.commit()


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).upper().replace(".", "").replace(",", " ").split())


def normalized_address(properties: dict) -> str:
    lower = {str(k).lower(): v for k, v in properties.items()}
    for field in ADDRESS_FIELDS:
        value = lower.get(field)
        if value:
            return normalize_text(value)

    number = lower.get("st_num") or lower.get("stnum") or lower.get("addressnum") or lower.get("street_num") or lower.get("house_num") or lower.get("housenum")
    street = lower.get("street") or lower.get("st_name") or lower.get("stname") or lower.get("addressnam") or lower.get("street_name") or lower.get("str_name")
    suffix = lower.get("suffix") or lower.get("st_type") or lower.get("street_type")
    if number and street:
        return normalize_text(f"{number} {street} {suffix or ''}")
    return ""


def parcel_key(properties: dict) -> str:
    lower = {str(k).lower(): v for k, v in properties.items()}
    for field in PARCEL_ID_FIELDS:
        value = lower.get(field)
        if value not in (None, ""):
            return normalize_text(value)
    return ""


def source_object_id(properties: dict) -> str:
    lower = {str(k).lower(): v for k, v in properties.items()}
    return str(lower.get("objectid") or lower.get("fid") or lower.get("id") or "")


def geometry_centroid(geometry: dict | None) -> tuple[float | None, float | None]:
    if not geometry:
        return None, None
    coords = geometry.get("coordinates")
    if not coords:
        return None, None

    points: list[tuple[float, float]] = []

    def collect(value: object) -> None:
        if not isinstance(value, list):
            return
        if len(value) >= 2 and all(isinstance(v, (int, float)) for v in value[:2]):
            points.append((float(value[0]), float(value[1])))
            return
        for item in value:
            collect(item)

    collect(coords)
    if not points:
        return None, None
    lon = sum(point[0] for point in points) / len(points)
    lat = sum(point[1] for point in points) / len(points)
    return lat, lon


def arcgis_feature_centroid(feature: dict) -> tuple[float | None, float | None]:
    centroid = feature.get("centroid")
    if isinstance(centroid, dict) and centroid.get("x") is not None and centroid.get("y") is not None:
        return float(centroid["y"]), float(centroid["x"])
    geometry = feature.get("geometry")
    if isinstance(geometry, dict) and geometry.get("x") is not None and geometry.get("y") is not None:
        return float(geometry["y"]), float(geometry["x"])
    if isinstance(geometry, dict) and geometry.get("rings"):
        points = [point for ring in geometry.get("rings", []) for point in ring if len(point) >= 2]
        if points:
            lon = sum(float(point[0]) for point in points) / len(points)
            lat = sum(float(point[1]) for point in points) / len(points)
            return lat, lon
    return None, None


def seed_parcels(conn: sqlite3.Connection, limit: int | None = None) -> int:
    features = fetch_arcgis_json(PARCEL_FEED, limit=limit)
    inserted = 0
    now = utc_now()
    for feature in features:
        props = feature.get("attributes") or feature.get("properties") or {}
        geom = feature.get("geometry")
        key = parcel_key(props)
        obj_id = source_object_id(props)
        address = normalized_address(props)
        lat, lon = arcgis_feature_centroid(feature)
        existing = conn.execute(
            "SELECT id FROM parcels WHERE source_object_id = ? OR (parcel_key != '' AND parcel_key = ?)",
            (obj_id, key),
        ).fetchone()
        if existing:
            continue
        conn.execute(
            """
            INSERT INTO parcels
                (source_object_id, parcel_key, address, lat, lon, properties_json, geometry_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (obj_id, key, address, lat, lon, json.dumps(props, sort_keys=True), json.dumps(geom), now),
        )
        inserted += 1
    conn.commit()
    return inserted


def refresh_open_data(conn: sqlite3.Connection, limit: int | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    now = utc_now()
    for feed in OPEN_DATA_FEEDS:
        features = fetch_arcgis_geojson(feed, limit=limit)
        conn.execute("DELETE FROM feed_records WHERE feed_name = ?", (feed["name"],))
        for feature in features:
            props = feature.get("properties") or {}
            geom = feature.get("geometry")
            lat, lon = geometry_centroid(geom)
            conn.execute(
                """
                INSERT INTO feed_records
                    (feed_name, source_object_id, parcel_key, address, lat, lon, properties_json, geometry_json, refreshed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    feed["name"],
                    source_object_id(props),
                    parcel_key(props),
                    normalized_address(props),
                    lat,
                    lon,
                    json.dumps(props, sort_keys=True),
                    json.dumps(geom),
                    now,
                ),
            )
        counts[feed["name"]] = len(features)
    conn.commit()
    return counts


def distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def matching_records(conn: sqlite3.Connection, parcel: sqlite3.Row) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}
    for feed in OPEN_DATA_FEEDS:
        records: list[sqlite3.Row] = []
        if parcel["parcel_key"]:
            records.extend(
                conn.execute(
                    "SELECT * FROM feed_records WHERE feed_name = ? AND parcel_key = ? LIMIT 20",
                    (feed["name"], parcel["parcel_key"]),
                ).fetchall()
            )
        if parcel["address"]:
            records.extend(
                conn.execute(
                    "SELECT * FROM feed_records WHERE feed_name = ? AND address = ? LIMIT 20",
                    (feed["name"], parcel["address"]),
                ).fetchall()
            )
        if parcel["lat"] is not None and parcel["lon"] is not None:
            nearby = conn.execute(
                """
                SELECT * FROM feed_records
                WHERE feed_name = ? AND lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?
                LIMIT 100
                """,
                (feed["name"], parcel["lat"] - 0.0005, parcel["lat"] + 0.0005, parcel["lon"] - 0.0005, parcel["lon"] + 0.0005),
            ).fetchall()
            for record in nearby:
                if record["lat"] is not None and record["lon"] is not None:
                    if distance_meters(parcel["lat"], parcel["lon"], record["lat"], record["lon"]) <= 40:
                        records.append(record)

        seen: set[int] = set()
        packed: list[dict] = []
        for record in records:
            if record["id"] in seen:
                continue
            seen.add(record["id"])
            packed.append(json.loads(record["properties_json"]))
        results[feed["name"]] = packed
    return results


def fetch_google_streetview(parcel: sqlite3.Row) -> tuple[str | None, str | None]:
    key = os.getenv("GOOGLE_STREETVIEW_API_KEY") or os.getenv("STREETVIEW_API_KEY")
    if not key:
        return None, "GOOGLE_STREETVIEW_API_KEY is not set"
    if parcel["lat"] is None or parcel["lon"] is None:
        return None, "parcel has no coordinates"

    params = {
        "location": f"{parcel['lat']},{parcel['lon']}",
        "size": "1000x1000",
        "fov": 70,
        "pitch": 8,
        "source": "outdoor",
        "key": key,
    }
    image = request_bytes("https://maps.googleapis.com/maps/api/streetview", params=params)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_name = f"parcel-{parcel['id']:06d}.jpg"
    image_path = IMAGES_DIR / image_name
    image_path.write_bytes(image)
    return f"images/{image_name}", None


def fetch_property_image(parcel: sqlite3.Row) -> tuple[str | None, str | None]:
    provider = os.getenv("PROPERTY_IMAGE_PROVIDER", "none").lower()
    if provider in ("", "none", "free"):
        return None, "No free parcel-level street image provider is configured."
    if provider == "google":
        return fetch_google_streetview(parcel)
    return None, f"Unsupported PROPERTY_IMAGE_PROVIDER={provider!r}"


def image_quality(image_path: Path | None, image_error: str | None = None) -> dict:
    if image_error:
        return {"available": False, "needs_rerun": True, "note": image_error}
    if not image_path or not image_path.exists():
        return {"available": False, "needs_rerun": True, "note": "No image file found."}
    size = image_path.stat().st_size
    status = {
        "available": True,
        "bytes": size,
        "needs_rerun": False,
        "warnings": [],
    }
    if size < 10000:
        status["needs_rerun"] = True
        status["warnings"].append("Image file is unexpectedly small.")
    head = image_path.read_bytes()[:32]
    if b"error" in head.lower() or b"<html" in head.lower():
        status["needs_rerun"] = True
        status["warnings"].append("Image file may contain an API error response.")
    return status


def summarize_records(matches: dict[str, list[dict]]) -> list[str]:
    summaries = []
    labels = {feed["name"]: feed["label"] for feed in OPEN_DATA_FEEDS}
    for name, rows in matches.items():
        if rows:
            summaries.append(f"{labels[name]}: {len(rows)} matching record{'s' if len(rows) != 1 else ''}")
    return summaries


def analyze_image(image_path: Path, parcel: sqlite3.Row, matches: dict[str, list[dict]]) -> dict:
    if not image_path.exists():
        return {"available": False, "note": "No Street View image was available for analysis."}
    provider = os.getenv("VISION_PROVIDER", "ollama").lower()

    prompt = build_vision_prompt(parcel, matches)
    data_url = "data:image/jpeg;base64," + base64.b64encode(image_path.read_bytes()).decode("ascii")
    analysis = analyze_image_with_provider(provider, data_url, prompt)
    if analysis.get("available"):
        return analysis

    fallback = os.getenv("VISION_FALLBACK_PROVIDER", "").lower().strip()
    if fallback and fallback != provider:
        fallback_analysis = analyze_image_with_provider(fallback, data_url, prompt)
        if fallback_analysis.get("available"):
            fallback_analysis["fallback_from"] = provider
            return fallback_analysis
        analysis["fallback_note"] = fallback_analysis.get("note")
    return analysis


def analyze_image_with_provider(provider: str, data_url: str, prompt: dict) -> dict:
    if provider == "ollama":
        return analyze_image_ollama(data_url, prompt)
    if provider == "gemini":
        return analyze_image_gemini(data_url, prompt)
    if provider == "openai":
        return analyze_image_openai(data_url, prompt)
    return {"available": False, "note": f"Unsupported VISION_PROVIDER={provider!r}; image analysis skipped."}


def build_vision_prompt(parcel: sqlite3.Row, matches: dict[str, list[dict]]) -> dict:
    return {
        "role": "You are a cautious civic data assistant reviewing a public street-level exterior image for a property atlas.",
        "property": {
            "address": parcel["address"],
            "parcel_key": parcel["parcel_key"],
            "coordinates": {"lat": parcel["lat"], "lon": parcel["lon"]},
        },
        "known_public_records": summarize_records(matches),
        "task": [
            "Describe only visible exterior property conditions from the image.",
            "Compare visible conditions against known_public_records and call out possible image-only issues only when they are plainly visible.",
            "Use cautious language. Do not infer ownership, occupancy, code violations, criminal activity, socioeconomic status, or protected-class information.",
            "Do not identify, describe, transcribe, or track people, faces, license plates, or private personal details.",
            "If the property is blocked, image quality is poor, or the view may show the wrong parcel, lower confidence and explain the caveat.",
            "When you flag visible issues, include approximate normalized bounding boxes in image_annotations. Use x, y, width, and height as fractions from 0 to 1 relative to the full image.",
            "Only create bounding boxes for visible property-condition issues, not people, vehicles, license plates, or unrelated background objects.",
            "Return valid JSON only. Do not wrap it in Markdown.",
        ],
        "schema": AI_ANALYSIS_SCHEMA,
    }


def analyze_image_ollama(data_url: str, prompt: dict) -> dict:
    model = os.getenv("OLLAMA_VISION_MODEL", "llava:latest")
    endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    timeout = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "600"))
    payload = {
        "model": model,
        "prompt": json.dumps(prompt),
        "images": [data_url.split(",", 1)[1]],
        "stream": False,
        "format": "json",
    }
    try:
        result = post_json(endpoint, payload, timeout=timeout)
    except Exception as exc:
        return {"available": False, "note": f"Ollama vision request failed: {exc}"}
    text = result.get("response", "")
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        parsed = {"summary": text, "visible_conditions": [], "possible_unrecorded_issues": [], "confidence": "unknown", "caveats": []}
    parsed["available"] = True
    parsed["provider"] = f"ollama:{model}"
    return normalize_ai_analysis(parsed)


def analyze_image_gemini(data_url: str, prompt: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"available": False, "note": "GEMINI_API_KEY is not set; Gemini image analysis skipped."}
    model = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model)}:generateContent"
    image_b64 = data_url.split(",", 1)[1]
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Return valid JSON only, with no Markdown fence. "
                            "Use this property-analysis instruction object:\n"
                            + json.dumps(prompt)
                        )
                    },
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}},
                ],
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }
    url = f"{endpoint}?{urllib.parse.urlencode({'key': api_key})}"
    try:
        result = post_json(url, payload, timeout=int(os.getenv("GEMINI_TIMEOUT_SECONDS", "180")))
    except Exception as exc:
        return {"available": False, "note": f"Gemini vision request failed: {exc}"}

    parts = (
        result.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "\n".join(part.get("text", "") for part in parts if part.get("text"))
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        parsed = {"summary": text or "", "visible_conditions": [], "possible_unrecorded_issues": [], "confidence": "unknown", "caveats": []}
    parsed["available"] = True
    parsed["provider"] = f"gemini:{model}"
    return normalize_ai_analysis(parsed)


def analyze_image_openai(data_url: str, prompt: dict) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"available": False, "note": "OPENAI_API_KEY is not set; OpenAI image analysis skipped."}
    payload = {
        "model": os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini"),
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": json.dumps(prompt)},
                    {"type": "input_image", "image_url": data_url, "detail": "high"},
                ],
            }
        ],
        "text": {"format": {"type": "json_object"}},
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"available": False, "note": f"OpenAI vision request failed: HTTP {exc.code}"}

    text = result.get("output_text")
    if not text:
        parts = []
        for item in result.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))
        text = "\n".join(parts)
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        parsed = {"summary": text or "", "visible_conditions": [], "possible_unrecorded_issues": [], "confidence": "unknown", "caveats": []}
    parsed["available"] = True
    parsed["provider"] = payload["model"]
    return normalize_ai_analysis(parsed)


def normalize_ai_analysis(parsed: dict) -> dict:
    parsed.setdefault("summary", "")
    parsed.setdefault("visible_conditions", [])
    parsed.setdefault("possible_unrecorded_issues", [])
    parsed.setdefault("condition_scores", {})
    parsed.setdefault("visible_flags", {})
    parsed.setdefault("image_annotations", [])
    parsed.setdefault("confidence", "unknown")
    parsed.setdefault("caveats", [])
    parsed.setdefault("property_type_guess", "unclear")
    review = parsed.get("needs_human_review", False)
    if isinstance(review, str):
        parsed["needs_human_review"] = review.strip().lower() in ("true", "yes", "1")
    else:
        parsed["needs_human_review"] = bool(review)
    return parsed


def census_tract_context(parcel: sqlite3.Row) -> dict:
    if parcel["lat"] is None or parcel["lon"] is None:
        return {"available": False, "note": "Parcel has no coordinates."}
    try:
        tract_info = lookup_census_tract(parcel["lat"], parcel["lon"])
        state = tract_info["state"]
        county = tract_info["county"]
        tract = tract_info["tract"]
        if not os.getenv("CENSUS_API_KEY"):
            return {
                "available": True,
                "source": "Census tract lookup; ACS metrics skipped",
                "name": tract_info.get("name"),
                "state": state,
                "county": county,
                "tract": tract,
                "tract_lookup": tract_info.get("source"),
                "metrics": {},
                "note": "CENSUS_API_KEY is not set; ACS metrics skipped. Census API keys are free but now required for data calls.",
            }
        variables = ["NAME", *ACS_VARIABLES.keys()]
        year, rows = fetch_acs_profile_rows(state, county, tract, variables)
        header, values = rows[0], rows[1]
        row = dict(zip(header, values))
        metrics = {label: row.get(code) for code, label in ACS_VARIABLES.items()}
        return {
            "available": True,
            "source": f"{year} ACS 5-year profile",
            "name": row.get("NAME") or tract_info.get("NAME"),
            "state": state,
            "county": county,
            "tract": tract,
            "tract_lookup": tract_info.get("source"),
            "metrics": metrics,
        }
    except Exception as exc:
        return {"available": False, "note": f"Census tract lookup failed: {exc}"}


def fetch_acs_profile_rows(state: str, county: str, tract: str, variables: list[str]) -> tuple[str, list[list[str]]]:
    requested = os.getenv("ACS_YEAR")
    years = [requested] if requested else ["2024", "2023", "2022"]
    last_error: Exception | None = None
    for year in years:
        if not year:
            continue
        try:
            rows = request_json(
                f"https://api.census.gov/data/{year}/acs/acs5/profile",
                {
                    "get": ",".join(variables),
                    "for": f"tract:{tract}",
                    "in": f"state:{state} county:{county}",
                    "key": os.getenv("CENSUS_API_KEY", ""),
                },
                timeout=30,
            )
            return year, rows
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"ACS profile request failed for {', '.join(years)}: {last_error}")


def lookup_census_tract(lat: float, lon: float) -> dict:
    try:
        benchmark = os.getenv("CENSUS_GEOCODER_BENCHMARK", "4")
        vintage = os.getenv("CENSUS_GEOCODER_VINTAGE", "4")
        geo = request_json(
            "https://geocoding.geo.census.gov/geocoder/geographies/coordinates",
            {
                "x": lon,
                "y": lat,
                "benchmark": benchmark,
                "vintage": vintage,
                "format": "json",
            },
            timeout=30,
        )
        tract_info = geo["result"]["geographies"]["Census Tracts"][0]
        return {
            "state": tract_info["STATE"],
            "county": tract_info["COUNTY"],
            "tract": tract_info["TRACT"],
            "name": tract_info.get("NAME"),
            "source": "Census Geocoder",
        }
    except Exception:
        raw = request_text(
            "https://geo.fcc.gov/api/census/block/find",
            {"latitude": lat, "longitude": lon, "format": "json", "showall": "false"},
            timeout=30,
        )
        try:
            data = json.loads(raw)
            fips = str(data["Block"]["FIPS"])
            county_name = data.get("County", {}).get("name")
        except json.JSONDecodeError:
            fips_match = re.search(r"FIPS:([0-9]{15})", raw)
            county_match = re.search(r"County:\{FIPS:[0-9]+,name:([^}]+)\}", raw)
            if not fips_match:
                raise
            fips = fips_match.group(1)
            county_name = county_match.group(1) if county_match else None
        return {
            "state": fips[:2],
            "county": fips[2:5],
            "tract": fips[5:11],
            "name": county_name,
            "source": "FCC Census Block API",
        }


def osm_context(parcel: sqlite3.Row) -> dict:
    if parcel["lat"] is None or parcel["lon"] is None:
        return {"available": False, "note": "Parcel has no coordinates.", "features": []}
    radius = int(os.getenv("OSM_RADIUS_METERS", "60"))
    query = textwrap.dedent(
        f"""
        [out:json][timeout:25];
        (
          way(around:{radius},{parcel['lat']},{parcel['lon']})["building"];
          way(around:{radius},{parcel['lat']},{parcel['lon']})["landuse"];
          node(around:{radius},{parcel['lat']},{parcel['lon']})["amenity"];
          node(around:{radius},{parcel['lat']},{parcel['lon']})["shop"];
          node(around:{radius},{parcel['lat']},{parcel['lon']})["historic"];
        );
        out tags center 20;
        """
    ).strip()
    endpoint = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
    try:
        data = post_json(endpoint, {"data": query}, timeout=45, form=True)
    except Exception as exc:
        return {"available": False, "note": f"OpenStreetMap lookup failed: {exc}", "features": []}
    features = []
    for element in data.get("elements", [])[:20]:
        tags = element.get("tags", {})
        features.append(
            {
                "type": element.get("type"),
                "id": element.get("id"),
                "name": tags.get("name"),
                "building": tags.get("building"),
                "amenity": tags.get("amenity"),
                "shop": tags.get("shop"),
                "landuse": tags.get("landuse"),
                "historic": tags.get("historic"),
                "tags": tags,
            }
        )
    return {
        "available": True,
        "radius_meters": radius,
        "features": features,
        "summary": summarize_osm_features(features),
        "notable_features": notable_osm_features(features),
    }


def summarize_osm_features(features: list[dict]) -> dict:
    summary = {
        "buildings": 0,
        "named_features": 0,
        "amenities": {},
        "shops": {},
        "landuse": {},
        "historic": {},
    }
    for feature in features:
        if feature.get("building"):
            summary["buildings"] += 1
        if feature.get("name"):
            summary["named_features"] += 1
        for key, bucket in (("amenity", "amenities"), ("shop", "shops"), ("landuse", "landuse"), ("historic", "historic")):
            value = feature.get(key)
            if value:
                summary[bucket][value] = summary[bucket].get(value, 0) + 1
    return summary


def notable_osm_features(features: list[dict]) -> list[dict]:
    notable = []
    for feature in features:
        tags = feature.get("tags") or {}
        label = feature.get("name")
        category = None
        for key in ("amenity", "shop", "landuse", "historic"):
            if feature.get(key):
                category = f"{key}: {feature[key]}"
                break
        if not label and category:
            label = category
        if not label and feature.get("building") not in (None, "yes"):
            label = f"building: {feature['building']}"
        if not label:
            continue
        notable.append(
            {
                "label": label,
                "category": category or ("building" if feature.get("building") else "feature"),
                "type": feature.get("type"),
                "id": feature.get("id"),
                "tags": {k: v for k, v in tags.items() if k in ("name", "amenity", "shop", "landuse", "historic", "building")},
            }
        )
    return notable[:10]


def display_address(parcel: sqlite3.Row) -> str:
    if parcel["address"]:
        return parcel["address"].title()
    if parcel["lat"] is not None and parcel["lon"] is not None:
        return f"{parcel['lat']:.5f}, {parcel['lon']:.5f}"
    return f"Parcel {parcel['id']}"


def load_entries() -> list[dict]:
    if not ENTRIES_PATH.exists():
        return []
    return json.loads(ENTRIES_PATH.read_text(encoding="utf-8"))


def save_entries(entries: list[dict]) -> None:
    ENTRIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES_PATH.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")


def property_url(entry_id: int | str) -> str:
    return f"properties/{int(entry_id):06d}/"


def parcel_progress() -> dict:
    if not DB_PATH.exists():
        return {"generated_at": utc_now(), "total": 0, "published": 0, "unpublished": 0, "parcels": []}
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, parcel_key, address, lat, lon, published_at
            FROM parcels
            WHERE lat IS NOT NULL AND lon IS NOT NULL
            ORDER BY id
            """
        ).fetchall()
    entries_by_id = {entry.get("id"): entry for entry in load_entries()}
    parcels = []
    for row in rows:
        entry = entries_by_id.get(row["id"])
        layers = entry_layers(entry) if entry else {}
        review = review_reasons(entry) if entry else []
        parcels.append(
            {
                "id": row["id"],
                "parcel_key": row["parcel_key"],
                "address": row["address"].title() if row["address"] else f"Parcel {row['id']}",
                "lat": row["lat"],
                "lon": row["lon"],
                "published": bool(row["published_at"]),
                "published_at": row["published_at"],
                "url": property_url(row["id"]) if row["published_at"] else None,
                "layers": layers,
                "review": review,
            }
        )
    published = sum(1 for parcel in parcels if parcel["published"])
    return {
        "generated_at": utc_now(),
        "total": len(parcels),
        "published": published,
        "unpublished": len(parcels) - published,
        "parcels": parcels,
    }


def entry_layers(entry: dict | None) -> dict:
    if not entry:
        return {}
    open_data = entry.get("open_data") or {}
    ai = entry.get("ai_analysis") or {}
    return {
        "vacant": bool(open_data.get("vacant_properties")),
        "rental": bool(open_data.get("rental_registry")),
        "code": bool(open_data.get("code_violations")),
        "unfit": bool(open_data.get("unfit_properties")),
        "ai_flag": bool(ai.get("possible_unrecorded_issues")),
        "review": bool(entry.get("review_reasons") or review_reasons(entry)),
    }


def issue_flags(matches: dict[str, list[dict]], ai_analysis: dict, image_status: dict | None = None) -> list[str]:
    flags = summarize_records(matches)
    if image_status and image_status.get("needs_rerun"):
        flags.append("Image needs rerun")
    possible = ai_analysis.get("possible_unrecorded_issues") if ai_analysis.get("available") else None
    if isinstance(possible, list):
        for item in possible:
            if item:
                flags.append(f"Image-only flag: {item}")
    if ai_analysis.get("needs_human_review") in (True, "true", "yes", "Yes"):
        flags.append("Needs human review")
    return flags


def review_reasons(entry: dict) -> list[str]:
    reasons = []
    image_status = entry.get("image_quality") or {}
    ai = entry.get("ai_analysis") or {}
    if image_status.get("needs_rerun"):
        reasons.append("Image needs rerun")
    if not ai.get("available"):
        reasons.append("AI analysis unavailable")
    if ai.get("needs_human_review") in (True, "true", "yes", "Yes"):
        reasons.append("AI requested human review")
    possible = ai.get("possible_unrecorded_issues")
    if isinstance(possible, list) and any(possible):
        reasons.append("Possible image-only issue")
    flags = ai.get("visible_flags") or {}
    for label, value in flags.items():
        if value == "yes":
            reasons.append(label.replace("_", " "))
    return sorted(set(reasons))


def publish_entry(conn: sqlite3.Connection) -> dict:
    conn.row_factory = sqlite3.Row
    parcel = conn.execute("SELECT * FROM parcels WHERE published_at IS NULL ORDER BY id ASC LIMIT 1").fetchone()
    if not parcel:
        raise RuntimeError("No unpublished parcels available. Run seed first or reset published_at.")
    return publish_parcel(conn, parcel)


def find_parcel(conn: sqlite3.Connection, id_: int | None = None, address: str | None = None) -> sqlite3.Row:
    conn.row_factory = sqlite3.Row
    if id_ is not None:
        parcel = conn.execute("SELECT * FROM parcels WHERE id = ?", (id_,)).fetchone()
        if not parcel:
            raise RuntimeError(f"No parcel found with id {id_}.")
        return parcel
    if address:
        target = normalize_text(address)
        parcel = conn.execute(
            "SELECT * FROM parcels WHERE address = ? ORDER BY id LIMIT 1",
            (target,),
        ).fetchone()
        if not parcel:
            parcel = conn.execute(
                "SELECT * FROM parcels WHERE address LIKE ? ORDER BY id LIMIT 1",
                (f"%{target}%",),
            ).fetchone()
        if not parcel:
            raise RuntimeError(f"No parcel found matching address: {address}")
        return parcel
    raise RuntimeError("Pass id_ or address.")


def publish_parcel(conn: sqlite3.Connection, parcel: sqlite3.Row) -> dict:
    matches = matching_records(conn, parcel)
    image_rel, image_error = fetch_property_image(parcel)
    image_path = ROOT / image_rel if image_rel else ROOT / "missing.jpg"
    image_status = image_quality(image_path if image_rel else None, image_error)
    ai = analyze_image(image_path, parcel, matches) if image_rel else {"available": False, "note": image_error}
    census = census_tract_context(parcel)
    osm = osm_context(parcel)
    entry = {
        "id": parcel["id"],
        "published_at": utc_now(),
        "title": display_address(parcel),
        "address": display_address(parcel),
        "parcel_key": parcel["parcel_key"],
        "lat": parcel["lat"],
        "lon": parcel["lon"],
        "image": image_rel,
        "image_note": image_error,
        "image_quality": image_status,
        "open_data": matches,
        "census_tract": census,
        "osm": osm,
        "ai_analysis": ai,
        "flags": issue_flags(matches, ai, image_status),
    }
    entry["review_reasons"] = review_reasons(entry)
    entries = load_entries()
    entries = [item for item in entries if item.get("id") != parcel["id"]]
    entries.insert(0, entry)
    save_entries(entries)
    build_site(entries)
    conn.execute("UPDATE parcels SET published_at = ? WHERE id = ?", (entry["published_at"], parcel["id"]))
    conn.commit()
    return entry


def compact_value(value: object) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    text = " ".join(str(value).split())
    return text[:120]


def record_preview(records: list[dict], limit: int = 4) -> str:
    if not records:
        return "<p>No matching records found in this feed.</p>"
    pieces = []
    for record in records[:limit]:
        fields = [(k, compact_value(v)) for k, v in record.items() if compact_value(v)]
        fields = fields[:6]
        rows = "".join(f"<dt>{html.escape(str(k))}</dt><dd>{html.escape(str(v))}</dd>" for k, v in fields)
        pieces.append(f"<dl>{rows}</dl>")
    return "".join(pieces)


def list_html(values: object) -> str:
    if isinstance(values, str):
        values = [values] if values else []
    if not isinstance(values, list) or not values:
        return "<li>No items reported.</li>"
    return "".join(f"<li>{html.escape(str(value))}</li>" for value in values if value)


def osm_summary_html(osm: dict) -> str:
    if not osm.get("available"):
        return f"<p>{html.escape(osm.get('note') or 'No nearby OSM features returned.')}</p>"

    summary = osm.get("summary") or summarize_osm_features(osm.get("features") or [])
    notable = osm.get("notable_features") or notable_osm_features(osm.get("features") or [])
    bits = []
    buildings = summary.get("buildings", 0)
    if buildings:
        bits.append(f"{buildings} mapped building footprint{'s' if buildings != 1 else ''}")
    named = summary.get("named_features", 0)
    if named:
        bits.append(f"{named} named feature{'s' if named != 1 else ''}")
    for key, label in (("amenities", "amenity"), ("shops", "shop"), ("landuse", "land-use"), ("historic", "historic")):
        values = summary.get(key) or {}
        for value, count in sorted(values.items()):
            bits.append(f"{count} {label}: {value}")

    summary_html = "".join(f"<li>{html.escape(bit)}</li>" for bit in bits) or "<li>No meaningful OSM tags found nearby.</li>"
    notable_html = "".join(
        f"<li><strong>{html.escape(str(item.get('label')))}</strong><span>{html.escape(str(item.get('type')))} #{html.escape(str(item.get('id')))}</span></li>"
        for item in notable
    )
    notable_block = f"<h5>Notable mapped features</h5><ul class=\"osm-results\">{notable_html}</ul>" if notable_html else ""
    return f"<h5>Summary</h5><ul class=\"osm-results\">{summary_html}</ul>{notable_block}"


def annotation_overlays(ai: dict) -> str:
    overlays = []
    for item in ai.get("image_annotations") or []:
        bbox = item.get("bbox") or {}
        try:
            x = max(0, min(1, float(bbox.get("x", 0)))) * 100
            y = max(0, min(1, float(bbox.get("y", 0)))) * 100
            width = max(0, min(1, float(bbox.get("width", 0)))) * 100
            height = max(0, min(1, float(bbox.get("height", 0)))) * 100
        except (TypeError, ValueError):
            continue
        if width <= 0 or height <= 0:
            continue
        label = html.escape(str(item.get("label") or "AI review area"))
        confidence = html.escape(str(item.get("confidence") or "unknown"))
        overlays.append(
            f"""
            <span class="annotation-box" style="left:{x:.2f}%;top:{y:.2f}%;width:{width:.2f}%;height:{height:.2f}%;">
              <span>{label} · {confidence}</span>
            </span>
            """
        )
    return "".join(overlays)


def build_site(entries: list[dict]) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_review_queue(entries)
    build_tract_pages(entries)
    progress = parcel_progress()
    PROGRESS_PATH.write_text(json.dumps(progress, separators=(",", ":")), encoding="utf-8")
    build_property_pages(entries)
    latest = entries[0] if entries else None
    cards = []
    for entry in entries[:24]:
        image = entry.get("image")
        image_html = f'<img src="{html.escape(image)}" alt="Street View image for {html.escape(entry["title"])}">' if image else '<div class="image-missing">No Street View image</div>'
        summary = entry.get("ai_analysis", {}).get("summary") or entry.get("ai_analysis", {}).get("note") or "AI analysis has not run for this entry."
        flags = entry.get("flags") or []
        cards.append(
            f"""
            <article class="entry-card">
                <div class="entry-image">{image_html}</div>
                <div class="entry-body">
                    <p class="entry-date">{html.escape(entry.get("published_at", ""))}</p>
                    <h3>{html.escape(entry["title"])}</h3>
                    <p>{html.escape(str(summary))}</p>
                    <div class="flag-row">{''.join(f'<span>{html.escape(flag)}</span>' for flag in flags[:3]) or '<span>No open-data match yet</span>'}</div>
                    <a href="{property_url(entry['id'])}">Open entry</a>
                </div>
            </article>
            """
        )

    latest_title = html.escape(latest["title"]) if latest else "No published entries yet"
    latest_summary = html.escape(str((latest or {}).get("ai_analysis", {}).get("summary") or "Run the hourly job to publish the first parcel."))
    total = progress["total"]
    published = progress["published"]
    progress_pct = round((published / total) * 100, 2) if total else 0
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Syracuse Property Atlas | DataCuse</title>
  <meta name="description" content="An EveryLot-style Syracuse parcel atlas combining Street View, AI image notes, and city open data.">
  <link rel="canonical" href="https://www.datacuse.com/projects/syracuse-property-atlas/">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav class="site-nav" aria-label="Primary">
    <a class="brand" href="/">
      <span class="brand-mark">D</span>
      <span>Data<span>Cuse</span></span>
    </a>
    <div class="nav-links">
      <a href="#latest">Latest</a>
      <a href="#map">Map</a>
      <a href="#search">Search</a>
      <a href="#entries">Entries</a>
      <a href="#method">Method</a>
      <a href="/">All projects</a>
    </div>
  </nav>
  <header class="hero" id="latest">
    <section>
      <p class="eyebrow">Syracuse Property Atlas</p>
      <h1>One Syracuse parcel at a time.</h1>
      <p class="lede">A slow, sourced field notebook for city properties: parcel data, Street View, AI image observations, city open-data matches, tract context, and OpenStreetMap features.</p>
      <div class="stats">
        <div><strong>{len(entries)}</strong><span>published entries</span></div>
        <div><strong>{total}</strong><span>mapped parcels</span></div>
        <div><strong>{progress_pct}%</strong><span>complete</span></div>
      </div>
    </section>
    <aside class="latest-card">
      <span>Latest parcel</span>
      <h2>{latest_title}</h2>
      <p>{latest_summary}</p>
      <a href="#entries">Browse entries</a>
    </aside>
  </header>
  <main>
    <section class="section atlas-tools" id="map">
      <div class="section-heading">
        <p class="eyebrow">Atlas map</p>
        <h2>Progress across Syracuse</h2>
        <p>Orange points are published entries. Gray points are parcels still waiting in the queue. Select a point to open the property popup.</p>
      </div>
      <div class="tool-shell">
        <div class="map-toolbar" id="search">
          <label for="parcelSearch">Search address or parcel ID</label>
          <input id="parcelSearch" type="search" placeholder="Try Spring St, Ross Pk, or 002-22-090">
          <div class="status-filter" aria-label="Map status filter">
            <button type="button" class="is-active" data-status-filter="all">All</button>
            <button type="button" data-status-filter="published">Published</button>
            <button type="button" data-status-filter="queued">Queued</button>
          </div>
          <div class="layer-filter" aria-label="Map layer filter">
            <label><input type="checkbox" value="vacant"> Vacant records</label>
            <label><input type="checkbox" value="rental"> Rental registry</label>
            <label><input type="checkbox" value="code"> Code violations</label>
            <label><input type="checkbox" value="unfit"> Unfit records</label>
            <label><input type="checkbox" value="ai_flag"> AI flags</label>
            <label><input type="checkbox" value="review"> Review queue</label>
          </div>
          <div class="progress-bar" aria-label="Publishing progress"><span style="width: {progress_pct}%"></span></div>
          <p><strong id="publishedCount">{published}</strong> of <strong id="totalCount">{total}</strong> mapped parcels published.</p>
          <div id="searchResults" class="search-results" aria-live="polite"></div>
        </div>
        <div id="atlasMap" class="atlas-map" aria-label="Syracuse parcel publishing map"></div>
      </div>
    </section>

    <section class="section" id="entries">
      <div class="section-heading">
        <p class="eyebrow">Published properties</p>
        <h2>Newest entries</h2>
        <p>Each entry is generated by the hourly pipeline. AI notes are treated as field observations, not official code findings.</p>
      </div>
      <div class="entry-grid">
        {''.join(cards) or '<p>No entries have been published yet.</p>'}
      </div>
    </section>
    <section class="method" id="method">
      <div>
        <p class="eyebrow">Method</p>
        <h2>Open data first, AI second.</h2>
        <p>The database starts with Syracuse parcels and enriches each selected property with vacant, rental registry, code violation, and unfit-property feeds. Census geocoding adds tract-level ACS context, OpenStreetMap adds nearby mapped features, and optional image analysis adds a visible-condition read when a free or paid image source is configured.</p>
      </div>
      <ul>
        <li>Parcel feed: 2025 Syracuse parcel map from data.syr.gov ArcGIS.</li>
        <li>Open-data joins use parcel IDs, normalized addresses, and nearby coordinates.</li>
        <li>ACS source: Census API, defaulting to the 2024 ACS 5-year profile.</li>
        <li>OSM source: Overpass API, queried with an identifying User-Agent by the Python runtime.</li>
        <li>AI output is intentionally cautious and limited to exterior conditions visible from the configured image source.</li>
      </ul>
    </section>
  </main>
  <footer class="site-footer">
    <a class="brand" href="/"><span class="brand-mark">D</span><span>Data<span>Cuse</span></span></a>
    <p>Independent Syracuse data stories, tools, and field notes.</p>
  </footer>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="app.js"></script>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(html_doc, encoding="utf-8")


def write_review_queue(entries: list[dict]) -> None:
    queue = []
    for entry in entries:
        reasons = entry.get("review_reasons") or review_reasons(entry)
        if not reasons:
            continue
        queue.append(
            {
                "id": entry.get("id"),
                "title": entry.get("title"),
                "published_at": entry.get("published_at"),
                "reasons": reasons,
                "url": property_url(entry.get("id")),
            }
        )
    REVIEW_PATH.write_text(json.dumps(queue, indent=2, sort_keys=True), encoding="utf-8")


def tract_key(entry: dict) -> str | None:
    census = entry.get("census_tract") or {}
    state = census.get("state")
    county = census.get("county")
    tract = census.get("tract")
    if not (state and county and tract):
        return None
    return f"{state}{county}{tract}"


def build_tract_pages(entries: list[dict]) -> None:
    if TRACTS_DIR.exists():
        shutil.rmtree(TRACTS_DIR)
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        key = tract_key(entry)
        if key:
            groups.setdefault(key, []).append(entry)
    if not groups:
        return
    TRACTS_DIR.mkdir(parents=True, exist_ok=True)
    cards = []
    for key, tract_entries in sorted(groups.items()):
        page_dir = TRACTS_DIR / key
        page_dir.mkdir(parents=True, exist_ok=True)
        page_dir.joinpath("index.html").write_text(tract_page_html(key, tract_entries), encoding="utf-8")
        census = tract_entries[0].get("census_tract") or {}
        cards.append(
            f"""
            <a class="tract-card" href="{key}/">
              <strong>{html.escape(census.get("name") or f"Tract {key}")}</strong>
              <span>{len(tract_entries)} published propert{'ies' if len(tract_entries) != 1 else 'y'}</span>
            </a>
            """
        )
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tract Index | Syracuse Property Atlas</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <nav class="site-nav" aria-label="Primary"><a class="brand" href="../"><span class="brand-mark">D</span><span>Data<span>Cuse</span></span></a></nav>
  <main class="section"><div class="section-heading"><p class="eyebrow">Census tracts</p><h1>Published property entries by tract.</h1><p>Tract pages summarize published atlas entries as the hourly pipeline grows.</p></div><div class="tract-grid">{''.join(cards)}</div></main>
</body>
</html>"""
    (TRACTS_DIR / "index.html").write_text(index_html, encoding="utf-8")


def tract_page_html(key: str, entries: list[dict]) -> str:
    census = entries[0].get("census_tract") or {}
    metrics = census.get("metrics") or {}
    metrics_html = "".join(
        f"<dt>{html.escape(str(name))}</dt><dd>{html.escape(str(value))}</dd>"
        for name, value in metrics.items()
        if value not in (None, "", "-888888888")
    ) or f"<p>{html.escape(census.get('note') or 'No ACS metrics available.')}</p>"
    cards = "".join(
        f"""
        <a class="project-card" href="../../{property_url(entry['id'])}">
          <div class="project-copy">
            <p class="card-kicker">{html.escape(entry.get("published_at", ""))}</p>
            <h3>{html.escape(entry.get("title", "Property"))}</h3>
            <p>{html.escape(str((entry.get("ai_analysis") or {}).get("summary") or "No AI summary available."))}</p>
          </div>
        </a>
        """
        for entry in entries
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(census.get("name") or key)} | Syracuse Property Atlas</title>
  <link rel="stylesheet" href="../../style.css">
</head>
<body>
  <nav class="site-nav" aria-label="Primary"><a class="brand" href="../../"><span class="brand-mark">D</span><span>Data<span>Cuse</span></span></a></nav>
  <main class="section">
    <div class="section-heading"><p class="eyebrow">Census tract</p><h1>{html.escape(census.get("name") or key)}</h1><p>{len(entries)} published atlas entries in this tract.</p></div>
    <section class="feed-panel"><h4>ACS context</h4><dl>{metrics_html}</dl></section>
    <div class="entry-grid">{cards}</div>
  </main>
</body>
</html>"""


def build_property_pages(entries: list[dict]) -> None:
    if PROPERTIES_DIR.exists():
        shutil.rmtree(PROPERTIES_DIR)
    for entry in entries:
        page_dir = PROPERTIES_DIR / f"{int(entry['id']):06d}"
        page_dir.mkdir(parents=True, exist_ok=True)
        page_dir.joinpath("index.html").write_text(property_page_html(entry), encoding="utf-8")


def property_page_html(entry: dict) -> str:
    feeds = []
    for feed in OPEN_DATA_FEEDS:
        records = entry.get("open_data", {}).get(feed["name"], [])
        feeds.append(
            f"""
            <section class="feed-panel">
                <h4>{html.escape(feed["label"])} <span>{len(records)}</span></h4>
                {record_preview(records)}
            </section>
            """
        )
    ai = entry.get("ai_analysis", {})
    condition_scores = ai.get("condition_scores") or {}
    condition_html = "".join(
        f"<dt>{html.escape(str(key).replace('_', ' ').title())}</dt><dd>{html.escape(str(value))}</dd>"
        for key, value in condition_scores.items()
    ) or "<p>No structured condition scores available.</p>"
    visible_flags = ai.get("visible_flags") or {}
    visible_flags_html = "".join(
        f"<dt>{html.escape(str(key).replace('_', ' ').title())}</dt><dd>{html.escape(str(value))}</dd>"
        for key, value in visible_flags.items()
    ) or "<p>No structured visible flags available.</p>"
    image_status = entry.get("image_quality") or {}
    image_status_html = "".join(
        f"<dt>{html.escape(str(key).replace('_', ' ').title())}</dt><dd>{html.escape(str(value))}</dd>"
        for key, value in image_status.items()
        if key != "warnings"
    )
    review_html = list_html(entry.get("review_reasons") or review_reasons(entry))
    census = entry.get("census_tract", {})
    census_metrics = census.get("metrics") or {}
    census_html = "".join(
        f"<dt>{html.escape(str(key))}</dt><dd>{html.escape(str(value))}</dd>"
        for key, value in census_metrics.items()
        if value not in (None, "", "-888888888")
    ) or f"<p>{html.escape(census.get('note') or 'No ACS tract context available.')}</p>"
    osm = entry.get("osm", {})
    osm_html = osm_summary_html(osm)
    image = entry.get("image")
    annotations = annotation_overlays(ai)
    image_html = f'<img src="../../{html.escape(image)}" alt="Street View image for {html.escape(entry["title"])}">{annotations}' if image else '<div class="image-missing">No Street View image</div>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(entry["title"])} | Syracuse Property Atlas</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../style.css">
</head>
<body>
  <nav class="site-nav" aria-label="Primary">
    <a class="brand" href="../../"><span class="brand-mark">D</span><span>Data<span>Cuse</span></span></a>
    <div class="nav-links"><a href="../../#map">Map</a><a href="../../#search">Search</a><a href="../../#entries">Latest</a></div>
  </nav>
  <main class="property-page">
    <article class="entry-detail">
      <header class="property-hero">
        <div>
          <p class="eyebrow">Property entry</p>
          <h1>{html.escape(entry["title"])}</h1>
          <p>Published {html.escape(entry.get("published_at", ""))}</p>
          <p>Parcel key: {html.escape(str(entry.get("parcel_key") or "Unknown"))}</p>
        </div>
        <div class="property-image">{image_html}</div>
      </header>
      <div class="detail-grid">
        <section>
          <h4>AI image read</h4>
          <p>{html.escape(str(ai.get("summary") or ai.get("note") or "No AI summary available."))}</p>
          <p><strong>Property type guess:</strong> {html.escape(str(ai.get("property_type_guess") or "unclear"))}</p>
          <h5>Visible conditions</h5>
          <ul>{list_html(ai.get("visible_conditions"))}</ul>
          <h5>Condition scores</h5>
          <dl>{condition_html}</dl>
          <h5>Visible flags</h5>
          <dl>{visible_flags_html}</dl>
          <h5>Possible image-only flags</h5>
          <ul>{list_html(ai.get("possible_unrecorded_issues"))}</ul>
          <h5>AI review boxes</h5>
          <ul>{list_html([f"{item.get('label', 'AI review area')}: {item.get('reason', '')}" for item in (ai.get("image_annotations") or [])])}</ul>
          <h5>Review reasons</h5>
          <ul>{review_html}</ul>
          <h5>Image quality</h5>
          <dl>{image_status_html}</dl>
          <p class="caveat">{html.escape(str(ai.get("caveats") or ""))}</p>
        </section>
        <section>
          <h4>ACS tract context</h4>
          <p>{html.escape(census.get("name") or census.get("source") or "")}</p>
          <dl>{census_html}</dl>
        </section>
        <section>
          <h4>OpenStreetMap nearby</h4>
          <p>{html.escape(str(osm.get("radius_meters") or ""))} meter search radius</p>
          {osm_html}
        </section>
      </div>
      <div class="feed-grid">{''.join(feeds)}</div>
    </article>
  </main>
  <footer class="site-footer">
    <a class="brand" href="../../"><span class="brand-mark">D</span><span>Data<span>Cuse</span></span></a>
    <p>Independent Syracuse data stories, tools, and field notes.</p>
  </footer>
</body>
</html>
"""


def cmd_seed(args: argparse.Namespace) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        inserted = seed_parcels(conn, limit=args.limit)
    print(f"Seeded {inserted} new parcels into {DB_PATH}")


def cmd_refresh(args: argparse.Namespace) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        counts = refresh_open_data(conn, limit=args.limit)
    print(json.dumps(counts, indent=2, sort_keys=True))


def cmd_run_once(args: argparse.Namespace) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        if conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0] == 0:
            print("Parcel table is empty; seeding parcels first.")
            seed_parcels(conn, limit=args.limit)
        if conn.execute("SELECT COUNT(*) FROM parcels WHERE published_at IS NULL").fetchone()[0] == 0:
            print("No unpublished parcels found; seeding any missing parcels from the parcel feed.")
            seed_parcels(conn, limit=args.limit)
        if args.refresh_open_data or conn.execute("SELECT COUNT(*) FROM feed_records").fetchone()[0] == 0:
            print("Refreshing open-data feeds.")
            refresh_open_data(conn, limit=args.limit)
        if args.id or args.address:
            parcel = find_parcel(conn, id_=args.id, address=args.address)
            entry = publish_parcel(conn, parcel)
        else:
            entry = publish_entry(conn)
    print(f"Published {entry['title']} to {SITE_DIR / 'index.html'}")


def cmd_build(args: argparse.Namespace) -> None:
    build_site(load_entries())
    print(f"Built {SITE_DIR / 'index.html'}")


def cmd_status(args: argparse.Namespace) -> None:
    if not DB_PATH.exists():
        print(f"No database found at {DB_PATH}")
        return
    with sqlite3.connect(DB_PATH) as conn:
        parcels = conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0]
        unpublished = conn.execute("SELECT COUNT(*) FROM parcels WHERE published_at IS NULL").fetchone()[0]
        published = conn.execute("SELECT COUNT(*) FROM parcels WHERE published_at IS NOT NULL").fetchone()[0]
        feeds = conn.execute(
            "SELECT feed_name, COUNT(*) FROM feed_records GROUP BY feed_name ORDER BY feed_name"
        ).fetchall()
    print(f"Parcels: {parcels}")
    print(f"Published: {published}")
    print(f"Unpublished: {unpublished}")
    if feeds:
        print("Open-data records:")
        for name, count in feeds:
            print(f"  {name}: {count}")


def cmd_reset(args: argparse.Namespace) -> None:
    if not DB_PATH.exists():
        raise RuntimeError(f"No database found at {DB_PATH}")
    if not args.id and not args.address:
        raise RuntimeError("Pass --id or --address.")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if args.id:
            rows = conn.execute("SELECT id, address, published_at FROM parcels WHERE id = ?", (args.id,)).fetchall()
        else:
            target = normalize_text(args.address)
            rows = conn.execute(
                "SELECT id, address, published_at FROM parcels WHERE address = ?",
                (target,),
            ).fetchall()

        if not rows:
            raise RuntimeError("No matching parcel found.")

        for row in rows:
            conn.execute("UPDATE parcels SET published_at = NULL WHERE id = ?", (row["id"],))
        conn.commit()

    reset_ids = {row["id"] for row in rows}
    entries = [entry for entry in load_entries() if entry.get("id") not in reset_ids]
    save_entries(entries)
    build_site(entries)

    print(f"Reset {len(rows)} parcel(s):")
    for row in rows:
        print(f"  {row['id']}: {row['address'] or '(no address)'}")


def main() -> None:
    load_local_env()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    seed = sub.add_parser("seed", help="Seed the SQLite parcel database from the parcel feed.")
    seed.add_argument("--limit", type=int, default=None, help="Limit records for testing.")
    seed.set_defaults(func=cmd_seed)

    refresh = sub.add_parser("refresh-open-data", help="Refresh cached open-data feed records.")
    refresh.add_argument("--limit", type=int, default=None, help="Limit records for testing.")
    refresh.set_defaults(func=cmd_refresh)

    run_once = sub.add_parser("run-once", help="Publish the next unpublished property.")
    run_once.add_argument("--limit", type=int, default=None, help="Limit records when bootstrapping for testing.")
    run_once.add_argument("--refresh-open-data", action="store_true", help="Refresh open-data feeds before publishing.")
    run_once.add_argument("--id", type=int, default=None, help="Publish a specific parcel row id.")
    run_once.add_argument("--address", type=str, default=None, help="Publish the first parcel matching this address.")
    run_once.set_defaults(func=cmd_run_once)

    build = sub.add_parser("build-site", help="Rebuild the static website from entries.json.")
    build.set_defaults(func=cmd_build)

    status = sub.add_parser("status", help="Show local database counts.")
    status.set_defaults(func=cmd_status)

    reset = sub.add_parser("reset", help="Clear published_at for a parcel so it can be republished.")
    reset.add_argument("--id", type=int, default=None, help="Parcel row id to reset.")
    reset.add_argument("--address", type=str, default=None, help="Normalized or display address to reset.")
    reset.set_defaults(func=cmd_reset)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
