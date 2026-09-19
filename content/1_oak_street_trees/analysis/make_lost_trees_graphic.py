"""Render the lost-trees companion. Importing the shared art module also
regenerates the original map and pictogram, keeping the set consistent.
"""
import json
import math
from PIL import Image, ImageDraw
import make_blog_graphics as art

d = art.data
selected = d[d.STREET.eq("Oak St") & d.tree_name.isin(["oak", "maple"])].copy()
counts = selected.groupby("tree_name").size().to_dict()
assert counts == {"maple": 56, "oak": 6}

out = Image.new("RGB", (2400, 2100), art.BG)
draw = ImageDraw.Draw(out)
art.text(out, (80, 60), "LOST TREES / SYRACUSE", 30, art.MUTED, bold=True)
art.text(out, (75, 128), "Oak Street has", 115, serif=True, bold=True)
art.text(out, (75, 258), "an identity crisis.", 115, serif=True, bold=True)
art.text(out, (83, 405), "56 maples. 6 oaks. Someone missed the memo.", 42)

# Crop and enlarge the cached, projected basemap around the Oak St corridor.
cx, cy = art.world_pixel(-76.1348, 43.0628)
crop_w, crop_h = 770, 980
left = round(cx - art.LEFT - crop_w/2)
top = round(cy - art.TOP - crop_h/2)
assert left >= 0 and top >= 0 and left+crop_w <= art.WIDTH and top+crop_h <= art.HEIGHT
map_w, map_h = 1100, 1400
mx, my = 80, 500
map_image = art.basemap.crop((left, top, left+crop_w, top+crop_h)).resize((map_w, map_h), Image.Resampling.LANCZOS)
out.paste(map_image, (mx, my))
draw.rectangle((mx, my, mx+map_w, my+map_h), outline=art.LINE, width=2)
scale = map_w / crop_w

points = []
for row in selected.itertuples():
    wx, wy = art.world_pixel(row.LONGITUDE, row.LATITUDE)
    x = mx + (wx-art.LEFT-left)*scale
    y = my + (wy-art.TOP-top)*scale
    assert mx < x < mx+map_w and my < y < my+map_h
    points.append(dict(id=int(row.ID), species=row.SPP_COM, kind=row.tree_name, x=x, y=y,
                       latitude=row.LATITUDE, longitude=row.LONGITUDE))

# Place symbols near exact points without overlaps; dots stay geographically fixed.
occupied = []
for p in sorted(points, key=lambda p: (p["y"], p["x"])):
    candidates = [(dx, dy) for dx in range(-280, 281, 28) for dy in range(-136, 153, 24)]
    candidates.sort(key=lambda v: v[0]**2 + (v[1]+8)**2)
    for dx, dy in candidates:
        px, py = p["x"]+dx, p["y"]+dy
        box = (px-25, py-52, px+25, py+4)
        if all(box[2] <= b[0] or box[0] >= b[2] or box[3] <= b[1] or box[1] >= b[3] for b in occupied):
            occupied.append(box)
            p["icon_x"], p["icon_y"] = px, py
            break
    else:
        raise RuntimeError("Could not place a tree icon without overlap")
    draw.line((p["x"], p["y"], p["icon_x"], p["icon_y"]), fill=art.COLORS[p["kind"]], width=2)
for p in points:
    art.tree(out, p["kind"], (p["icon_x"], p["icon_y"]), 48)
for p in points:
    x, y = p["x"], p["y"]
    draw.ellipse((x-4, y-4, x+4, y+4), fill=art.COLORS[p["kind"]], outline=art.BG, width=1)

draw.rounded_rectangle((110, 535, 440, 640), 8, fill=art.BG)
art.text(out, (132, 552), "OAK STREET", 34, bold=True)
art.text(out, (132, 595), "Syracuse, New York", 25, art.MUTED)
draw.rounded_rectangle((110, 1740, 550, 1860), 8, fill=art.BG)
art.text(out, (138, 1752), "N ↑", 26, bold=True)
mpp = math.cos(math.radians(43.0628))*2*math.pi*6378137/(256*2**art.ZOOM)/scale
length = round(500/mpp)
draw.line((138, 1828, 138+length, 1828), fill=art.INK, width=4)
art.text(out, (138+length+14, 1808), "500 m", 25)

rx = 1300
art.text(out, (rx, 520), "THE WRONG ADDRESS CLUB", 30, art.MUTED, bold=True)
art.text(out, (rx, 572), "Maples on Oak St", 51, serif=True, bold=True)
art.text(out, (2280, 562), "56", 70, bold=True, anchor="ra")
art.text(out, (rx, 645), "Every illustrated tree counts as one.", 28, art.MUTED)
for i in range(counts["maple"]):
    art.tree(out, "maple", (rx+53+(i%8)*122, 800+(i//8)*103), 83)

draw.line((rx, 1468, 2310, 1468), fill=art.LINE, width=2)
art.text(out, (rx, 1500), "Oaks on Oak St", 51, serif=True, bold=True)
art.text(out, (2280, 1490), "6", 70, bold=True, anchor="ra")
for i in range(counts["oak"]):
    art.tree(out, "oak", (rx+53+i*122, 1685), 83)
art.text(out, (rx, 1760), "Outnumbered on their own street.", 36, serif=True)
art.text(out, (rx, 1822), "The map shows these 62 trees only.", 28, art.MUTED)
art.text(out, (rx, 1864), "Oak St has other kinds of trees, too.", 28, art.MUTED)

art.text(out, (80, 1937), "Elsewhere: 11 oaks on Butternut St. 8 on Walnut Pl. 4 on Cedar St. The plot thickens.", 31)
art.text(out, (80, 1986), "Dots mark CSV coordinates; illustrated trees are offset and connected to keep every tree visible. Art is symbolic.", 26, art.MUTED)
art.text(out, (80, 2027), "Source: supplied Syracuse tree inventory CSV  •  Basemap © OpenStreetMap contributors (openstreetmap.org/copyright)", 25, art.MUTED)
out.save(art.IMAGES / "lost-trees-oak-street.png", dpi=(200, 200))
selected.to_csv(art.ROOT / "lost_trees_oak_street.csv", index=False)
(art.ROOT / "lost_trees_audit.json").write_text(json.dumps({"counts": counts, "points": points}, indent=2), encoding="utf-8")
print(f"Rendered {len(points)} geographic points and {sum(counts.values())} pictogram trees")
print("Saved lost-trees-oak-street.png (2400 x 2100)")
