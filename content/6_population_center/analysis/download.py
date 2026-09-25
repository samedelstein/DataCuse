"""Download matching 2020 Census place and block geography, including POP100."""
import json,hashlib,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
BASE='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2020/tigerWMS_Census2020/MapServer'
manifest_path=R/'provenance.json'
manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else []
def fetch(layer,params,name):
    path=R/name
    if path.exists():return json.loads(path.read_text())
    url=BASE+'/'+str(layer)+('/query' if 'where' in params else '')+'?'+urllib.parse.urlencode(params)
    with urllib.request.urlopen(url,timeout=90) as response: raw=response.read()
    data=json.loads(raw)
    if 'error' in data:raise RuntimeError(data['error'])
    if data.get('exceededTransferLimit'):raise RuntimeError('Incomplete Census download')
    path.write_bytes(raw)
    manifest.append({'file':name,'url':url,'downloaded_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    manifest_path.write_text(json.dumps(manifest,indent=2))
    return data
fetch(10,{'f':'pjson'},'blocks_metadata.json')
fetch(26,{'f':'pjson'},'place_metadata.json')
place=fetch(26,{'where':"STATE='36' AND PLACE='73000'",'outFields':'*','outSR':4326,'f':'geojson'},'syracuse_place_2020.geojson')
assert len(place['features'])==1
from shapely.geometry import shape
bounds=shape(place['features'][0]['geometry']).bounds
params={'where':"STATE='36' AND COUNTY='067'",'geometry':','.join(map(str,bounds)),'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','outSR':4326,'f':'geojson','orderByFields':'GEOID','resultRecordCount':10000}
blocks=fetch(10,params,'blocks_candidate_2020.geojson')
print(json.dumps({'place_properties':place['features'][0]['properties'],'candidate_blocks':len(blocks['features']),'sample':blocks['features'][0]['properties']},indent=2))
