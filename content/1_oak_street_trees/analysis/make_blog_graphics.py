"""Render reproducible blog PNGs with exact CSV counts and geographic positions.

Dependencies: pandas, Pillow, requests.
First run download_map_tiles.py if map_tiles is not already populated.
AI-generated tree-icons.png supplies symbolic art, never geographic data.
"""
from pathlib import Path
import json
import re
import math

import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps

from download_map_tiles import ZOOM, WIDTH, HEIGHT, LEFT, TOP, world_pixel

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT.parent / "images"
IMAGES.mkdir(exist_ok=True)
BG = "#f7f3e8"
INK = "#213d32"
MUTED = "#616a5e"
LINE = "#d6d7c9"
COLORS = {"oak": "#225c41", "maple": "#ad651e", "lilac": "#75894d"}
FONT_DIR = Path("C:/Windows/Fonts")


def font(size, serif=False, bold=False):
    name = "georgiab.ttf" if serif and bold else "georgia.ttf" if serif else "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def text(canvas, xy, value, size=30, color=INK, serif=False, bold=False, anchor=None):
    ImageDraw.Draw(canvas).text(xy, value, font=font(size, serif, bold), fill=color, anchor=anchor)


data = pd.read_csv(ROOT / "Syracuse_Tree_Data_7832308158023752279.csv")
data["tree_name"] = data.SPP_COM.fillna("").str.split(",").str[0].str.strip().str.lower()
mask = [bool(t) and bool(re.search(r"\b" + re.escape(t) + r"\b", s.lower()))
        for t, s in zip(data.tree_name, data.STREET.fillna(""))]
matches = data.loc[mask].copy()
assert matches.ID.is_unique
assert matches[["LATITUDE", "LONGITUDE"]].notna().all().all()

# Extract the three isolated illustrations from the transparent sprite sheet.
sheet = Image.open(IMAGES / "tree-icons.png").convert("RGBA")
assert sheet.getchannel("A").getextrema()[0] == 0, "Icons must have transparency"
icons = {}
for i, name in enumerate(("oak", "maple", "lilac")):
    tile = sheet.crop((round(i * sheet.width / 3), 0, round((i + 1) * sheet.width / 3), sheet.height))
    icons[name] = tile.crop(tile.getbbox())
    icons[name].save(IMAGES / f"icon-{name}.png")


def tree(canvas, kind, bottom_center, height):
    source = icons[kind]
    art = source.resize((round(source.width * height / source.height), height), Image.Resampling.LANCZOS)
    x, y = bottom_center
    canvas.paste(art, (round(x - art.width / 2), round(y - height)), art)


groups = [("Oak St", "oak"), ("Maple St", "maple"), ("Maple Ter", "maple"), ("Lilac St", "lilac")]
counts = {street: int(matches.STREET.eq(street).sum()) for street, _ in groups}
assert sum(counts.values()) == len(matches)

# Assemble real OSM tiles in the same Web Mercator projection as our points.
basemap = Image.new("RGB", (WIDTH, HEIGHT), BG)
for x in range(LEFT // 256, (LEFT + WIDTH - 1) // 256 + 1):
    for y in range(TOP // 256, (TOP + HEIGHT - 1) // 256 + 1):
        tile = Image.open(ROOT / "map_tiles" / f"{ZOOM}-{x}-{y}.png").convert("RGB")
        basemap.paste(tile, (x * 256 - LEFT, y * 256 - TOP))
# A muted map keeps the illustrated trees legible while preserving street geometry.
basemap = Image.blend(ImageOps.grayscale(basemap).convert("RGB"), Image.new("RGB", basemap.size, BG), 0.38)

canvas = Image.new("RGB", (2400, 2100), BG)
draw = ImageDraw.Draw(canvas)
text(canvas, (80, 60), "SYRACUSE  /  A VERY LITERAL URBAN FOREST", 28, MUTED, bold=True)
text(canvas, (75, 125), "Trees that understood", 112, serif=True, bold=True)
text(canvas, (75, 249), "the assignment.", 112, serif=True, bold=True)
text(canvas, (84, 390), f"{len(matches)} trees. {len(groups)} streets. A suspicious amount of nominative determinism.", 36)

MX, MY = 80, 480
canvas.paste(basemap, (MX, MY))
draw.rectangle((MX, MY, MX + WIDTH, MY + HEIGHT), outline=LINE, width=2)

points = []
for row in matches.itertuples():
    wx, wy = world_pixel(row.LONGITUDE, row.LATITUDE)
    x, y = MX + wx - LEFT, MY + wy - TOP
    assert MX <= x <= MX + WIDTH and MY <= y <= MY + HEIGHT
    points.append(dict(id=int(row.ID), street=row.STREET, kind=row.tree_name, x=x, y=y,
                       latitude=row.LATITUDE, longitude=row.LONGITUDE))

# Offset crowded illustrations, never the location dots. Leader lines connect
# displaced trunk bases to exact CSV coordinates. Offsets are display pixels.
offsets = {
    50389: (-32, -14), 56066: (37, 4),
    57720: (-45, -18), 57726: (38, -15),
    81957: (-41, 13), 81958: (-53, -55), 81959: (25, 42),
    49260: (65, 5), 50606: (15, 75), 50607: (0, -24),
    50608: (-30, -24), 53356: (-12, 71),
    76030: (-34, -13), 76031: (36, -5),
}
for point in points:
    dx, dy = offsets.get(point["id"], (0, -8))
    point["icon_x"], point["icon_y"] = point["x"] + dx, point["y"] + dy
    draw.line((point["x"], point["y"], point["icon_x"], point["icon_y"]), fill=COLORS[point["kind"]], width=3)
for point in sorted(points, key=lambda p: p["icon_y"]):
    tree(canvas, point["kind"], (point["icon_x"], point["icon_y"]), 76)
for point in points:
    x, y = point["x"], point["y"]
    draw.ellipse((x-5, y-5, x+5, y+5), fill=COLORS[point["kind"]], outline=BG, width=2)


def callout(label, detail, xy, target):
    x, y = xy
    tw = max(draw.textlength(label, font=font(32, bold=True)), draw.textlength(detail, font=font(25)))
    w, h = int(tw) + 36, 88
    draw.line((x+w/2, y+h/2, target[0], target[1]), fill=INK, width=2)
    draw.rounded_rectangle((x, y, x+w, y+h), 9, fill=BG, outline=LINE, width=2)
    text(canvas, (x+18, y+9), label, 32, bold=True)
    text(canvas, (x+18, y+50), detail, 25, MUTED)


def centroid(street):
    ps = [p for p in points if p["street"] == street]
    return sum(p["x"] for p in ps)/len(ps), sum(p["y"] for p in ps)/len(ps)

callout("Oak St", "6 oaks. On brand.", (1040, 620), centroid("Oak St"))
callout("Lilac St", "One tree. Full commitment.", (145, 660), centroid("Lilac St"))
callout("Maple St", "6 maples", (1160, 1310), centroid("Maple St"))
callout("Maple Ter", "6 more maples", (1120, 1645), centroid("Maple Ter"))

# North and scale bar are calculated in the map's local latitude.
draw.rounded_rectangle((110, 1730, 445, 1855), 8, fill=BG)
text(canvas, (140, 1748), "N ↑", 28, bold=True)
meters_per_pixel = math.cos(math.radians(43.057)) * 2 * math.pi * 6378137 / (256 * 2**ZOOM)
scale_length = round(500 / meters_per_pixel)
draw.line((142, 1828, 142+scale_length, 1828), fill=INK, width=5)
for sx in (142, 142+scale_length):
    draw.line((sx, 1819, sx, 1837), fill=INK, width=4)
text(canvas, (142+scale_length+15, 1809), "500 m", 25)

RX = 1610
text(canvas, (RX, 495), "THE HONOR ROLL", 30, MUTED, bold=True)
text(canvas, (RX, 546), "One picture. One tree.", 36, serif=True)
for index, (street, kind) in enumerate(groups):
    top = 650 + index * 245
    text(canvas, (RX, top), street, 46, serif=True, bold=True)
    text(canvas, (2295, top+2), str(counts[street]), 46, bold=True, anchor="ra")
    for j in range(counts[street]):
        tree(canvas, kind, (RX+48+j*100, top+166), 104)
    draw.line((RX, top+194, 2310, top+194), fill=LINE, width=2)

text(canvas, (RX, 1665), "Apparently, some trees", 36, serif=True)
text(canvas, (RX, 1718), "read the street signs.", 36, serif=True)
text(canvas, (RX, 1820), "Art identifies broad tree groups;", 25, MUTED)
text(canvas, (RX, 1856), "canopy size and season are illustrative.", 25, MUTED)

text(canvas, (80, 1930), "Dots mark recorded locations. Nearby illustrations are offset for legibility and connected by lines.", 27, MUTED)
text(canvas, (80, 1973), "Whole-word common-name matches only: Oakwood and Maplehurst sit this round out. Aliases are not normalized.", 27, MUTED)
text(canvas, (80, 2016), "Source: supplied Syracuse tree inventory CSV  •  Basemap © OpenStreetMap contributors (openstreetmap.org/copyright)", 25, MUTED)
canvas.save(IMAGES / "trees-map-blog.png", dpi=(200, 200))

# A second, standalone tree pictogram for a narrower blog column.
chart = Image.new("RGB", (1800, 1250), BG)
text(chart, (80, 55), "SYRACUSE / THE HONOR ROLL", 25, MUTED, bold=True)
text(chart, (75, 112), "A bar chart, but make it trees.", 66, serif=True, bold=True)
text(chart, (82, 208), "Trees growing on streets that share their common name. One icon = one tree.", 30)
for index, (street, kind) in enumerate(groups):
    yy = 380 + index * 195
    text(chart, (80, yy), street, 42, serif=True, bold=True)
    for j in range(counts[street]):
        tree(chart, kind, (570 + j*165, yy+95), 135)
    text(chart, (1655, yy+12), str(counts[street]), 60, bold=True)
text(chart, (80, 1140), "19 matching trees • Whole-word matches • Source: supplied Syracuse tree inventory CSV", 27, MUTED)
text(chart, (80, 1185), "Illustrations are symbolic. Common names use the text before the comma; aliases are not normalized.", 23, MUTED)
chart.save(IMAGES / "trees-pictogram-blog.png", dpi=(200, 200))

matches.to_csv(ROOT / "blog_map_trees.csv", index=False)
(ROOT / "blog_map_audit.json").write_text(json.dumps({"counts": counts, "points": points}, indent=2), encoding="utf-8")
print(f"Rendered {len(points)} map points; pictogram counts: {counts}")
print("Saved trees-map-blog.png (2400 x 2100) and trees-pictogram-blog.png (1800 x 1250)")
