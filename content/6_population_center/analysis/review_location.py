"""Check street names and save dated aerial context for the computed point."""
import json,hashlib,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from shapely.geometry import shape,Point
from shapely.ops import transform
from pyproj import Transformer
R=Path(__file__).resolve().parent;r=json.loads((R/'results.json').read_text())
T=Transformer.from_crs(4326,26918,always_xy=True).transform;c=Point(r['easting'],r['northing'])
city_path=R.parents[1]/'4_name_changes/analysis/streets_city_reference.geojson'
rows=[];fs=[]
for f in json.loads(city_path.read_text())['features']:
    d=transform(T,shape(f['geometry'])).distance(c)
    if d<180:rows.append({'name':f['properties'].get('FULLNAME'),'distance_metres':d});fs.append(f)
rows.sort(key=lambda r:r['distance_metres'])
(R/'city_street_check.geojson').write_text(json.dumps({'type':'FeatureCollection','features':fs},separators=(',',':')))
web=Transformer.from_crs(4326,3857,always_xy=True).transform
x,y=web(r['longitude'],r['latitude']);bounds=[x-250,y-250,x+250,y+250]
url='https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer/export?'+urllib.parse.urlencode({'bbox':','.join(map(str,bounds)),'bboxSR':3857,'imageSR':3857,'size':'1000,1000','format':'png','f':'image'})
raw=urllib.request.urlopen(url,timeout=45).read();(R/'population_center_aerial_2022.png').write_bytes(raw)
(R/'location_review.json').write_text(json.dumps({'city_street_source':'https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Streets/FeatureServer/0','city_street_snapshot_date':'2026-09-19','city_street_snapshot_sha256':hashlib.sha256(city_path.read_bytes()).hexdigest(),'nearby_streets':rows,'aerial_url':url,'aerial_bounds_3857':bounds,'aerial_year':2022,'downloaded_utc':datetime.now(timezone.utc).isoformat(),'aerial_sha256':hashlib.sha256(raw).hexdigest(),'limitation':'Dated imagery is a location check, not evidence of current site conditions or public access.'},indent=2))
print(json.dumps(rows[:6],indent=2))
