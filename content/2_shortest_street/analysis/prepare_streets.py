"""Download the city street layer and export an analysis starter shapefile.

Requires pyshp (import shapefile). Run from any directory with Python 3.
The output retains the service coverage; it is NOT clipped or street-filtered.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from zipfile import ZipFile, ZIP_DEFLATED

import shapefile


ROOT = Path(__file__).resolve().parent
SERVICE = "https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Streets/FeatureServer/0"
FIELDS = [
    "FID", "CITYST_ID", "FULLNAME", "PREFIX", "NAME", "TYPE", "SUFFIX",
    "CFCC", "FNODE_", "TNODE_", "L_F_ADD", "L_T_ADD", "R_F_ADD",
    "R_T_ADD", "FIPMCD90_L", "FIPMCD90_R", "FIPPLC90_L", "FIPPLC90_R",
    "BLKSTREET", "ST_FLAG", "LINECODE",
]
WGS84 = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'


def get_json(path, **params):
    # POST avoids the server's URL-length limit for batches of object IDs.
    with urlopen(path, data=urlencode(params).encode("ascii"), timeout=60) as response:
        data = json.load(response)
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def main():
    metadata = get_json(SERVICE, f="json")
    ids = sorted(get_json(SERVICE + "/query", where="1=1", returnIdsOnly="true", f="json")["objectIds"])
    features = []
    for offset in range(0, len(ids), 1000):
        batch = get_json(
            SERVICE + "/query", objectIds=",".join(map(str, ids[offset:offset + 1000])),
            outFields="*", returnGeometry="true", outSR=4326, f="geojson",
        )
        features.extend(batch["features"])
    actual_ids = [feature["properties"]["FID"] for feature in features]
    if sorted(actual_ids) != ids:
        raise RuntimeError("Downloaded IDs do not match the complete source ID list")
    for feature in features:
        geom = feature["geometry"]
        if not geom or geom["type"] not in ("LineString", "MultiLineString"):
            raise ValueError("Unexpected or missing street geometry")
    source = ROOT / "streets_city.geojson"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    (ROOT / "streets_city_service_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    folder = ROOT / "syracuse_streets"
    folder.mkdir(exist_ok=True)
    stem = folder / "syracuse_streets"
    definitions = {field["name"]: field for field in metadata["fields"]}
    with shapefile.Writer(str(stem), shapeType=shapefile.POLYLINE, encoding="utf-8") as writer:
        for name in FIELDS:
            field = definitions[name]
            if field["type"] == "esriFieldTypeString":
                writer.field(name, "C", size=min(field["length"], 254))
            else:
                writer.field(name, "N", size=18, decimal=0)
        for feature in features:
            geom = feature["geometry"]
            parts = [geom["coordinates"]] if geom["type"] == "LineString" else geom["coordinates"]
            writer.line(parts)
            writer.record(*[feature["properties"].get(name) for name in FIELDS])
    stem.with_suffix(".prj").write_text(WGS84, encoding="ascii")
    stem.with_suffix(".cpg").write_text("UTF-8", encoding="ascii")
    with shapefile.Reader(str(stem), encoding="utf-8") as reader:
        if len(reader) != len(ids) or len(reader.shapes()) != len(ids):
            raise RuntimeError("Shapefile round-trip count mismatch")
        for original, restored in zip(features, reader.iterShapeRecords()):
            expected = original["properties"]
            for name in FIELDS:
                value = expected.get(name)
                if value is None and definitions[name]["type"] == "esriFieldTypeString":
                    value = ""  # DBF character fields cannot distinguish null from blank.
                if isinstance(value, str):
                    value = value.strip()
                if restored.record[name] != value:
                    raise RuntimeError(f"Field mismatch: {name}")
            geom = original["geometry"]
            parts = [geom["coordinates"]] if geom["type"] == "LineString" else geom["coordinates"]
            expected_points = [tuple(point) for part in parts for point in part]
            if list(map(tuple, restored.shape.points)) != expected_points:
                raise RuntimeError("Coordinate round-trip mismatch")
    with ZipFile(ROOT / "syracuse_streets_shapefile.zip", "w", ZIP_DEFLATED) as archive:
        for extension in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
            path = stem.with_suffix(extension)
            archive.write(path, path.name)
    provenance = {
        "downloaded_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": SERVICE, "feature_count": len(features), "crs": "EPSG:4326",
        "coverage": "Full service extent, not clipped to the Syracuse municipal boundary",
        "filters": "None; not yet screened for public named streets or geometry artifacts",
        "shapefile_fields": FIELDS,
        "format_note": "DBF null strings become blanks; original nulls are preserved in GeoJSON.",
        "geojson_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_editing_info": metadata.get("editingInfo"),
        "measurement": "Coordinates are degrees. Reproject or use ellipsoidal lengths before ranking.",
        "validation": "All source IDs downloaded; shapefile count, retained attributes and coordinates round-trip checked",
    }
    (ROOT / "streets_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
