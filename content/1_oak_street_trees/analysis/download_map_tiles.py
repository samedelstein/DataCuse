"""Download and cache the small OSM basemap area used in the blog graphic."""
from pathlib import Path
import math
import requests

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "map_tiles"
CACHE.mkdir(exist_ok=True)
ZOOM = 15
WIDTH, HEIGHT = 1440, 1410


def world_pixel(lon, lat):
    scale = 256 * 2**ZOOM
    return ((lon + 180) / 360 * scale,
            (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * scale)


CX, CY = world_pixel(-76.138, 43.057)
LEFT, TOP = round(CX - WIDTH / 2), round(CY - HEIGHT / 2)


if __name__ == "__main__":
    session = requests.Session()
    session.headers["User-Agent"] = "SyracuseTreeBlogMap/1.0 (one-off local blog illustration)"
    downloaded = 0
    for x in range(LEFT // 256, (LEFT + WIDTH - 1) // 256 + 1):
        for y in range(TOP // 256, (TOP + HEIGHT - 1) // 256 + 1):
            path = CACHE / f"{ZOOM}-{x}-{y}.png"
            if path.exists():
                continue
            response = session.get(f"https://tile.openstreetmap.org/{ZOOM}/{x}/{y}.png", timeout=30)
            response.raise_for_status()
            if not response.headers.get("content-type", "").startswith("image/png"):
                raise RuntimeError("Expected a PNG map tile")
            path.write_bytes(response.content)
            downloaded += 1
    print(f"Downloaded {downloaded} tiles; cached tiles retained for reuse.")
