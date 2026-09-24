"""Verify whole-path measurements independently from saved geometry."""
import json,math
from pathlib import Path
from shapely.geometry import shape,LineString
from shapely.ops import transform
from pyproj import Transformer
from straightness import score
ROOT=Path(__file__).resolve().parent
T=Transformer.from_crs(4326,26918,always_xy=True).transform
assert score(LineString([(0,0),(50,0),(100,0)]))['ratio']==1
elbow=score(LineString([(0,0),(100,0),(100,100)]))
assert abs(elbow['ratio']-math.sqrt(2))<1e-12
assert abs(elbow['max_offset_m']-math.sqrt(5000))<1e-9
fs=json.loads((ROOT/'straightness_geometry.geojson').read_text())['features']
for f in fs:
    p=f['properties'];g=transform(T,shape(f['geometry']));pts=list(g.coords)
    a=pts[0];b=pts[-1];vx=b[0]-a[0];vy=b[1]-a[1];d2=vx*vx+vy*vy
    offsets=[]
    for x,y in pts:
        t=max(0,min(1,((x-a[0])*vx+(y-a[1])*vy)/d2))
        offsets.append(math.hypot(x-a[0]-t*vx,y-a[1]-t*vy))
    length=sum(math.dist(x,y) for x,y in zip(pts,pts[1:]))
    assert abs(length-p['length_m'])<1e-5
    assert abs(max(offsets)-p['max_offset_m'])<1e-5
    assert abs(length/math.sqrt(d2)-p['ratio'])<1e-7
    assert abs(sum(p['run_lengths_m'])-length)<.01
    assert p['changes']==len(p['names'])-1
r=json.loads((ROOT/'straightness_results.json').read_text())
assert r['sensitivity'][0]['max_changes']==2
assert len(r['sensitivity'][0]['winners'])==2
assert all(s['max_changes']==2 for s in r['sensitivity'])
out=dict(passed=True,geometry_windows_checked=len(fs),toy_cases=['straight line','right-angle elbow'],
         checks=['independent endpoint distance','independent maximum finite-chord offset','path length','name-run length conservation','name-change counts','baseline and sensitivity maxima'])
(ROOT/'straightness_validation.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
