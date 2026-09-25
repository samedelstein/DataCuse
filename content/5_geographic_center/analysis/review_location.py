import json, math, urllib.request, urllib.parse, hashlib
from pathlib import Path
from datetime import datetime, timezone
from shapely.geometry import shape,Point,mapping
from shapely.ops import transform
from pyproj import Transformer
R=Path(__file__).resolve().parent
r=json.loads((R/'results.json').read_text())
t=Transformer.from_crs(4326,3857,always_xy=True).transform
x,y=t(r['longitude'],r['latitude']); bounds=[x-250,y-250,x+250,y+250]
url='https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer/export?'+urllib.parse.urlencode(dict(bbox=','.join(map(str,bounds)),bboxSR=3857,imageSR=3857,size='1000,1000',format='png',f='image'))
raw=urllib.request.urlopen(url,timeout=45).read(); (R/'center_aerial_2022.png').write_bytes(raw)
city_path=R.parents[1]/'4_name_changes/analysis/streets_city_reference.geojson'
city=json.loads(city_path.read_text())
project=Transformer.from_crs(4326,26918,always_xy=True).transform
c=Point(r['easting'],r['northing']); near=[]; features=[]
for f in city['features']:
    g=transform(project,shape(f['geometry'])); d=g.distance(c)
    if d<160:
        near.append({'name':f['properties'].get('FULLNAME'),'distance_metres':d}); features.append(f)
near.sort(key=lambda a:a['distance_metres'])
(R/'city_streets_check.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features}))
(R/'location_review.json').write_text(json.dumps({'aerial_url':url,'aerial_bounds_3857':bounds,'aerial_year':2022,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'aerial_sha256':hashlib.sha256(raw).hexdigest(),'city_streets_source':'https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Streets/FeatureServer/0','city_streets_downloaded':'2026-09-19','city_streets_sha256':hashlib.sha256(city_path.read_bytes()).hexdigest(),'nearby_city_streets':near,'limitation':'2022 aerial is historical. No claim about current buildings, construction, or public access.'},indent=2))
print(json.dumps(near[:5],indent=2))
