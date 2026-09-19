"""Prioritize short links for aerial review; this is not a final block classifier."""
import csv,json
from collections import defaultdict
from shapely.geometry import shape,Point
from shapely.ops import transform
from calculate import ROOT,PROJECT

fs=json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']
byname=defaultdict(list);byid={}
for f in fs:
    g=transform(PROJECT,shape(f['geometry']))
    byname[(f['properties']['CompleteStreetName'] or '').upper()].append(g)
    byid[f['properties']['NYSStreetID']]=g
rows=list(csv.DictReader((ROOT/'block_rankings.csv').open(encoding='utf-8-sig')))
review=[]
for r in rows:
    if float(r['length_ft'])>100:break
    ids=r['source_ids'].split(';')
    if len(ids)!=1:continue
    g=byid[ids[0]]
    if g.geom_type!='LineString':continue
    p0,p1=Point(g.coords[0]),Point(g.coords[-1]);dx=p1.x-p0.x;dy=p1.y-p0.y
    crosses=[]
    for p in (p0,p1):
        side=set();labels=set()
        for name in set((r['endpoint_a']+';'+r['endpoint_b']).split(';')):
            for h in byname[name]:
                if h.geom_type!='LineString' or p.distance(h)>0.5:continue
                d=h.project(p)
                for target in (max(0,d-10),min(h.length,d+10)):
                    q=h.interpolate(target)
                    if p.distance(q)<1:continue
                    cross=dx*(q.y-p.y)-dy*(q.x-p.x)
                    if abs(cross)>1:side.add(1 if cross>0 else -1);labels.add(name)
        crosses.append((side,labels))
    if crosses[0][0]&crosses[1][0] and not crosses[0][1]&crosses[1][1]:
        review.append(r)
print(json.dumps(review,indent=2))
(ROOT/'junction_review_queue.json').write_text(json.dumps(review,indent=2))
