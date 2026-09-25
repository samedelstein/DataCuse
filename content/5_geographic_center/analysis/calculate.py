"""Download the municipal polygon and calculate an area-weighted center."""
import json, hashlib, math, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from shapely.geometry import shape, mapping, Point
from shapely.ops import transform, unary_union
from pyproj import Transformer, Geod
ROOT = Path(__file__).resolve().parent
SERVICE = 'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Civil_Boundaries/MapServer/4'
def download(url, name):
    raw = urllib.request.urlopen(url, timeout=60).read()
    (ROOT/name).write_bytes(raw)
    return json.loads(raw), {'url':url,'file':name,'sha256':hashlib.sha256(raw).hexdigest(),'downloaded_utc':datetime.now(timezone.utc).isoformat()}
if not (ROOT/'syracuse_boundary.geojson').exists():
    meta, a = download(SERVICE+'?f=pjson', 'boundary_metadata.json')
    params = urllib.parse.urlencode({'where':"NAME = 'Syracuse'",'outFields':'*','outSR':4326,'f':'geojson'})
    data, b = download(SERVICE+'/query?'+params, 'syracuse_boundary.geojson')
    (ROOT/'provenance.json').write_text(json.dumps([a,b],indent=2))
else:
    data = json.loads((ROOT/'syracuse_boundary.geojson').read_text())
assert len(data['features']) == 1
boundary = shape(data['features'][0]['geometry'])
assert boundary.is_valid
project = Transformer.from_crs(4326,26918,always_xy=True).transform
unproject = Transformer.from_crs(26918,4326,always_xy=True).transform
b = transform(project,boundary)
c = b.centroid
lon,lat = unproject(c.x,c.y)
ea = transform(Transformer.from_crs(4326,5070,always_xy=True).transform,boundary).centroid
elon,elat = Transformer.from_crs(5070,4326,always_xy=True).transform(ea.x,ea.y)
geod = Geod(ellps='WGS84')
# Independent shoelace calculation, including signed interior-ring areas.
def ring_moments(coords):
    # Offset to avoid cancellation from large projected coordinates.
    pts = [(x-c.x,y-c.y) for x,y in coords]
    twice = mx = my = 0
    for (x,y),(u,v) in zip(pts,pts[1:]):
        cross = x*v-u*y
        twice += cross; mx += (x+u)*cross; my += (y+v)*cross
    return twice/2, mx/6, my/6
area = mx = my = 0
for poly in ([b] if b.geom_type=='Polygon' else b.geoms):
    for ring,sign in [(poly.exterior,1)]+[(r,-1) for r in poly.interiors]:
        a,x,y = ring_moments(ring.coords)
        direction=sign*(1 if a>0 else -1)
        area+=direction*a; mx+=direction*x; my+=direction*y
independent = Point(c.x+mx/area,c.y+my/area)
roads_path=ROOT.parents[1]/'4_name_changes/analysis/streets_nys_current.geojson'
roads=json.loads(roads_path.read_text())['features']
near=[]; context=[]; context_area=b.buffer(400)
for feature in roads:
    road=transform(project,shape(feature['geometry']))
    name=feature['properties'].get('CompleteStreetName','')
    if not name: continue
    dist=road.distance(c)
    if dist < 500:
        near.append({'name':name,'distance_metres':dist,'id':feature['properties'].get('NYSStreetID')})
    if road.intersects(context_area):
        context.append({'type':'Feature','properties':{'name':name},'geometry':feature['geometry']})
near.sort(key=lambda r:r['distance_metres'])
(ROOT/'streets_context.geojson').write_text(json.dumps({'type':'FeatureCollection','features':context},separators=(',',':')))
results={'definition':'Area-weighted centroid of full NYS Syracuse municipal polygon; water inside the boundary is included.', 'source':SERVICE,'projection':'EPSG:26918 (NAD83 / UTM zone 18N)', 'latitude':lat,'longitude':lon,'easting':c.x,'northing':c.y,'area_square_miles':b.area/1609.344**2,'area_square_metres':b.area,'inside_city':b.contains(c),'equal_area_check':{'projection':'EPSG:5070','latitude':elat,'longitude':elon,'separation_metres':geod.inv(lon,lat,elon,elat)[2]},'independent_centroid_difference_metres':c.distance(independent),'source_properties':data['features'][0]['properties'],'nearest_street_segments':near[:15],'street_source':{'file':'../../4_name_changes/analysis/streets_nys_current.geojson','download_date':'2026-09-19','sha256':hashlib.sha256(roads_path.read_bytes()).hexdigest()}}
assert results['inside_city']
assert results['independent_centroid_difference_metres'] < .001
assert results['equal_area_check']['separation_metres'] < 5
(ROOT/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))

