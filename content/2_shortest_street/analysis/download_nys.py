"""Download current NYS streets in a Syracuse-area envelope and city boundary."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
STREETS = 'https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS_Streets/FeatureServer/0'
BOUNDARY = 'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Civil_Boundaries/MapServer/4'

def get(url, **params):
    with urlopen(url, data=urlencode(params).encode(), timeout=90) as response:
        data = json.load(response)
    if 'error' in data:
        raise RuntimeError(data['error'])
    return data

def save(name, data):
    (ROOT / name).write_text(json.dumps(data), encoding='utf-8')

if __name__ == '__main__':
    bmeta = get(BOUNDARY, f='json')
    save('boundary_metadata.json', bmeta)
    print('Boundary fields:', [f['name'] for f in bmeta['fields']], flush=True)
    boundary = get(BOUNDARY+'/query', where="NAME='Syracuse'", outFields='*', outSR=4326, f='geojson')
    assert len(boundary['features']) == 1, boundary
    save('syracuse_boundary.geojson', boundary)
    meta = get(STREETS, f='json')
    save('nys_metadata.json', meta)
    selection = dict(geometry='-76.25,42.97,-76.04,43.13', geometryType='esriGeometryEnvelope', inSR=4326, spatialRel='esriSpatialRelIntersects', where='1=1')
    ids = sorted(get(STREETS+'/query', **selection, returnIdsOnly='true', f='json')['objectIds'])
    features = []
    for i in range(0, len(ids), 1000):
        data = get(STREETS+'/query', objectIds=','.join(map(str,ids[i:i+1000])), outFields='*', returnGeometry='true', outSR=4326, f='geojson')
        features.extend(data['features'])
    assert sorted(f['properties']['OBJECTID'] for f in features) == ids
    save('streets_nys_current.geojson', dict(type='FeatureCollection',features=features))
    save('nys_provenance.json',dict(downloaded_utc=datetime.now(timezone.utc).isoformat(),streets_url=STREETS,boundary_url=BOUNDARY,selection=selection,feature_count=len(features),editingInfo=meta.get('editingInfo')))
    print('Downloaded',len(features),'streets; boundary:',boundary['features'][0]['properties'])
