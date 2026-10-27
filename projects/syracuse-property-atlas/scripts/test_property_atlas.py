import datetime as dt
import sqlite3
import unittest
import urllib.error
from unittest.mock import patch

import property_atlas as atlas


class FeedTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        atlas.init_db(self.conn)
        self.addCleanup(self.conn.close)

    def add_record(self, key, address, marker):
        self.conn.execute(
            "INSERT INTO feed_records (feed_name,parcel_key,address,lat,lon,properties_json,refreshed_at) VALUES (?,?,?,?,?,?,?)",
            ("code_violations", key, address, 43.05, -76.15, '{"marker":"' + marker + '"}', atlas.utc_now()),
        )

    def test_city_address_fields_and_nonproperty_identifiers(self):
        self.assertEqual(atlas.normalized_address({"PropertyAddress": "109 Wilmore Pl"}), "109 WILMORE PL")
        self.assertEqual(atlas.normalized_address({"complaint_address": "283 Croly St."}), "283 CROLY ST")
        self.assertEqual(atlas.normalized_address({"address": " ", "PropertyAddress": "1 Main St"}), "1 MAIN ST")
        self.assertEqual(atlas.normalized_address({"mailadd": "1 Owner St"}), "")
        self.assertEqual(atlas.parcel_key({"ObjectId": 1}), "")
        self.assertEqual(atlas.parcel_key({"SBL": " ", "PRINTKEY": "002.-22-09.0"}), "002-22-090")

    def test_exact_matches_exclude_neighbors_and_conflicting_ids(self):
        self.add_record("A", "1 MAIN ST", "exact")
        self.add_record("", "1 MAIN ST", "address")
        self.add_record("B", "3 MAIN ST", "neighbor")
        self.add_record("C", "1 MAIN ST", "conflict")
        result = atlas.matching_records(self.conn, {"parcel_key": "A", "address": "1 MAIN ST", "lat": 43.05, "lon": -76.15})
        self.assertEqual(result["code_violations"], [{"marker": "exact"}, {"marker": "address"}])

    def test_matches_are_not_silently_capped_at_twenty(self):
        for i in range(25):
            self.add_record("A", "1 MAIN ST", str(i))
        result = atlas.matching_records(self.conn, {"parcel_key": "A", "address": "1 MAIN ST"})
        self.assertEqual(len(result["code_violations"]), 25)

    def test_geojson_nested_transfer_limit_continues_short_pages(self):
        pages = [
            {"features": [{"id": 1}], "properties": {"exceededTransferLimit": True}},
            {"features": [{"id": 2}], "properties": {"exceededTransferLimit": False}},
        ]
        with patch.object(atlas, "request_json", side_effect=pages) as request, patch.object(atlas.time, "sleep"):
            self.assertEqual(len(atlas.fetch_arcgis_geojson({"name": "test", "url": "test"}, page_size=1000)), 2)
            self.assertEqual(request.call_args.kwargs["params"]["resultOffset"], 1)

    def test_arcgis_error_is_not_an_empty_feed(self):
        with patch.object(atlas, "request_json", return_value={"error": {"code": 500}}):
            with self.assertRaises(RuntimeError):
                atlas.fetch_arcgis_geojson({"name": "test", "url": "test"})

    def test_incomplete_refresh_keeps_cached_records(self):
        self.add_record("A", "1 MAIN ST", "cached")
        self.conn.execute("UPDATE feed_records SET feed_name='vacant_properties'")
        with patch.object(atlas, "request_json", return_value={"count": 2}), patch.object(atlas, "fetch_arcgis_geojson", return_value=[{"properties": {"ObjectId": 1}}]):
            with self.assertRaises(RuntimeError):
                atlas.refresh_open_data(self.conn)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM feed_records").fetchone()[0], 1)

    def test_duplicate_pages_cannot_replace_cached_feed(self):
        self.add_record("A", "1 MAIN ST", "cached")
        self.conn.execute("UPDATE feed_records SET feed_name='vacant_properties'")
        duplicates = [{"properties": {"ObjectId": 1}}, {"properties": {"ObjectId": 1}}]
        with patch.object(atlas, "request_json", return_value={"count": 2}), patch.object(atlas, "fetch_arcgis_geojson", return_value=duplicates):
            with self.assertRaises(RuntimeError):
                atlas.refresh_open_data(self.conn)
        self.assertEqual(self.conn.execute("SELECT parcel_key FROM feed_records").fetchone()[0], "A")

    def test_partial_or_stale_cache_requires_refresh(self):
        self.assertTrue(atlas.feeds_need_refresh(self.conn))
        for feed in atlas.OPEN_DATA_FEEDS:
            self.conn.execute("INSERT INTO feed_sync VALUES (?,?,?,?)", (feed["name"], atlas.utc_now(), 1000, 1))
        self.assertFalse(atlas.feeds_need_refresh(self.conn))
        self.conn.execute("UPDATE feed_sync SET complete=0 WHERE feed_name='rental_registry'")
        self.assertTrue(atlas.feeds_need_refresh(self.conn))
        stale = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=8)).isoformat()
        self.conn.execute("UPDATE feed_sync SET complete=1, refreshed_at=?", (stale,))
        self.assertTrue(atlas.feeds_need_refresh(self.conn))


class OsmTests(unittest.TestCase):
    def test_failure_retains_radius_and_diagnostics(self):
        with patch.dict(atlas.os.environ, {"OSM_RADIUS_METERS": "75"}), patch.object(atlas, "query_overpass", side_effect=RuntimeError("HTTP 406")):
            result = atlas.osm_context({"lat": 43.05, "lon": -76.15})
        self.assertFalse(result["available"])
        self.assertEqual(result["radius_meters"], 75)
        self.assertEqual(result["error"], "HTTP 406")
        self.assertNotIn("406", atlas.osm_summary_html(result))

    def test_fallback_and_rate_limit_pause(self):
        error = urllib.error.HTTPError("test", 406, "Not Acceptable", {}, None)
        with patch.dict(atlas.os.environ, {"OVERPASS_URL": "https://primary", "OVERPASS_FALLBACK_URLS": "https://fallback"}), patch.object(atlas, "post_json", side_effect=[error, {"elements": []}]), patch.object(atlas.time, "sleep") as sleep:
            data, endpoint = atlas.query_overpass("query")
        self.assertEqual(endpoint, "https://fallback")
        self.assertEqual(data, {"elements": []})
        sleep.assert_called_once_with(30)

    def test_partial_overpass_response_is_failure(self):
        with patch.dict(atlas.os.environ, {"OVERPASS_URL": "https://primary", "OVERPASS_FALLBACK_URLS": ""}), patch.object(atlas, "post_json", return_value={"elements": [], "remark": "runtime error: Query timed out"}):
            with self.assertRaises(RuntimeError):
                atlas.query_overpass("query")

    def test_batch_keeps_empty_and_nonempty_parcels_separate(self):
        data = {"elements": [{"type": "count"}, {"type": "count"}, {"type": "way", "id": 123, "tags": {"building": "yes"}}]}
        with patch.object(atlas, "query_overpass", return_value=(data, "test")):
            results = atlas.osm_context_batch([{"lat": 1, "lon": 2}, {"lat": 3, "lon": 4}])
        self.assertEqual(results[0]["features"], [])
        self.assertEqual(results[1]["features"][0]["id"], 123)

    def test_batch_rejects_missing_markers(self):
        with patch.object(atlas, "query_overpass", return_value=({"elements": []}, "test")):
            with self.assertRaises(RuntimeError):
                atlas.osm_context_batch([{"lat": 1, "lon": 2}])

    def test_old_failure_page_does_not_render_blank_radius(self):
        page = atlas.property_page_html({"title": "1 Main St", "osm": {"available": False, "note": "OpenStreetMap lookup failed: HTTP Error 406: Not Acceptable"}})
        self.assertNotIn("HTTP Error 406", page)
        self.assertNotIn("meter search radius", page)
        self.assertIn("temporarily unavailable", page)


if __name__ == "__main__":
    unittest.main()
