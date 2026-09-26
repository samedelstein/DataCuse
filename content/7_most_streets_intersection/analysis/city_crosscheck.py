import json,math,sys,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from shapely.geometry import shape,Point,mapping
from shapely.ops import transform
from pyproj import Transformer
R=Path(__file__).resolve().parent;S=R.parents[1]/'4_name_changes/analysis';T=Transformer.from_crs(4326,26918,always_xy=True).transform;U=Transformer.from_crs(26918,4326,always_xy=True).transform
boundary=transform(T,shape(json.loads((S/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']))
nodes=defaultdict(list);seen=set();excluded=Counter()
for f in json.loads((S/'streets_city_reference.geojson').read_text())['features']:
 p=f['properties'];name=' '.join((p.get('FULLNAME') or '').upper().split());fcc=p.get('CFCC','')
 if not name or 'UNNAMED' in name or not (fcc.startswith(('A2','A3','A4')) or fcc in ('A61','A62')):excluded['class_or_name']+=1;continue
 g=transform(T,shape(f['geometry']))
 if g.geom_type!='LineString':excluded['multipart']+=1;continue
 sig=(name,g.normalize().wkb)
 if sig in seen:excluded['duplicate']+=1;continue
 seen.add(sig)
 for end,key in [(0,'FNODE_'),(-1,'TNODE_')]:
  x,y=g.coords[end];nodes[p[key]].append({'id':p['FID'],'name':name,'x':x,'y':y})
rows=[]
for key,arms in nodes.items():
 if len(arms)<3:continue
 x=sum(a['x'] for a in arms)/len(arms);y=sum(a['y'] for a in arms)/len(arms)
 if not boundary.covers(Point(x,y)):continue
 lon,lat=U(x,y);names=sorted({a['name'] for a in arms});rows.append({'node':key,'arms':len(arms),'name_count':len(names),'names':names,'x':x,'y':y,'longitude':lon,'latitude':lat,'diameter_m':max(math.hypot(a['x']-b['x'],a['y']-b['y']) for a in arms for b in arms)})
rows.sort(key=lambda r:(-r['arms'],-r['name_count']));matches=[]
for r in json.loads((R/'node_rankings.json').read_text())[:6]:
 nearest=sorted(rows,key=lambda c:math.hypot(c['x']-r['x'],c['y']-r['y']))[:3]
 matches.append({'nys_node':r['node'],'nys_names':r['names'],'city_nearby':[dict(c,distance_from_nys_m=math.hypot(c['x']-r['x'],c['y']-r['y'])) for c in nearest]})
(R/'city_crosscheck.json').write_text(json.dumps({'method':'Independent city FNODE_/TNODE_ topology, surface street CFCC classes; exact duplicate name/geometry removed. Older reference, not same-date ground truth.','excluded':dict(excluded),'intersection_count':len(rows),'top':[r for r in rows if r['arms']>=5 or r['name_count']>=4],'matches':matches},indent=2))
print('CITY TOP',json.dumps(rows[:12],indent=2))
print('MATCHES',json.dumps(matches,indent=2))
